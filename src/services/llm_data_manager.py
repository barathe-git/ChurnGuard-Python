# src/services/llm_data_manager.py
"""
LLM Data Manager - Manages data flow from LLM response to application
"""
import pandas as pd
import json
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class LLMDataManager:
    """Manages data from LLM analysis and provides it to the application"""
    
    def __init__(self):
        """Initialize the data manager"""
        self.analysis_data: Optional[Dict[str, Any]] = None
        self.customer_df: Optional[pd.DataFrame] = None
        self.summary_data: Optional[Dict[str, Any]] = None
        self.original_csv_data: Optional[pd.DataFrame] = None
        
    def load_llm_analysis(self, analysis_result: Dict[str, Any], original_csv_data: Optional[pd.DataFrame] = None):
        """Load LLM analysis result and create application data"""
        try:
            logger.info("=== LLM DATA MANAGER LOADING START ===")
            logger.info(f"Analysis result keys: {list(analysis_result.keys())}")
            
            self.analysis_data = analysis_result
            self.original_csv_data = original_csv_data
            
            # Extract summary data
            self.summary_data = analysis_result.get('summary', {})
            logger.info(f"Summary data loaded: {self.summary_data}")
            
            # Create customer DataFrame from churn predictions
            self._create_customer_dataframe()
            
            logger.info("=== LLM DATA MANAGER LOADING END ===")
            logger.info("LLM analysis loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LLM analysis: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _create_customer_dataframe(self):
        """Create customer DataFrame from LLM churn predictions"""
        try:
            logger.info("=== CREATING CUSTOMER DATAFRAME START ===")
            churn_predictions = self.analysis_data.get('churn_predictions', {})
            logger.info(f"Churn predictions count: {len(churn_predictions)}")
            
            if not churn_predictions:
                logger.warning("No churn predictions found in LLM response")
                return
            
            # Create email mapping from original CSV data if available
            email_mapping = {}
            if self.original_csv_data is not None:
                logger.info("Creating email mapping from original CSV data")
                # Check if CSV has CustomerID and Email columns
                if 'CustomerID' in self.original_csv_data.columns and 'Email' in self.original_csv_data.columns:
                    email_mapping = dict(zip(self.original_csv_data['CustomerID'], self.original_csv_data['Email']))
                    logger.info(f"Created email mapping for {len(email_mapping)} customers")
                else:
                    logger.warning("CSV data missing CustomerID or Email columns")
            else:
                logger.warning("No original CSV data available for email mapping")
            
            # Convert to DataFrame
            customer_data = []
            for customer_id, data in churn_predictions.items():
                # Get email from mapping or use default
                customer_email = email_mapping.get(data.get('customer_id', customer_id), 'barath.contact@gmail.com')
                
                customer_record = {
                    'customer_id': data.get('customer_id', customer_id),
                    'email': customer_email,
                    'churn_probability': data.get('churn_probability', 0.0),
                    'risk_level': data.get('risk_level', 'low'),
                    'primary_risk_factors': ', '.join(data.get('primary_risk_factors', [])),
                    'retention_recommendation': data.get('retention_recommendation', 'monitor'),
                    'estimated_revenue_impact': data.get('estimated_revenue_impact', 0)
                }
                customer_data.append(customer_record)
                logger.debug(f"Processed customer {customer_id}: {customer_record}")
            
            self.customer_df = pd.DataFrame(customer_data)
            logger.info(f"Created customer DataFrame with {len(self.customer_df)} customers")
            logger.info(f"DataFrame columns: {list(self.customer_df.columns)}")
            
            # Add additional calculated fields
            self._add_calculated_fields()
            
            logger.info("=== CREATING CUSTOMER DATAFRAME END ===")
            
        except Exception as e:
            logger.error(f"Error creating customer DataFrame: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _add_calculated_fields(self):
        """Add calculated fields to customer DataFrame"""
        try:
            if self.customer_df is None:
                return
            
            # Add risk category
            self.customer_df['risk_category'] = self.customer_df['churn_probability'].apply(
                lambda x: 'high' if x >= 0.7 else 'medium' if x >= 0.4 else 'low'
            )
            
            # Add revenue tier
            self.customer_df['revenue_tier'] = self.customer_df['estimated_revenue_impact'].apply(
                lambda x: 'high' if x >= 10000 else 'medium' if x >= 1000 else 'low'
            )
            
            # Add priority score (combination of churn probability and revenue impact)
            self.customer_df['priority_score'] = (
                self.customer_df['churn_probability'] * 0.7 + 
                (self.customer_df['estimated_revenue_impact'] / 10000) * 0.3
            ).clip(0, 1)
            
        except Exception as e:
            logger.error(f"Error adding calculated fields: {str(e)}")
    
    def get_customer_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the customer DataFrame"""
        return self.customer_df
    
    def get_summary_data(self) -> Optional[Dict[str, Any]]:
        """Get summary data"""
        return self.summary_data
    
    def get_customer_segments(self) -> Optional[Dict[str, Any]]:
        """Get customer segments data"""
        return self.analysis_data.get('customer_segments', {}) if self.analysis_data else None
    
    def get_insights(self) -> Optional[Dict[str, Any]]:
        """Get insights data"""
        return self.analysis_data.get('insights', {}) if self.analysis_data else None
    
    def get_analytics(self) -> Optional[Dict[str, Any]]:
        """Get analytics data"""
        return self.analysis_data.get('analytics', {}) if self.analysis_data else None
    
    def get_churn_distribution(self) -> Optional[Dict[str, int]]:
        """Get churn probability distribution"""
        analytics = self.get_analytics()
        return analytics.get('churn_probability_distribution', {}) if analytics else None
    
    def get_revenue_at_risk(self) -> Optional[Dict[str, float]]:
        """Get revenue at risk by segment"""
        analytics = self.get_analytics()
        return analytics.get('revenue_at_risk_by_segment', {}) if analytics else None
    
    def get_engagement_trends(self) -> Optional[Dict[str, int]]:
        """Get engagement trends"""
        analytics = self.get_analytics()
        return analytics.get('engagement_trends', {}) if analytics else None
    
    def get_top_churn_drivers(self) -> Optional[List[str]]:
        """Get top churn drivers"""
        insights = self.get_insights()
        return insights.get('top_churn_drivers', []) if insights else None
    
    def get_retention_opportunities(self) -> Optional[List[str]]:
        """Get retention opportunities"""
        insights = self.get_insights()
        return insights.get('retention_opportunities', []) if insights else None
    
    def get_recommended_actions(self) -> Optional[List[str]]:
        """Get recommended actions"""
        insights = self.get_insights()
        return insights.get('recommended_actions', []) if insights else None
    
    def get_high_risk_customers(self) -> Optional[pd.DataFrame]:
        """Get high-risk customers"""
        if self.customer_df is None:
            return None
        
        return self.customer_df[self.customer_df['risk_level'] == 'high'].copy()
    
    def get_medium_risk_customers(self) -> Optional[pd.DataFrame]:
        """Get medium-risk customers"""
        if self.customer_df is None:
            return None
        
        return self.customer_df[self.customer_df['risk_level'] == 'medium'].copy()
    
    def get_low_risk_customers(self) -> Optional[pd.DataFrame]:
        """Get low-risk customers"""
        if self.customer_df is None:
            return None
        
        return self.customer_df[self.customer_df['risk_level'] == 'low'].copy()
    
    def get_customers_by_revenue_tier(self, tier: str) -> Optional[pd.DataFrame]:
        """Get customers by revenue tier"""
        if self.customer_df is None:
            return None
        
        return self.customer_df[self.customer_df['revenue_tier'] == tier].copy()
    
    def get_priority_customers(self, limit: int = 10) -> Optional[pd.DataFrame]:
        """Get top priority customers"""
        if self.customer_df is None:
            return None
        
        return self.customer_df.nlargest(limit, 'priority_score').copy()
    
    def is_data_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.analysis_data is not None and self.customer_df is not None
