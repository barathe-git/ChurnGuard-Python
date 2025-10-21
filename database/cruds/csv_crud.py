"""
CSV CRUD Operations
All database operations related to CSV file storage
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class CSVRUD:
    """CRUD operations for CSV file entities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_csv(self, user_id: str, csv_data: Dict[str, Any]) -> Optional[str]:
        """Store CSV file and return the file ID"""
        try:
            csv_data['upload_date'] = csv_data.get('upload_date', datetime.now())
            
            success = self.db_manager.store_user_data('csv_files', user_id, csv_data)
            
            if success:
                # Get the stored document to return its ID
                stored_files = self.get_csv_files(user_id)
                if stored_files:
                    latest_file = max(stored_files, key=lambda x: x.get('upload_date', datetime.min))
                    file_id = str(latest_file['_id'])
                    logger.info(f"CSV file stored with ID: {file_id}")
                    return file_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating CSV: {str(e)}")
            return None
    
    def get_csv_files(self, user_id: str, query: Dict = None) -> List[Dict[str, Any]]:
        """Get CSV files for a user"""
        try:
            return self.db_manager.get_user_data('csv_files', user_id, query)
            
        except Exception as e:
            logger.error(f"Error getting CSV files: {str(e)}")
            return []
    
    def get_csv_by_id(self, user_id: str, file_id: str) -> Optional[Dict[str, Any]]:
        """Get specific CSV file by ID"""
        try:
            csv_files = self.get_csv_files(user_id)
            
            for csv_file in csv_files:
                if str(csv_file['_id']) == file_id:
                    return csv_file
            
            logger.warning(f"CSV file with ID {file_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting CSV by ID: {str(e)}")
            return None
    
    def get_latest_csv(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent CSV file"""
        try:
            csv_files = self.get_csv_files(user_id)
            if csv_files:
                return max(csv_files, key=lambda x: x.get('upload_date', datetime.min))
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest CSV: {str(e)}")
            return None
    
    def delete_csv(self, user_id: str, file_id: str = None) -> bool:
        """Delete CSV file(s)"""
        try:
            query = {"_id": file_id} if file_id else {}
            return self.db_manager.delete_user_data('csv_files', user_id, query)
            
        except Exception as e:
            logger.error(f"Error deleting CSV: {str(e)}")
            return False
    
    def delete_all_csv(self, user_id: str) -> bool:
        """Delete all CSV files for a user"""
        try:
            return self.delete_csv(user_id)
            
        except Exception as e:
            logger.error(f"Error deleting all CSV files: {str(e)}")
            return False

