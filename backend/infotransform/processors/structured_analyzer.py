"""
Structured Analyzer for extracting structured data from markdown content using Pydantic AI
"""

import asyncio
from typing import Any, Type, Dict, Optional, List
from enum import Enum
import logging

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from infotransform.config import config
from config.analysis_schemas import AVAILABLE_MODELS
from infotransform.utils.token_counter import log_token_count

logger = logging.getLogger(__name__)


class StructuredAnalyzer:
    """Analyzes markdown content and extracts structured data using Pydantic AI"""
    
    def __init__(self):
        """Initialize the structured analyzer"""
        self.config = config
        self.agents = {}  # Cache for agents by model type
    
    def _get_or_create_agent(
        self, 
        model_class: Type[BaseModel], 
        model_key: str,
        ai_model_name: Optional[str] = None
    ) -> Agent:
        """Get or create a Pydantic AI agent for the specified model"""
        # Use provided AI model or default
        if ai_model_name is None:
            ai_model_name = self.config.get('models.ai_models.default_model', 'gpt-4o-mini')
        
        # Create cache key
        cache_key = f"{model_key}_{ai_model_name}"
        
        # Return cached agent if exists
        if cache_key in self.agents:
            return self.agents[cache_key]
        
        # Initialize AI model - pass model name directly to OpenAIModel
        model = OpenAIModel(ai_model_name)
        
        # Get system prompt
        system_prompt = self.config.get_analysis_prompt(model_key)
        
        # Create agent
        agent = Agent(
            model,
            output_type=model_class,
            system_prompt=system_prompt
        )
        
        # Cache the agent
        self.agents[cache_key] = agent
        
        return agent
    
    async def analyze_content(
        self,
        content: str,
        model_key: str,
        custom_instructions: Optional[str] = None,
        ai_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze markdown content and extract structured data
        
        Args:
            content: Markdown content to analyze
            model_key: Key of the analysis model to use
            custom_instructions: Optional custom instructions
            ai_model: Optional AI model override
            
        Returns:
            Dictionary containing the structured analysis result
        """
        try:
            # Validate model key
            if model_key not in AVAILABLE_MODELS:
                raise ValueError(f"Invalid model key: {model_key}")
            
            model_class = AVAILABLE_MODELS[model_key]
            
            # Log token count for the content
            log_token_count(f"analysis_{model_key}", content)
            
            # Get or create agent
            agent = self._get_or_create_agent(model_class, model_key, ai_model)
            
            # Prepare prompt
            model_description = model_class.__doc__ or f"Analysis using {model_class.__name__}"
            
            prompt_template = self.config.get_prompt_template('analysis_prompt')
            if prompt_template:
                prompt = prompt_template.format(
                    model_description=model_description,
                    model_name=model_class.__name__,
                    custom_instructions=custom_instructions if custom_instructions else "",
                    content=content
                )
            else:
                # Fallback prompt
                prompt = f"""Analyze the following content.

Task: {model_description}

You should extract information according to the {model_class.__name__} schema.
{custom_instructions if custom_instructions else ""}

Content to analyze:

{content}
"""
            
            # Check if streaming is enabled
            streaming_enabled = self.config.is_feature_enabled('streaming_responses')
            
            if streaming_enabled:
                # Streaming mode
                async with agent.run_stream(prompt) as result:
                    async for message, last in result.stream_structured(debounce_by=0.1):
                        if last:
                            validated_result = await result.validate_structured_output(message)
                            result_dict = validated_result.model_dump()
                            
                            # Convert Enums to strings
                            result_dict = self._convert_enums_to_strings(result_dict)
                            
                            return {
                                'success': True,
                                'model_used': model_class.__name__,
                                'ai_model_used': ai_model or self.config.get('models.ai_models.default_model'),
                                'result': result_dict
                            }
            else:
                # Non-streaming mode
                result = await agent.run(prompt)
                result_dict = result.data.model_dump()
                
                # Convert Enums to strings
                result_dict = self._convert_enums_to_strings(result_dict)
                
                return {
                    'success': True,
                    'model_used': model_class.__name__,
                    'ai_model_used': ai_model or self.config.get('models.ai_models.default_model'),
                    'result': result_dict
                }
                
        except Exception as e:
            logger.error(f"Error in structured analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_used': model_key,
                'ai_model_used': ai_model or self.config.get('models.ai_models.default_model')
            }
    
    def _convert_enums_to_strings(self, data: Any) -> Any:
        """Recursively convert Enum values to strings for JSON serialization"""
        if isinstance(data, dict):
            return {k: self._convert_enums_to_strings(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_enums_to_strings(item) for item in data]
        elif isinstance(data, Enum):
            return data.value
        else:
            return data
    
    async def analyze_batch(
        self,
        contents: Dict[str, str],
        model_key: str,
        custom_instructions: Optional[str] = None,
        ai_model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple markdown contents in batch
        
        Args:
            contents: Dictionary mapping filenames to markdown content
            model_key: Key of the analysis model to use
            custom_instructions: Optional custom instructions
            ai_model: Optional AI model override
            
        Returns:
            List of analysis results
        """
        # Get max concurrent analyses from config
        max_concurrent = self.config.get('processing.analysis.max_concurrent_analyses', 5)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_limit(filename: str, content: str) -> Dict[str, Any]:
            async with semaphore:
                result = await self.analyze_content(
                    content, model_key, custom_instructions, ai_model
                )
                result['filename'] = filename
                return result
        
        # Create tasks
        tasks = [
            analyze_with_limit(filename, content)
            for filename, content in contents.items()
        ]
        
        # Set timeout for batch analysis
        batch_timeout = self.config.get('processing.analysis.timeouts.batch', 300)
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=batch_timeout
            )
            return results
        except asyncio.TimeoutError:
            logger.error("Batch analysis timeout")
            raise TimeoutError("Batch analysis timeout")
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available analysis models with detailed field info"""
        models_info = {}
        
        for key, model_class in AVAILABLE_MODELS.items():
            fields_info = {}
            for field_name, field in model_class.model_fields.items():
                # Get clean field type
                field_type = str(field.annotation).replace('typing.', '')
                
                # Extract constraints if it's a list field
                constraints = None
                if hasattr(field, 'metadata'):
                    for meta in field.metadata:
                        if hasattr(meta, 'min_length') or hasattr(meta, 'max_length'):
                            constraints = f"{getattr(meta, 'min_length', 0)}-{getattr(meta, 'max_length', 'unlimited')} items"
                
                fields_info[field_name] = {
                    'type': field_type,
                    'description': field.description or '',
                    'required': field.is_required(),
                    'constraints': constraints
                }
            
            models_info[key] = {
                "name": model_class.__name__,
                "description": model_class.__doc__ or "No description",
                "fields": fields_info
            }
        
        return models_info
    
    def get_available_ai_models(self) -> Dict[str, Any]:
        """Get available AI models and their configurations"""
        models = self.config.get('models.ai_models.models', {})
        return {
            "default_model": self.config.get('models.ai_models.default_model'),
            "models": {
                name: {
                    "temperature": cfg.get('temperature'),
                    "max_tokens": cfg.get('max_tokens'),
                    "streaming_enabled": cfg.get('streaming', {}).get('enabled', False)
                }
                for name, cfg in models.items()
            }
        }
