"""
Base AI Agent Class
Common functionality for all AI agents
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google Generative AI not available: {e}")
    GOOGLE_AI_AVAILABLE = False

from config.config import config


class BaseAIAgent:
    """Base class for AI agents with common functionality"""
    
    _first_init_logged = False
    
    def __init__(self, agent_name: str):
        """
        Initialize base AI agent
        
        Args:
            agent_name: Name of the agent for logging
        """
        self.agent_name = agent_name
        self.model = None
        
        if not GOOGLE_AI_AVAILABLE:
            if not BaseAIAgent._first_init_logged:
                logger.error(f"{agent_name} - Google Generative AI not available")
                BaseAIAgent._first_init_logged = True
            return
        
        try:
            # Configure API
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            if not BaseAIAgent._first_init_logged:
                logger.info(f"{agent_name} initialized successfully")
                BaseAIAgent._first_init_logged = True
                
        except Exception as e:
            logger.error(f"Error initializing {agent_name}: {str(e)}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if agent is available"""
        return self.model is not None and GOOGLE_AI_AVAILABLE
    
    def load_prompt_file(self, filename: str, fallback: str = "") -> str:
        """
        Load prompt from file
        
        Args:
            filename: Filename in resources/prompts/
            fallback: Fallback text if file not found
            
        Returns:
            Prompt text
        """
        try:
            prompt_path = Path("resources/prompts") / filename
            
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.debug(f"{self.agent_name} - Loaded prompt: {filename}")
                return content
            else:
                logger.error(f"{self.agent_name} - Prompt file not found: {filename}")
                return fallback
                
        except Exception as e:
            logger.error(f"{self.agent_name} - Error loading prompt: {str(e)}")
            return fallback
    
    def parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from LLM
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        try:
            # Clean response
            cleaned = response_text.strip()
            
            # Remove markdown formatting
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
            
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            logger.debug(f"{self.agent_name} - JSON parsing successful")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.agent_name} - JSON decode error: {str(e)}")
            logger.error(f"Response preview: {response_text[:500]}...")
            return None
        except Exception as e:
            logger.error(f"{self.agent_name} - Error parsing JSON: {str(e)}")
            return None
    
    def generate_content(self, prompt: str, files: Optional[list] = None) -> Optional[str]:
        """
        Generate content using the model
        
        Args:
            prompt: Prompt text
            files: Optional list of uploaded files
            
        Returns:
            Generated text or None if generation fails
        """
        if not self.model:
            logger.error(f"{self.agent_name} - Model not available")
            return None
        
        try:
            if files:
                response = self.model.generate_content([prompt] + files)
            else:
                response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"{self.agent_name} - Error generating content: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def log_request(self, operation: str, details: Dict[str, Any]):
        """Log AI request details"""
        logger.info(f"{self.agent_name} - {operation} REQUEST")
        for key, value in details.items():
            logger.info(f"  {key}: {value}")
    
    def log_response(self, operation: str, response_length: int):
        """Log AI response details"""
        logger.info(f"{self.agent_name} - {operation} RESPONSE: {response_length} chars")

