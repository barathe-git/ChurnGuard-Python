"""
ChurnGuard Application Constants
Centralized location for all static messages, UI text, and configuration values
"""

# ============================================================================
# APPLICATION INFORMATION
# ============================================================================
APP_NAME = "ChurnGuard"
APP_VERSION = "1.0.0"
APP_TAGLINE = "AI-Powered Customer Retention Platform"
APP_ICON = "🛡️"
APP_COPYRIGHT = "© 2025 ChurnGuard. All rights reserved."

# ============================================================================
# PAGE TITLES AND CAPTIONS
# ============================================================================
PAGE_TITLES = {
    'analytics': "📊 ChurnGuard Analytics",
    'chat': "💬 ChurnGuard AI Assistant",
    'outreach': "📢 Outreach Campaigns",
    'settings': "⚙️ Settings",
    'login': f"{APP_ICON} ChurnGuard Login"
}

PAGE_CAPTIONS = {
    'analytics': "AI-powered churn analysis and data visualization",
    'chat': "Chat with AI about your customer data and churn analysis",
    'outreach': "Create and manage automated outreach campaigns to retain customers",
    'login': APP_TAGLINE
}

# ============================================================================
# NAVIGATION
# ============================================================================
NAV_ITEMS = {
    'analytics': "📊 Analytics",
    'chat': "💬 Chat Assistant",
    'outreach': "📢 Outreach",
    'settings': "⚙️ Settings"
}

# ============================================================================
# AUTHENTICATION MESSAGES
# ============================================================================
AUTH_MESSAGES = {
    'login_success': "✅ Login successful!",
    'logout_success': "✅ Logged out successfully!",
    'register_success': "✅ Account created successfully! Please login.",
    'demo_mode_success': "✅ Entered demo mode!",
    'login_failed': "❌ Invalid username or password",
    'register_failed': "❌ Failed to create account",
    'passwords_mismatch': "❌ Passwords do not match",
    'password_too_short': "❌ Password must be at least 6 characters long",
    'fill_all_fields': "Please fill in all required fields",
    'user_exists': "User already exists",
    'db_connection_failed': "Database connection failed"
}

# ============================================================================
# FILE UPLOAD MESSAGES
# ============================================================================
UPLOAD_MESSAGES = {
    'csv_loaded': "✅ Loaded {rows:,} records ({size:.2f} MB) | Processing: **{processing}** rows",
    'csv_limited': "⚠️ CSV has {total:,} rows. **Free tier will analyze first {limit} rows only.** Remaining {remaining:,} rows will be skipped.",
    'csv_stored': "✅ CSV file stored in MongoDB (ID: {id}...)",
    'csv_store_failed': "❌ Failed to store CSV file in MongoDB",
    'csv_validation_failed': "❌ CSV Validation Failed: {error}",
    'file_processing_error': "❌ Error processing file: {error}",
    'header_validation_success': "✅ {message}",
    'header_validation_failed': "❌ {message}",
    'no_data_upload_first': "👆 Please upload CSV data and run AI analysis from the Analytics page first",
    'no_data_available': "No customer data available"
}

# ============================================================================
# AI ANALYSIS MESSAGES
# ============================================================================
ANALYSIS_MESSAGES = {
    'analysis_started': "🚀 AI analysis started in background!",
    'analysis_running': "⏳ AI Analysis Running...",
    'analysis_complete': "✅ AI Analysis Complete",
    'analysis_failed': "❌ Error starting AI analysis: {error}",
    'analysis_in_progress_info': """⏳ **AI Analysis in Progress**

Your data is currently being analyzed. Please wait...

The analysis continues in the background. You can stay on this page and it will automatically 
update when complete, or return to the Analytics page.""",
    'analysis_not_available': "❌ AI processor not available. Please check your configuration.",
    'background_analysis_banner': "⏳ **AI Analysis in Progress** - Your data is being analyzed in the background."
}

# ============================================================================
# CHAT MESSAGES
# ============================================================================
CHAT_MESSAGES = {
    'welcome': "👋 **Welcome to ChurnGuard AI Assistant!** Please upload and analyze your CSV file first from the Analytics page to start chatting about your data.",
    'ai_not_available': "AI assistant not available",
    'thinking': "Thinking...",
    'data_not_available': "Upload CSV file first to enable chat...",
    'using_ai_data': "✅ Using AI-analyzed data",
    'using_sample_data': "📊 Using sample data",
    'no_data_warning': "⚠️ No data available - please upload CSV file first"
}

QUICK_ACTIONS = {
    'summary': "📊 Show Summary",
    'top_risks': "🎯 Top Risks",
    'recommendations': "💡 Recommendations"
}

QUICK_ACTION_QUERIES = {
    'summary': "Give me a summary of the customer data",
    'top_risks': "What are the top risk factors for churn?",
    'recommendations': "What recommendations do you have for customer retention?"
}

# ============================================================================
# OUTREACH CAMPAIGN MESSAGES
# ============================================================================
CAMPAIGN_MESSAGES = {
    'email_created': "✅ Email campaign '{name}' created successfully!",
    'email_scheduled': "✅ Email campaign '{name}' scheduled successfully!",
    'email_completed': "✅ Email campaign '{name}' completed!",
    'email_failed': "❌ Error creating email campaign: {error}",
    'sms_created': "✅ SMS campaign '{name}' created successfully!",
    'voice_created': "✅ Voice campaign '{name}' created successfully!",
    'campaign_validation_error': "Please fill in campaign name and message template",
    'sms_too_long': "⚠️ Message too long: {count}/160 characters",
    'sms_length_ok': "✅ Message length: {count}/160 characters",
    'no_recipients': "⚠️ No customers found for the selected segment. Please run churn analysis first.",
    'missing_emails': "⚠️ Warning: {count} customer(s) don't have email addresses and will be skipped",
    'no_email_column': "⚠️ No email addresses found in the customer data. Please ensure your CSV file includes an 'email' column."
}

EMAIL_SCHEDULE_INFO = """📧 Campaign Scheduled:
- Target segment: {segment}
- Scheduled for: {datetime}
- Priority: {priority}
- Total recipients: {total}
- Valid emails: {valid}"""

EMAIL_RESULT_INFO = """📧 Campaign Results:
- Emails sent: {sent}
- Failed: {failed}
- Skipped (no email): {skipped}
- Target segment: {segment}
- Sent at: {datetime}
- Priority: {priority}"""

SMS_CAMPAIGN_INFO = """📱 Campaign Details:
- Target: {segment}
- Scheduled: {date}
- Priority: {priority}"""

VOICE_CAMPAIGN_INFO = """📞 Campaign Details:
- Target: {segment}
- Scheduled: {date}
- Window: {window}
- Agent: {agent}"""

# ============================================================================
# EMAIL CONFIGURATION MESSAGES
# ============================================================================
EMAIL_CONFIG_MESSAGES = {
    'config_loaded': "✅ Email configuration loaded from environment variables",
    'config_missing': "⚠️ Email configuration required in .env file to send real emails",
    'config_hint': "💡 Please set SENDER_EMAIL and SENDER_PASSWORD in your .env file"
}

# ============================================================================
# EMAIL TEMPLATES
# ============================================================================
EMAIL_TEMPLATES = {
    'retention': """Hi {customer_name},

We noticed you might be considering leaving us, and we'd love to understand how we can better serve you.

Your feedback is valuable to us! We're committed to providing you with the best possible experience.

Please take a moment to let us know:
- What we can do better
- Any concerns you might have
- How we can improve your experience

We're here to help and want to make things right.

Best regards,
The Customer Success Team""",
    
    'win_back': """Hi {customer_name},

We miss you! It's been a while since we've seen you, and we have some exciting updates and special offers just for you.

Here's what's new:
- New features you'll love
- Special discount just for you
- Improved customer support

We'd love to have you back!

Best regards,
The Team""",
    
    'nurturing': """Hi {customer_name},

Thank you for being a valued customer! Here are some tips to get the most out of our service:

- Pro tip: Use feature X to save time
- New tutorial: How to maximize your results
- Community: Join our user group

We're here to help you succeed!

Best regards,
The Customer Success Team""",
    
    'custom': """Hi {customer_name},

Thank you for being a valued customer!

We hope you're enjoying our services.

Best regards,
The ChurnGuard Team"""
}

# ============================================================================
# SMS TEMPLATES
# ============================================================================
SMS_TEMPLATES = {
    'default': "Hi {customer_name}! We miss you. Special offer just for you: 20% off. Reply STOP to opt out."
}

# ============================================================================
# VOICE CALL SCRIPTS
# ============================================================================
VOICE_CALL_SCRIPTS = {
    'default': """Hello {customer_name}, this is {agent_name} from {company_name}. 

I'm calling because we noticed you might be considering leaving us, and we'd love to understand how we can better serve you.

Your feedback is valuable to us! We're committed to providing you with the best possible experience.

Do you have a few minutes to discuss:
- What we can do better
- Any concerns you might have
- How we can improve your experience

We're here to help and want to make things right."""
}

# ============================================================================
# DATA MANAGEMENT MESSAGES
# ============================================================================
DATA_MESSAGES = {
    'reset_success': "✅ All data has been reset successfully!",
    'reset_failed': "❌ Failed to reset data. Please try again or contact support.",
    'no_data': "✨ No data stored yet - your account is fresh!",
    'total_records': "Total stored records: **{count}**",
    'reset_warning': """**⚠️ Warning: This action cannot be undone!**

Resetting will permanently delete:
- All uploaded CSV files
- All AI analysis results
- All chat conversation history
- All session data

Your account information will remain intact."""
}

# ============================================================================
# SETTINGS MESSAGES
# ============================================================================
SETTINGS_MESSAGES = {
    'optimization_applied': """**Recent Optimizations Applied:**
- ✅ CSV Analysis: Sample-based processing (100 rows instead of all)
- ✅ Chat Queries: Smart context routing (summary vs full data)
- ✅ Conversation History: Limited to 4 recent messages
- ✅ Token Reduction: ~90% less tokens for typical queries""",
    
    'token_tips': """**Tips to Save Tokens:**
- Ask general questions to use summary mode
- Be specific when you need detailed customer lists
- Clear chat history periodically
- Reset all data when starting fresh analysis"""
}

# ============================================================================
# FREE TIER LIMITS
# ============================================================================
FREE_TIER_INFO = """**🆓 Free Tier Limits:**
- Maximum file size: **{max_size} MB**
- Maximum rows: **{max_rows}** (only first {max_rows} rows will be analyzed)
- Maximum columns: **{max_columns}**

💡 If your CSV has more than {max_rows} rows, only the **first {max_rows} records** will be processed."""

TIER_LIMITS_DISPLAY = {
    'free': '🆓 Free',
    'pro': '⭐ Pro',
    'enterprise': '🏢 Enterprise'
}

# ============================================================================
# ABOUT INFORMATION
# ============================================================================
ABOUT_INFO = f"""### {APP_ICON} {APP_NAME} - {APP_TAGLINE}

**Version:** {APP_VERSION}

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

{APP_COPYRIGHT}"""

# ============================================================================
# RISK LEVEL LABELS
# ============================================================================
RISK_LEVELS = {
    'high': 'High Risk',
    'medium': 'Medium Risk',
    'low': 'Low Risk'
}

RISK_COLORS = {
    'high': '#ff4444',
    'medium': '#ffaa00',
    'low': '#44ff44'
}

# ============================================================================
# SEGMENT OPTIONS
# ============================================================================
SEGMENT_OPTIONS = [
    "High Risk",
    "Medium Risk", 
    "Low Risk",
    "All Customers"
]

# ============================================================================
# PRIORITY OPTIONS
# ============================================================================
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

# ============================================================================
# CAMPAIGN TYPES
# ============================================================================
CAMPAIGN_TYPES = {
    'email': 'Email',
    'sms': 'SMS',
    'voice': 'Voice'
}

# ============================================================================
# CAMPAIGN STATUS
# ============================================================================
CAMPAIGN_STATUS = {
    'scheduled': 'Scheduled',
    'active': 'Active',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
}

# ============================================================================
# TEMPLATE TYPES
# ============================================================================
TEMPLATE_TYPES = ["Retention", "Win-back", "Nurturing", "Custom"]

# ============================================================================
# CALL WINDOWS
# ============================================================================
CALL_WINDOWS = ["9 AM - 5 PM", "10 AM - 6 PM", "11 AM - 7 PM"]

# ============================================================================
# CSV SUMMARY TEMPLATE
# ============================================================================
CSV_SUMMARY_TEMPLATE = """📊 **CSV Analysis Complete!**

**Key Statistics:**
• **Total Customers:** {total_customers}
• **High Risk:** {high_risk_customers} customers ({high_risk_percent:.1f}%)
• **Medium Risk:** {medium_risk_customers} customers ({medium_risk_percent:.1f}%)
• **Low Risk:** {low_risk_customers} customers ({low_risk_percent:.1f}%)
• **Revenue at Risk:** ${revenue_at_risk:,.2f}

**Top Insights:**
{top_insights}

**Immediate Actions Needed:**
{recommended_actions}

Ask me anything about your customer data! 🚀"""

CSV_SUMMARY_FALLBACK = "📊 **CSV Analysis Complete!** Your data has been analyzed. Ask me anything about your customers! 🚀"

# ============================================================================
# LOG MESSAGES
# ============================================================================
LOG_MESSAGES = {
    'user_created': "User created successfully: {username}",
    'user_authenticated': "User authenticated successfully: {username}",
    'analysis_started': "Starting background analysis for user: {user_id}",
    'analysis_completed': "Background analysis completed successfully for user: {user_id}",
    'csv_stored': "CSV file stored in MongoDB with ID: {file_id}",
    'chat_stored': "Chat interaction stored in MongoDB for user: {user_id}",
    'data_reset': "Data reset completed successfully for user: {user_id}"
}

# ============================================================================
# ERROR MESSAGES
# ============================================================================
ERROR_MESSAGES = {
    'mongodb_not_connected': "MongoDB not connected - cannot load user data",
    'session_state_clear_error': "Error clearing session state: {error}",
    'analysis_error': "Error in background analysis for user {user_id}: {error}",
    'csv_load_error': "Could not load CSV content: {error}",
    'email_send_error': "Failed to send email to {email}: {error}",
    'generic_error': "An unexpected error occurred. Please try again."
}

