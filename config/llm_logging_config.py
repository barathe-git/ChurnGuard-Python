# config/llm_logging_config.py
"""
LLM Logging Configuration - Dedicated logging for LLM interactions
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

def setup_llm_logging():
    """Setup dedicated logging for LLM interactions"""
    
    # Create LLM logger
    llm_logger = logging.getLogger('llm_interactions')
    
    # Check if already configured (avoid duplicate setup in Streamlit)
    if any(hasattr(h, '_churnguard_llm_handler') for h in llm_logger.handlers):
        return llm_logger
    
    # Create logs directory structure
    log_dir = Path(__file__).parent.parent / "logs"
    llm_log_dir = log_dir / "llm"
    
    # Create subdirectories
    log_dir.mkdir(exist_ok=True)
    llm_log_dir.mkdir(exist_ok=True)
    
    llm_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in llm_logger.handlers[:]:
        llm_logger.removeHandler(handler)
    
    # Create file handler for LLM logs with daily rotation
    # Creates one log file per day (llm_interactions_YYYYMMDD.log)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        llm_log_dir / 'llm_interactions.log',
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.suffix = "%Y%m%d"
    file_handler.setLevel(logging.INFO)
    file_handler._churnguard_llm_handler = True  # Mark as ChurnGuard LLM handler
    
    # Create console handler for LLM logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler._churnguard_llm_handler = True  # Mark as ChurnGuard LLM handler
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    llm_logger.addHandler(file_handler)
    llm_logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    llm_logger.propagate = False
    
    return llm_logger

def get_llm_logger():
    """Get the LLM logger instance"""
    return logging.getLogger('llm_interactions')

def log_llm_request(logger, request_type: str, data: dict):
    """Log LLM request with structured data"""
    logger.info(f"=== {request_type.upper()} REQUEST ===")
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 500:
            logger.info(f"{key}: {value[:500]}... (truncated)")
        else:
            logger.info(f"{key}: {value}")
    logger.info(f"=== {request_type.upper()} REQUEST END ===")

def log_llm_response(logger, response_type: str, response_data: str):
    """Log LLM response with structured data"""
    logger.info(f"=== {response_type.upper()} RESPONSE ===")
    logger.info(f"Response Length: {len(response_data)} characters")
    logger.info(f"Response: {response_data}")
    logger.info(f"=== {response_type.upper()} RESPONSE END ===")

def log_llm_error(logger, error_type: str, error_message: str, exception=None):
    """Log LLM error with detailed information"""
    logger.error(f"=== {error_type.upper()} ERROR ===")
    logger.error(f"Error: {error_message}")
    if exception:
        logger.error(f"Exception Type: {type(exception).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    logger.error(f"=== {error_type.upper()} ERROR END ===")
