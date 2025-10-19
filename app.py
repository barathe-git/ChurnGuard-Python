"""
ChurnGuard - AI-Powered Customer Retention Platform
Main Streamlit Application Entry Point
"""
import streamlit as st
from frontend.pages import auth, analytics, chat, outreach
from config.config import Config
from config.logging_config import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ChurnGuard - Customer Retention Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_async_status():
    """Check for any running async processes and update session state"""
    try:
        from frontend.pages.analytics import check_analysis_status
        
        if st.session_state.get('authenticated', False):
            user_id = st.session_state.get('user_id', 'demo_user')
            
            # Check if analysis is completed
            if check_analysis_status(user_id):
                # Clear analysis started flag if analysis is complete
                if 'analysis_started' in st.session_state:
                    del st.session_state['analysis_started']
                if 'analysis_start_time' in st.session_state:
                    del st.session_state['analysis_start_time']
                    
    except Exception as e:
        logger.error(f"Error checking async status: {str(e)}")

def main():
    """Main application entry point"""

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.email = None
        st.session_state.organization = None
        st.session_state.subscription_tier = None
        st.session_state.session_id = None

    # Authentication check
    if not st.session_state.authenticated:
        auth.render_login_page()
    else:
        # Check for any completed async processes
        check_async_status()
        
        # Sidebar navigation
        with st.sidebar:
            # st.image("https://via.placeholder.com/200x80?text=ChurnGuard", width=200)
            # st.markdown("---")
            
            # User info
            st.markdown(f"**Welcome, {st.session_state.username}!**")
            st.markdown(f"*{st.session_state.organization}*")
            st.markdown(f"Tier: {st.session_state.subscription_tier.title()}")
            
            # Async status indicator
            if st.session_state.get('analysis_started', False):
                st.markdown("---")
                st.info("⏳ AI Analysis Running...")
                st.markdown("🔄 Analysis continues in background")
            
            st.markdown("---")

            page = st.radio(
                "Navigation",
                ["📊 Analytics", "💬 Chat Assistant", "📢 Outreach", "⚙️ Settings"]
            )

            if st.button("🚪 Logout"):
                auth.render_logout()

        # Route to appropriate page
        if page == "📊 Analytics":
            analytics.render_analytics_page()
        elif page == "💬 Chat Assistant":
            chat.render_chat_page()
        elif page == "📢 Outreach":
            outreach.render_outreach()
        else:
            st.info("Settings page coming soon!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("An unexpected error occurred. Please try again.")
