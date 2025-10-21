"""
Chat page with AI assistant for customer data queries
"""
import streamlit as st
import pandas as pd
import logging
from datetime import datetime

# Import services
from src.services.llm_data_manager import LLMDataManager
from ai_agents.nlq_agent.nlq_direct import DirectNLQAgent
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

def clear_user_session_state():
    """Clear user-specific session state to prevent data leakage"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        logger.info(f"Clearing chat session state for user: {user_id}")
        
        # Clear user-specific data
        keys_to_clear = [
            'llm_analysis', 'llm_customer_data', 'uploaded_csv_path',
            'csv_summary_message', 'csv_summary_generated', 'messages',
            'nlq_agent', 'data_source'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                logger.info(f"Cleared chat session state key: {key}")
        
        # Reset data manager
        if 'llm_data_manager' in st.session_state:
            st.session_state.llm_data_manager = LLMDataManager()
        
        logger.info(f"Chat session state cleared for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing chat session state: {str(e)}")

def render_chat_page():
    """Render chat page with AI assistant"""
    st.title("💬 ChurnGuard AI Assistant")
    st.caption("Chat with AI about your customer data and churn analysis")
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    .stError {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    .stChatMessage {
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0d5aa7;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize services
    if 'llm_data_manager' not in st.session_state:
        st.session_state.llm_data_manager = LLMDataManager()
    
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    # Check if user has changed and clear session state
    current_user_id = st.session_state.get('user_id', 'demo_user')
    if 'last_user_id' not in st.session_state:
        st.session_state.last_user_id = current_user_id
    elif st.session_state.last_user_id != current_user_id:
        logger.info(f"Chat user changed from {st.session_state.last_user_id} to {current_user_id}")
        clear_user_session_state()
        st.session_state.last_user_id = current_user_id
    
    # Try to load existing data for the user
    if not st.session_state.llm_data_manager.is_data_loaded():
        load_user_data_from_mongodb(current_user_id)
    
    # Check for background analysis completion
    if not st.session_state.llm_data_manager.is_data_loaded():
        from frontend.pages.analytics import check_analysis_status
        if check_analysis_status(current_user_id):
            st.rerun()  # Refresh to show the loaded data
    
    # Check if analysis is available or in progress
    if not st.session_state.llm_data_manager.is_data_loaded():
        # Check if analysis is currently running
        analysis_in_progress = st.session_state.get('analysis_started', False)
        
        if analysis_in_progress:
            st.info("⏳ **AI Analysis in Progress**")
            st.markdown("""
            Your data is currently being analyzed. Please wait...
            
            The analysis continues in the background. You can stay on this page and it will automatically 
            update when complete, or return to the Analytics page.
            """)
            
            # Auto-refresh every 3 seconds to check if analysis is complete
            import time
            time.sleep(10)
            st.rerun()
        else:
            st.info("👆 Please upload and analyze CSV data first from the Analytics page")
        
        return
    
    # Initialize chat agent
    _init_chat_agent()
    
    # Data source status
    if st.session_state.get('data_source') == 'llm_analysis':
        st.success("✅ Using AI-analyzed data")
    elif st.session_state.get('data_source') == 'none':
        st.warning("⚠️ No data available - please upload CSV file first")
    else:
        st.info("📊 Using sample data")
    
    st.markdown("---")
    
    # Quick action buttons
    st.markdown("#### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Show Summary", use_container_width=True, disabled=st.session_state.get('data_source') != 'llm_analysis'):
            if st.session_state.nlq_agent and st.session_state.nlq_agent.is_available():
                # Add user question to chat
                user_question = "Give me a summary of the customer data"
                st.session_state.messages.append({"role": "user", "content": user_question})
                
                # Pass conversation history to the LLM
                conversation_history = st.session_state.messages[:-1]  # Exclude the current user message
                response = st.session_state.nlq_agent.ask(user_question, conversation_history)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": response})
                store_chat_interaction(user_question, response)
                st.rerun()
    
    with col2:
        if st.button("🎯 Top Risks", use_container_width=True, disabled=st.session_state.get('data_source') != 'llm_analysis'):
            if st.session_state.nlq_agent and st.session_state.nlq_agent.is_available():
                # Add user question to chat
                user_question = "What are the top risk factors for churn?"
                st.session_state.messages.append({"role": "user", "content": user_question})
                
                # Pass conversation history to the LLM
                conversation_history = st.session_state.messages[:-1]  # Exclude the current user message
                response = st.session_state.nlq_agent.ask(user_question, conversation_history)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": response})
                store_chat_interaction(user_question, response)
                st.rerun()
    
    with col3:
        if st.button("💡 Recommendations", use_container_width=True, disabled=st.session_state.get('data_source') != 'llm_analysis'):
            if st.session_state.nlq_agent and st.session_state.nlq_agent.is_available():
                # Add user question to chat
                user_question = "What recommendations do you have for customer retention?"
                st.session_state.messages.append({"role": "user", "content": user_question})
                
                # Pass conversation history to the LLM
                conversation_history = st.session_state.messages[:-1]  # Exclude the current user message
                response = st.session_state.nlq_agent.ask(user_question, conversation_history)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": response})
                store_chat_interaction(user_question, response)
                st.rerun()
    
    st.markdown("---")
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    st.markdown("---")
    
    # Chat input
    if st.session_state.get('data_source') == 'llm_analysis':
        # Enable chat input only when real data is available
        if prompt := st.chat_input("Ask about your customer data..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            if st.session_state.nlq_agent and st.session_state.nlq_agent.is_available():
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Pass conversation history to the LLM
                        conversation_history = st.session_state.messages[:-1]  # Exclude the current user message
                        response = st.session_state.nlq_agent.ask(prompt, conversation_history)
                        st.markdown(response)
                
                # Add assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Store chat interaction in MongoDB
                store_chat_interaction(prompt, response)
            else:
                with st.chat_message("assistant"):
                    st.error("AI assistant not available")
    else:
        # Disable chat input when no data is available
        st.chat_input("Upload CSV file first to enable chat...", disabled=True)

def load_user_data_from_mongodb(user_id: str):
    """Load user's existing data from MongoDB for chat"""
    try:
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - cannot load user data")
            return
        
        # Load analytics data
        analytics_data = db_manager.get_user_data('analytics', user_id)
        if analytics_data:
            # Get the most recent analysis
            latest_analysis = max(analytics_data, key=lambda x: x.get('analysis_date', datetime.min))
            
            # Load CSV data to get email mapping
            csv_data = db_manager.get_user_data('csv_files', user_id)
            original_csv_df = None
            if csv_data:
                latest_csv = max(csv_data, key=lambda x: x.get('upload_date', datetime.min))
                try:
                    # Convert stored CSV content back to DataFrame
                    import io
                    csv_content = latest_csv.get('file_content')
                    if csv_content:
                        original_csv_df = pd.read_csv(io.BytesIO(csv_content))
                        logger.info(f"Loaded original CSV data with {len(original_csv_df)} records")
                except Exception as e:
                    logger.warning(f"Could not load CSV content: {str(e)}")
                
                # Store CSV file ID and content in session state
                st.session_state.uploaded_csv_id = str(latest_csv['_id'])
                st.session_state.uploaded_csv_content = latest_csv.get('file_content')
            
            # Load analysis into data manager with original CSV data
            st.session_state.llm_data_manager.load_llm_analysis(latest_analysis['analysis_result'], original_csv_df)
            
            # Store in session state
            st.session_state.llm_analysis = latest_analysis['analysis_result']
            st.session_state.llm_customer_data = st.session_state.llm_data_manager.get_customer_dataframe()
            
            logger.info(f"Loaded existing data for chat user: {user_id}")
            
    except Exception as e:
        logger.error(f"Error loading user data for chat from MongoDB: {str(e)}")

def _init_chat_agent():
    """Initialize chat agent with LLM data and CSV file path"""
    # Always check for LLM analysis data first
    if 'llm_customer_data' in st.session_state and st.session_state.llm_customer_data is not None:
        # Use LLM-generated customer data
        df = st.session_state.llm_customer_data.copy()
        
        # Get CSV file ID and content from session state
        csv_file_id = st.session_state.get('uploaded_csv_id')
        csv_content = st.session_state.get('uploaded_csv_content')
        
        # Initialize or reinitialize agent with LLM data and CSV content
        st.session_state.nlq_agent = DirectNLQAgent()
        st.session_state.nlq_agent.load(df, csv_file_id, csv_content)  # Pass CSV file ID and content
        st.session_state.data_source = "llm_analysis"
        
        # Generate CSV summary as first message if not already done
        if "csv_summary_generated" not in st.session_state:
            _generate_csv_summary()
            st.session_state.csv_summary_generated = True
        
        logger.info(f"Chat agent initialized with CSV file ID: {csv_file_id}")
        
    elif "nlq_agent" not in st.session_state:
        # No fallback to sample data - require real data
        st.session_state.data_source = "none"
        
        # Initialize messages for no data
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": "👋 **Welcome to ChurnGuard AI Assistant!** Please upload and analyze your CSV file first from the Analytics page to start chatting about your data."
            }]

def _generate_csv_summary():
    """Generate CSV summary as first chat message"""
    try:
        # Check if summary message was generated in analytics
        if 'csv_summary_message' in st.session_state:
            summary_text = st.session_state.csv_summary_message
        else:
            # Generate summary from LLM data
            summary = st.session_state.llm_data_manager.get_summary_data()
            insights = st.session_state.llm_data_manager.get_insights()
            
            if summary and insights:
                summary_text = f"""📊 **CSV Analysis Complete!**

**Key Statistics:**
• **Total Customers:** {summary.get('total_customers', 0)}
• **High Risk:** {summary.get('high_risk_customers', 0)} customers ({summary.get('high_risk_customers', 0)/summary.get('total_customers', 1)*100:.1f}%)
• **Medium Risk:** {summary.get('medium_risk_customers', 0)} customers ({summary.get('medium_risk_customers', 0)/summary.get('total_customers', 1)*100:.1f}%)
• **Low Risk:** {summary.get('low_risk_customers', 0)} customers ({summary.get('low_risk_customers', 0)/summary.get('total_customers', 1)*100:.1f}%)
• **Revenue at Risk:** ${summary.get('total_revenue_at_risk', 0):,.2f}

**Top Insights:**
{chr(10).join([f"• {insight}" for insight in insights.get('top_churn_drivers', [])[:2]])}

**Immediate Actions Needed:**
{chr(10).join([f"• {action}" for action in insights.get('recommended_actions', [])[:2]])}

Ask me anything about your customer data! 🚀"""
            else:
                summary_text = "📊 **CSV Analysis Complete!** Your data has been analyzed. Ask me anything about your customers! 🚀"
        
        # Set as first message
        st.session_state.messages = [{"role": "assistant", "content": summary_text}]
        
    except Exception as e:
        logger.error(f"Error generating CSV summary: {str(e)}")
        # Fallback message
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "📊 **CSV Analysis Complete!** Your data has been analyzed. Ask me anything about your customers! 🚀"
        }]

def store_chat_interaction(question, answer):
    """Store chat interaction in MongoDB with SaaS data separation"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - chat interaction not persisted")
            return
        
        chat_data = {
            "timestamp": datetime.now(),
            "question": question,
            "answer": answer,
            "session_id": st.session_state.get('session_id', 'default')
        }
        
        # Store in MongoDB with SaaS separation
        db_manager.store_user_data('chat_interactions', user_id, chat_data)
        logger.info(f"Chat interaction stored in MongoDB for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error storing chat interaction in MongoDB: {str(e)}")
