"""
CSV Processor Agent
Optimized version for churn analysis
"""
import pandas as pd
import logging
from typing import Dict, Any, Optional

from .base_agent import BaseAIAgent

logger = logging.getLogger(__name__)


class CSVProcessor(BaseAIAgent):
    """Processes CSV data for churn analysis"""
    
    def __init__(self):
        """Initialize CSV processor"""
        super().__init__("CSVProcessor")
        
        # Load prompts
        self.system_prompt = self.load_prompt_file(
            "churn_analysis_system_prompt.txt",
            fallback="You are ChurnGuard AI, an expert customer retention analyst."
        )
        
        self.user_prompt_template = self.load_prompt_file(
            "csv_analysis_user_prompt_template.txt",
            fallback="## Customer Data to Analyze\n\n{csv_text}\n\n## Analysis Output:"
        )
    
    def process_csv(self, csv_data: pd.DataFrame, 
                   csv_file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process CSV data and return churn analysis
        
        Args:
            csv_data: DataFrame to analyze (already limited to 100 rows)
            csv_file_path: Optional file path for logging
            
        Returns:
            Analysis result dictionary or None if processing fails
        """
        if not self.model:
            logger.error("Model not available")
            return None
        
        try:
            # Safety check - enforce 100 row limit for free tier
            csv_data = self._enforce_row_limit(csv_data, max_rows=100)
            
            # Log processing details
            self._log_processing_start(csv_data, csv_file_path)
            
            # Convert DataFrame to text
            csv_text = self._dataframe_to_text(csv_data)
            
            # Build prompt
            user_prompt = self.user_prompt_template.format(csv_text=csv_text)
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            # Generate analysis
            response = self.generate_content(full_prompt)
            
            if not response:
                logger.error("Failed to generate analysis")
                return None
            
            # Parse JSON response
            analysis_result = self.parse_json_response(response)
            
            if analysis_result:
                self._log_analysis_result(analysis_result)
                logger.info("CSV processed successfully")
                return analysis_result
            else:
                logger.error("Failed to parse analysis response")
                return None
                
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _enforce_row_limit(self, df: pd.DataFrame, max_rows: int = 100) -> pd.DataFrame:
        """Enforce row limit for free tier"""
        original_count = len(df)
        
        if original_count > max_rows:
            logger.warning(f"Limiting {original_count} rows to {max_rows} for free tier")
            return df.head(max_rows)
        
        return df
    
    def _log_processing_start(self, df: pd.DataFrame, file_path: Optional[str]):
        """Log processing start details"""
        details = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
        
        if file_path:
            details["file_path"] = file_path
        
        self.log_request("CSV_ANALYSIS", details)
    
    def _dataframe_to_text(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to text format optimized for AI analysis
        
        Args:
            df: DataFrame to convert
            
        Returns:
            Text representation of data
        """
        try:
            text = f"Dataset Overview:\n"
            text += f"- Total Records: {len(df)}\n"
            text += f"- Columns: {', '.join(df.columns.tolist())}\n\n"
            
            text += "Customer Data:\n"
            text += df.to_string(index=False)
            text += "\n\n"
            
            # Add statistical summary
            text += self._build_statistical_summary(df)
            
            # Add analysis instructions
            text += f"\n\nIMPORTANT: Generate churn predictions for these {len(df)} customers. "
            text += "Each customer needs: customer_id, churn_probability, risk_level, "
            text += "primary_risk_factors, retention_recommendation, and estimated_revenue_impact.\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Error converting DataFrame to text: {str(e)}")
            return str(df)
    
    def _build_statistical_summary(self, df: pd.DataFrame) -> str:
        """Build statistical summary section"""
        summary = f"Statistical Summary ({len(df)} records):\n"
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                summary += f"- {col}: "
                summary += f"min={df[col].min()}, "
                summary += f"max={df[col].max()}, "
                summary += f"mean={df[col].mean():.2f}, "
                summary += f"median={df[col].median():.2f}, "
                summary += f"std={df[col].std():.2f}\n"
            else:
                unique_vals = df[col].nunique()
                summary += f"- {col}: {unique_vals} unique values"
                
                if unique_vals <= 10:
                    values = ', '.join(df[col].unique().astype(str).tolist())
                    summary += f" ({values})"
                
                summary += "\n"
        
        return summary
    
    def _log_analysis_result(self, result: Dict[str, Any]):
        """Log analysis result summary"""
        logger.info("=== ANALYSIS RESULT ===")
        logger.info(f"Keys: {list(result.keys())}")
        
        # Log summary data
        if 'summary' in result:
            summary = result['summary']
            logger.info(f"Total Customers: {summary.get('total_customers', 'N/A')}")
            logger.info(f"High Risk: {summary.get('high_risk_customers', 'N/A')}")
            logger.info(f"Medium Risk: {summary.get('medium_risk_customers', 'N/A')}")
            logger.info(f"Low Risk: {summary.get('low_risk_customers', 'N/A')}")
            logger.info(f"Revenue at Risk: {summary.get('total_revenue_at_risk', 'N/A')}")
        
        # Log predictions count
        if 'churn_predictions' in result:
            predictions = result['churn_predictions']
            logger.info(f"Predictions: {len(predictions)}")
        
        # Log insights count
        if 'insights' in result:
            insights = result['insights']
            logger.info(f"Churn Drivers: {len(insights.get('top_churn_drivers', []))}")
            logger.info(f"Opportunities: {len(insights.get('retention_opportunities', []))}")
            logger.info(f"Actions: {len(insights.get('recommended_actions', []))}")

