"""
CSV Header Validator Agent
Optimized version for header validation
"""
import pandas as pd
import logging
from typing import Dict, Any, List

from .base_agent import BaseAIAgent

logger = logging.getLogger(__name__)


class CSVHeaderValidator(BaseAIAgent):
    """Validates CSV headers for churn detection suitability"""
    
    def __init__(self):
        """Initialize CSV header validator"""
        super().__init__("CSVHeaderValidator")
        
        # Load validation prompt
        self.validation_prompt = self.load_prompt_file(
            "csv_header_validation_prompt.txt",
            fallback="Analyze these CSV headers and determine if churn prediction is possible."
        )
    
    def validate_headers(self, headers: List[str]) -> Dict[str, Any]:
        """
        Validate CSV headers for churn detection
        
        Args:
            headers: List of column names
            
        Returns:
            Validation result dictionary
        """
        if not self.model:
            return self._get_fallback_response("Validator not available")
        
        if not headers or len(headers) == 0:
            return self._get_fallback_response("No headers provided")
        
        try:
            # Build validation prompt
            prompt = self._build_validation_prompt(headers)
            
            # Log request
            self.log_request("HEADER_VALIDATION", {
                "num_headers": len(headers),
                "headers": ', '.join(headers)
            })
            
            # Generate validation
            response = self.generate_content(prompt)
            
            if not response:
                return self._get_fallback_response("Failed to generate validation")
            
            # Parse response
            result = self.parse_json_response(response)
            
            if result:
                result = self._ensure_required_fields(result)
                logger.info(f"Validation: Suitable={result.get('is_suitable')}, "
                          f"Confidence={result.get('confidence')}")
                return result
            else:
                return self._get_fallback_response("Failed to parse validation response")
                
        except Exception as e:
            logger.error(f"Error validating headers: {str(e)}")
            return self._get_fallback_response(f"Validation error: {str(e)}")
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame headers
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validation result dictionary
        """
        headers = list(df.columns)
        return self.validate_headers(headers)
    
    def _build_validation_prompt(self, headers: List[str]) -> str:
        """Build validation prompt with headers"""
        headers_text = ", ".join(headers)
        
        prompt = f"""{self.validation_prompt}

## CSV Headers to Validate

The uploaded CSV file has the following column headers:

{headers_text}

## Your Analysis

Analyze these headers and provide your validation response in JSON format as specified above."""
        
        return prompt
    
    def _ensure_required_fields(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present"""
        required_fields = {
            'is_suitable': False,
            'confidence': 'low',
            'reasoning': 'N/A',
            'message': 'N/A'
        }
        
        for field, default_value in required_fields.items():
            if field not in result:
                logger.warning(f"Missing field: {field}, using default")
                result[field] = default_value
        
        return result
    
    def _get_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """
        Return fallback response when validation fails
        
        Args:
            error_message: Error description
            
        Returns:
            Fallback validation result (permissive to not block users)
        """
        return {
            "is_suitable": True,  # Default to True to not block users
            "confidence": "low",
            "reasoning": f"Automatic validation unavailable: {error_message}. Proceeding with caution.",
            "identified_fields": {},
            "missing_critical_fields": [],
            "recommendations": "Manual review recommended",
            "message": f"⚠️ Unable to validate headers ({error_message}). "
                      "You can proceed, but ensure your data contains customer behavioral metrics."
        }


# Create singleton instance for backward compatibility
csv_header_validator = CSVHeaderValidator()

