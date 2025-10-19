# ai_agents/csv_processor/csv_to_llm.py
"""
CSV to LLM Processor - Sends CSV data to LLM for analysis
"""
import pandas as pd
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Import LLM logging utilities
try:
    from config.llm_logging_config import setup_llm_logging, get_llm_logger, log_llm_request, log_llm_response, log_llm_error
    LLM_LOGGING_AVAILABLE = True
except ImportError:
    LLM_LOGGING_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google Generative AI not available: {e}")
    GOOGLE_AI_AVAILABLE = False

from config.config import config

class CSVToLLMProcessor:
    """Processes CSV data through LLM for churn analysis"""
    
    def __init__(self):
        """Initialize the processor"""
        self.model = None
        self.system_prompt = ""
        
        # Setup LLM logging
        if LLM_LOGGING_AVAILABLE:
            self.llm_logger = setup_llm_logging()
        else:
            self.llm_logger = logger
        
        if not GOOGLE_AI_AVAILABLE:
            logger.error("Google Generative AI not available - cannot initialize processor")
            return
            
        try:
            # Configure the API
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Load system prompt
            self._load_system_prompt()
            
            logger.info("CSV to LLM processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing CSV processor: {str(e)}")
            self.model = None
    
    def _load_system_prompt(self):
        """Load system prompt from file"""
        try:
            prompt_file = "resources/prompts/churn_analysis_system_prompt.txt"
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read()
                logger.info("System prompt loaded successfully")
            else:
                logger.error(f"System prompt file not found: {prompt_file}")
                self.system_prompt = "You are ChurnGuard AI, an expert customer retention analyst."
        except Exception as e:
            logger.error(f"Error loading system prompt: {str(e)}")
            self.system_prompt = "You are ChurnGuard AI, an expert customer retention analyst."
    
    def process_csv(self, csv_data: pd.DataFrame, csv_file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Process CSV data through LLM and return structured analysis"""
        if not self.model:
            logger.error("Model not available - cannot process CSV")
            return None
            
        try:
            # Convert DataFrame to readable format
            csv_text = self._dataframe_to_text(csv_data)
            
            # Create the prompt
            prompt = f"""{self.system_prompt}

## Customer Data to Analyze

{csv_text}

Please analyze this customer data and provide a comprehensive churn analysis in the exact JSON format specified above.

Remember:
- Base ALL analysis on the provided data
- Output ONLY valid JSON (no additional text)
- Include all required fields and structure
- Use realistic numbers based on the data
- Ensure JSON is properly formatted and parseable

## Analysis Output:"""
            
            # Log the prompt being sent to LLM
            if LLM_LOGGING_AVAILABLE:
                log_llm_request(self.llm_logger, "CSV_ANALYSIS", {
                    "csv_shape": csv_data.shape,
                    "csv_columns": list(csv_data.columns),
                    "prompt_length": len(prompt),
                    "system_prompt_length": len(self.system_prompt),
                    "csv_preview": csv_text[:500] + "..." if len(csv_text) > 500 else csv_text,
                    "csv_file_path": csv_file_path
                })
            else:
                logger.info("=== LLM REQUEST START ===")
                logger.info(f"CSV Data Shape: {csv_data.shape}")
                logger.info(f"CSV Columns: {list(csv_data.columns)}")
                logger.info(f"Prompt Length: {len(prompt)} characters")
                logger.info(f"System Prompt Length: {len(self.system_prompt)} characters")
                if csv_file_path:
                    logger.info(f"CSV File Path: {csv_file_path}")
                logger.info("=== LLM REQUEST END ===")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Log the raw LLM response
            if LLM_LOGGING_AVAILABLE:
                log_llm_response(self.llm_logger, "CSV_ANALYSIS", response.text)
            else:
                logger.info("=== LLM RESPONSE START ===")
                logger.info(f"Response Length: {len(response.text)} characters")
                logger.info(f"Raw Response: {response.text}")
                logger.info("=== LLM RESPONSE END ===")
            
            # Parse JSON response
            analysis_result = self._parse_json_response(response.text)
            
            if analysis_result:
                logger.info("=== PARSED ANALYSIS RESULT ===")
                logger.info(f"Analysis Keys: {list(analysis_result.keys())}")
                
                # Log summary data
                if 'summary' in analysis_result:
                    summary = analysis_result['summary']
                    logger.info(f"Summary - Total Customers: {summary.get('total_customers', 'N/A')}")
                    logger.info(f"Summary - High Risk: {summary.get('high_risk_customers', 'N/A')}")
                    logger.info(f"Summary - Medium Risk: {summary.get('medium_risk_customers', 'N/A')}")
                    logger.info(f"Summary - Low Risk: {summary.get('low_risk_customers', 'N/A')}")
                    logger.info(f"Summary - Revenue at Risk: {summary.get('total_revenue_at_risk', 'N/A')}")
                
                # Log churn predictions count
                if 'churn_predictions' in analysis_result:
                    churn_predictions = analysis_result['churn_predictions']
                    logger.info(f"Churn Predictions Count: {len(churn_predictions)}")
                
                # Log insights
                if 'insights' in analysis_result:
                    insights = analysis_result['insights']
                    logger.info(f"Top Churn Drivers: {len(insights.get('top_churn_drivers', []))}")
                    logger.info(f"Retention Opportunities: {len(insights.get('retention_opportunities', []))}")
                    logger.info(f"Recommended Actions: {len(insights.get('recommended_actions', []))}")
                
                logger.info("=== PARSED ANALYSIS RESULT END ===")
                logger.info("CSV processed successfully through LLM")
                return analysis_result
            else:
                logger.error("Failed to parse LLM response as JSON")
                return None
                
        except Exception as e:
            logger.error(f"Error processing CSV through LLM: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _dataframe_to_text(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to readable text format"""
        try:
            # Get basic info
            text = f"Dataset Overview:\n"
            text += f"- Total Records: {len(df)}\n"
            text += f"- Columns: {', '.join(df.columns.tolist())}\n\n"
            
            # Add ALL data (not just sample)
            text += "Complete Customer Data:\n"
            text += df.to_string(index=False)
            text += "\n\n"
            
            # Add column statistics
            text += "Column Statistics:\n"
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    text += f"- {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}\n"
                else:
                    text += f"- {col}: {df[col].nunique()} unique values\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Error converting DataFrame to text: {str(e)}")
            return str(df)
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from LLM"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Log parsing attempt
            logger.info("=== JSON PARSING START ===")
            logger.info(f"Original response length: {len(response_text)}")
            logger.info(f"Cleaned response length: {len(cleaned_text)}")
            
            # Remove any markdown formatting
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
                logger.info("Removed ```json prefix")
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
                logger.info("Removed ``` suffix")
            
            # Log first 200 characters of cleaned text
            logger.info(f"Cleaned text preview: {cleaned_text[:200]}...")
            
            # Parse JSON
            result = json.loads(cleaned_text)
            logger.info("JSON parsing successful")
            
            # Validate required fields
            required_fields = ['summary', 'churn_predictions', 'customer_segments', 'insights', 'analytics']
            missing_fields = []
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)
                    logger.warning(f"Missing required field: {field}")
                else:
                    logger.info(f"Found required field: {field}")
            
            if missing_fields:
                logger.warning(f"Missing fields: {missing_fields}")
            else:
                logger.info("All required fields present")
            
            logger.info("=== JSON PARSING END ===")
            return result
            
        except json.JSONDecodeError as e:
            logger.error("=== JSON DECODE ERROR ===")
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Error at line {e.lineno}, column {e.colno}")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            logger.error(f"Response text (last 500 chars): {response_text[-500:]}")
            logger.error("=== JSON DECODE ERROR END ===")
            return None
        except Exception as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def is_available(self) -> bool:
        """Check if the processor is available"""
        return self.model is not None and GOOGLE_AI_AVAILABLE
