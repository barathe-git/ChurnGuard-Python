"""
User CRUD Operations
All database operations related to user management
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class UserCRUD:
    """CRUD operations for user entities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        try:
            if not self.db_manager.is_connected():
                logger.error("MongoDB not connected - cannot create user")
                return False
            
            user_data['created_at'] = datetime.now()
            user_data['is_active'] = user_data.get('is_active', True)
            
            self.db_manager.get_collection('users').insert_one(user_data)
            logger.info(f"User created successfully: {user_data.get('username')}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID"""
        try:
            if not self.db_manager.is_connected():
                return None
            
            user = self.db_manager.get_collection('users').find_one({"user_id": user_id})
            if user:
                user.pop('password_hash', None)  # Remove sensitive data
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            if not self.db_manager.is_connected():
                return None
            
            user = self.db_manager.get_collection('users').find_one({
                "$or": [
                    {"username": username},
                    {"email": username}
                ],
                "is_active": True
            })
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            # Remove sensitive fields that shouldn't be updated directly
            updates.pop('password_hash', None)
            updates.pop('user_id', None)
            updates.pop('created_at', None)
            
            updates['updated_at'] = datetime.now()
            
            result = self.db_manager.get_collection('users').update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            
            logger.info(f"User updated: {user_id}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            result = self.db_manager.get_collection('users').update_one(
                {"user_id": user_id},
                {"$set": {"last_login": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            return False
    
    def user_exists(self, username: str, email: str) -> bool:
        """Check if user exists by username or email"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            existing_user = self.db_manager.get_collection('users').find_one({
                "$or": [
                    {"username": username},
                    {"email": email}
                ]
            })
            
            return existing_user is not None
            
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}")
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            result = self.db_manager.get_collection('users').update_one(
                {"user_id": user_id},
                {"$set": {"is_active": False, "deactivated_at": datetime.now()}}
            )
            
            logger.info(f"User deactivated: {user_id}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return False

