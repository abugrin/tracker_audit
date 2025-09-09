"""
Logging configuration for Tracker Audit Tool.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    console_output: bool = True,
    console_level: str = "WARNING"
) -> None:
    """Set up logging configuration for the entire project.
    
    Args:
        log_file: Path to log file. If None, uses default naming
        log_level: Logging level for file (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to also output logs to console
        console_level: Logging level for console output
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    console_numeric_level = getattr(logging, console_level.upper(), logging.WARNING)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use RotatingFileHandler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)  # Reduce noise from requests
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")


def get_log_filename(output_file: str) -> str:
    """Generate log filename based on output Excel file.
    
    Args:
        output_file: Path to output Excel file
        
    Returns:
        Path to log file
    """
    output_path = Path(output_file)
    log_filename = output_path.stem + '.log'
    return str(output_path.parent / log_filename)


def log_api_statistics(stats: dict) -> None:
    """Log API usage statistics.
    
    Args:
        stats: Statistics dictionary from TrackerApiClient
    """
    logger = logging.getLogger('api_stats')
    logger.info("API Usage Statistics:")
    logger.info(f"  Total requests: {stats['total_requests']}")
    logger.info(f"  Failed requests: {stats['failed_requests']}")
    logger.info(f"  Success rate: {stats['success_rate']:.1f}%")
    logger.info(f"  Elapsed time: {stats['elapsed_time']:.1f}s")
    logger.info(f"  Average RPS: {stats['average_rps']:.2f}")
    logger.info(f"  Rate limit hits: {stats.get('rate_limit_hits', 0)}")
    logger.info(f"  Final RPS setting: {stats.get('current_rps', 'N/A')}")
    if stats.get('rate_limit_hits', 0) > 0:
        logger.info(f"  Final delay between requests: {stats.get('current_delay', 'N/A'):.3f}s")


def log_audit_summary(queues_count: int, access_entries_count: int, elapsed_time: float) -> None:
    """Log audit summary.
    
    Args:
        queues_count: Number of queues audited
        access_entries_count: Number of access entries found
        elapsed_time: Total elapsed time in seconds
    """
    logger = logging.getLogger('audit_summary')
    logger.info("Audit Summary:")
    logger.info(f"  Queues audited: {queues_count}")
    logger.info(f"  Access entries found: {access_entries_count}")
    logger.info(f"  Total time: {elapsed_time:.1f}s")
    logger.info(f"  Average time per queue: {elapsed_time/max(queues_count, 1):.1f}s")
