"""
Configuration management for ChurnGuard
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Application Settings
    APP_NAME = "ChurnGuard"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # MongoDB Atlas Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "churnguard_db")
    MONGODB_COLLECTION_PREFIX = os.getenv("MONGODB_COLLECTION_PREFIX", "churnguard")
    
    # MongoDB Connection Settings
    MONGODB_MAX_POOL_SIZE = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    MONGODB_MIN_POOL_SIZE = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_MAX_IDLE_TIME_MS = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000"))
    MONGODB_CONNECT_TIMEOUT_MS = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "10000"))
    MONGODB_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    RESOURCES_DIR = BASE_DIR / "resources"
    SAMPLE_DATA_DIR = RESOURCES_DIR / "sample_data"
    LOGS_DIR = BASE_DIR / "logs"

    # Model Configuration
    CHURN_MODEL_PATH = RESOURCES_DIR / "models" / "churn_model.pkl"
    CHURN_SCALER_PATH = RESOURCES_DIR / "models" / "scaler.pkl"

    # LangChain Configuration
    LANGCHAIN_TEMPERATURE = 0.7
    LANGCHAIN_MAX_TOKENS = 1000

    # Email Configuration
    EMAIL_CONFIG = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': os.getenv('EMAIL_USERNAME', ''),
        'password': os.getenv('EMAIL_PASSWORD', ''),
        'from_email': os.getenv('FROM_EMAIL', ''),
        'use_tls': True
    }
    
    # SMS Configuration
    SMS_CONFIG = {
        'api_key': os.getenv('TWILIO_API_KEY', ''),
        'api_secret': os.getenv('TWILIO_API_SECRET', ''),
        'from_number': os.getenv('TWILIO_FROM_NUMBER', ''),
        'provider': 'twilio'
    }
    
    # Call Configuration
    CALL_CONFIG = {
        'api_key': os.getenv('TWILIO_API_KEY', ''),
        'api_secret': os.getenv('TWILIO_API_SECRET', ''),
        'from_number': os.getenv('TWILIO_FROM_NUMBER', ''),
        'provider': 'twilio'
    }
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    # Rate Limiting
    RATE_LIMITS = {
        'email': {'requests_per_minute': 100, 'requests_per_hour': 1000},
        'sms': {'requests_per_minute': 10, 'requests_per_hour': 100},
        'call': {'requests_per_minute': 5, 'requests_per_hour': 50}
    }
    
    # Campaign Configuration
    CAMPAIGN_BATCH_SIZE = 10
    CAMPAIGN_MAX_RETRIES = 3
    CAMPAIGN_RETRY_DELAY = 60  # seconds
    
    # Churn Prediction Configuration
    CHURN_THRESHOLD_HIGH = 0.7
    CHURN_THRESHOLD_MEDIUM = 0.4
    CHURN_ANALYSIS_DAYS = 30
    
    # CSV Upload Limits (Free Tier - optimized for token efficiency)
    CSV_MAX_FILE_SIZE_MB = int(os.getenv("CSV_MAX_FILE_SIZE_MB", "10"))  # 10 MB for free tier
    CSV_MAX_ROWS = int(os.getenv("CSV_MAX_ROWS", "100"))  # 100 rows for free tier
    CSV_MAX_COLUMNS = int(os.getenv("CSV_MAX_COLUMNS", "30"))  # 30 columns for free tier
    CSV_MIN_ROWS = int(os.getenv("CSV_MIN_ROWS", "1"))  # Minimum 1 row
    
    # Monitoring Configuration
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Cloud Deployment Configuration
    CLOUD_PROVIDER = os.getenv('CLOUD_PROVIDER', 'local')  # aws, gcp, azure, local
    REGION = os.getenv('REGION', 'us-east-1')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600))

    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI not set in environment variables")

        # Create necessary directories
        cls.LOGS_DIR.mkdir(exist_ok=True)

config = Config()
config.validate()