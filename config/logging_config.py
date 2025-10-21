"""
Logging configuration for ChurnGuard using best practices
"""
import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configure application-wide logging with rotation and formatting"""
    
    # Check if logging is already configured (avoid duplicate setup in Streamlit)
    root_logger = logging.getLogger()
    
    # If handlers already exist with our specific names, skip setup
    if any(hasattr(h, '_churnguard_handler') for h in root_logger.handlers):
        return
    
    # Create logs directory structure
    log_dir = Path(__file__).parent.parent / "logs"
    app_log_dir = log_dir / "application"
    error_log_dir = log_dir / "errors"
    
    # Create subdirectories
    log_dir.mkdir(exist_ok=True)
    app_log_dir.mkdir(exist_ok=True)
    error_log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger.setLevel(logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console Handler - INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    console_handler._churnguard_handler = True  # Mark as ChurnGuard handler

    # File Handler with Daily Rotation - DEBUG level
    # Creates one log file per day (churnguard_YYYYMMDD.log)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        app_log_dir / "churnguard.log",
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    # Add date suffix to rotated files
    file_handler.suffix = "%Y%m%d"
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    file_handler._churnguard_handler = True  # Mark as ChurnGuard handler

    # Error File Handler - ERROR level with daily rotation
    error_handler = logging.handlers.TimedRotatingFileHandler(
        error_log_dir / "errors.log",
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of error logs
        encoding='utf-8'
    )
    error_handler.suffix = "%Y%m%d"
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    error_handler._churnguard_handler = True  # Mark as ChurnGuard handler

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    logging.info("Logging configured successfully (one-time setup)")