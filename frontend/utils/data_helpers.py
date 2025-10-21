"""
Data loading and processing helpers
Utility functions for loading and processing user data from MongoDB
"""
import logging
import pandas as pd
import io
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)


def convert_csv_bytes_to_dataframe(csv_content: bytes) -> Optional[pd.DataFrame]:
    """Convert CSV bytes to DataFrame"""
    try:
        if csv_content:
            return pd.read_csv(io.BytesIO(csv_content))
        return None
    except Exception as e:
        logger.warning(f"Could not convert CSV bytes to DataFrame: {str(e)}")
        return None


def load_user_analytics_data(db_manager, user_id: str) -> Tuple[Optional[Dict], Optional[pd.DataFrame], Optional[str]]:
    """
    Load user's analytics data from MongoDB
    
    Returns:
        Tuple of (analytics_data, original_csv_df, csv_file_id)
    """
    try:
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - cannot load analytics data")
            return None, None, None
        
        # Load analytics data
        analytics_data = db_manager.get_user_data('analytics', user_id)
        if not analytics_data:
            return None, None, None
        
        # Get the most recent analysis
        latest_analysis = max(analytics_data, key=lambda x: x.get('analysis_date', datetime.min))
        
        # Load CSV data to get email mapping
        original_csv_df, csv_file_id = load_user_csv_data(db_manager, user_id)
        
        return latest_analysis, original_csv_df, csv_file_id
        
    except Exception as e:
        logger.error(f"Error loading analytics data: {str(e)}")
        return None, None, None


def load_user_csv_data(db_manager, user_id: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load user's CSV data from MongoDB
    
    Returns:
        Tuple of (dataframe, csv_file_id)
    """
    try:
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - cannot load CSV data")
            return None, None
        
        csv_data = db_manager.get_user_data('csv_files', user_id)
        if not csv_data:
            return None, None
        
        latest_csv = max(csv_data, key=lambda x: x.get('upload_date', datetime.min))
        csv_content = latest_csv.get('file_content')
        csv_file_id = str(latest_csv['_id'])
        
        if csv_content:
            df = convert_csv_bytes_to_dataframe(csv_content)
            if df is not None:
                logger.info(f"Loaded CSV data with {len(df)} records")
            return df, csv_file_id
        
        return None, csv_file_id
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {str(e)}")
        return None, None


def store_csv_file(db_manager, user_id: str, uploaded_file, df: pd.DataFrame) -> Optional[str]:
    """
    Store CSV file in MongoDB
    
    Returns:
        CSV file ID if successful, None otherwise
    """
    try:
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - CSV not persisted")
            return None
        
        csv_data = {
            "file_name": uploaded_file.name,
            "file_content": uploaded_file.getvalue(),
            "file_size": len(uploaded_file.getvalue()),
            "upload_date": datetime.now(),
            "record_count": len(df),
            "columns": list(df.columns),
            "sample_data": df.head(5).to_dict('records'),
            "mime_type": uploaded_file.type
        }
        
        success = db_manager.store_user_data('csv_files', user_id, csv_data)
        
        if success:
            stored_files = db_manager.get_user_data('csv_files', user_id)
            if stored_files:
                latest_file = max(stored_files, key=lambda x: x.get('upload_date', datetime.min))
                file_id = str(latest_file['_id'])
                logger.info(f"CSV file stored in MongoDB with ID: {file_id}")
                return file_id
        
        logger.error("Failed to store CSV file in MongoDB")
        return None
        
    except Exception as e:
        logger.error(f"Error storing CSV in MongoDB: {str(e)}")
        return None


def store_analytics_data(db_manager, user_id: str, analysis_result: Dict, csv_file_id: str) -> bool:
    """
    Store analytics results in MongoDB
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - analytics not persisted")
            return False
        
        analysis_data = {
            "analysis_date": datetime.now(),
            "analysis_result": analysis_result,
            "summary": analysis_result.get('summary', {}),
            "churn_predictions": analysis_result.get('churn_predictions', {}),
            "insights": analysis_result.get('insights', {}),
            "analytics": analysis_result.get('analytics', {}),
            "csv_file_id": csv_file_id,
            "status": "completed"
        }
        
        success = db_manager.store_user_data('analytics', user_id, analysis_data)
        logger.info(f"Analytics storage success: {success}")
        return success
        
    except Exception as e:
        logger.error(f"Error storing analytics in MongoDB: {str(e)}")
        return False


def store_chat_interaction(db_manager, user_id: str, question: str, answer: str, session_id: str) -> bool:
    """
    Store chat interaction in MongoDB
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - chat interaction not persisted")
            return False
        
        chat_data = {
            "timestamp": datetime.now(),
            "question": question,
            "answer": answer,
            "session_id": session_id
        }
        
        success = db_manager.store_user_data('chat_interactions', user_id, chat_data)
        if success:
            logger.info(f"Chat interaction stored for user: {user_id}")
        return success
        
    except Exception as e:
        logger.error(f"Error storing chat interaction: {str(e)}")
        return False

