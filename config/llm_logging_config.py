# config/llm_logging_config.py
"""
LLM Logging Configuration - Dedicated logging for LLM interactions
"""
import logging
import os
from datetime import datetime

def setup_llm_logging():
    """Setup dedicated logging for LLM interactions"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create LLM logger
    llm_logger = logging.getLogger('llm_interactions')
    llm_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in llm_logger.handlers[:]:
        llm_logger.removeHandler(handler)
    
    # Create file handler for LLM logs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    llm_log_file = f'logs/llm_interactions_{timestamp}.log'
    
    file_handler = logging.FileHandler(llm_log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler for LLM logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
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
