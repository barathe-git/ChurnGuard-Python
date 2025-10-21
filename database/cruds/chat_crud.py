"""
Chat CRUD Operations
All database operations related to chat interactions
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ChatCRUD:
    """CRUD operations for chat interaction entities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_chat_interaction(self, user_id: str, chat_data: Dict[str, Any]) -> bool:
        """Store chat interaction"""
        try:
            chat_data['timestamp'] = chat_data.get('timestamp', datetime.now())
            
            return self.db_manager.store_user_data('chat_interactions', user_id, chat_data)
            
        except Exception as e:
            logger.error(f"Error creating chat interaction: {str(e)}")
            return False
    
    def get_chat_interactions(self, user_id: str, query: Dict = None, limit: int = None) -> List[Dict[str, Any]]:
        """Get chat interactions for a user"""
        try:
            interactions = self.db_manager.get_user_data('chat_interactions', user_id, query)
            
            # Sort by timestamp descending
            interactions.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            
            if limit:
                interactions = interactions[:limit]
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error getting chat interactions: {str(e)}")
            return []
    
    def get_recent_chat_interactions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat interactions"""
        try:
            return self.get_chat_interactions(user_id, limit=limit)
            
        except Exception as e:
            logger.error(f"Error getting recent chat interactions: {str(e)}")
            return []
    
    def get_chat_by_session(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """Get chat interactions for a specific session"""
        try:
            query = {"session_id": session_id}
            return self.get_chat_interactions(user_id, query)
            
        except Exception as e:
            logger.error(f"Error getting chat by session: {str(e)}")
            return []
    
    def delete_chat_interactions(self, user_id: str, chat_id: str = None) -> bool:
        """Delete chat interaction(s)"""
        try:
            query = {"_id": chat_id} if chat_id else {}
            return self.db_manager.delete_user_data('chat_interactions', user_id, query)
            
        except Exception as e:
            logger.error(f"Error deleting chat interactions: {str(e)}")
            return False
    
    def delete_all_chat_interactions(self, user_id: str) -> bool:
        """Delete all chat interactions for a user"""
        try:
            return self.delete_chat_interactions(user_id)
            
        except Exception as e:
            logger.error(f"Error deleting all chat interactions: {str(e)}")
            return False

