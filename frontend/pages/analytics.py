"""
Analytics page with CSV upload and data visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import os
import threading
import time
from datetime import datetime

# Import services
from src.services.llm_data_manager import LLMDataManager
from ai_agents.csv_processor.csv_to_llm import CSVToLLMProcessor
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

def run_background_analysis(df, csv_file_id, user_id):
    """Run AI analysis in background thread"""
    try:
        logger.info(f"Starting background analysis for user: {user_id}")
        
        # Create a new database manager instance for the background thread
        db_manager = DatabaseManager()
        
        # Initialize CSV processor
        csv_processor = CSVToLLMProcessor()
        
        if csv_processor.is_available():
            # Process CSV through LLM
            analysis_result = csv_processor.process_csv(df, None)
            
            if analysis_result:
                # Store analytics in MongoDB
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
                
                # Store in MongoDB
                success = db_manager.store_user_data('analytics', user_id, analysis_data)
                
                if success:
                    logger.info(f"Background analysis completed successfully for user: {user_id}")
                else:
                    logger.error(f"Failed to store analysis results for user: {user_id}")
            else:
                logger.error(f"Analysis failed for user: {user_id}")
        else:
            logger.error(f"CSV processor not available for user: {user_id}")
            
    except Exception as e:
        logger.error(f"Error in background analysis for user {user_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()

def check_analysis_status(user_id):
    """Check if analysis is completed and load data if ready"""
    try:
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        if not db_manager.is_connected():
            return False
        
        # Check for completed analysis
        analytics_data = db_manager.get_user_data('analytics', user_id)
        if analytics_data:
            # Get the most recent analysis
            latest_analysis = max(analytics_data, key=lambda x: x.get('analysis_date', datetime.min))
            
            if latest_analysis.get('status') == 'completed':
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
                
                # Load analysis into data manager with original CSV data
                st.session_state.llm_data_manager.load_llm_analysis(latest_analysis['analysis_result'], original_csv_df)
                
                # Store in session state
                st.session_state.llm_analysis = latest_analysis['analysis_result']
                st.session_state.llm_customer_data = st.session_state.llm_data_manager.get_customer_dataframe()
                
                logger.info(f"Analysis data loaded for user: {user_id}")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking analysis status for user {user_id}: {str(e)}")
        return False

def clear_user_session_state():
    """Clear user-specific session state to prevent data leakage"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        logger.info(f"Clearing session state for user: {user_id}")
        
        # Clear user-specific data
        keys_to_clear = [
            'llm_analysis', 'llm_customer_data', 'uploaded_csv_path',
            'csv_summary_message', 'csv_summary_generated', 'messages',
            'nlq_agent', 'data_source'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                logger.info(f"Cleared session state key: {key}")
        
        # Reset data manager
        if 'llm_data_manager' in st.session_state:
            st.session_state.llm_data_manager = LLMDataManager()
        
        logger.info(f"Session state cleared for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing session state: {str(e)}")

def render_analytics_page():
    """Render analytics page with CSV upload and data visualization"""
    st.title("📊 ChurnGuard Analytics")
    st.caption("AI-powered churn analysis and data visualization")
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
    if 'csv_processor' not in st.session_state:
        st.session_state.csv_processor = CSVToLLMProcessor()
    
    if 'llm_data_manager' not in st.session_state:
        st.session_state.llm_data_manager = LLMDataManager()
    
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    # Check if user has changed and clear session state
    current_user_id = st.session_state.get('user_id', 'demo_user')
    if 'last_user_id' not in st.session_state:
        st.session_state.last_user_id = current_user_id
    elif st.session_state.last_user_id != current_user_id:
        logger.info(f"User changed from {st.session_state.last_user_id} to {current_user_id}")
        clear_user_session_state()
        st.session_state.last_user_id = current_user_id
    
    # Try to load existing data for the user
    if not st.session_state.llm_data_manager.is_data_loaded():
        load_user_data_from_mongodb(current_user_id)
    
    # Check for background analysis completion
    if not st.session_state.llm_data_manager.is_data_loaded():
        if check_analysis_status(current_user_id):
            st.rerun()  # Refresh to show the loaded data
    
    # CSV Upload Section
    render_csv_upload_section()
    
    # Check if analysis is available
    if not st.session_state.llm_data_manager.is_data_loaded():
        # Show welcome message when no data is loaded
        st.info("👆 Please upload your CSV file above to start the analysis")
        return
    
    # Analytics Dashboard
    render_analytics_dashboard()

def render_csv_upload_section():
    """Render CSV upload section"""
    st.subheader("📁 Upload Customer Data")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload CSV with customer data",
        type=['csv'],
        help="CSV will be analyzed by AI to generate churn predictions and insights",
        key="csv_uploader"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            
            # Store CSV file directly in MongoDB
            csv_file_id = store_csv_in_mongodb(uploaded_file, df)
            
            if csv_file_id:
                # Store file ID in session state instead of file path
                st.session_state.uploaded_csv_id = csv_file_id
                st.success(f"✅ CSV file stored in MongoDB (ID: {csv_file_id[:8]}...)")
            else:
                st.error("❌ Failed to store CSV file in MongoDB")
                return
            
            # Preview data
            with st.expander("📊 Preview Data", expanded=True):
                st.dataframe(df.head(10))
                
                # Show data info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Records", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
            
            # AI Analysis Button
            st.subheader("🤖 AI Analysis")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🚀 Analyze with AI", type="primary", use_container_width=True):
                    if st.session_state.csv_processor.is_available():
                        try:
                            # Start background analysis
                            user_id = st.session_state.get('user_id', 'demo_user')
                            
                            # Store analysis status in session state
                            st.session_state.analysis_started = True
                            st.session_state.analysis_start_time = datetime.now()
                            
                            # Start background thread
                            analysis_thread = threading.Thread(
                                target=run_background_analysis,
                                args=(df, csv_file_id, user_id),
                                daemon=True
                            )
                            analysis_thread.start()
                            
                            st.success("🚀 AI analysis started in background!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error starting AI analysis: {str(e)}")
                    else:
                        st.error("❌ AI processor not available. Please check your configuration.")
            
            with col2:
                if st.session_state.llm_data_manager.is_data_loaded():
                    st.success("✅ AI Analysis Complete")
                elif st.session_state.get('analysis_started', False):
                    st.info("⏳ AI Analysis Running...")
                else:
                    st.info("⏳ Ready for AI Analysis")
            
            # Show analysis status
            if st.session_state.llm_data_manager.is_data_loaded():
                st.subheader("📊 Analysis Results")
                summary = st.session_state.llm_data_manager.get_summary_data()
                
                if summary:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Customers", summary.get('total_customers', 0))
                    with col2:
                        st.metric("High Risk", summary.get('high_risk_customers', 0))
                    with col3:
                        st.metric("Medium Risk", summary.get('medium_risk_customers', 0))
                    with col4:
                        st.metric("Low Risk", summary.get('low_risk_customers', 0))
            elif st.session_state.get('analysis_started', False):
                # Show analysis progress
                st.subheader("⏳ Analysis Status")
                st.info("🤖 AI is analyzing your data in the background...")
                
                # Show elapsed time
                if 'analysis_start_time' in st.session_state:
                    elapsed = datetime.now() - st.session_state.analysis_start_time
                    st.info(f"⏱️ Analysis running for: {elapsed.seconds // 60} minutes {elapsed.seconds % 60} seconds")
                
                st.info("💡 You can navigate to other pages - the analysis will continue running!")
                st.info("🔄 Check back in a few minutes to see the results.")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logger.error(f"File processing error: {str(e)}")

def load_user_data_from_mongodb(user_id: str):
    """Load user's existing data from MongoDB"""
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
            
            # Load analysis into data manager with original CSV data
            st.session_state.llm_data_manager.load_llm_analysis(latest_analysis['analysis_result'], original_csv_df)
            
            # Store in session state
            st.session_state.llm_analysis = latest_analysis['analysis_result']
            st.session_state.llm_customer_data = st.session_state.llm_data_manager.get_customer_dataframe()
            
            # Load CSV file ID
            csv_data = db_manager.get_user_data('csv_files', user_id)
            if csv_data:
                latest_csv = max(csv_data, key=lambda x: x.get('upload_date', datetime.min))
                st.session_state.uploaded_csv_id = str(latest_csv['_id'])
            
            logger.info(f"Loaded existing data for user: {user_id}")
            logger.info(f"Analytics data found: {len(analytics_data)} records")
            logger.info(f"CSV data found: {len(csv_data) if csv_data else 0} records")
            
    except Exception as e:
        logger.error(f"Error loading user data from MongoDB: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def store_csv_in_mongodb(uploaded_file, df):
    """Store CSV file directly in MongoDB"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        logger.info(f"Storing CSV file in MongoDB for user: {user_id}")
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - CSV not persisted")
            return None
        
        # Store CSV file data
        csv_data = {
            "file_name": uploaded_file.name,
            "file_content": uploaded_file.getvalue(),  # Store binary content
            "file_size": len(uploaded_file.getvalue()),
            "upload_date": datetime.now(),
            "record_count": len(df),
            "columns": list(df.columns),
            "sample_data": df.head(5).to_dict('records'),
            "mime_type": uploaded_file.type
        }
        
        # Store in MongoDB with SaaS separation
        success = db_manager.store_user_data('csv_files', user_id, csv_data)
        
        if success:
            # Get the stored document to return its ID
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
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def retrieve_csv_from_mongodb(file_id, user_id):
    """Retrieve CSV file from MongoDB"""
    try:
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - cannot retrieve CSV")
            return None
        
        # Get CSV file data
        csv_files = db_manager.get_user_data('csv_files', user_id)
        
        # Find the specific file by ID
        for csv_file in csv_files:
            if str(csv_file['_id']) == file_id:
                return csv_file
        
        logger.warning(f"CSV file with ID {file_id} not found")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving CSV from MongoDB: {str(e)}")
        return None

def store_analytics_in_mongodb(analysis_result, df, csv_file_id):
    """Store analytics results in MongoDB with SaaS data separation"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        logger.info(f"Storing analytics data for user: {user_id}")
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - analytics not persisted")
            return
        
        # Store LLM analysis results
        analysis_data = {
            "analysis_date": datetime.now(),
            "analysis_result": analysis_result,
            "summary": analysis_result.get('summary', {}),
            "churn_predictions": analysis_result.get('churn_predictions', {}),
            "insights": analysis_result.get('insights', {}),
            "analytics": analysis_result.get('analytics', {}),
            "csv_file_id": csv_file_id  # Reference to the CSV file in MongoDB
        }
        
        # Store in MongoDB with SaaS separation
        analytics_success = db_manager.store_user_data('analytics', user_id, analysis_data)
        
        logger.info(f"Analytics storage success: {analytics_success}")
        logger.info(f"Analytics data stored in MongoDB for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error storing analytics in MongoDB: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def render_analytics_dashboard():
    """Render simplified analytics dashboard"""
    st.subheader("📈 Analytics Dashboard")
    
    # Get data from LLM analysis
    customer_df = st.session_state.llm_data_manager.get_customer_dataframe()
    summary = st.session_state.llm_data_manager.get_summary_data()
    insights = st.session_state.llm_data_manager.get_insights()
    
    if customer_df is None:
        st.error("No customer data available")
        return
    
    # Summary metrics - simplified layout
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(customer_df))
    with col2:
        st.metric("High Risk", len(customer_df[customer_df['risk_level'] == 'high']))
    with col3:
        st.metric("Medium Risk", len(customer_df[customer_df['risk_level'] == 'medium']))
    with col4:
        st.metric("Low Risk", len(customer_df[customer_df['risk_level'] == 'low']))
    
    # Revenue at risk
    st.metric("Revenue at Risk", f"${customer_df['estimated_revenue_impact'].sum():,.2f}")
    
    st.markdown("---")
    
    # Single chart - Customer Risk Distribution
    st.subheader("📊 Customer Risk Distribution")
    risk_counts = customer_df['risk_level'].value_counts()
    fig_pie = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Customer Risk Distribution",
        color_discrete_map={'high': '#ff4444', 'medium': '#ffaa00', 'low': '#44ff44'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Key Insights - simplified
    st.subheader("💡 Key Insights")
    
    if insights:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Top Churn Drivers")
            if insights.get('top_churn_drivers'):
                for i, driver in enumerate(insights['top_churn_drivers'][:3], 1):
                    st.write(f"**{i}.** {driver}")
        
        with col2:
            st.markdown("#### 🎯 Recommended Actions")
            if insights.get('recommended_actions'):
                for i, action in enumerate(insights['recommended_actions'][:3], 1):
                    st.write(f"**{i}.** {action}")
    
    st.markdown("---")
    
    # High-risk customers table - simplified
    st.subheader("🚨 High-Risk Customers")
    high_risk = customer_df[customer_df['risk_level'] == 'high'].head(5)
    
    if not high_risk.empty:
        st.dataframe(
            high_risk[['customer_id', 'churn_probability', 'estimated_revenue_impact']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 No high-risk customers found!")
