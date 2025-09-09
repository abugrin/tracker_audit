"""Audit functionality for Yandex Tracker queues and access permissions."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.table import Table
from translations import t
from api_client import TrackerApiClient, PermissionDeniedError

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class QueueInfo:
    """Information about a Tracker queue."""
    key: str
    name: str
    description: Optional[str]
    lead: Optional[str]
    default_type: Optional[str]
    default_priority: Optional[str]


@dataclass
class AccessInfo:
    """Information about queue access permissions."""
    queue_key: str
    permission_type: str
    subject_type: str  # user, group, etc.
    subject_id: str
    subject_display: str
    granted_permissions: List[str]


@dataclass
class AccessIssue:
    """Information about queue access issues."""
    queue_key: str
    queue_name: str
    owner_name: str
    owner_email: str
    is_deleted: bool
    error_message: str


class TrackerAuditor:
    """Audits Yandex Tracker queues and access permissions."""
    
    def __init__(self, token: str, org_id: str, org_type: str = "360"):
        """Initialize the auditor.
        
        Args:
            token: OAuth token for Yandex Tracker API
            org_id: Organization ID
            org_type: Organization type ('360' or 'cloud')
        """
        # Initialize API client with rate limiting
        self.api_client = TrackerApiClient(token, org_id, org_type, max_rps=5.0)
        
        self.queues: List[QueueInfo] = []
        self.access_info: List[AccessInfo] = []
        self.access_issues: List[AccessIssue] = []
        self._users_cache: Optional[List[Dict[str, Any]]] = None
        self._groups_cache: Optional[List[Dict[str, Any]]] = None
        self._all_users_group_id: Optional[str] = None
        
        logger.info(f"Initialized TrackerAuditor for org {org_id} (type: {org_type})")
    
    def show_access_issues_summary(self):
        """Display a summary table of queues with access issues."""
        if not self.access_issues:
            return
        
        console.print("\n" + "="*60)
        console.print(f"🚫 {t('access_issues_title')}")
        
        table = Table()
        table.add_column(t('access_issues_queue_key'), style="cyan", no_wrap=True)
        table.add_column(t('access_issues_queue_name'), style="blue")
        table.add_column(t('access_issues_owner'), style="green")
        table.add_column(t('access_issues_email'), style="yellow")
        table.add_column(t('access_issues_status'), style="red")
        
        for issue in self.access_issues:
            status = t('access_issues_deleted') if issue.is_deleted else t('access_issues_active')
            table.add_row(
                issue.queue_key,
                issue.queue_name,
                issue.owner_name,
                issue.owner_email,
                status
            )
        
        console.print(table)
        console.print(f"💡 {t('access_issues_contact_note')}")
    
    def get_all_queues(self) -> List[QueueInfo]:
        """Retrieve all queues from Yandex Tracker.
        
        Returns:
            List of QueueInfo objects
        """
        console.print(t("fetching_all_queues"), style="blue")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(t("loading_queues"), total=None)
                
                # Use API client to get queues
                queues_data = self.api_client.get_queues()
                progress.update(task, description=t("found_queues", count=len(queues_data)))
                
                self.queues = []
                for queue_data in queues_data:
                    queue_info = QueueInfo(
                        key=queue_data.get('key', ''),
                        name=queue_data.get('name', ''),
                        description=queue_data.get('description'),
                        lead=self._extract_reference_display(queue_data.get('lead')),
                        default_type=self._extract_reference_display(queue_data.get('defaultType')),
                        default_priority=self._extract_reference_display(queue_data.get('defaultPriority'))
                    )
                    self.queues.append(queue_info)
                
                progress.update(task, description=t("loaded_queues", count=len(self.queues)))
            
            console.print(t("queues_loaded", count=len(self.queues)), style="green")
            return self.queues
            
        except Exception as e:
            console.print(t("error_fetching_queues", error=str(e)), style="red")
            logger.error(t("error_fetching_queues", error=str(e)))
            return []
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users in the organization.
        
        Returns:
            List of user objects
        """
        if self._users_cache is not None:
            return self._users_cache
            
        try:
            self._users_cache = self.api_client.get_users()
            return self._users_cache
        except Exception as e:
            logger.warning(f"Could not get users: {str(e)}")
            return []
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Get all groups in the organization.
        
        Returns:
            List of group objects
        """
        if self._groups_cache is not None:
            return self._groups_cache
            
        try:
            self._groups_cache = self.api_client.get_groups()
            
            # Find the "all users" group (type=7)
            for group in self._groups_cache:
                if group.get('type') == 7:
                    self._all_users_group_id = group.get('id')
                    logger.info(f"Found all users group with ID: {self._all_users_group_id}")
                    break
            
            return self._groups_cache
        except Exception as e:
            logger.warning(f"Could not get groups: {str(e)}")
            return []
    
    def get_user_permissions(self, queue_key: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user permissions for a specific queue.
        
        Args:
            queue_key: Queue key
            user_id: User ID
            
        Returns:
            Permissions data or None if not accessible
        """
        try:
            return self.api_client.get_user_permissions(queue_key, user_id)
        except Exception as e:
            logger.debug(f"Could not get permissions for user {user_id} in queue {queue_key}: {str(e)}")
            return None
    
    def get_group_permissions(self, queue_key: str, group_id: str) -> Optional[Dict[str, Any]]:
        """Get group permissions for a specific queue.
        
        Args:
            queue_key: Queue key
            group_id: Group ID
            
        Returns:
            Permissions data or None if not accessible
        """
        try:
            return self.api_client.get_group_permissions(queue_key, group_id)
        except Exception as e:
            # Check if this is a permission denied error with access issue data
            if hasattr(e, 'access_issue_data') and e.access_issue_data:
                access_issue = AccessIssue(
                    queue_key=e.access_issue_data['queue_key'],
                    queue_name=e.access_issue_data['queue_name'],
                    owner_name=e.access_issue_data['owner_name'],
                    owner_email=e.access_issue_data['owner_email'],
                    is_deleted=e.access_issue_data['is_deleted'],
                    error_message=e.access_issue_data['error_message']
                )
                # Check if we already have this access issue (avoid duplicates)
                if not any(issue.queue_key == access_issue.queue_key for issue in self.access_issues):
                    self.access_issues.append(access_issue)
            
            logger.debug(f"Could not get permissions for group {group_id} in queue {queue_key}: {str(e)}")
            return None

    def audit_queue_access(self, queue_key: str, scope: str = "both") -> List[AccessInfo]:
        """Audit access permissions for a specific queue.
        
        Args:
            queue_key: Queue key to audit
            scope: Audit scope - 'groups', 'users', 'both', or 'all_users_group'
            
        Returns:
            List of AccessInfo objects
        """
        access_list = []
        
        try:
            # Process only "all users" group if requested
            if scope == "all_users_group":
                # Ensure we have the all users group ID
                if self._all_users_group_id is None:
                    self.get_all_groups()  # This will find and set the all users group ID
                
                if self._all_users_group_id:
                    # Check if this queue has permissions for the "all users" group
                    permissions_data = self.get_group_permissions(queue_key, self._all_users_group_id)
                    if permissions_data:
                        # Extract permissions from the response
                        group_info = permissions_data.get('group', {})
                        permissions = permissions_data.get('permissions', {})
                        
                        for perm_type, perm_details in permissions.items():
                            # Check if group has permissions (any of users, groups, or roles)
                            has_permission = False
                            granted_via = []
                        
                            if 'groups' in perm_details and perm_details['groups']:
                                has_permission = True
                                granted_via.append('group')
                            if 'users' in perm_details and perm_details['users']:
                                has_permission = True
                                granted_via.append('users')
                            if 'roles' in perm_details and perm_details['roles']:
                                has_permission = True
                                granted_via.append('roles')
                            
                            if has_permission:
                                access_info = AccessInfo(
                                    queue_key=queue_key,
                                    permission_type=perm_type,
                                    subject_type='all_users_group',
                                    subject_id=self._all_users_group_id,
                                    subject_display=group_info.get('display') or 'All Users Group',
                                    granted_permissions=[f'{perm_type} (via {", ".join(granted_via)})']
                                )
                                access_list.append(access_info)
                
                # For "all_users_group" scope, we only return results if the all users group has access
                return access_list
                
            # Process groups if requested
            if scope in ["groups", "both"]:
                # Get all groups first (they're more likely to have permissions than individual users)
                groups = self.get_all_groups()
                for group in groups:
                    group_id = group.get('id')
                    if group_id:
                        permissions_data = self.get_group_permissions(queue_key, group_id)
                        if permissions_data:
                            # Extract permissions from the response
                            group_info = permissions_data.get('group', {})
                            permissions = permissions_data.get('permissions', {})
                            
                            for perm_type, perm_details in permissions.items():
                                # Check if group has permissions (any of users, groups, or roles)
                                has_permission = False
                                granted_via = []
                            
                                if 'groups' in perm_details and perm_details['groups']:
                                    has_permission = True
                                    granted_via.append('group')
                                if 'users' in perm_details and perm_details['users']:
                                    has_permission = True
                                    granted_via.append('users')
                                if 'roles' in perm_details and perm_details['roles']:
                                    has_permission = True
                                    granted_via.append('roles')
                                
                                if has_permission:
                                    access_info = AccessInfo(
                                        queue_key=queue_key,
                                        permission_type=perm_type,
                                        subject_type='group',
                                        subject_id=group_info.get('id', group_id),
                                        subject_display=group_info.get('display') or group.get('name') or f'Group {group_id}',
                                        granted_permissions=[f'{perm_type} (via {", ".join(granted_via)})']
                                    )
                                    access_list.append(access_info)
            
            # Process users if requested
            if scope in ["users", "both"]:
                # Check users for direct permissions and role-based permissions
                # Exclude robots and permissions granted only via groups
                users = self.get_all_users()
                for user in users:
                    user_display = user.get('display', '')
                    
                    # Skip robots
                    if 'робот' in user_display.lower() or 'robot' in user_display.lower():
                        continue
                    
                    user_id = user.get('uid') or user.get('trackerUid') or user.get('id')
                    if user_id:
                        permissions_data = self.get_user_permissions(queue_key, user_id)
                        if permissions_data:
                            # Extract permissions from the response
                            user_info = permissions_data.get('user', {})
                            permissions = permissions_data.get('permissions', {})
                        
                        for perm_type, perm_details in permissions.items():
                            # Only include permissions that are granted directly or via roles
                            # Exclude permissions granted only via groups
                            has_direct_permission = 'users' in perm_details and perm_details['users']
                            has_role_permission = 'roles' in perm_details and perm_details['roles']
                            has_group_permission = 'groups' in perm_details and perm_details['groups']
                            
                            # Include if user has direct or role permissions
                            # Skip if only granted via groups
                            if has_direct_permission or has_role_permission:
                                granted_via = []
                                if has_direct_permission:
                                    granted_via.append('direct')
                                if has_role_permission:
                                    granted_via.append('roles')
                                
                                access_info = AccessInfo(
                                    queue_key=queue_key,
                                    permission_type=perm_type,
                                    subject_type='user',
                                    subject_id=user_info.get('id', user_id),
                                    subject_display=user_info.get('display', user_display),
                                    granted_permissions=[f'{perm_type} (via {", ".join(granted_via)})']
                                )
                                access_list.append(access_info)
            
            return access_list
            
        except Exception as e:
            logger.warning(f"Could not audit permissions for queue {queue_key}: {str(e)}")
            return []
    
    def audit_all_queues(self, scope: str = "both") -> List[AccessInfo]:
        """Audit access permissions for all queues.
        
        Args:
            scope: Audit scope - 'groups', 'users', 'both', or 'all_users_group'
        
        Returns:
            List of all AccessInfo objects
        """
        if not self.queues:
            self.get_all_queues()
        
        console.print(t("auditing_access_permissions"), style="blue")
        
        all_access_info = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(t("auditing_queues"), total=len(self.queues))
            
            for i, queue in enumerate(self.queues):
                current_queue_info = t("auditing_queue_with_progress", 
                                     queue=queue.key, 
                                     current=i+1, 
                                     total=len(self.queues))
                progress.update(task, description=current_queue_info)
                
                queue_access = self.audit_queue_access(queue.key, scope=scope)
                all_access_info.extend(queue_access)
                
                progress.advance(task)
        
        self.access_info = all_access_info
        console.print(t("audited_summary", queues=len(self.queues), entries=len(all_access_info)), style="green")
        
        return all_access_info
    
    def display_summary(self) -> None:
        """Display a summary of the audit results."""
        if not self.queues:
            console.print(t("no_queue_data"), style="red")
            return
        
        # Queues summary
        table = Table(title=t("queue_summary"))
        table.add_column(t("col_queue_key"), style="cyan")
        table.add_column(t("col_name"), style="white")
        table.add_column(t("col_lead"), style="yellow")
        table.add_column(t("col_access_entries"), justify="right", style="green")
        
        for queue in self.queues[:10]:  # Show first 10 queues
            access_count = len([a for a in self.access_info if a.queue_key == queue.key])
            table.add_row(
                queue.key,
                queue.name[:50] + "..." if len(queue.name) > 50 else queue.name,
                queue.lead or "N/A",
                str(access_count)
            )
        
        console.print(table)
        
        if len(self.queues) > 10:
            console.print(t("more_queues", count=len(self.queues) - 10), style="dim")
        
        # Access summary
        if self.access_info:
            console.print(f"\n{t('access_summary')}")
            console.print(t("total_access_entries", count=len(self.access_info)))
            
            # Group by subject type
            subject_types = {}
            for access in self.access_info:
                subject_types[access.subject_type] = subject_types.get(access.subject_type, 0) + 1
            
            for subject_type, count in subject_types.items():
                console.print(t("subject_type_count", type=subject_type, count=count))
    
    def _extract_reference_display(self, ref_obj: Optional[Any]) -> Optional[str]:
        """Extract display name from reference object.
        
        Args:
            ref_obj: Reference object from API response (now a dict from v3 API)
            
        Returns:
            Display name or None
        """
        if not ref_obj:
            return None
        
        # Handle dict objects from v3 API
        if isinstance(ref_obj, dict):
            # Try to get display name in order of preference
            return (ref_obj.get('display') or 
                   ref_obj.get('name') or 
                   ref_obj.get('id') or 
                   ref_obj.get('key'))
        
        # Handle legacy Reference objects (if any remain)
        if hasattr(ref_obj, 'display'):
            return getattr(ref_obj, 'display', None)
        elif hasattr(ref_obj, 'name'):
            return getattr(ref_obj, 'name', None)
        elif hasattr(ref_obj, 'id'):
            return getattr(ref_obj, 'id', None)
        elif hasattr(ref_obj, 'key'):
            return getattr(ref_obj, 'key', None)
        
        # Fallback to string representation
        return str(ref_obj) if ref_obj else None
