"""
Campaign CRUD Operations
All database operations related to outreach campaigns
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class CampaignCRUD:
    """CRUD operations for campaign entities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_campaign(self, user_id: str, campaign_data: Dict[str, Any]) -> bool:
        """Create new campaign"""
        try:
            campaign_data['created_at'] = campaign_data.get('created_at', datetime.now())
            campaign_data['status'] = campaign_data.get('status', 'scheduled')
            
            return self.db_manager.store_user_data('campaigns', user_id, campaign_data)
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return False
    
    def get_campaigns(self, user_id: str, query: Dict = None) -> List[Dict[str, Any]]:
        """Get campaigns for a user"""
        try:
            return self.db_manager.get_user_data('campaigns', user_id, query)
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {str(e)}")
            return []
    
    def get_campaign_by_id(self, user_id: str, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get specific campaign by ID"""
        try:
            campaigns = self.get_campaigns(user_id)
            
            for campaign in campaigns:
                if str(campaign['_id']) == campaign_id:
                    return campaign
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting campaign by ID: {str(e)}")
            return None
    
    def get_campaigns_by_type(self, user_id: str, campaign_type: str) -> List[Dict[str, Any]]:
        """Get campaigns by type (email, sms, voice)"""
        try:
            query = {"type": campaign_type}
            return self.get_campaigns(user_id, query)
            
        except Exception as e:
            logger.error(f"Error getting campaigns by type: {str(e)}")
            return []
    
    def get_campaigns_by_status(self, user_id: str, status: str) -> List[Dict[str, Any]]:
        """Get campaigns by status"""
        try:
            query = {"status": status}
            return self.get_campaigns(user_id, query)
            
        except Exception as e:
            logger.error(f"Error getting campaigns by status: {str(e)}")
            return []
    
    def update_campaign(self, user_id: str, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """Update campaign"""
        try:
            query = {"_id": campaign_id}
            update = {"$set": updates}
            
            return self.db_manager.update_user_data('campaigns', user_id, query, update)
            
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            return False
    
    def update_campaign_status(self, user_id: str, campaign_id: str, status: str) -> bool:
        """Update campaign status"""
        try:
            updates = {
                "status": status,
                "status_updated_at": datetime.now()
            }
            return self.update_campaign(user_id, campaign_id, updates)
            
        except Exception as e:
            logger.error(f"Error updating campaign status: {str(e)}")
            return False
    
    def delete_campaign(self, user_id: str, campaign_id: str) -> bool:
        """Delete campaign"""
        try:
            query = {"_id": campaign_id}
            return self.db_manager.delete_user_data('campaigns', user_id, query)
            
        except Exception as e:
            logger.error(f"Error deleting campaign: {str(e)}")
            return False
    
    def delete_all_campaigns(self, user_id: str) -> bool:
        """Delete all campaigns for a user"""
        try:
            return self.db_manager.delete_user_data('campaigns', user_id, {})
            
        except Exception as e:
            logger.error(f"Error deleting all campaigns: {str(e)}")
            return False

