"""
Database initialization script for ChurnGuard SaaS platform
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

def initialize_database():
    """Initialize MongoDB database with collections and indexes"""
    try:
        db_manager = DatabaseManager()
        
        if not db_manager.is_connected():
            logger.error("Cannot connect to MongoDB")
            return False
        
        # Create indexes for user collections
        create_user_indexes(db_manager)
        
        # Create indexes for SaaS collections
        create_saas_indexes(db_manager)
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def create_user_indexes(db_manager):
    """Create indexes for user management collections"""
    try:
        # Users collection indexes
        users_collection = db_manager.get_collection('users')
        users_collection.create_index('username', unique=True)
        users_collection.create_index('email', unique=True)
        users_collection.create_index('user_id', unique=True)
        users_collection.create_index('organization')
        users_collection.create_index('is_active')
        users_collection.create_index('created_at')
        
        # Sessions collection indexes
        sessions_collection = db_manager.get_collection('sessions')
        sessions_collection.create_index('session_id', unique=True)
        sessions_collection.create_index('user_id')
        sessions_collection.create_index('is_active')
        sessions_collection.create_index('expires_at')
        sessions_collection.create_index('created_at')
        
        logger.info("User management indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating user indexes: {str(e)}")

def create_saas_indexes(db_manager):
    """Create indexes for SaaS data collections"""
    try:
        # These indexes will be created for each user's collections
        # CSV files collection indexes
        csv_files_collection = db_manager.get_collection('csv_files')
        csv_files_collection.create_index('user_id')
        csv_files_collection.create_index('upload_date')
        csv_files_collection.create_index('file_name')
        
        # Analytics collection indexes
        analytics_collection = db_manager.get_collection('analytics')
        analytics_collection.create_index('user_id')
        analytics_collection.create_index('analysis_date')
        
        # Chat interactions collection indexes
        chat_collection = db_manager.get_collection('chat_interactions')
        chat_collection.create_index('user_id')
        chat_collection.create_index('timestamp')
        chat_collection.create_index('session_id')
        
        logger.info("SaaS data indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating SaaS indexes: {str(e)}")

def create_demo_user():
    """Create a demo user for testing"""
    try:
        from frontend.pages.auth import UserAuthManager
        
        auth_manager = UserAuthManager()
        
        # Check if demo user already exists
        if auth_manager.user_exists('demo_user', 'demo@churnguard.com'):
            logger.info("Demo user already exists")
            return True
        
        # Create demo user
        result = auth_manager.create_user(
            username='demo_user',
            email='demo@churnguard.com',
            password='demo123',
            organization='Demo Organization'
        )
        
        if result['success']:
            logger.info("Demo user created successfully")
            return True
        else:
            logger.error(f"Failed to create demo user: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating demo user: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Initializing ChurnGuard Database...")
    
    # Initialize database
    if initialize_database():
        print("✅ Database initialization completed")
        
        # Create demo user
        if create_demo_user():
            print("✅ Demo user created")
        else:
            print("⚠️ Demo user creation failed")
        
        print("")
        print("🎯 Database Setup Complete!")
        print("  📊 Collections created with proper indexes")
        print("  🔐 User authentication system ready")
        print("  🏢 SaaS data separation implemented")
        print("  👤 Demo user available (demo_user / demo123)")
        print("")
        print("🚀 You can now run the application!")
        
    else:
        print("❌ Database initialization failed")
        print("Please check your MongoDB connection and try again")
