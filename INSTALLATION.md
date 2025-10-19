# ChurnGuard Installation Guide

## Quick Start

### Option 1: Automated Installation (Recommended)
```bash
# Run the installation script
./install.sh
```

### Option 2: Manual Installation

#### Step 1: Prerequisites
- Python 3.11+
- MongoDB Atlas account (or local MongoDB)
- Redis server
- Git

#### Step 2: Clone and Setup
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd ChurnGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your configuration
nano .env  # or use your preferred editor
```

#### Step 4: Database Setup
```bash
# Initialize database
python scripts/db_init.py

# Optimize database for performance
python scripts/db_optimization.py
```

## Environment Variables

### Required Variables
```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=churnguard_db

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Optional Variables
```bash
# Email Configuration
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourcompany.com

# SMS/Voice Configuration
TWILIO_API_KEY=your-twilio-account-sid
TWILIO_API_SECRET=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Running the Application

### 1. Start Redis Server
```bash
# On macOS with Homebrew
brew services start redis

# On Ubuntu/Debian
sudo systemctl start redis-server

# On Windows
redis-server
```

### 2. Start the Application

#### Option A: Streamlit UI (Recommended for development)
```bash
streamlit run app.py
```

#### Option B: FastAPI Server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Option C: Docker Compose (Production-like)
```bash
docker-compose up -d
```

### 3. Start Background Workers (Optional)
```bash
# Start Celery worker
celery -A app.celery worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.celery beat --loglevel=info
```

## Access Points

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000/api

## Cloud Deployment

### AWS Deployment
```bash
python scripts/deploy_cloud.py --provider aws --environment production
```

### Google Cloud Deployment
```bash
python scripts/deploy_cloud.py --provider gcp --environment production
```

### Azure Deployment
```bash
python scripts/deploy_cloud.py --provider azure --environment production
```

## Verification

### 1. Check Application Health
```bash
# For Streamlit
curl http://localhost:8501

# For FastAPI
curl http://localhost:8000/health
```

### 2. Test Database Connection
```bash
python -c "
from database.connection.db_manager import DatabaseManager
db = DatabaseManager()
print('Database connection successful!')
"
```

### 3. Test AI Components
```bash
python -c "
from ai_agents.churn_predictor.predictor import ChurnPredictor
predictor = ChurnPredictor()
print('Churn predictor loaded successfully!')
"
```

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error
```
Error: Could not connect to MongoDB
```
**Solution**: Check your `MONGODB_URI` in `.env` file and ensure MongoDB is accessible.

#### 2. Redis Connection Error
```
Error: Could not connect to Redis
```
**Solution**: Start Redis server or check `REDIS_URL` configuration.

#### 3. Missing Dependencies
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution**: Run `pip install -r requirements.txt` in your virtual environment.

#### 4. Permission Errors
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Check file permissions and ensure you're running in the correct directory.

### Logs
Check the logs directory for detailed error information:
```bash
tail -f logs/churnguard.log
tail -f logs/errors.log
```

## Development Setup

### 1. Install Development Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest tests/
```

### 3. Code Formatting
```bash
black .
flake8 .
mypy .
```

### 4. Pre-commit Hooks (Optional)
```bash
pip install pre-commit
pre-commit install
```

## Production Considerations

### 1. Security
- Change default `SECRET_KEY`
- Use environment-specific configurations
- Enable HTTPS
- Set up proper authentication

### 2. Performance
- Configure Redis for caching
- Set up database indexes
- Use connection pooling
- Enable compression

### 3. Monitoring
- Set up Sentry for error tracking
- Configure logging
- Set up health checks
- Monitor resource usage

### 4. Scaling
- Use load balancers
- Set up database replicas
- Configure auto-scaling
- Use CDN for static assets

## Support

If you encounter issues during installation:

1. Check the logs in the `logs/` directory
2. Verify all environment variables are set correctly
3. Ensure all services (MongoDB, Redis) are running
4. Check the troubleshooting section above
5. Create an issue in the repository

## Next Steps

After successful installation:

1. **Upload Data**: Use the CSV upload feature in the Streamlit UI
2. **Configure AI**: Set up your Gemini API key
3. **Create Campaigns**: Set up your first outreach campaign
4. **Monitor Performance**: Check the analytics dashboard
5. **Scale Up**: Deploy to cloud for production use

---

**Note**: This installation guide covers the most common scenarios. For specific cloud provider setups, refer to the individual deployment scripts in the `scripts/` directory.
