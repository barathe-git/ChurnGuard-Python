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

class DirectNLQAgent:
    """Direct Natural Language Query agent using Google Generative AI"""
    
    def __init__(self):
        """Initialize with Google Generative AI directly"""
        self.df: Optional[pd.DataFrame] = None
        self.model = None
        self.csv_file_id: Optional[str] = None  # Store CSV file ID from MongoDB
        self.csv_content: Optional[bytes] = None  # Store CSV content from MongoDB
        self.uploaded_file = None  # Store uploaded CSV file reference for GenAI
        self.system_prompt: str = ""
        self.user_prompt_template: str = ""
        self.csv_metadata: dict = {}  # Store CSV metadata (size, rows, columns)
        
        if not GOOGLE_AI_AVAILABLE:
            logger.error("Google Generative AI not available - cannot initialize NLQ agent")
            return
            
        try:
            # Configure the API
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            # Load prompts from files
            self._load_prompts()
            
            logger.info("Direct NLQ agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Direct NLQ agent: {str(e)}")
            self.model = None
    
    def _load_prompts(self):
        """Load system and user prompt templates from files"""
        try:
            # Load system prompt
            system_prompt_file = "resources/prompts/nlq_system_prompt.txt"
            if os.path.exists(system_prompt_file):
                with open(system_prompt_file, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read()
                logger.info("NLQ system prompt loaded successfully")
            else:
                logger.error(f"System prompt file not found: {system_prompt_file}")
                self.system_prompt = "You are a customer retention analyst for ChurnGuard."
            
            # Load user prompt template
            user_prompt_file = "resources/prompts/nlq_user_prompt_template.txt"
            if os.path.exists(user_prompt_file):
                with open(user_prompt_file, 'r', encoding='utf-8') as f:
                    self.user_prompt_template = f.read()
                logger.info("NLQ user prompt template loaded successfully")
            else:
                logger.error(f"User prompt template file not found: {user_prompt_file}")
                self.user_prompt_template = "**Question:** {question}\n\n**Answer:**"
                
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            self.system_prompt = "You are a customer retention analyst for ChurnGuard."
            self.user_prompt_template = "**Question:** {question}\n\n**Answer:**"
    
    def load(self, df: pd.DataFrame, csv_file_id: Optional[str] = None, csv_content: Optional[bytes] = None):
        """
        Load DataFrame and CSV content from MongoDB
        
        Args:
            df: DataFrame to load
            csv_file_id: MongoDB file ID
            csv_content: CSV file content in bytes
        """
        try:
            # Build metadata from DataFrame (validation already done in frontend)
            self.csv_metadata = {
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "columns": list(df.columns)
            }
            
            self.df = df
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
                    logger.info(f"CSV uploaded to Google AI - {self.csv_metadata.get('num_rows', 0):,} rows")
                except Exception as e:
                    logger.error(f"Error uploading CSV content to Google AI: {str(e)}")
                    self.uploaded_file = None
                    raise Exception(f"Failed to upload CSV to AI: {str(e)}")
            
            logger.info(f"Loaded {len(df):,} customer records from MongoDB")
            if csv_file_id:
                logger.info(f"CSV file ID: {csv_file_id}")
                
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def ask(self, question: str, conversation_history: Optional[list] = None) -> str:
        """
        Answer question using Google Generative AI with optimized data context
        
        Args:
            question: User's question
            conversation_history: Optional list of previous messages
            
        Returns:
            AI-generated response
        """
        if not self.model:
            return "NLQ agent not available - Google AI initialization failed."
            
        if self.df is None:
            return "Please load data first."
        
        try:
            # Build conversation context (limit to last 4 messages to save tokens)
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n**Previous Conversation:**\n"
                for msg in conversation_history[-4:]:  # Reduced from 6 to 4
                    role = "User" if msg["role"] == "user" else "Assistant"
                    # Truncate long messages
                    content = msg['content'][:500] if len(msg['content']) > 500 else msg['content']
                    conversation_context += f"{role}: {content}\n"
            
            # OPTIMIZATION: Determine if we need full CSV or just summary
            # Simple questions can be answered with cached summary
            needs_full_csv = self._needs_full_csv_analysis(question)
            
            if needs_full_csv and hasattr(self, 'uploaded_file') and self.uploaded_file:
                # Complex query - use full CSV file (already uploaded, cached by Gemini)
                data_info = f"""**Dataset Information:**
- Total Rows: {self.csv_metadata.get('num_rows', len(self.df)):,}
- Total Columns: {self.csv_metadata.get('num_columns', len(self.df.columns))}
- Available Fields: {', '.join(self.csv_metadata.get('columns', list(self.df.columns)))}

**Note:** Full CSV data is attached for detailed analysis."""
                
                # Build the complete prompt
                user_prompt = self.user_prompt_template.format(
                    context=data_info,
                    conversation_history=conversation_context,
                    question=question
                )
                full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
                
                logger.info(f"NLQ Request: Complex query, using full CSV ({self.csv_metadata.get('num_rows', 0):,} rows)")
                
                # Generate response with both prompt and cached CSV file
                response = self.model.generate_content([full_prompt, self.uploaded_file])
            else:
                # Simple query - use summary data only (TOKEN SAVER!)
                summary_data = self._get_summary_statistics()
                data_info = f"""**Dataset Summary:**
- Total Rows: {self.csv_metadata.get('num_rows', len(self.df)):,}
- Total Columns: {self.csv_metadata.get('num_columns', len(self.df.columns))}
- Available Fields: {', '.join(self.csv_metadata.get('columns', list(self.df.columns)))}

**Statistical Summary:**
{summary_data}

**Note:** This is a summary. For detailed row-level analysis, I can access the full dataset."""
                
                # Build the complete prompt
                user_prompt = self.user_prompt_template.format(
                    context=data_info,
                    conversation_history=conversation_context,
                    question=question
                )
                full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
                
                logger.info(f"NLQ Request: Simple query, using summary only (token optimized)")
                
                # Generate response with just prompt (no CSV file)
                response = self.model.generate_content(full_prompt)
            
            logger.info(f"NLQ Response: {len(response.text)} characters")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in NLQ query: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"I encountered an error processing your question: {str(e)}"
    
    def _needs_full_csv_analysis(self, question: str) -> bool:
        """
        Determine if question needs full CSV or can use summary
        TOKEN OPTIMIZATION: Most questions can be answered with summary stats
        """
        question_lower = question.lower()
        
        # Keywords that require full CSV access
        complex_keywords = [
            'list all', 'show all', 'give me all', 'every customer',
            'which customers', 'who are', 'specific customer',
            'customer id', 'customer with', 'customers where',
            'find customer', 'search for', 'details about',
            'individual', 'breakdown by customer'
        ]
        
        # If question has complex keywords, use full CSV
        if any(keyword in question_lower for keyword in complex_keywords):
            return True
        
        # Simple statistical questions use summary only
        return False
    
    def _get_summary_statistics(self) -> str:
        """Generate summary statistics for efficient token usage"""
        if self.df is None:
            return "No data available"
        
        try:
            summary = ""
            for col in self.df.columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    summary += f"\n{col}:\n"
                    summary += f"  - Min: {self.df[col].min()}\n"
                    summary += f"  - Max: {self.df[col].max()}\n"
                    summary += f"  - Mean: {self.df[col].mean():.2f}\n"
                    summary += f"  - Median: {self.df[col].median():.2f}\n"
                else:
                    unique_count = self.df[col].nunique()
                    summary += f"\n{col}: {unique_count} unique values"
                    if unique_count <= 10:
                        summary += f" - ({', '.join(self.df[col].unique().astype(str)[:10].tolist())})"
                    summary += "\n"
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary statistics: {str(e)}")
            return "Error generating summary"
    
    def is_available(self) -> bool:
        """Check if the agent is available"""
        return self.model is not None and GOOGLE_AI_AVAILABLE
