"""
CSV Header Validator Agent - Validates if CSV headers are suitable for churn detection
"""
import pandas as pd
import os
import json
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google Generative AI not available: {e}")
    GOOGLE_AI_AVAILABLE = False

from config.config import config


class CSVHeaderValidator:
    """Validates CSV headers to determine if churn detection is possible"""
    
    # Class-level flag to track if we've logged initialization (avoid spam in Streamlit reruns)
    _first_init_logged = False
    
    def __init__(self):
        """Initialize the CSV header validator"""
        self.model = None
        self.validation_prompt = ""
        
        if not GOOGLE_AI_AVAILABLE:
            if not CSVHeaderValidator._first_init_logged:
                logger.error("Google Generative AI not available - cannot initialize CSV header validator")
                CSVHeaderValidator._first_init_logged = True
            return
            
        try:
            # Configure the API
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            # Load validation prompt
            self._load_validation_prompt()
            
            # Only log on first initialization to avoid spam in Streamlit reruns
            if not CSVHeaderValidator._first_init_logged:
                logger.info("CSV header validator initialized successfully")
                CSVHeaderValidator._first_init_logged = True
            
        except Exception as e:
            logger.error(f"Error initializing CSV header validator: {str(e)}")
            self.model = None
    
    def _load_validation_prompt(self):
        """Load validation prompt from file"""
        try:
            prompt_file = "resources/prompts/csv_header_validation_prompt.txt"
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.validation_prompt = f.read()
                # Suppress repetitive logging - main initialization message is logged in __init__
            else:
                # Only log errors on first init
                if not CSVHeaderValidator._first_init_logged:
                    logger.error(f"Validation prompt file not found: {prompt_file}")
                self.validation_prompt = "Analyze these CSV headers and determine if churn prediction is possible."
        except Exception as e:
            # Only log errors on first init
            if not CSVHeaderValidator._first_init_logged:
                logger.error(f"Error loading validation prompt: {str(e)}")
            self.validation_prompt = "Analyze these CSV headers and determine if churn prediction is possible."
    
    def validate_headers(self, headers: List[str]) -> Dict[str, Any]:
        """
        Validate CSV headers for churn detection suitability
        
        Args:
            headers: List of column names from CSV
            
        Returns:
            Dictionary with validation results:
            {
                "is_suitable": bool,
                "confidence": str,
                "reasoning": str,
                "identified_fields": dict,
                "missing_critical_fields": list,
                "recommendations": str,
                "message": str
            }
        """
        if not self.model:
            return self._get_fallback_response("Validator not available")
        
        if not headers or len(headers) == 0:
            return self._get_fallback_response("No headers provided")
        
        try:
            # Build the validation request
            headers_text = ", ".join(headers)
            
            prompt = f"""{self.validation_prompt}

## CSV Headers to Validate

The uploaded CSV file has the following column headers:

{headers_text}

## Your Analysis

Analyze these headers and provide your validation response in JSON format as specified above."""
            
            # Log the validation request
            logger.info("=== CSV HEADER VALIDATION REQUEST START ===")
            logger.info(f"Number of headers: {len(headers)}")
            logger.info(f"Headers: {headers_text}")
            logger.info("=== CSV HEADER VALIDATION REQUEST END ===")
            
            # Generate validation response
            response = self.model.generate_content(prompt)
            
            # Log the raw response
            logger.info("=== CSV HEADER VALIDATION RESPONSE START ===")
            logger.info(f"Response length: {len(response.text)} characters")
            logger.info(f"Raw response: {response.text}")
            logger.info("=== CSV HEADER VALIDATION RESPONSE END ===")
            
            # Parse JSON response
            validation_result = self._parse_json_response(response.text)
            
            if validation_result:
                logger.info(f"Validation result: Suitable={validation_result.get('is_suitable')}, "
                          f"Confidence={validation_result.get('confidence')}")
                return validation_result
            else:
                logger.error("Failed to parse validation response")
                return self._get_fallback_response("Failed to parse validation response")
                
        except Exception as e:
            logger.error(f"Error validating CSV headers: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_fallback_response(f"Validation error: {str(e)}")
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate a DataFrame's headers for churn detection suitability
        
        Args:
            df: Pandas DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        headers = list(df.columns)
        return self.validate_headers(headers)
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from LLM"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown formatting if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            result = json.loads(cleaned_text)
            
            # Validate required fields
            required_fields = ['is_suitable', 'confidence', 'reasoning', 'message']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing required field in validation response: {field}")
                    # Add default value
                    if field == 'is_suitable':
                        result[field] = False
                    elif field == 'confidence':
                        result[field] = 'low'
                    else:
                        result[field] = 'N/A'
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing validation response: {str(e)}")
            return None
    
    def _get_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Return a fallback response when validation fails"""
        return {
            "is_suitable": True,  # Default to True to not block users
            "confidence": "low",
            "reasoning": f"Automatic validation unavailable: {error_message}. Proceeding with caution.",
            "identified_fields": {},
            "missing_critical_fields": [],
            "recommendations": "Manual review recommended",
            "message": f"⚠️ Unable to automatically validate headers ({error_message}). You can proceed, but ensure your data contains customer behavioral metrics for accurate churn prediction."
        }
    
    def is_available(self) -> bool:
        """Check if the validator is available"""
        return self.model is not None and GOOGLE_AI_AVAILABLE


# Create singleton instance
csv_header_validator = CSVHeaderValidator()

