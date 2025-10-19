"""
Main dashboard with LLM-based CSV analysis and insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Import services
from src.services.llm_data_manager import LLMDataManager
from ai_agents.csv_processor.csv_to_llm import CSVToLLMProcessor

logger = logging.getLogger(__name__)

def render_dashboard():
    """Render main dashboard"""
    st.title("🛡️ ChurnGuard Dashboard")
    st.caption("Upload customer data for AI-powered churn analysis and insights")
    
    # Initialize LLM processor and data manager
    if 'csv_processor' not in st.session_state:
        st.session_state.csv_processor = CSVToLLMProcessor()
    
    if 'llm_data_manager' not in st.session_state:
        st.session_state.llm_data_manager = LLMDataManager()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Data Upload", "📊 AI Analysis", "📢 Outreach Campaigns", "📈 Insights"])
    
    with tab1:
        render_data_upload()
    
    with tab2:
        render_ai_analysis()
    
    with tab3:
        render_outreach_campaigns()
    
    with tab4:
        render_insights()

def render_data_upload():
    """Render data upload section"""
    st.header("📤 Upload Customer Data")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload CSV with customer data",
        type=['csv'],
        help="CSV will be analyzed by AI to generate churn predictions and insights"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            
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
                        with st.spinner("🤖 AI is analyzing your data..."):
                            try:
                                # Process CSV through LLM
                                analysis_result = st.session_state.csv_processor.process_csv(df)
                                
                                if analysis_result:
                                    # Load analysis into data manager with original CSV data
                                    st.session_state.llm_data_manager.load_llm_analysis(analysis_result, df)
                                    
                                    # Store in session state for other components
                                    st.session_state.llm_analysis = analysis_result
                                    st.session_state.llm_customer_data = st.session_state.llm_data_manager.get_customer_dataframe()
                                    
                                    st.success("✅ AI analysis completed!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to process data with AI")
                            except Exception as e:
                                st.error(f"❌ Error during AI analysis: {str(e)}")
                    else:
                        st.error("❌ AI processor not available. Please check your configuration.")
            
            with col2:
                if st.session_state.llm_data_manager.is_data_loaded():
                    st.success("✅ AI Analysis Complete")
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
                    
                    st.metric("Revenue at Risk", f"${summary.get('total_revenue_at_risk', 0):,}")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logger.error(f"File processing error: {str(e)}")

def render_ai_analysis():
    """Render AI analysis results"""
    st.header("📊 AI Analysis Results")
    
    if not st.session_state.llm_data_manager.is_data_loaded():
        st.info("👆 Please upload and analyze data first")
        return
    
    # Get data from LLM analysis
    customer_df = st.session_state.llm_data_manager.get_customer_dataframe()
    summary = st.session_state.llm_data_manager.get_summary_data()
    insights = st.session_state.llm_data_manager.get_insights()
    
    if not customer_df is not None:
        st.error("No customer data available")
        return
    
    # Summary metrics
    st.subheader("📈 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(customer_df))
    with col2:
        st.metric("High Risk", len(customer_df[customer_df['risk_level'] == 'high']))
    with col3:
        st.metric("Medium Risk", len(customer_df[customer_df['risk_level'] == 'medium']))
    with col4:
        st.metric("Low Risk", len(customer_df[customer_df['risk_level'] == 'low']))
    
    # Churn probability distribution
    st.subheader("📊 Churn Probability Distribution")
    
    # Create distribution chart
    fig = px.histogram(
        customer_df, 
        x='churn_probability', 
        nbins=20,
        title="Distribution of Churn Probabilities",
        labels={'churn_probability': 'Churn Probability', 'count': 'Number of Customers'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk level pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = customer_df['risk_level'].value_counts()
        fig_pie = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Customer Risk Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Revenue impact chart
        revenue_data = customer_df.groupby('risk_level')['estimated_revenue_impact'].sum().reset_index()
        fig_bar = px.bar(
            revenue_data,
            x='risk_level',
            y='estimated_revenue_impact',
            title="Revenue at Risk by Risk Level",
            labels={'estimated_revenue_impact': 'Revenue at Risk ($)', 'risk_level': 'Risk Level'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Customer details table
    st.subheader("👥 Customer Details")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "high", "medium", "low"])
    with col2:
        sort_by = st.selectbox("Sort by", ["priority_score", "churn_probability", "estimated_revenue_impact"])
    
    # Apply filters
    filtered_df = customer_df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    
    # Sort data
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
    
    # Display table
    st.dataframe(
        filtered_df[['customer_id', 'churn_probability', 'risk_level', 'priority_score', 'estimated_revenue_impact']],
        use_container_width=True
    )

def render_outreach_campaigns():
    """Render outreach campaigns section"""
    st.header("📢 Outreach Campaigns")
    
    if not st.session_state.llm_data_manager.is_data_loaded():
        st.info("👆 Please upload and analyze data first")
        return
    
    customer_df = st.session_state.llm_data_manager.get_customer_dataframe()
    insights = st.session_state.llm_data_manager.get_insights()
    
    # Campaign recommendations
    st.subheader("🎯 Campaign Recommendations")
    
    if insights and insights.get('recommended_actions'):
        for i, action in enumerate(insights['recommended_actions'], 1):
            st.write(f"{i}. {action}")
    
    # High-risk customers for immediate outreach
    st.subheader("🚨 High-Risk Customers")
    high_risk = customer_df[customer_df['risk_level'] == 'high'].head(10)
    
    if not high_risk.empty:
        st.dataframe(
            high_risk[['customer_id', 'churn_probability', 'estimated_revenue_impact', 'retention_recommendation']],
            use_container_width=True
        )
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 Email Campaign", use_container_width=True):
                st.info("Email campaign feature coming soon!")
        with col2:
            if st.button("📱 SMS Campaign", use_container_width=True):
                st.info("SMS campaign feature coming soon!")
        with col3:
            if st.button("📞 Call Campaign", use_container_width=True):
                st.info("Call campaign feature coming soon!")
    else:
        st.info("No high-risk customers found")

def render_insights():
    """Render insights section"""
    st.header("📈 AI Insights")
    
    if not st.session_state.llm_data_manager.is_data_loaded():
        st.info("👆 Please upload and analyze data first")
        return
    
    insights = st.session_state.llm_data_manager.get_insights()
    analytics = st.session_state.llm_data_manager.get_analytics()
    
    if not insights:
        st.error("No insights available")
        return
    
    # Top churn drivers
    st.subheader("🔍 Top Churn Drivers")
    if insights.get('top_churn_drivers'):
        for i, driver in enumerate(insights['top_churn_drivers'], 1):
            st.write(f"**{i}.** {driver}")
    
    # Retention opportunities
    st.subheader("💡 Retention Opportunities")
    if insights.get('retention_opportunities'):
        for i, opportunity in enumerate(insights['retention_opportunities'], 1):
            st.write(f"**{i}.** {opportunity}")
    
    # Analytics charts
    if analytics:
        st.subheader("📊 Advanced Analytics")
        
        # Churn probability distribution
        churn_dist = analytics.get('churn_probability_distribution', {})
        if churn_dist:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_dist = px.bar(
                    x=list(churn_dist.keys()),
                    y=list(churn_dist.values()),
                    title="Churn Probability Distribution",
                    labels={'x': 'Probability Range', 'y': 'Number of Customers'}
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                # Revenue at risk by segment
                revenue_segments = analytics.get('revenue_at_risk_by_segment', {})
                if revenue_segments:
                    fig_revenue = px.pie(
                        values=list(revenue_segments.values()),
                        names=list(revenue_segments.keys()),
                        title="Revenue at Risk by Segment"
                    )
                    st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Engagement trends
        engagement_trends = analytics.get('engagement_trends', {})
        if engagement_trends:
            fig_engagement = px.bar(
                x=list(engagement_trends.keys()),
                y=list(engagement_trends.values()),
                title="Customer Engagement Trends",
                labels={'x': 'Engagement Level', 'y': 'Number of Customers'}
            )
            st.plotly_chart(fig_engagement, use_container_width=True)
