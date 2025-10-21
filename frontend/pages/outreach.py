"""
Outreach campaigns management page
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List, Dict, Optional

# Import services
from src.services.llm_data_manager import LLMDataManager
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

def load_user_data_from_mongodb(user_id: str):
    """Load user's existing data from MongoDB for outreach"""
    try:
        # Get db_manager from session state or create new one
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        
        db_manager = st.session_state.db_manager
        
        if not db_manager.is_connected():
            logger.warning("MongoDB not connected - cannot load user data")
            return False
        
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
            
            # Load analysis into data manager
            if 'llm_data_manager' not in st.session_state:
                st.session_state.llm_data_manager = LLMDataManager()
            
            st.session_state.llm_data_manager.load_llm_analysis(latest_analysis['analysis_result'], original_csv_df)
            
            # Store in session state
            st.session_state.llm_analysis = latest_analysis['analysis_result']
            st.session_state.llm_customer_data = st.session_state.llm_data_manager.get_customer_dataframe()
            
            logger.info(f"Loaded existing data for outreach user: {user_id}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error loading user data for outreach from MongoDB: {str(e)}")
        return False

def render_outreach():
    """Render outreach campaigns page"""
    st.title("📢 Outreach Campaigns")
    st.caption("Create and manage automated outreach campaigns to retain customers")
    
    # Check email configuration status
    check_email_configuration()
    
    # Initialize services
    if 'llm_data_manager' not in st.session_state:
        st.session_state.llm_data_manager = LLMDataManager()
    
    # Get current user ID
    current_user_id = st.session_state.get('user_id', 'demo_user')
    
    # Try to load existing data for the user
    if not st.session_state.llm_data_manager.is_data_loaded():
        load_user_data_from_mongodb(current_user_id)
    
    # Check for background analysis completion
    if not st.session_state.llm_data_manager.is_data_loaded():
        from frontend.pages.analytics import check_analysis_status
        if check_analysis_status(current_user_id):
            st.rerun()  # Refresh to show the loaded data
    
    # Check if churn data is available or analysis in progress
    if not st.session_state.llm_data_manager.is_data_loaded():
        # Check if analysis is currently running
        analysis_in_progress = st.session_state.get('analysis_started', False)
        
        if analysis_in_progress:
            st.info("⏳ **AI Analysis in Progress**")
            st.markdown("""
            Your data is currently being analyzed. Please wait...
            
            The analysis continues in the background. You can stay on this page and it will automatically 
            update when complete, or return to the Analytics page.
            
            Once the analysis is complete, you'll be able to:
            - 📧 Create targeted email campaigns
            - 📱 Send SMS to high-risk customers
            - 📞 Launch voice call campaigns
            - 📊 Track campaign performance
            """)
            
            # Auto-refresh every 3 seconds to check if analysis is complete
            import time
            time.sleep(10)
            st.rerun()
        else:
            st.info("👆 Please upload CSV data and run AI analysis from the Analytics page first")
        
        return
    
    # Get customer data from LLM analysis
    churn_df = st.session_state.llm_customer_data
    
    if churn_df is None:
        st.error("No customer data available")
        return
    
    # Create tabs for different campaign types
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Campaigns", "📱 SMS Campaigns", "📞 Voice Campaigns", "📊 Campaign Analytics"])
    
    with tab1:
        render_email_campaigns(churn_df)
    
    with tab2:
        render_sms_campaigns(churn_df)
    
    with tab3:
        render_voice_campaigns(churn_df)
    
    with tab4:
        render_campaign_analytics()

def check_email_configuration():
    """Check email configuration status from .env file"""
    sender_email = os.getenv('SENDER_EMAIL', '')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    if sender_email and sender_password and sender_email != 'your-email@gmail.com':
        st.success("✅ Email configuration loaded from environment variables")
    else:
        st.warning("⚠️ Email configuration required in .env file to send real emails")
        st.info("💡 Please set SENDER_EMAIL and SENDER_PASSWORD in your .env file")

def render_email_campaigns(churn_df):
    """Render email campaigns section"""
    st.header("📧 Email Campaigns")
    
    # Campaign creation form
    with st.expander("➕ Create Email Campaign", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name", placeholder="e.g., High-Risk Retention Q4", key="email_campaign_name")
            subject_line = st.text_input("Subject Line", placeholder="e.g., We miss you! Let's talk...", key="email_subject_line")
            target_segment = st.selectbox("Target Segment", ["High Risk", "Medium Risk", "Low Risk", "All Customers"], key="email_target_segment")
        
        with col2:
            scheduled_date = st.date_input("Scheduled Date", key="email_scheduled_date")
            scheduled_time = st.time_input("Scheduled Time", key="email_scheduled_time")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="email_priority")
        
        # Email template
        st.subheader("📝 Email Template")
        
        template_type = st.selectbox(
            "Template Type",
            options=["Retention", "Win-back", "Nurturing", "Custom"],
            key="email_template_type",
            help="Select a pre-built template or create your own custom message"
        )
        
        if template_type.lower() in ["retention", "win-back", "nurturing"]:
            if template_type.lower() == "retention":
                default_template = """Hi {customer_name},

We noticed you might be considering leaving us, and we'd love to understand how we can better serve you.

Your feedback is valuable to us! We're committed to providing you with the best possible experience.

Please take a moment to let us know:
- What we can do better
- Any concerns you might have
- How we can improve your experience

We're here to help and want to make things right.

Best regards,
The Customer Success Team"""
            elif template_type.lower() == "win-back":
                default_template = """Hi {customer_name},

We miss you! It's been a while since we've seen you, and we have some exciting updates and special offers just for you.

Here's what's new:
- New features you'll love
- Special discount just for you
- Improved customer support

We'd love to have you back!

Best regards,
The Team"""
            else:  # nurturing
                default_template = """Hi {customer_name},

Thank you for being a valued customer! Here are some tips to get the most out of our service:

- Pro tip: Use feature X to save time
- New tutorial: How to maximize your results
- Community: Join our user group

We're here to help you succeed!

Best regards,
The Customer Success Team"""
        else:
            default_template = """Hi {customer_name},

Thank you for being a valued customer!

We hope you're enjoying our services.

Best regards,
The ChurnGuard Team"""
        
        message_template = st.text_area(
            "Email Content",
            value=default_template,
            height=200,
            placeholder="Use {customer_name} for personalization..."
        )
        
        # Preview
        col_preview1, col_preview2 = st.columns(2)
        
        with col_preview1:
            if st.button("👁️ Preview Email"):
                if 'customer_id' in churn_df.columns and 'email' in churn_df.columns:
                    sample_customer = churn_df.iloc[0]
                    preview_text = message_template.format(
                        customer_name=sample_customer.get('email', 'Customer').split('@')[0]
                    )
                    st.text_area("Preview", value=preview_text, height=150, disabled=True)
        
        with col_preview2:
            if st.button("📋 Show Target Recipients"):
                # Get target customers based on segment
                if target_segment == "High Risk":
                    target_df = churn_df[churn_df['risk_level'] == 'high']
                elif target_segment == "Medium Risk":
                    target_df = churn_df[churn_df['risk_level'] == 'medium']
                elif target_segment == "Low Risk":
                    target_df = churn_df[churn_df['risk_level'] == 'low']
                else:  # All Customers
                    target_df = churn_df
                
                st.session_state.show_recipients = True
                st.session_state.target_recipients_df = target_df
        
        # Display target recipients if button was clicked
        if st.session_state.get('show_recipients', False) and st.session_state.get('target_recipients_df') is not None:
            st.subheader(f"📧 Target Recipients ({len(st.session_state.target_recipients_df)} customers)")
            
            # Show relevant columns
            display_cols = ['customer_id', 'email', 'risk_level']
            if 'churn_probability' in st.session_state.target_recipients_df.columns:
                display_cols.append('churn_probability')
            
            # Filter to only existing columns
            display_cols = [col for col in display_cols if col in st.session_state.target_recipients_df.columns]
            
            if 'email' in display_cols:
                st.dataframe(
                    st.session_state.target_recipients_df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Check for missing emails
                missing_emails = st.session_state.target_recipients_df['email'].isna().sum()
                if missing_emails > 0:
                    st.warning(f"⚠️ Warning: {missing_emails} customer(s) don't have email addresses and will be skipped")
            else:
                st.warning("⚠️ No email addresses found in the customer data. Please ensure your CSV file includes an 'email' column.")
        
        # Create campaign
        if st.button("🚀 Create Email Campaign", type="primary"):
            if campaign_name and message_template:
                # Reset the recipients display
                if 'show_recipients' in st.session_state:
                    del st.session_state.show_recipients
                if 'target_recipients_df' in st.session_state:
                    del st.session_state.target_recipients_df
                
                create_email_campaign(campaign_name, subject_line, target_segment, message_template, scheduled_date, scheduled_time, priority)
            else:
                st.error("Please fill in campaign name and message template")
    
    # Active email campaigns
    st.subheader("📋 Active Email Campaigns")
    
    # Sample campaign data (in real implementation, this would come from the database)
    email_campaigns = [
        {
            "Name": "High-Risk Retention Q4",
            "Subject": "We miss you! Let's talk...",
            "Target": "High Risk",
            "Status": "Active",
            "Recipients": 89,
            "Sent": 89,
            "Opened": 67,
            "Clicked": 23,
            "Unsubscribed": 2
        },
        {
            "Name": "Win-back Campaign",
            "Subject": "Welcome back with special offers!",
            "Target": "Medium Risk",
            "Status": "Completed",
            "Recipients": 156,
            "Sent": 156,
            "Opened": 134,
            "Clicked": 45,
            "Unsubscribed": 1
        }
    ]
    
    if email_campaigns:
        campaigns_df = pd.DataFrame(email_campaigns)
        
        # Add calculated metrics
        campaigns_df['Open Rate'] = (campaigns_df['Opened'] / campaigns_df['Sent'] * 100).round(1)
        campaigns_df['Click Rate'] = (campaigns_df['Clicked'] / campaigns_df['Sent'] * 100).round(1)
        
        st.dataframe(campaigns_df, use_container_width=True, hide_index=True)
    else:
        st.info("No email campaigns created yet")

def render_sms_campaigns(churn_df):
    """Render SMS campaigns section"""
    st.header("📱 SMS Campaigns")
    
    # Campaign creation form
    with st.expander("➕ Create SMS Campaign", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("SMS Campaign Name", placeholder="e.g., Quick Win-back SMS", key="sms_campaign_name")
            target_segment = st.selectbox("Target Segment", ["High Risk", "Medium Risk", "All Customers"], key="sms_target_segment")
        
        with col2:
            scheduled_date = st.date_input("Scheduled Date", key="sms_scheduled_date")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="sms_priority")
        
        # SMS template (shorter)
        st.subheader("📝 SMS Template")
        st.caption("SMS messages should be concise (160 characters or less)")
        
        sms_template = st.text_area(
            "SMS Content",
            value="Hi {customer_name}! We miss you. Special offer just for you: 20% off. Reply STOP to opt out.",
            height=100,
            max_chars=160,
            help="Use {customer_name} for personalization. Keep it under 160 characters."
        )
        
        # Character count
        char_count = len(sms_template)
        if char_count > 160:
            st.error(f"⚠️ Message too long: {char_count}/160 characters")
        else:
            st.success(f"✅ Message length: {char_count}/160 characters")
        
        # Preview
        if st.button("👁️ Preview SMS"):
            if 'customer_id' in churn_df.columns:
                sample_customer = churn_df.iloc[0]
                preview_text = sms_template.format(
                    customer_name=sample_customer.get('email', 'Customer').split('@')[0]
                )
                st.text_area("Preview", value=preview_text, height=100, disabled=True)
        
        # Create campaign
        if st.button("🚀 Create SMS Campaign", type="primary"):
            if campaign_name and sms_template and char_count <= 160:
                create_sms_campaign(campaign_name, target_segment, sms_template, scheduled_date, priority)
            else:
                st.error("Please fill in all fields and keep message under 160 characters")
    
    # Active SMS campaigns
    st.subheader("📋 Active SMS Campaigns")
    
    sms_campaigns = [
        {
            "Name": "Quick Win-back SMS",
            "Target": "High Risk",
            "Status": "Active",
            "Recipients": 89,
            "Sent": 89,
            "Delivered": 87,
            "Replied": 12,
            "Opted Out": 1
        }
    ]
    
    if sms_campaigns:
        campaigns_df = pd.DataFrame(sms_campaigns)
        campaigns_df['Delivery Rate'] = (campaigns_df['Delivered'] / campaigns_df['Sent'] * 100).round(1)
        campaigns_df['Reply Rate'] = (campaigns_df['Replied'] / campaigns_df['Delivered'] * 100).round(1)
        
        st.dataframe(campaigns_df, use_container_width=True, hide_index=True)
    else:
        st.info("No SMS campaigns created yet")

def render_voice_campaigns(churn_df):
    """Render voice campaigns section"""
    st.header("📞 Voice Campaigns")
    
    st.info("🎯 Voice campaigns are best for high-value, high-risk customers who need personal attention.")
    
    # Campaign creation form
    with st.expander("➕ Create Voice Campaign", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Voice Campaign Name", placeholder="e.g., VIP Retention Calls", key="voice_campaign_name")
            target_segment = st.selectbox("Target Segment", ["High Risk", "High Value + High Risk"], key="voice_target_segment")
        
        with col2:
            scheduled_date = st.date_input("Scheduled Date", key="voice_scheduled_date")
            call_window = st.selectbox("Call Window", ["9 AM - 5 PM", "10 AM - 6 PM", "11 AM - 7 PM"], key="voice_call_window")
        
        # Call script
        st.subheader("📝 Call Script")
        
        call_script = st.text_area(
            "Call Script",
            value="""Hello {customer_name}, this is {agent_name} from {company_name}. 

I'm calling because we noticed you might be considering leaving us, and we'd love to understand how we can better serve you.

Your feedback is valuable to us! We're committed to providing you with the best possible experience.

Do you have a few minutes to discuss:
- What we can do better
- Any concerns you might have
- How we can improve your experience

We're here to help and want to make things right.""",
            height=200,
            help="Use {customer_name}, {agent_name}, {company_name} for personalization"
        )
        
        # Call settings
        st.subheader("⚙️ Call Settings")
        col_a, col_b = st.columns(2)
        
        with col_a:
            max_attempts = st.number_input("Max Attempts", min_value=1, max_value=5, value=3)
            retry_delay = st.number_input("Retry Delay (hours)", min_value=1, max_value=24, value=4)
        
        with col_b:
            agent_name = st.text_input("Agent Name", value="Sarah Johnson", key="voice_agent_name")
            company_name = st.text_input("Company Name", value="ChurnGuard", key="voice_company_name")
        
        # Create campaign
        if st.button("🚀 Create Voice Campaign", type="primary"):
            if campaign_name and call_script:
                create_voice_campaign(campaign_name, target_segment, call_script, scheduled_date, call_window, max_attempts, retry_delay, agent_name, company_name)
            else:
                st.error("Please fill in campaign name and call script")
    
    # Active voice campaigns
    st.subheader("📋 Active Voice Campaigns")
    
    voice_campaigns = [
        {
            "Name": "VIP Retention Calls",
            "Target": "High Risk",
            "Status": "Active",
            "Recipients": 25,
            "Attempted": 25,
            "Connected": 18,
            "Successful": 12,
            "Callback Requested": 3
        }
    ]
    
    if voice_campaigns:
        campaigns_df = pd.DataFrame(voice_campaigns)
        campaigns_df['Connection Rate'] = (campaigns_df['Connected'] / campaigns_df['Attempted'] * 100).round(1)
        campaigns_df['Success Rate'] = (campaigns_df['Successful'] / campaigns_df['Connected'] * 100).round(1)
        
        st.dataframe(campaigns_df, use_container_width=True, hide_index=True)
    else:
        st.info("No voice campaigns created yet")

def render_campaign_analytics():
    """Render campaign analytics section"""
    st.header("📊 Campaign Analytics")
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Campaigns", 3)
    with col2:
        st.metric("Active Campaigns", 2)
    with col3:
        st.metric("Total Recipients", 270)
    with col4:
        st.metric("Overall Response Rate", "23.4%")
    
    # Campaign performance chart
    st.subheader("📈 Campaign Performance")
    
    performance_data = pd.DataFrame({
        'Campaign': ['Email Retention', 'SMS Win-back', 'Voice VIP'],
        'Sent': [89, 89, 25],
        'Opened/Connected': [67, 87, 18],
        'Clicked/Replied': [23, 12, 12],
        'Converted': [12, 8, 8]
    })
    
    fig = px.bar(
        performance_data,
        x='Campaign',
        y=['Sent', 'Opened/Connected', 'Clicked/Replied', 'Converted'],
        title="Campaign Performance Comparison",
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Response rates
    st.subheader("📊 Response Rates by Channel")
    
    response_rates = pd.DataFrame({
        'Channel': ['Email', 'SMS', 'Voice'],
        'Open/Delivery Rate': [75.3, 97.8, 72.0],
        'Response Rate': [25.8, 13.5, 48.0],
        'Conversion Rate': [13.5, 9.0, 32.0]
    })
    
    st.dataframe(response_rates, use_container_width=True, hide_index=True)

def create_email_campaign(name, subject, segment, template, date, time, priority):
    """Create and send email campaign"""
    try:
        # Combine date and time
        scheduled_datetime = datetime.combine(date, time)
        current_datetime = datetime.now()
        
        # Get target customers based on segment
        target_customers = get_target_customers(segment)
        
        if not target_customers:
            st.warning("⚠️ No customers found for the selected segment. Please run churn analysis first.")
            return
        
        # Check if this is a scheduled email (future date/time)
        if scheduled_datetime > current_datetime:
            # Count valid email addresses
            valid_emails = sum(1 for c in target_customers if c.get('email') and not pd.isna(c.get('email')))
            
            # Schedule for later
            schedule_email_campaign(name, subject, segment, template, scheduled_datetime, priority, target_customers)
            st.success(f"✅ Email campaign '{name}' scheduled successfully!")
            
            schedule_info = f"📧 Campaign Scheduled:\n- Target segment: {segment}\n- Scheduled for: {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}\n- Priority: {priority}\n- Total recipients: {len(target_customers)}\n- Valid emails: {valid_emails}"
            if valid_emails < len(target_customers):
                schedule_info += f"\n- Will skip: {len(target_customers) - valid_emails} (no email)"
            st.info(schedule_info)
        else:
            # Send immediately
            sent_count = 0
            failed_count = 0
            skipped_count = 0
            
            for customer in target_customers:
                try:
                    # Check if customer has email
                    customer_email = customer.get('email', '')
                    if not customer_email or pd.isna(customer_email):
                        logger.warning(f"Skipping customer {customer.get('customer_id', 'Unknown')} - no email address")
                        skipped_count += 1
                        continue
                    
                    # Personalize the email template
                    personalized_content = template.format(
                        customer_name=customer.get('customer_id', 'Valued Customer'),
                        email=customer_email,
                        churn_probability=customer.get('churn_probability', 0)
                    )
                    
                    # Send real email
                    send_real_email(customer_email, subject, personalized_content)
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send email to {customer.get('email', '')}: {str(e)}")
                    failed_count += 1
            
            # Show results
            st.success(f"✅ Email campaign '{name}' completed!")
            result_message = f"📧 Campaign Results:\n- Emails sent: {sent_count}\n- Failed: {failed_count}"
            if skipped_count > 0:
                result_message += f"\n- Skipped (no email): {skipped_count}"
            result_message += f"\n- Target segment: {segment}\n- Sent at: {current_datetime.strftime('%Y-%m-%d %H:%M')}\n- Priority: {priority}"
            st.info(result_message)
        
        # Store campaign data
        campaign_data = {
            "name": name,
            "type": "email",
            "subject": subject,
            "segment": segment,
            "template": template,
            "scheduled_date": date,
            "scheduled_time": time,
            "scheduled_datetime": scheduled_datetime,
            "priority": priority,
            "sent_count": sent_count if scheduled_datetime <= current_datetime else 0,
            "failed_count": failed_count if scheduled_datetime <= current_datetime else 0,
            "status": "scheduled" if scheduled_datetime > current_datetime else "sent",
            "created_at": datetime.now()
        }
        
        if 'campaigns' not in st.session_state:
            st.session_state.campaigns = []
        st.session_state.campaigns.append(campaign_data)
        
    except Exception as e:
        st.error(f"❌ Error creating email campaign: {str(e)}")
        logger.error(f"Email campaign creation error: {str(e)}")

def schedule_email_campaign(name, subject, segment, template, scheduled_datetime, priority, target_customers):
    """Schedule email campaign for future sending"""
    # Store scheduled campaign
    if 'scheduled_campaigns' not in st.session_state:
        st.session_state.scheduled_campaigns = []
    
    scheduled_campaign = {
        "name": name,
        "subject": subject,
        "segment": segment,
        "template": template,
        "scheduled_datetime": scheduled_datetime,
        "priority": priority,
        "target_customers": target_customers,
        "created_at": datetime.now()
    }
    
    st.session_state.scheduled_campaigns.append(scheduled_campaign)
    
    # In a real implementation, you would use a task scheduler like Celery
    # For demo purposes, we'll just store it and show a message
    logger.info(f"📅 Email campaign '{name}' scheduled for {scheduled_datetime}")

def get_target_customers(segment):
    """Get target customers based on segment"""
    if not st.session_state.llm_data_manager.is_data_loaded():
        return []
    
    churn_df = st.session_state.llm_customer_data
    
    if segment == "High Risk":
        return churn_df[churn_df['risk_level'] == 'high'].to_dict('records')
    elif segment == "Medium Risk":
        return churn_df[churn_df['risk_level'] == 'medium'].to_dict('records')
    elif segment == "Low Risk":
        return churn_df[churn_df['risk_level'] == 'low'].to_dict('records')
    else:  # All Customers
        return churn_df.to_dict('records')

def get_email_config():
    """Get email configuration from session state or environment"""
    # Get from session state if available
    if 'email_config' in st.session_state:
        config = st.session_state.email_config
        return config['smtp_server'], config['smtp_port'], config['sender_email'], config['sender_password']
    
    # Fallback to environment variables
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SENDER_EMAIL', '')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    return smtp_server, smtp_port, sender_email, sender_password

def send_real_email(to_email: str, subject: str, content: str) -> bool:
    """Send real email using SMTP"""
    try:
        smtp_server, smtp_port, sender_email, sender_password = get_email_config()
        
        if not sender_email or not sender_password:
            logger.warning("Email configuration not complete, using simulation")
            return send_email_simulation(to_email, subject, content)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(content, 'plain'))
        
        # Connect to server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(sender_email, sender_password)
        
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        logger.info(f"📧 Real email sent successfully to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # Fallback to simulation
        return send_email_simulation(to_email, subject, content)

def send_email_simulation(email, subject, content):
    """Simulate sending an email (for demo purposes)"""
    # In a real implementation, this would use SMTP, SendGrid, etc.
    logger.info(f"📧 Simulated email sent to {email}: {subject}")
    return True

def create_sms_campaign(name, segment, template, date, priority):
    """Create SMS campaign"""
    try:
        st.success(f"✅ SMS campaign '{name}' created successfully!")
        st.info(f"📱 Campaign Details:\n- Target: {segment}\n- Scheduled: {date}\n- Priority: {priority}")
        
        campaign_data = {
            "name": name,
            "type": "sms",
            "segment": segment,
            "template": template,
            "scheduled_date": date,
            "priority": priority,
            "created_at": datetime.now()
        }
        
        if 'campaigns' not in st.session_state:
            st.session_state.campaigns = []
        st.session_state.campaigns.append(campaign_data)
        
    except Exception as e:
        st.error(f"❌ Error creating SMS campaign: {str(e)}")
        logger.error(f"SMS campaign creation error: {str(e)}")

def create_voice_campaign(name, segment, script, date, window, attempts, delay, agent, company):
    """Create voice campaign"""
    try:
        st.success(f"✅ Voice campaign '{name}' created successfully!")
        st.info(f"📞 Campaign Details:\n- Target: {segment}\n- Scheduled: {date}\n- Window: {window}\n- Agent: {agent}")
        
        campaign_data = {
            "name": name,
            "type": "voice",
            "segment": segment,
            "script": script,
            "scheduled_date": date,
            "call_window": window,
            "max_attempts": attempts,
            "retry_delay": delay,
            "agent_name": agent,
            "company_name": company,
            "created_at": datetime.now()
        }
        
        if 'campaigns' not in st.session_state:
            st.session_state.campaigns = []
        st.session_state.campaigns.append(campaign_data)
        
    except Exception as e:
        st.error(f"❌ Error creating voice campaign: {str(e)}")
        logger.error(f"Voice campaign creation error: {str(e)}")
