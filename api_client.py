"""
Centralized API client for Yandex Tracker with rate limiting and error handling.
"""

import logging
import time
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from translations import t

logger = logging.getLogger(__name__)


class PermissionDeniedError(requests.HTTPError):
    """Custom exception for 403 permission denied errors with additional context."""
    
    def __init__(self, message: str, access_issue_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.access_issue_data = access_issue_data


@dataclass
class ApiResponse:
    """Wrapper for API response data."""
    data: Any
    status_code: int
    headers: Dict[str, str]
    url: str
    elapsed_time: float


class RateLimiter:
    """Rate limiter to ensure we don't exceed API limits."""
    
    def __init__(self, max_requests_per_second: float = 5.0):
        """Initialize rate limiter.
        
        Args:
            max_requests_per_second: Maximum requests per second allowed
        """
        self.max_rps = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
        self.request_count = 0
        self.rate_limit_hits = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def reduce_rate_on_limit_hit(self):
        """Reduce rate limit when hitting 429 errors."""
        self.rate_limit_hits += 1
        if self.max_rps > 3.0:
            old_rps = self.max_rps
            self.max_rps = 3.0
            self.min_interval = 1.0 / self.max_rps
            logger.warning(f"Rate limit hit! Reducing RPS from {old_rps} to {self.max_rps}")
        else:
            # Already at minimum, increase delay further
            self.min_interval = min(self.min_interval * 1.5, 2.0)  # Cap at 2 seconds
            logger.warning(f"Rate limit hit again! Increasing delay to {self.min_interval:.2f}s between requests")


class TrackerApiClient:
    """Centralized API client for Yandex Tracker with rate limiting and error handling."""
    
    def __init__(self, token: str, org_id: str, org_type: str = "360", max_rps: float = 5.0):
        """Initialize API client.
        
        Args:
            token: OAuth token for authentication
            org_id: Organization ID
            org_type: Organization type ('360' or 'cloud')
            max_rps: Maximum requests per second
        """
        self.base_url = "https://api.tracker.yandex.net"
        self.token = token
        self.org_id = org_id
        self.org_type = org_type
        self.rate_limiter = RateLimiter(max_rps)
        
        # Set up headers
        self.headers = {
            'Authorization': f'OAuth {token}',
            'Content-Type': 'application/json'
        }
        
        if org_type == "cloud":
            self.headers['X-Cloud-Org-ID'] = org_id
        else:
            self.headers['X-Org-ID'] = org_id
        
        # Statistics
        self.total_requests = 0
        self.failed_requests = 0
        self.start_time = datetime.now()
    
    def _log_permission_denied_error(self, url: str, response):
        """Log detailed information about 403 permission denied errors to file only.
        
        Args:
            url: The URL that was requested
            response: The HTTP response object
            
        Returns:
            Dict with parsed error information or None if parsing failed
        """
        try:
            # Parse the JSON response to extract useful information
            error_data = response.json()
            
            # Extract key information
            queue_info = error_data.get('errorsData', {}).get('queue', {})
            owner_info = error_data.get('errorsData', {}).get('owner', {})
            error_messages = error_data.get('errorMessages', [])
            permission_message = error_data.get('errorsData', {}).get('permissionDeniedMessage', '')
            
            # Build a comprehensive log message
            log_parts = [
                f"Permission denied for request: {url}",
                f"Queue: {queue_info.get('key', 'Unknown')} - {queue_info.get('display', 'Unknown')}",
            ]
            
            if queue_info.get('deleted'):
                log_parts.append("Note: Queue is marked as deleted")
            
            if owner_info:
                owner_display = owner_info.get('display', 'Unknown')
                owner_email = owner_info.get('email', 'Unknown')
                log_parts.append(f"Queue owner: {owner_display} ({owner_email})")
            
            if permission_message:
                log_parts.append(f"Permission message: {permission_message}")
            
            if error_messages:
                log_parts.append(f"Error messages: {'; '.join(error_messages)}")
            
            # Log as INFO level to file only (console is set to ERROR level, so this won't show in console)
            logger.info("ACCESS_DENIED: " + " | ".join(log_parts))
            
            # Return parsed information for use by caller
            return {
                'queue_key': queue_info.get('key', 'Unknown'),
                'queue_name': queue_info.get('display', 'Unknown'),
                'owner_name': owner_info.get('display', 'Unknown') if owner_info else 'Unknown',
                'owner_email': owner_info.get('email', 'Unknown') if owner_info else 'Unknown',
                'is_deleted': queue_info.get('deleted', False),
                'error_message': error_messages[0] if error_messages else permission_message or 'Access denied'
            }
            
        except Exception as e:
            # Fallback if JSON parsing fails
            logger.info(f"ACCESS_DENIED: Permission denied for {url} - Could not parse error details: {str(e)}")
            return None
    
    def _make_request(self, method: str, endpoint: str, max_retries: int = 3, **kwargs) -> ApiResponse:
        """Make HTTP request with rate limiting, retry logic, and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            max_retries: Maximum number of retries for rate limit errors
            **kwargs: Additional arguments for requests
            
        Returns:
            ApiResponse object
            
        Raises:
            requests.RequestException: On API errors
        """
        # Construct full URL
        url = f"{self.base_url}{endpoint}"
        
        # Merge headers
        headers = {**self.headers, **kwargs.pop('headers', {})}
        
        # Retry loop for rate limit errors
        for attempt in range(max_retries + 1):
            # Apply rate limiting before each attempt
            self.rate_limiter.wait_if_needed()
            
            # Log request
            if attempt > 0:
                logger.info(f"API Request (attempt {attempt + 1}): {method} {url}")
            else:
                logger.debug(f"API Request: {method} {url}")
            
            start_time = time.time()
            self.total_requests += 1
            
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=30,  # 30 second timeout
                    **kwargs
                )
                
                elapsed_time = time.time() - start_time
                
                # Log response
                logger.debug(f"API Response: {response.status_code} in {elapsed_time:.3f}s")
                
                # Handle HTTP errors
                if response.status_code >= 400:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    
                    if response.status_code == 429:
                        # Rate limit error - implement retry logic
                        if attempt < max_retries:
                            logger.warning(f"Rate limit hit (429) on attempt {attempt + 1}, retrying...")
                            self.rate_limiter.reduce_rate_on_limit_hit()
                            # Add exponential backoff
                            backoff_time = min(2 ** attempt, 10)  # Cap at 10 seconds
                            logger.info(f"Backing off for {backoff_time}s before retry")
                            time.sleep(backoff_time)
                            continue  # Retry the request
                        else:
                            # Max retries exceeded
                            self.failed_requests += 1
                            logger.error(f"Rate limit exceeded after {max_retries} retries: {error_msg}")
                            raise requests.HTTPError(t("api_error_rate_limit"))
                    
                    # Handle other HTTP errors (no retry)
                    self.failed_requests += 1
                    
                    if response.status_code == 401:
                        logger.error(error_msg)
                        raise requests.HTTPError(t("api_error_unauthorized"))
                    elif response.status_code == 403:
                        # Handle 403 errors specially - log detailed info to file only, no console output
                        access_issue_data = self._log_permission_denied_error(url, response)
                        raise PermissionDeniedError(t("api_error_forbidden"), access_issue_data)
                    elif response.status_code == 404:
                        # For 404, we might want to handle it gracefully in some cases
                        logger.warning(f"Resource not found: {url}")
                    elif response.status_code >= 500:
                        logger.error(error_msg)
                        raise requests.HTTPError(t("api_error_server", code=response.status_code))
                    else:
                        # For other 4xx errors, log normally
                        logger.error(error_msg)
                    
                    response.raise_for_status()
                
                # Successful response
                return ApiResponse(
                    data=response.json() if response.content else None,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    url=url,
                    elapsed_time=elapsed_time
                )
                
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    logger.warning(f"Request timeout on attempt {attempt + 1}, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    self.failed_requests += 1
                    logger.error(f"Request timeout for {url}")
                    raise requests.RequestException(t("api_error_timeout"))
            
            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    logger.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    self.failed_requests += 1
                    logger.error(f"Connection error for {url}")
                    raise requests.RequestException(t("api_error_connection"))
            
            except requests.exceptions.RequestException as e:
                self.failed_requests += 1
                # Don't log 403 permission errors at ERROR level - they're already logged as INFO
                if "❌ Доступ запрещен: Недостаточно прав" not in str(e) and "api_error_forbidden" not in str(e):
                    logger.error(f"Request failed for {url}: {str(e)}")
                raise
        
        # This should never be reached due to the retry loop structure
        raise requests.RequestException("Unexpected error in retry loop")
    
    def get(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make GET request."""
        return self._make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make POST request."""
        return self._make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make PUT request."""
        return self._make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    # Specific API methods
    def get_queues(self, per_page: int = 50) -> List[Dict[str, Any]]:
        """Get all queues from the API.
        
        Args:
            per_page: Number of queues per page
            
        Returns:
            List of queue dictionaries
        """
        all_queues = []
        page = 1
        
        while True:
            params = {
                'perPage': per_page,
                'page': page
            }
            
            response = self.get('/v3/queues', params=params)
            queues = response.data
            
            if not queues:
                break
            
            all_queues.extend(queues)
            
            # If we got fewer than per_page, we're done
            if len(queues) < per_page:
                break
            
            page += 1
        
        logger.debug(f"Retrieved {len(all_queues)} queues")
        return all_queues
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users in the organization."""
        response = self.get('/v3/users')
        users = response.data or []
        logger.debug(f"Retrieved {len(users)} users")
        return users
    
    def get_groups(self, per_page: int = 1000) -> List[Dict[str, Any]]:
        """Get all groups in the organization using pagination.
        
        Args:
            per_page: Number of groups to retrieve per page (max 1000)
            
        Returns:
            List of group dictionaries
        """
        all_groups = []
        page = 1
        
        while True:
            params = {
                'perPage': per_page,
                'page': page
            }
            
            response = self.get('/v3/groups', params=params)
            groups = response.data
            
            if not groups:
                break
            
            all_groups.extend(groups)
            
            # If we got fewer than per_page, we're done
            if len(groups) < per_page:
                break
            
            page += 1
        
        logger.debug(f"Retrieved {len(all_groups)} groups")
        return all_groups
    
    def get_user_permissions(self, queue_key: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user permissions for a specific queue.
        
        Args:
            queue_key: Queue key
            user_id: User ID
            
        Returns:
            Permission data or None if not found
        """
        try:
            response = self.get(f'/v3/queues/{queue_key}/permissions/users/{user_id}')
            return response.data
        except requests.HTTPError as e:
            if "404" in str(e):
                # No specific permissions found
                return None
            raise
    
    def get_group_permissions(self, queue_key: str, group_id: str) -> Optional[Dict[str, Any]]:
        """Get group permissions for a specific queue.
        
        Args:
            queue_key: Queue key
            group_id: Group ID
            
        Returns:
            Permission data or None if not found
        """
        try:
            response = self.get(f'/v3/queues/{queue_key}/permissions/groups/{group_id}')
            return response.data
        except requests.HTTPError as e:
            if "404" in str(e):
                # No specific permissions found
                return None
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        elapsed = datetime.now() - self.start_time
        return {
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'success_rate': (self.total_requests - self.failed_requests) / max(self.total_requests, 1) * 100,
            'elapsed_time': elapsed.total_seconds(),
            'average_rps': self.total_requests / max(elapsed.total_seconds(), 1),
            'rate_limit_hits': self.rate_limiter.rate_limit_hits,
            'current_rps': self.rate_limiter.max_rps,
            'current_delay': self.rate_limiter.min_interval
        }
