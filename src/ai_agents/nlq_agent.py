"""
Natural Language Query Agent
Optimized version with clean, modular code
"""
import pandas as pd
import io
import logging
from typing import Optional, List, Dict, Any

from .base_agent import BaseAIAgent, genai

logger = logging.getLogger(__name__)


class NLQAgent(BaseAIAgent):
    """Natural Language Query agent for customer data analysis"""
    
    def __init__(self):
        """Initialize NLQ agent"""
        super().__init__("NLQAgent")
        
        self.df: Optional[pd.DataFrame] = None
        self.csv_file_id: Optional[str] = None
        self.csv_content: Optional[bytes] = None
        self.uploaded_file = None
        self.csv_metadata: Dict[str, Any] = {}
        
        # Load prompts
        self.system_prompt = self.load_prompt_file(
            "nlq_system_prompt.txt",
            fallback="You are a customer retention analyst for ChurnGuard."
        )
        
        self.user_prompt_template = self.load_prompt_file(
            "nlq_user_prompt_template.txt",
            fallback="**Question:** {question}\n\n**Answer:**"
        )
    
    def load(self, df: pd.DataFrame, csv_file_id: Optional[str] = None, 
             csv_content: Optional[bytes] = None):
        """
        Load DataFrame and CSV content
        
        Args:
            df: Customer data DataFrame
            csv_file_id: MongoDB file ID
            csv_content: CSV bytes for AI upload
        """
        try:
            # Store data
            self.df = df
            self.csv_file_id = csv_file_id
            self.csv_content = csv_content
            
            # Build metadata
            self.csv_metadata = {
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "columns": list(df.columns)
            }
            
            # Upload CSV to Google AI if available
            if csv_content and self.model:
                self._upload_csv_to_ai(csv_content)
            
            logger.info(f"Loaded {len(df):,} records (File ID: {csv_file_id})")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _upload_csv_to_ai(self, csv_content: bytes):
        """Upload CSV content to Google AI"""
        try:
            csv_file_obj = io.BytesIO(csv_content)
            csv_file_obj.name = "customer_data.csv"
            
            self.uploaded_file = genai.upload_file(csv_file_obj, mime_type="text/csv")
            logger.info(f"CSV uploaded to Google AI - {self.csv_metadata['num_rows']:,} rows")
            
        except Exception as e:
            logger.error(f"Error uploading CSV to AI: {str(e)}")
            self.uploaded_file = None
            raise Exception(f"Failed to upload CSV to AI: {str(e)}")
    
    def ask(self, question: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Answer question using AI with optimized context
        
        Args:
            question: User's question
            conversation_history: Previous conversation messages
            
        Returns:
            AI-generated response
        """
        if not self.model:
            return "AI agent not available - initialization failed."
        
        if self.df is None:
            return "Please load data first."
        
        try:
            # Build conversation context (limited for token efficiency)
            context = self._build_conversation_context(conversation_history)
            
            # Determine if full CSV needed or summary sufficient
            needs_full_csv = self._needs_full_csv_analysis(question)
            
            if needs_full_csv and self.uploaded_file:
                response = self._query_with_full_csv(question, context)
            else:
                response = self._query_with_summary(question, context)
            
            logger.info(f"Response generated: {len(response)} chars")
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return f"I encountered an error: {str(e)}"
    
    def _build_conversation_context(self, history: Optional[List[Dict]]) -> str:
        """Build conversation context from history"""
        if not history:
            return ""
        
        context = "\n**Previous Conversation:**\n"
        
        # Limit to last 4 messages for token efficiency
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg['content']
            
            # Truncate long messages
            if len(content) > 500:
                content = content[:500] + "..."
            
            context += f"{role}: {content}\n"
        
        return context
    
    def _needs_full_csv_analysis(self, question: str) -> bool:
        """
        Determine if question needs full CSV or summary
        
        Args:
            question: User's question
            
        Returns:
            True if full CSV needed, False for summary only
        """
        question_lower = question.lower()
        
        # Keywords requiring full CSV
        complex_keywords = [
            'list all', 'show all', 'give me all', 'every customer',
            'which customers', 'who are', 'specific customer',
            'customer id', 'customer with', 'customers where',
            'find customer', 'search for', 'details about',
            'individual', 'breakdown by customer'
        ]
        
        return any(keyword in question_lower for keyword in complex_keywords)
    
    def _query_with_full_csv(self, question: str, context: str) -> str:
        """Query with full CSV file (for complex questions)"""
        try:
            # Build data info
            data_info = f"""**Dataset Information:**
- Total Rows: {self.csv_metadata['num_rows']:,}
- Total Columns: {self.csv_metadata['num_columns']}
- Fields: {', '.join(self.csv_metadata['columns'])}

**Note:** Full CSV data attached for detailed analysis."""
            
            # Build complete prompt
            user_prompt = self.user_prompt_template.format(
                context=data_info,
                conversation_history=context,
                question=question
            )
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Complex query - using full CSV ({self.csv_metadata['num_rows']:,} rows)")
            
            # Generate with CSV file
            response = self.generate_content(full_prompt, [self.uploaded_file])
            return response if response else "Error generating response."
            
        except Exception as e:
            logger.error(f"Error in full CSV query: {str(e)}")
            return f"Error: {str(e)}"
    
    def _query_with_summary(self, question: str, context: str) -> str:
        """Query with summary only (for simple questions - token saver!)"""
        try:
            # Get summary statistics
            summary = self._get_summary_statistics()
            
            # Build data info
            data_info = f"""**Dataset Summary:**
- Total Rows: {self.csv_metadata['num_rows']:,}
- Total Columns: {self.csv_metadata['num_columns']}
- Fields: {', '.join(self.csv_metadata['columns'])}

**Statistical Summary:**
{summary}

**Note:** Summary mode. For detailed row-level analysis, I can access full dataset."""
            
            # Build complete prompt
            user_prompt = self.user_prompt_template.format(
                context=data_info,
                conversation_history=context,
                question=question
            )
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info("Simple query - using summary only (token optimized)")
            
            # Generate with prompt only
            response = self.generate_content(full_prompt)
            return response if response else "Error generating response."
            
        except Exception as e:
            logger.error(f"Error in summary query: {str(e)}")
            return f"Error: {str(e)}"
    
    def _get_summary_statistics(self) -> str:
        """Generate summary statistics for token efficiency"""
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
                        values = ', '.join(self.df[col].unique().astype(str)[:10].tolist())
                        summary += f" - ({values})"
                    summary += "\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Error generating summary"

