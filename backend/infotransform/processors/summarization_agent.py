"""
Summarization Agent for condensing long documents while preserving key data points
"""

import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from infotransform.config import config
from infotransform.utils.token_counter import log_token_count

logger = logging.getLogger(__name__)


class DocumentSummary(BaseModel):
    """Model for document summarization output"""
    summary: str = Field(description="Condensed version of the document preserving all key data points")


class SummarizationAgent:
    """Agent for summarizing long documents before structured analysis"""
    
    def __init__(self):
        """Initialize the summarization agent"""
        self.config = config
        self.agents = {}  # Cache for agents by model
        
        # Get summarization config from new structure
        self.token_threshold = self.config.get('ai_pipeline.summarization.token_threshold', 200000)
        self.summary_temperature = self.config.get('ai_pipeline.summarization.temperature', 0.1)
        self.summarizing_prompt = self.config.get('ai_pipeline.summarization.prompt', '')
        self.summary_model = self.config.get('ai_pipeline.summarization.model', 'vertex_ai.gemini-1.5-pro')
    
    def _get_or_create_agent(self, fields: List[str]) -> Agent:
        """Get or create a Pydantic AI agent for summarization"""
        # Create cache key based on model
        cache_key = self.summary_model
        
        # Return cached agent if exists
        if cache_key in self.agents:
            return self.agents[cache_key]
        
        # Initialize AI model
        model = OpenAIModel(self.summary_model)
        
        # Format the system prompt with fields
        fields_str = ', '.join(fields)
        system_prompt = self.summarizing_prompt.format(fields=fields_str)
        
        # Create agent
        agent = Agent(
            model,
            output_type=DocumentSummary,
            system_prompt=system_prompt
        )
        
        # Cache the agent
        self.agents[cache_key] = agent
        
        return agent
    
    async def summarize_content(
        self,
        content: str,
        fields: List[str],
        filename: str = "document"
    ) -> Dict[str, Any]:
        """
        Summarize markdown content while preserving key data points
        
        Args:
            content: Markdown content to summarize
            fields: List of field names that will be extracted later
            filename: Name of the file being processed
            
        Returns:
            Dictionary containing the summarization result
        """
        try:
            # Log token count for the input
            log_token_count(f"summarization_input_{filename}", content)
            
            # Get or create agent with fields
            agent = self._get_or_create_agent(fields)
            
            # Create the prompt
            prompt = f"""Please summarize the following document content. 
Focus on preserving all information relevant to these fields: {', '.join(fields)}.

Document content:

{content}
"""
            
            # Get model config for temperature
            model_config = self.config.get_ai_model_config(self.summary_model)
            
            # Get model settings (temperature and seed if available)
            model_settings = {}
            if model_config and 'temperature' in model_config:
                model_settings['temperature'] = model_config['temperature']
            if model_config and 'seed' in model_config:
                model_settings['seed'] = model_config['seed']
            
            # Run summarization
            result = await agent.run(prompt, model_settings=model_settings)
            summary_text = result.data.summary
            
            # Log token count for the output
            log_token_count(f"summarization_output_{filename}", summary_text)
            
            return {
                'success': True,
                'summary': summary_text,
                'original_length': len(content),
                'summary_length': len(summary_text),
                'compression_ratio': len(content) / len(summary_text) if len(summary_text) > 0 else 0,
                'model_used': self.summary_model
            }
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_content': content  # Return original on failure
            }
    
    def should_summarize(self, content: str) -> bool:
        """
        Check if content should be summarized based on token count
        
        Args:
            content: The content to check
            
        Returns:
            True if content exceeds token threshold
        """
        try:
            from infotransform.utils.token_counter import count_tokens_quiet
            token_count = count_tokens_quiet(content)
            return token_count > self.token_threshold
        except Exception as e:
            logger.warning(f"Error counting tokens, skipping summarization: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get current summarization configuration"""
        return {
            'token_threshold': self.token_threshold,
            'summary_temperature': self.summary_temperature,
            'summary_model': self.summary_model,
            'prompt_template': self.summarizing_prompt
        }
