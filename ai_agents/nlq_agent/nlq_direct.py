# ai_agents/nlq_agent/nlq_direct.py
"""
Direct Natural Language Query agent using Google Generative AI
"""
import pandas as pd
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google Generative AI not available: {e}")
    GOOGLE_AI_AVAILABLE = False

from config.config import config

def build_context(df: pd.DataFrame) -> str:
    """Build statistical context from DataFrame"""
    ctx = {}
    
    # Basic stats
    ctx["total_customers"] = len(df)
    
    # Churn stats
    if "churn_probability" in df.columns:
        ctx["avg_churn_probability"] = round(float(df["churn_probability"].mean()), 3)
        ctx["high_risk_customers"] = int((df["churn_probability"] > 0.7).sum())
        ctx["medium_risk_customers"] = int(((df["churn_probability"] >= 0.4) & (df["churn_probability"] < 0.7)).sum())
        ctx["low_risk_customers"] = int((df["churn_probability"] < 0.4).sum())
    
    # Spend stats
    if "total_spend" in df.columns:
        ctx["avg_total_spend"] = round(float(df["total_spend"].mean()), 2)
        ctx["max_total_spend"] = round(float(df["total_spend"].max()), 2)
        ctx["min_total_spend"] = round(float(df["total_spend"].min()), 2)
    
    # Activity stats
    if "days_since_last_activity" in df.columns:
        ctx["avg_days_inactive"] = round(float(df["days_since_last_activity"].mean()), 1)
        ctx["customers_inactive_60_plus"] = int((df["days_since_last_activity"] >= 60).sum())
        ctx["customers_inactive_30_plus"] = int((df["days_since_last_activity"] >= 30).sum())
    
    # Transaction stats
    if "total_transactions" in df.columns:
        ctx["avg_transactions"] = round(float(df["total_transactions"].mean()), 1)
    
    # Account status
    if "account_status" in df.columns:
        ctx["active_customers"] = int((df["account_status"] == "active").sum())
        ctx["inactive_customers"] = int((df["account_status"] == "inactive").sum())
    
    # Format as readable text
    lines = []
    for key, value in ctx.items():
        formatted_key = key.replace("_", " ").title()
        lines.append(f"{formatted_key}: {value}")
    
    return "\n".join(lines)

class DirectNLQAgent:
    """Direct Natural Language Query agent using Google Generative AI"""
    
    def __init__(self):
        """Initialize with Google Generative AI directly"""
        self.df: Optional[pd.DataFrame] = None
        self.context: str = ""
        self.model = None
        self.csv_file_id: Optional[str] = None  # Store CSV file ID from MongoDB
        self.csv_content: Optional[bytes] = None  # Store CSV content from MongoDB
        
        if not GOOGLE_AI_AVAILABLE:
            logger.error("Google Generative AI not available - cannot initialize NLQ agent")
            return
            
        try:
            # Configure the API
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            logger.info("Direct NLQ agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Direct NLQ agent: {str(e)}")
            self.model = None
    
    def load(self, df: pd.DataFrame, csv_file_id: Optional[str] = None, csv_content: Optional[bytes] = None):
        """Load DataFrame and CSV content from MongoDB"""
        self.df = df
        self.context = build_context(df)
        self.csv_file_id = csv_file_id
        self.csv_content = csv_content
        
        # Upload CSV content to Google AI if available
        if csv_content and self.model:
            try:
                # Create a temporary file-like object from bytes
                import io
                csv_file_obj = io.BytesIO(csv_content)
                csv_file_obj.name = "customer_data.csv"  # Set a name for the file
                
                self.uploaded_file = genai.upload_file(csv_file_obj, mime_type="text/csv")
                logger.info("CSV content uploaded to Google AI from MongoDB")
            except Exception as e:
                logger.error(f"Error uploading CSV content to Google AI: {str(e)}")
                self.uploaded_file = None
        
        logger.info(f"Loaded {len(df)} customer records")
        if csv_file_id:
            logger.info(f"CSV file ID from MongoDB: {csv_file_id}")
    
    def ask(self, question: str, conversation_history: Optional[list] = None) -> str:
        """Answer question using Google Generative AI with CSV file and conversation history"""
        if not self.model:
            return "NLQ agent not available - Google AI initialization failed."
            
        if self.df is None:
            return "Please load data first."
        
        try:
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n\n**Previous Conversation:**\n"
                for msg in conversation_history[-6:]:  # Last 6 messages to avoid token limits
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_context += f"{role}: {msg['content']}\n"
            
            # Create the prompt
            prompt = f"""You are a customer retention analyst for ChurnGuard, an AI-powered retention platform.

**Available Customer Data Summary:**
{self.context}

{conversation_context}

**Current User Question:** {question}

**Instructions:**
- Answer based on the data summary provided above AND the uploaded CSV file
- Consider the conversation history when providing context
- Be specific and use exact numbers from the context
- If the data doesn't contain information to answer, say so clearly
- Keep answers concise but informative
- Use bullet points for multiple items
- Focus on actionable insights for customer retention
- Reference previous questions/answers when relevant

**Answer:**"""
            
            # Log the NLQ request
            logger.info("=== NLQ REQUEST START ===")
            logger.info(f"Question: {question}")
            logger.info(f"Context length: {len(self.context)} characters")
            logger.info(f"Conversation history length: {len(conversation_context)} characters")
            logger.info(f"Prompt length: {len(prompt)} characters")
            if hasattr(self, 'uploaded_file') and self.uploaded_file:
                logger.info("CSV file will be included in LLM request")
            logger.info("=== NLQ REQUEST END ===")
            
            # Generate response with CSV file if available
            if hasattr(self, 'uploaded_file') and self.uploaded_file:
                # Generate response with both prompt and CSV file
                response = self.model.generate_content([prompt, self.uploaded_file])
                logger.info("CSV file included in LLM request")
            else:
                # Generate response with prompt only
                response = self.model.generate_content(prompt)
                if self.csv_file_id:
                    logger.warning(f"CSV file not uploaded: {self.csv_file_id}")
            
            # Log the NLQ response
            logger.info("=== NLQ RESPONSE START ===")
            logger.info(f"Response length: {len(response.text)} characters")
            logger.info(f"Response: {response.text}")
            logger.info("=== NLQ RESPONSE END ===")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in NLQ query: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"I encountered an error processing your question: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if the agent is available"""
        return self.model is not None and GOOGLE_AI_AVAILABLE
