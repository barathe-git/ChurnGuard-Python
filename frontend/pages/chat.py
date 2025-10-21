"""
Chat page with AI assistant for customer data queries
Refactored version with clean, modular code
"""
import streamlit as st
import logging
from src.ai_agents import NLQAgent
from config.constants import (
    PAGE_TITLES, PAGE_CAPTIONS, CHAT_MESSAGES, QUICK_ACTIONS,
    QUICK_ACTION_QUERIES, CSV_SUMMARY_TEMPLATE, CSV_SUMMARY_FALLBACK
)
from frontend.utils import (
    load_page_css, clear_user_session_state, check_user_change,
    initialize_services, get_current_user_id, is_analysis_running,
    load_user_analytics_data, load_user_csv_data, store_chat_interaction
)

logger = logging.getLogger(__name__)


def render_chat_page():
    """Render chat page with AI assistant"""
    st.title(PAGE_TITLES['chat'])
    st.caption(PAGE_CAPTIONS['chat'])
    
    # Load CSS
    load_page_css('main.css', 'chat.css')
    
    # Initialize services and check user change
    initialize_services()
    current_user_id = get_current_user_id()
    check_user_change(current_user_id)
    
    # Try to load existing data
    if not st.session_state.llm_data_manager.is_data_loaded():
        _load_user_data(current_user_id)
    
    # Check for background analysis completion
    if not st.session_state.llm_data_manager.is_data_loaded():
        from frontend.pages.analytics import check_analysis_status
        if check_analysis_status(current_user_id):
            st.rerun()
    
    # Check if data is available
    if not st.session_state.llm_data_manager.is_data_loaded():
        _handle_no_data()
        return
    
    # Initialize chat agent
    _initialize_chat_agent()
    
    # Show data source status
    _show_data_status()
    
    st.markdown("---")
    
    # Quick action buttons
    _render_quick_actions()
    
    st.markdown("---")
    
    # Chat messages
    _render_chat_messages()
    
    st.markdown("---")
    
    # Chat input
    _render_chat_input()


def _load_user_data(user_id: str):
    """Load user's existing data from MongoDB"""
    try:
        db_manager = st.session_state.db_manager
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - cannot load user data")
            return
        
        # Load analytics and CSV data
        analytics, csv_df, csv_file_id = load_user_analytics_data(db_manager, user_id)
        
        if analytics:
            # Load into data manager
            st.session_state.llm_data_manager.load_llm_analysis(
                analytics['analysis_result'], csv_df
            )
            
            # Store in session state
            st.session_state.llm_analysis = analytics['analysis_result']
            st.session_state.llm_customer_data = st.session_state.llm_data_manager.get_customer_dataframe()
            st.session_state.uploaded_csv_id = csv_file_id
            
            logger.info(f"Loaded existing data for chat user: {user_id}")
            
    except Exception as e:
        logger.error(f"Error loading user data for chat: {str(e)}")


def _handle_no_data():
    """Handle case when no data is available"""
    if is_analysis_running():
        st.info("⏳ **AI Analysis in Progress**")
        st.markdown("""
        Your data is currently being analyzed. Please wait...
        
        The analysis continues in the background. You can stay on this page and it will automatically 
        update when complete, or return to the Analytics page.
        """)
        
        import time
        time.sleep(10)
        st.rerun()
    else:
        st.info("👆 Please upload and analyze CSV data first from the Analytics page")


def _initialize_chat_agent():
    """Initialize chat agent with LLM data"""
    if 'llm_customer_data' in st.session_state and st.session_state.llm_customer_data is not None:
        df = st.session_state.llm_customer_data.copy()
        csv_file_id = st.session_state.get('uploaded_csv_id')
        csv_content = st.session_state.get('uploaded_csv_content')
        
        st.session_state.nlq_agent = NLQAgent()
        st.session_state.nlq_agent.load(df, csv_file_id, csv_content)
        st.session_state.data_source = "llm_analysis"
        
        # Generate CSV summary as first message
        if "csv_summary_generated" not in st.session_state:
            _generate_csv_summary()
            st.session_state.csv_summary_generated = True
            
    elif "nlq_agent" not in st.session_state:
        st.session_state.data_source = "none"
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": CHAT_MESSAGES['welcome']
            }]


def _generate_csv_summary():
    """Generate CSV summary as first chat message"""
    try:
        if 'csv_summary_message' in st.session_state:
            summary_text = st.session_state.csv_summary_message
        else:
            summary = st.session_state.llm_data_manager.get_summary_data()
            insights = st.session_state.llm_data_manager.get_insights()
            
            if summary and insights:
                total = summary.get('total_customers', 0)
                high = summary.get('high_risk_customers', 0)
                medium = summary.get('medium_risk_customers', 0)
                low = summary.get('low_risk_customers', 0)
                
                summary_text = CSV_SUMMARY_TEMPLATE.format(
                    total_customers=total,
                    high_risk_customers=high,
                    high_risk_percent=(high/total*100) if total > 0 else 0,
                    medium_risk_customers=medium,
                    medium_risk_percent=(medium/total*100) if total > 0 else 0,
                    low_risk_customers=low,
                    low_risk_percent=(low/total*100) if total > 0 else 0,
                    revenue_at_risk=summary.get('total_revenue_at_risk', 0),
                    top_insights='\n'.join([f"• {i}" for i in insights.get('top_churn_drivers', [])[:2]]),
                    recommended_actions='\n'.join([f"• {a}" for a in insights.get('recommended_actions', [])[:2]])
                )
            else:
                summary_text = CSV_SUMMARY_FALLBACK
        
        st.session_state.messages = [{"role": "assistant", "content": summary_text}]
        
    except Exception as e:
        logger.error(f"Error generating CSV summary: {str(e)}")
        st.session_state.messages = [{
            "role": "assistant", 
            "content": CSV_SUMMARY_FALLBACK
        }]


def _show_data_status():
    """Show data source status"""
    data_source = st.session_state.get('data_source')
    
    if data_source == 'llm_analysis':
        st.success(CHAT_MESSAGES['using_ai_data'])
    elif data_source == 'none':
        st.warning(CHAT_MESSAGES['no_data_warning'])
    else:
        st.info(CHAT_MESSAGES['using_sample_data'])


def _render_quick_actions():
    """Render quick action buttons"""
    st.markdown("#### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    disabled = st.session_state.get('data_source') != 'llm_analysis'
    
    with col1:
        if st.button(QUICK_ACTIONS['summary'], use_container_width=True, disabled=disabled):
            _handle_quick_action('summary')
    
    with col2:
        if st.button(QUICK_ACTIONS['top_risks'], use_container_width=True, disabled=disabled):
            _handle_quick_action('top_risks')
    
    with col3:
        if st.button(QUICK_ACTIONS['recommendations'], use_container_width=True, disabled=disabled):
            _handle_quick_action('recommendations')


def _handle_quick_action(action_key: str):
    """Handle quick action button click"""
    if st.session_state.nlq_agent and st.session_state.nlq_agent.is_available():
        user_question = QUICK_ACTION_QUERIES[action_key]
        st.session_state.messages.append({"role": "user", "content": user_question})
        
        conversation_history = st.session_state.messages[:-1]
        response = st.session_state.nlq_agent.ask(user_question, conversation_history)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Store in database
        _store_chat(user_question, response)
        
        st.rerun()


def _render_chat_messages():
    """Render chat messages"""
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


def _render_chat_input():
    """Render chat input"""
    if st.session_state.get('data_source') == 'llm_analysis':
        if prompt := st.chat_input("Ask about your customer data..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            if st.session_state.nlq_agent and st.session_state.nlq_agent.is_available():
                with st.chat_message("assistant"):
                    with st.spinner(CHAT_MESSAGES['thinking']):
                        conversation_history = st.session_state.messages[:-1]
                        response = st.session_state.nlq_agent.ask(prompt, conversation_history)
                        st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Store in database
                _store_chat(prompt, response)
            else:
                with st.chat_message("assistant"):
                    st.error(CHAT_MESSAGES['ai_not_available'])
    else:
        st.chat_input(CHAT_MESSAGES['data_not_available'], disabled=True)


def _store_chat(question: str, answer: str):
    """Store chat interaction in MongoDB"""
    try:
        user_id = get_current_user_id()
        session_id = st.session_state.get('session_id', 'default')
        db_manager = st.session_state.db_manager
        
        store_chat_interaction(db_manager, user_id, question, answer, session_id)
        
    except Exception as e:
        logger.error(f"Error storing chat interaction: {str(e)}")

