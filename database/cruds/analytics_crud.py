"""
Analytics CRUD Operations
All database operations related to analytics data
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AnalyticsCRUD:
    """CRUD operations for analytics entities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_analytics(self, user_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Create new analytics record"""
        try:
            analytics_data['analysis_date'] = analytics_data.get('analysis_date', datetime.now())
            analytics_data['status'] = analytics_data.get('status', 'completed')
            
            return self.db_manager.store_user_data('analytics', user_id, analytics_data)
            
        except Exception as e:
            logger.error(f"Error creating analytics: {str(e)}")
            return False
    
    def get_analytics(self, user_id: str, query: Dict = None) -> List[Dict[str, Any]]:
        """Get analytics records for a user"""
        try:
            return self.db_manager.get_user_data('analytics', user_id, query)
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return []
    
    def get_latest_analytics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent analytics record"""
        try:
            analytics_data = self.get_analytics(user_id)
            if analytics_data:
                return max(analytics_data, key=lambda x: x.get('analysis_date', datetime.min))
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest analytics: {str(e)}")
            return None
    
    def update_analytics(self, user_id: str, analytics_id: str, updates: Dict[str, Any]) -> bool:
        """Update analytics record"""
        try:
            query = {"_id": analytics_id}
            update = {"$set": updates}
            
            return self.db_manager.update_user_data('analytics', user_id, query, update)
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
            return False
    
    def delete_analytics(self, user_id: str, analytics_id: str = None) -> bool:
        """Delete analytics record(s)"""
        try:
            query = {"_id": analytics_id} if analytics_id else {}
            return self.db_manager.delete_user_data('analytics', user_id, query)
            
        except Exception as e:
            logger.error(f"Error deleting analytics: {str(e)}")
            return False
    
    def delete_all_analytics(self, user_id: str) -> bool:
        """Delete all analytics records for a user"""
        try:
            return self.delete_analytics(user_id)
            
        except Exception as e:
            logger.error(f"Error deleting all analytics: {str(e)}")
            return False

