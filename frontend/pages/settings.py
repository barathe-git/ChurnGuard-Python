"""
Settings Page - User preferences and data management
"""
import streamlit as st
import logging
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

def render_settings_page():
    """Render the settings page"""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # Initialize database manager
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    db_manager = st.session_state.db_manager
    user_id = st.session_state.get('user_id', 'demo_user')
    username = st.session_state.get('username', 'User')
    
    # Create tabs for different settings
    tab1, tab2, tab3 = st.tabs(["👤 Account", "🗑️ Data Management", "ℹ️ About"])
    
    with tab1:
        render_account_settings()
    
    with tab2:
        render_data_management(db_manager, user_id, username)
    
    with tab3:
        render_about()

def render_account_settings():
    """Render account settings section"""
    st.subheader("👤 Account Information")
    
    # Display user information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Username:**")
        st.info(st.session_state.get('username', 'N/A'))
        
        st.markdown("**Organization:**")
        st.info(st.session_state.get('organization', 'N/A'))
    
    with col2:
        st.markdown("**Email:**")
        st.info(st.session_state.get('email', 'N/A'))
        
        st.markdown("**Subscription Tier:**")
        tier = st.session_state.get('subscription_tier', 'free')
        tier_display = {
            'free': '🆓 Free',
            'pro': '⭐ Pro',
            'enterprise': '🏢 Enterprise'
        }
        st.success(tier_display.get(tier, tier.title()))
    
    st.markdown("---")
    
    # Token Usage Optimization Info
    st.subheader("💡 Token Usage Optimization")
    st.success("""
    **Recent Optimizations Applied:**
    - ✅ CSV Analysis: Sample-based processing (100 rows instead of all)
    - ✅ Chat Queries: Smart context routing (summary vs full data)
    - ✅ Conversation History: Limited to 4 recent messages
    - ✅ Token Reduction: ~90% less tokens for typical queries
    """)
    
    st.info("""
    **Tips to Save Tokens:**
    - Ask general questions to use summary mode
    - Be specific when you need detailed customer lists
    - Clear chat history periodically
    - Reset all data when starting fresh analysis
    """)

def render_data_management(db_manager, user_id, username):
    """Render data management section with reset functionality"""
    st.subheader("🗑️ Data Management")
    
    # Show current data status
    st.markdown("### 📊 Current Data Status")
    
    try:
        # Get data counts
        analytics_count = len(db_manager.get_user_data('analytics', user_id) or [])
        csv_files_count = len(db_manager.get_user_data('csv_files', user_id) or [])
        chat_count = len(db_manager.get_user_data('chat_interactions', user_id) or [])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📈 Analysis Records", analytics_count)
        with col2:
            st.metric("📄 CSV Files", csv_files_count)
        with col3:
            st.metric("💬 Chat Messages", chat_count)
        
        total_records = analytics_count + csv_files_count + chat_count
        
        if total_records > 0:
            st.info(f"Total stored records: **{total_records}**")
        else:
            st.success("✨ No data stored yet - your account is fresh!")
        
    except Exception as e:
        logger.error(f"Error fetching data status: {str(e)}")
        st.warning("Unable to fetch data status")
    
    st.markdown("---")
    
    # Reset All Data Section
    st.markdown("### 🔄 Reset All Data")
    st.warning("""
    **⚠️ Warning: This action cannot be undone!**
    
    Resetting will permanently delete:
    - All uploaded CSV files
    - All AI analysis results
    - All chat conversation history
    - All session data
    
    Your account information will remain intact.
    """)
    
    # Confirmation checkbox
    confirm = st.checkbox(
        f"I understand that this will permanently delete all my data ({username})",
        key="confirm_reset"
    )
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button(
            "🗑️ Reset All Data",
            type="primary",
            disabled=not confirm,
            use_container_width=True
        ):
            if perform_reset(db_manager, user_id, username):
                st.success("✅ All data has been reset successfully!")
                st.balloons()
                # Clear session state
                clear_session_state()
                # Wait a moment then rerun
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Failed to reset data. Please try again or contact support.")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.confirm_reset = False
            st.rerun()

def perform_reset(db_manager, user_id, username):
    """Perform the actual data reset"""
    try:
        logger.info(f"Starting data reset for user: {username} (ID: {user_id})")
        
        # Collections to clear
        collections = ['analytics', 'csv_files', 'chat_interactions']
        
        success = True
        for collection_name in collections:
            try:
                # Get user-specific collection
                collection = db_manager.get_user_collection(collection_name, user_id)
                
                # Delete all documents for this user
                result = collection.delete_many({'user_id': user_id})
                logger.info(f"Deleted {result.deleted_count} records from {collection_name} for user {user_id}")
                
            except Exception as e:
                logger.error(f"Error clearing {collection_name}: {str(e)}")
                success = False
        
        if success:
            logger.info(f"Data reset completed successfully for user {user_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error performing data reset: {str(e)}")
        return False

def clear_session_state():
    """Clear session state data (except auth)"""
    keys_to_clear = [
        'llm_data_manager',
        'llm_analysis',
        'llm_customer_data',
        'uploaded_csv_path',
        'uploaded_csv_id',
        'uploaded_csv_content',
        'csv_summary_message',
        'messages',
        'nlq_agent',
        'last_validated_file',
        'cached_header_validation',
        'analysis_started',
        'analysis_start_time',
        'sync_analysis_running'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    logger.info("Session state cleared after reset")

def render_about():
    """Render about section"""
    st.subheader("ℹ️ About ChurnGuard")
    
    st.markdown("""
    ### 🛡️ ChurnGuard - AI-Powered Customer Retention Platform
    
    **Version:** 1.0.0
    
    **Features:**
    - 📊 AI-Powered Churn Analysis
    - 💬 Natural Language Query Interface  
    - 🎯 Customer Segmentation & Risk Scoring
    - 📈 Real-time Analytics Dashboard
    - 📢 Multi-channel Outreach Campaigns
    
    **Technology Stack:**
    - Frontend: Streamlit
    - Backend: Python
    - Database: MongoDB Atlas
    - AI: Google Gemini AI
    - Analytics: Pandas, Plotly
    
    **Recent Optimizations:**
    - Token-efficient CSV processing
    - Smart context routing for chat
    - Reduced API costs by ~90%
    - Daily log rotation
    
    ---
    
    ### 📊 Free Tier Limits
    
    - **Max CSV Size:** 10 MB
    - **Max Rows:** 100 (first 100 rows processed)
    - **Max Columns:** 30
    - **Chat History:** Last 4 messages
    - **Token Optimization:** ~90% reduction vs. unlimited
    
    ---
    
    ### 📞 Support
    
    For questions or issues, please contact your system administrator.
    
    © 2025 ChurnGuard. All rights reserved.
    """)

# Export the render function
__all__ = ['render_settings_page']

