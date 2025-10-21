"""
CSV Validation Service - Validates CSV uploads to prevent DoS attacks
"""
import pandas as pd
import io
from typing import Tuple, Optional
import logging

from config.config import config

logger = logging.getLogger(__name__)


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors"""
    pass


class CSVValidator:
    """Validates CSV files for size, rows, and columns limits"""
    
    def __init__(self):
        """Initialize validator with config limits"""
        self.max_file_size_bytes = config.CSV_MAX_FILE_SIZE_MB * 1024 * 1024
        self.max_rows = config.CSV_MAX_ROWS
        self.max_columns = config.CSV_MAX_COLUMNS
        self.min_rows = config.CSV_MIN_ROWS
    
    def validate_file_size(self, file_content: bytes) -> None:
        """
        Validate file size
        
        Args:
            file_content: File content in bytes
            
        Raises:
            CSVValidationError: If file exceeds size limit
        """
        file_size = len(file_content)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size > self.max_file_size_bytes:
            raise CSVValidationError(
                f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size "
                f"({config.CSV_MAX_FILE_SIZE_MB} MB)"
            )
        
        logger.info(f"File size validation passed: {file_size_mb:.2f} MB")
    
    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate DataFrame dimensions and apply free tier limits
        
        Args:
            df: DataFrame to validate
            
        Returns:
            DataFrame (potentially limited to max_rows for free tier)
            
        Raises:
            CSVValidationError: If DataFrame has critical validation issues
        """
        num_rows = len(df)
        num_columns = len(df.columns)
        original_row_count = num_rows
        
        # Check minimum rows
        if num_rows < self.min_rows:
            raise CSVValidationError(
                f"CSV has {num_rows} rows, minimum required is {self.min_rows}"
            )
        
        # Check maximum columns (hard limit - must reject)
        if num_columns > self.max_columns:
            raise CSVValidationError(
                f"CSV has {num_columns} columns, maximum allowed is {self.max_columns}"
            )
        
        # FREE TIER: Limit rows (soft limit - truncate instead of reject)
        if num_rows > self.max_rows:
            logger.info(f"CSV has {num_rows} rows, limiting to first {self.max_rows} rows (free tier)")
            df = df.head(self.max_rows)
            num_rows = len(df)
        
        logger.info(f"DataFrame validation passed: {num_rows:,} rows × {num_columns} columns")
        
        # Return the potentially limited DataFrame
        return df
    
    def validate_csv(self, file_content: bytes) -> Tuple[pd.DataFrame, dict]:
        """
        Validate CSV file and return DataFrame with metadata
        
        Args:
            file_content: CSV file content in bytes
            
        Returns:
            Tuple of (DataFrame, metadata dict)
            Metadata includes both original and processed row counts
            
        Raises:
            CSVValidationError: If validation fails
        """
        try:
            # Step 1: Validate file size
            self.validate_file_size(file_content)
            
            # Step 2: Read CSV
            try:
                df = pd.read_csv(io.BytesIO(file_content))
            except Exception as e:
                raise CSVValidationError(f"Failed to parse CSV file: {str(e)}")
            
            # Store original row count before any limiting
            original_row_count = len(df)
            
            # Step 3: Validate DataFrame dimensions (may limit rows for free tier)
            df = self.validate_dataframe(df)
            
            # Create metadata
            metadata = {
                "file_size_bytes": len(file_content),
                "file_size_mb": len(file_content) / (1024 * 1024),
                "num_rows": len(df),  # After limiting
                "original_row_count": original_row_count,  # Before limiting
                "num_columns": len(df.columns),
                "columns": list(df.columns),
                "validation_status": "passed",
                "was_limited": original_row_count > len(df)
            }
            
            logger.info(f"CSV validation successful: {metadata}")
            return df, metadata
            
        except CSVValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during CSV validation: {str(e)}")
            raise CSVValidationError(f"CSV validation failed: {str(e)}")
    
    def validate_uploaded_file(self, uploaded_file) -> Tuple[pd.DataFrame, dict]:
        """
        Validate Streamlit uploaded file and apply free tier limits
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (DataFrame, metadata dict)
            DataFrame may be limited to max_rows for free tier
            Metadata includes both original and processed row counts
            
        Raises:
            CSVValidationError: If validation fails
        """
        try:
            # Get file content
            file_content = uploaded_file.getvalue()
            
            # Validate (this may limit rows for free tier)
            df, metadata = self.validate_csv(file_content)
            
            # Add filename to metadata
            metadata["filename"] = uploaded_file.name
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error validating uploaded file: {str(e)}")
            raise
    
    def get_limits_info(self) -> dict:
        """Get current validation limits as dict"""
        return {
            "max_file_size_mb": config.CSV_MAX_FILE_SIZE_MB,
            "max_rows": config.CSV_MAX_ROWS,
            "max_columns": config.CSV_MAX_COLUMNS,
            "min_rows": config.CSV_MIN_ROWS
        }


# Create singleton instance
csv_validator = CSVValidator()

