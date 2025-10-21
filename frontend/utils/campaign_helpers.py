"""
Campaign management helpers
Utility functions for managing outreach campaigns
"""
import logging
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def get_target_customers(llm_data_manager, segment: str) -> List[Dict]:
    """
    Get target customers based on segment
    
    Args:
        llm_data_manager: LLM data manager instance
        segment: Target segment (High Risk, Medium Risk, Low Risk, All Customers)
    
    Returns:
        List of customer dictionaries
    """
    try:
        if not llm_data_manager.is_data_loaded():
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
            
    except Exception as e:
        logger.error(f"Error getting target customers: {str(e)}")
        return []


def personalize_message(template: str, customer: Dict) -> str:
    """
    Personalize message template with customer data
    
    Args:
        template: Message template with placeholders
        customer: Customer data dictionary
    
    Returns:
        Personalized message
    """
    try:
        return template.format(
            customer_name=customer.get('customer_id', 'Valued Customer'),
            email=customer.get('email', ''),
            churn_probability=customer.get('churn_probability', 0)
        )
    except Exception as e:
        logger.error(f"Error personalizing message: {str(e)}")
        return template


def count_valid_emails(customers: List[Dict]) -> int:
    """Count customers with valid email addresses"""
    try:
        return sum(1 for c in customers if c.get('email') and not pd.isna(c.get('email')))
    except Exception as e:
        logger.error(f"Error counting valid emails: {str(e)}")
        return 0


def validate_campaign_data(name: str, message: str) -> Tuple[bool, str]:
    """
    Validate campaign data
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Campaign name is required"
    
    if not message or not message.strip():
        return False, "Campaign message is required"
    
    return True, ""


def format_campaign_schedule_info(segment: str, scheduled_datetime: datetime, 
                                  priority: str, total: int, valid: int) -> str:
    """Format campaign schedule information"""
    info = f"""📧 Campaign Scheduled:
- Target segment: {segment}
- Scheduled for: {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}
- Priority: {priority}
- Total recipients: {total}
- Valid emails: {valid}"""
    
    if valid < total:
        info += f"\n- Will skip: {total - valid} (no email)"
    
    return info


def format_campaign_result_info(sent: int, failed: int, skipped: int, 
                                segment: str, sent_at: datetime, priority: str) -> str:
    """Format campaign result information"""
    info = f"""📧 Campaign Results:
- Emails sent: {sent}
- Failed: {failed}"""
    
    if skipped > 0:
        info += f"\n- Skipped (no email): {skipped}"
    
    info += f"""
- Target segment: {segment}
- Sent at: {sent_at.strftime('%Y-%m-%d %H:%M')}
- Priority: {priority}"""
    
    return info


def store_campaign(campaign_type: str, campaign_data: Dict):
    """Store campaign in session state"""
    try:
        if 'campaigns' not in st.session_state:
            st.session_state.campaigns = []
        
        campaign_data['type'] = campaign_type
        campaign_data['created_at'] = datetime.now()
        
        st.session_state.campaigns.append(campaign_data)
        logger.info(f"Campaign stored: {campaign_data.get('name')}")
        
    except Exception as e:
        logger.error(f"Error storing campaign: {str(e)}")


def schedule_campaign(campaign_data: Dict):
    """Store scheduled campaign in session state"""
    try:
        if 'scheduled_campaigns' not in st.session_state:
            st.session_state.scheduled_campaigns = []
        
        st.session_state.scheduled_campaigns.append(campaign_data)
        logger.info(f"Campaign scheduled: {campaign_data.get('name')}")
        
    except Exception as e:
        logger.error(f"Error scheduling campaign: {str(e)}")

