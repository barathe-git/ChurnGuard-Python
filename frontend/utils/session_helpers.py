"""
Session state management helpers
Utility functions for managing Streamlit session state
"""
import logging
import streamlit as st
from src.services.llm_data_manager import LLMDataManager
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


def clear_user_session_state():
    """Clear user-specific session state to prevent data leakage"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        logger.info(f"Clearing session state for user: {user_id}")
        
        # Keys to clear
        keys_to_clear = [
            'llm_analysis', 'llm_customer_data', 'uploaded_csv_path',
            'csv_summary_message', 'csv_summary_generated', 'messages',
            'nlq_agent', 'data_source', 'last_validated_file', 
            'cached_header_validation', 'analysis_started', 'analysis_start_time',
            'uploaded_csv_id', 'uploaded_csv_content', 'show_recipients',
            'target_recipients_df', 'campaigns', 'scheduled_campaigns'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                logger.debug(f"Cleared session state key: {key}")
        
        # Reset data manager
        if 'llm_data_manager' in st.session_state:
            st.session_state.llm_data_manager = LLMDataManager()
        
        logger.info(f"Session state cleared for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing session state: {str(e)}")


def check_user_change(current_user_id: str) -> bool:
    """
    Check if user has changed and clear session if needed
    
    Returns:
        True if user changed, False otherwise
    """
    try:
        if 'last_user_id' not in st.session_state:
            st.session_state.last_user_id = current_user_id
            return False
        elif st.session_state.last_user_id != current_user_id:
            logger.info(f"User changed from {st.session_state.last_user_id} to {current_user_id}")
            clear_user_session_state()
            st.session_state.last_user_id = current_user_id
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking user change: {str(e)}")
        return False


def initialize_services():
    """Initialize required services in session state"""
    try:
        if 'llm_data_manager' not in st.session_state:
            st.session_state.llm_data_manager = LLMDataManager()
        
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        logger.debug("Services initialized")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")


def get_current_user_id() -> str:
    """Get current user ID from session state"""
    return st.session_state.get('user_id', 'demo_user')


def is_analysis_running() -> bool:
    """Check if analysis is currently running"""
    return st.session_state.get('analysis_started', False)


def set_analysis_running(running: bool):
    """Set analysis running state"""
    st.session_state.analysis_started = running
    if running:
        from datetime import datetime
        st.session_state.analysis_start_time = datetime.now()
    elif 'analysis_start_time' in st.session_state:
        del st.session_state.analysis_start_time

