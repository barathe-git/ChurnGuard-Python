"""
MongoDB connection manager with connection pooling
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config.config import config
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manage MongoDB connections and collections"""
    
    # Class-level flag to track if we've logged initialization (avoid spam in Streamlit reruns)
    _first_init_logged = False

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize MongoDB client with connection pooling"""
        try:
            # MongoDB connection options
            connection_options = {
                'maxPoolSize': config.MONGODB_MAX_POOL_SIZE,
                'minPoolSize': config.MONGODB_MIN_POOL_SIZE,
                'maxIdleTimeMS': config.MONGODB_MAX_IDLE_TIME_MS,
                'connectTimeoutMS': config.MONGODB_CONNECT_TIMEOUT_MS,
                'serverSelectionTimeoutMS': config.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                'retryWrites': True,
                'w': 'majority'
            }

            self.client = MongoClient(config.MONGODB_URI, **connection_options)
            self.database = self.client[config.MONGODB_DATABASE]
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Only log on first initialization to avoid spam in Streamlit reruns
            if not DatabaseManager._first_init_logged:
                logger.info("MongoDB connection initialized successfully")
                DatabaseManager._first_init_logged = True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
            raise

    def get_collection(self, collection_name: str, user_id: str = None):
        """Get a MongoDB collection with optional user-specific prefixing"""
        if self.database is None:
            raise RuntimeError("Database not initialized")
        
        # For SaaS data separation, prefix collection names with user_id
        if user_id and user_id != 'demo_user':
            collection_name = f"{user_id}_{collection_name}"
        
        return self.database[collection_name]
    
    def get_user_collection(self, collection_name: str, user_id: str):
        """Get a user-specific collection for SaaS data separation"""
        return self.get_collection(collection_name, user_id)
    
    def store_user_data(self, collection_name: str, user_id: str, data: dict) -> bool:
        """Store data for a specific user with SaaS separation"""
        try:
            collection = self.get_user_collection(collection_name, user_id)
            
            # Add user_id and timestamp to data
            data['user_id'] = user_id
            data['created_at'] = data.get('created_at', self._get_current_timestamp())
            
            result = collection.insert_one(data)
            logger.info(f"Data stored for user {user_id} in collection {collection_name}")
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Error storing user data: {str(e)}")
            return False
    
    def get_user_data(self, collection_name: str, user_id: str, query: dict = None) -> list:
        """Get data for a specific user with SaaS separation"""
        try:
            collection = self.get_user_collection(collection_name, user_id)
            
            # Add user_id to query for additional security
            if query is None:
                query = {}
            query['user_id'] = user_id
            
            cursor = collection.find(query)
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return []
    
    def update_user_data(self, collection_name: str, user_id: str, query: dict, update: dict) -> bool:
        """Update data for a specific user with SaaS separation"""
        try:
            collection = self.get_user_collection(collection_name, user_id)
            
            # Add user_id to query for additional security
            query['user_id'] = user_id
            
            # Add update timestamp
            update['$set'] = update.get('$set', {})
            update['$set']['updated_at'] = self._get_current_timestamp()
            
            result = collection.update_one(query, update)
            logger.info(f"Data updated for user {user_id} in collection {collection_name}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating user data: {str(e)}")
            return False
    
    def delete_user_data(self, collection_name: str, user_id: str, query: dict) -> bool:
        """Delete data for a specific user with SaaS separation"""
        try:
            collection = self.get_user_collection(collection_name, user_id)
            
            # Add user_id to query for additional security
            query['user_id'] = user_id
            
            result = collection.delete_many(query)
            logger.info(f"Data deleted for user {user_id} in collection {collection_name}")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return False
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now()

    def get_organizations_collection(self):
        """Get organizations collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_organizations")

    def get_customers_collection(self):
        """Get customers collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_customers")

    def get_transactions_collection(self):
        """Get transactions collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_transactions")

    def get_feedback_collection(self):
        """Get feedback collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_feedback")

    def get_churn_scores_collection(self):
        """Get churn scores collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_churn_scores")

    def get_campaigns_collection(self):
        """Get campaigns collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_campaigns")

    def get_campaign_events_collection(self):
        """Get campaign events collection"""
        return self.get_collection(f"{config.MONGODB_COLLECTION_PREFIX}_campaign_events")

    def create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Organizations indexes
            org_collection = self.get_organizations_collection()
            org_collection.create_index("name", unique=True)
            
            # Customers indexes
            customers_collection = self.get_customers_collection()
            customers_collection.create_index("customer_external_id", unique=True)
            customers_collection.create_index("org_id")
            customers_collection.create_index("email")
            customers_collection.create_index("account_status")
            customers_collection.create_index([("org_id", 1), ("account_status", 1)])
            
            # Transactions indexes
            transactions_collection = self.get_transactions_collection()
            transactions_collection.create_index("customer_id")
            transactions_collection.create_index("transaction_date")
            transactions_collection.create_index([("customer_id", 1), ("transaction_date", -1)])
            
            # Feedback indexes
            feedback_collection = self.get_feedback_collection()
            feedback_collection.create_index("customer_id")
            feedback_collection.create_index("feedback_date")
            feedback_collection.create_index([("customer_id", 1), ("feedback_date", -1)])
            
            # Churn scores indexes
            churn_scores_collection = self.get_churn_scores_collection()
            churn_scores_collection.create_index("customer_id")
            churn_scores_collection.create_index("prediction_date")
            churn_scores_collection.create_index("churn_probability")
            churn_scores_collection.create_index([("customer_id", 1), ("prediction_date", -1)])
            
            # Campaigns indexes
            campaigns_collection = self.get_campaigns_collection()
            campaigns_collection.create_index("org_id")
            campaigns_collection.create_index("status")
            campaigns_collection.create_index("created_at")
            
            # Campaign events indexes
            campaign_events_collection = self.get_campaign_events_collection()
            campaign_events_collection.create_index("campaign_id")
            campaign_events_collection.create_index("customer_id")
            campaign_events_collection.create_index("event_date")
            campaign_events_collection.create_index([("campaign_id", 1), ("event_date", -1)])
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
            raise

    def is_connected(self) -> bool:
        """Check if MongoDB connection is active"""
        try:
            if self.client is None or self.database is None:
                return False
            
            # Test the connection
            self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection check failed: {str(e)}")
            return False

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")

# Singleton instance
db_manager = DatabaseManager()