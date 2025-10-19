# ChurnGuard 🛡️

## AI-Powered Customer Retention Platform

ChurnGuard is an enterprise-grade customer retention platform that leverages AI to predict customer churn, analyze sentiment, and automate engagement campaigns.

### 🌟 Features

- **Churn Prediction Engine**: ML-based prediction using behavioral and transactional data
- **Sentiment Analysis**: Analyze customer feedback to understand satisfaction levels
- **Natural Language Query**: Ask questions about your data in plain English (powered by Gemini AI)
- **Interactive Dashboard**: Beautiful Streamlit interface with Plotly visualizations
- **Campaign Management**: Track and manage retention campaigns
- **CSV Import**: Easy data ingestion from CSV files

### 🏗️ Architecture

```
ChurnGuard/
├── frontend/          # Streamlit UI components
├── backend/           # API, services, repositories
├── ai_agents/         # ML models and LangChain agents
├── database/          # Database connection and migrations
├── resources/         # Sample data and configurations
└── scripts/           # Utility scripts
```

### 🚀 Quick Start

**1. Clone and Setup**

```bash
cd ChurnGuard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure Environment**

```bash
cp config/.env.example .env
# Edit .env with your credentials:
# - GEMINI_API_KEY (get from Google AI Studio)
# - PostgreSQL database credentials
```

**3. Initialize Database**

```bash
python scripts/db_init.py
```

**4. (Optional) Train ML Model**

```bash
python scripts/train_model.py
```

**5. Run Application**

```bash
streamlit run app.py
```

Visit: `http://localhost:8501`

### 🔧 Configuration

Edit `.env` file with:
- `GEMINI_API_KEY`: Get from https://ai.google.dev/
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL connection details

### 📊 Usage

1. **Login**: Use demo credentials (demo@churnguard.ai / demo123)
2. **Upload Data**: Navigate to Dashboard → Upload CSV
3. **View Analytics**: Explore churn predictions and visualizations
4. **Chat Assistant**: Ask questions about your data using natural language
5. **Run Predictions**: Batch predict churn for all customers

### 🗃️ Database Schema

- **Organizations**: Company/tenant data
- **Customers**: Customer profiles and account information
- **Transactions**: Purchase history and transaction details
- **Feedback**: Customer feedback with sentiment analysis
- **ChurnScores**: ML prediction results with risk levels
- **Campaigns**: Retention campaigns and their configurations
- **CampaignEvents**: Campaign execution tracking and results

### 📝 CSV Upload Format

**Transactions CSV:**
```csv
customer_external_id,transaction_date,amount,transaction_type,product_category
CUST001,2024-10-01,125.50,purchase,electronics
CUST001,2024-10-15,89.99,purchase,clothing
```

**Feedback CSV:**
```csv
customer_external_id,feedback_text,feedback_date,source
CUST001,"Great service!",2024-10-16,email
CUST002,"Product quality could be better",2024-10-14,survey
```

### 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/
```

### 📝 Best Practices

This project follows:
- **Repository Pattern**: Clean separation of data access
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: Testable and modular code
- **Logging**: Comprehensive logging with rotation
- **Type Hints**: Full type annotations
- **Error Handling**: Robust exception management

### 🔐 Security Notes

- Never commit `.env` file to version control
- Change default SECRET_KEY in production
- Use strong passwords for database
- Implement proper OAuth in production
- Enable HTTPS for production deployments

### 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

### 📄 License

MIT License

### 🙏 Acknowledgments

- LangChain for agent framework
- Google Gemini for AI capabilities
- Streamlit for beautiful UI
- PostgreSQL for reliable data storage

---

**Built with ❤️ for SMBs and Retention Teams**

For questions or support, please open an issue on GitHub.