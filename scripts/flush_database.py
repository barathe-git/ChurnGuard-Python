#!/usr/bin/env python3
"""
Database flush script for ChurnGuard
Clears all collections and data from MongoDB
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from database.connection.db_manager import DatabaseManager
from config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def flush_database():
    """Flush all collections from MongoDB database"""
    try:
        db_manager = DatabaseManager()
        
        if not db_manager.is_connected():
            logger.error("Cannot connect to MongoDB")
            return False
        
        logger.info("🗑️ Starting database flush...")
        
        # Get all collections in the database
        collections = db_manager.database.list_collection_names()
        logger.info(f"Found {len(collections)} collections to flush")
        
        flushed_count = 0
        for collection_name in collections:
            try:
                collection = db_manager.database[collection_name]
                count = collection.count_documents({})
                
                if count > 0:
                    # Drop the entire collection
                    collection.drop()
                    logger.info(f"✅ Flushed collection '{collection_name}' ({count} documents)")
                    flushed_count += 1
                else:
                    logger.info(f"⏭️ Collection '{collection_name}' was already empty")
                    
            except Exception as e:
                logger.error(f"❌ Error flushing collection '{collection_name}': {str(e)}")
        
        logger.info(f"🎯 Database flush completed! Flushed {flushed_count} collections")
        return True
        
    except Exception as e:
        logger.error(f"Database flush failed: {str(e)}")
        return False

def flush_user_data(user_id: str = None):
    """Flush data for a specific user or all users"""
    try:
        db_manager = DatabaseManager()
        
        if not db_manager.is_connected():
            logger.error("Cannot connect to MongoDB")
            return False
        
        if user_id:
            logger.info(f"🗑️ Flushing data for user: {user_id}")
        else:
            logger.info("🗑️ Flushing data for all users")
        
        # Common collection names used by the application
        collection_names = [
            'csv_files',
            'analytics', 
            'chat_interactions',
            'campaigns',
            'campaign_events'
        ]
        
        flushed_count = 0
        for collection_name in collection_names:
            try:
                if user_id:
                    # Flush specific user's data
                    collection = db_manager.get_user_collection(collection_name, user_id)
                    count = collection.count_documents({})
                    if count > 0:
                        collection.drop()
                        logger.info(f"✅ Flushed {collection_name} for user {user_id} ({count} documents)")
                        flushed_count += 1
                else:
                    # Flush all users' data for this collection
                    # Get all collections that match the pattern
                    all_collections = db_manager.database.list_collection_names()
                    user_collections = [c for c in all_collections if c.startswith(f"{collection_name}_") or c == collection_name]
                    
                    for user_collection in user_collections:
                        collection = db_manager.database[user_collection]
                        count = collection.count_documents({})
                        if count > 0:
                            collection.drop()
                            logger.info(f"✅ Flushed collection '{user_collection}' ({count} documents)")
                            flushed_count += 1
                            
            except Exception as e:
                logger.error(f"❌ Error flushing collection '{collection_name}': {str(e)}")
        
        logger.info(f"🎯 User data flush completed! Flushed {flushed_count} collections")
        return True
        
    except Exception as e:
        logger.error(f"User data flush failed: {str(e)}")
        return False

def main():
    """Main function to handle command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Flush ChurnGuard database')
    parser.add_argument('--user', type=str, help='Flush data for specific user only')
    parser.add_argument('--all', action='store_true', help='Flush entire database (all collections)')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.confirm:
        if args.all:
            print("⚠️  WARNING: This will delete ALL data from the database!")
            print("   This includes all collections, users, and application data.")
        elif args.user:
            print(f"⚠️  WARNING: This will delete ALL data for user '{args.user}'!")
        else:
            print("⚠️  WARNING: This will delete all user data from the database!")
        
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Database flush cancelled")
            return
    
    print("🚀 Starting ChurnGuard Database Flush...")
    
    if args.all:
        # Flush entire database
        if flush_database():
            print("✅ Database flush completed successfully!")
        else:
            print("❌ Database flush failed!")
    else:
        # Flush user data only
        if flush_user_data(args.user):
            print("✅ User data flush completed successfully!")
        else:
            print("❌ User data flush failed!")

if __name__ == "__main__":
    main()
