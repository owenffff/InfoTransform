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

# Import from the correct path - add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from config.analysis_schemas import AVAILABLE_MODELS

logger = logging.getLogger(__name__)


class StructuredAnalyzerAgent:
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
            ai_model_name = self.config.get('ai_pipeline.structured_analysis.default_model', 'azure.gpt-4o')
        
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
    
    async def analyze_content_stream(
        self,
        content: str,
        model_key: str,
        custom_instructions: Optional[str] = None,
        ai_model: Optional[str] = None
    ):
        """
        Analyze markdown content and stream partial structured data updates
        
        Args:
            content: Markdown content to analyze
            model_key: Key of the document schema to use
            custom_instructions: Optional custom instructions
            ai_model: Optional AI model override
            
        Yields:
            Tuples of (partial_result, is_final) where partial_result is the current
            state of extracted fields and is_final indicates if this is the complete result
        """
        try:
            # Validate model key
            if model_key not in AVAILABLE_MODELS:
                raise ValueError(f"Invalid model key: {model_key}")
            
            model_class = AVAILABLE_MODELS[model_key]
            
            # Get or create agent
            agent = self._get_or_create_agent(model_class, model_key, ai_model)
            
            # Get model configuration and extract only temperature and seed
            model_name = ai_model or self.config.get('ai_pipeline.structured_analysis.default_model')
            model_config = self.config.get_ai_model_config(model_name)
            
            # Build model settings with only temperature and seed
            model_settings = {}
            if 'temperature' in model_config:
                model_settings['temperature'] = model_config['temperature']
            if 'seed' in model_config:
                model_settings['seed'] = model_config['seed']
            
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
            
            # Stream partial results
            async with agent.run_stream(prompt, model_settings=model_settings) as result:
                async for message, last in result.stream_structured(debounce_by=0.01):
                    if last:
                        # Final validated result
                        validated_result = await result.validate_structured_output(message)
                        result_dict = validated_result.model_dump()
                        result_dict = self._convert_enums_to_strings(result_dict)
                        
                        yield {
                            'success': True,
                            'model_used': model_class.__name__,
                            'ai_model_used': model_name,
                            'result': result_dict,
                            'final': True
                        }
                    else:
                        # Partial result - may have validation errors
                        try:
                            partial_result = await result.partial_structured_output(message)
                            if partial_result:
                                result_dict = partial_result.model_dump()
                                result_dict = self._convert_enums_to_strings(result_dict)
                                
                                yield {
                                    'success': True,
                                    'model_used': model_class.__name__,
                                    'ai_model_used': model_name,
                                    'result': result_dict,
                                    'final': False
                                }
                        except Exception as e:
                            # Skip partial results that fail validation
                            logger.debug(f"Partial result validation failed: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error in structured analysis stream: {e}")
            yield {
                'success': False,
                'error': str(e),
                'model_used': model_key,
                'ai_model_used': ai_model or self.config.get('ai_pipeline.structured_analysis.default_model'),
                'final': True
            }
    
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
            model_key: Key of the document schema to use
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
            
            
            # Get or create agent
            agent = self._get_or_create_agent(model_class, model_key, ai_model)
            
            # Get model configuration and extract only temperature and seed
            model_name = ai_model or self.config.get('ai_pipeline.structured_analysis.default_model')
            model_config = self.config.get_ai_model_config(model_name)
            
            # Build model settings with only temperature and seed
            model_settings = {}
            if 'temperature' in model_config:
                model_settings['temperature'] = model_config['temperature']
            if 'seed' in model_config:
                model_settings['seed'] = model_config['seed']
            
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
                async with agent.run_stream(prompt, model_settings=model_settings) as result:
                    async for message, last in result.stream_structured(debounce_by=0.01):
                        if last:
                            validated_result = await result.validate_structured_output(message)
                            result_dict = validated_result.model_dump()
                            
                            # Convert Enums to strings
                            result_dict = self._convert_enums_to_strings(result_dict)
                            
                            return {
                                'success': True,
                                'model_used': model_class.__name__,
                                'ai_model_used': model_name,
                                'result': result_dict
                            }
            else:
                # Non-streaming mode
                result = await agent.run(prompt, model_settings=model_settings)
                result_dict = result.output.model_dump()
                
                # Convert Enums to strings
                result_dict = self._convert_enums_to_strings(result_dict)
                
                return {
                    'success': True,
                    'model_used': model_class.__name__,
                    'ai_model_used': model_name,
                    'result': result_dict
                }
                
        except Exception as e:
            logger.error(f"Error in structured analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_used': model_key,
                'ai_model_used': ai_model or self.config.get('ai_pipeline.structured_analysis.default_model')
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
            model_key: Key of the document schema to use
            custom_instructions: Optional custom instructions
            ai_model: Optional AI model override
            
        Returns:
            List of analysis results
        """
        # Get max concurrent analyses from config
        max_concurrent = self.config.get('processing.analysis.max_concurrent', 5)
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
        
        # Set timeout for batch analysis from performance config
        batch_timeout = float(self.config.get_performance(
            'ai_processing.timeout_per_batch', 300
        ))
        
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
        """Get information about available document schemas with detailed field info"""
        import typing
        from typing import get_origin, get_args
        
        models_info = {}
        
        for key, model_class in AVAILABLE_MODELS.items():
            # Check if this is a response wrapper model with just an 'item' field
            actual_model_class = model_class
            model_fields = model_class.model_fields
            
            if len(model_fields) == 1 and 'item' in model_fields:
                # This looks like a wrapper response model
                item_field = model_fields['item']
                
                # Check if the item field is a List type
                if hasattr(item_field.annotation, '__origin__'):
                    origin = get_origin(item_field.annotation)
                    if origin is list or (hasattr(typing, 'List') and origin is typing.List):
                        # Get the actual model class from the List type
                        args = get_args(item_field.annotation)
                        if args and hasattr(args[0], 'model_fields'):
                            actual_model_class = args[0]
                            model_fields = actual_model_class.model_fields
            
            # Now extract fields from the actual model
            fields_info = {}
            for field_name, field in model_fields.items():
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
            
            # Use the original model class name for the response but actual model for description
            models_info[key] = {
                "name": model_class.__name__,
                "description": actual_model_class.__doc__ or model_class.__doc__ or "No description",
                "fields": fields_info
            }
        
        return models_info
    
    def get_available_ai_models(self) -> Dict[str, Any]:
        """Get available AI models for structured analysis only"""
        # Get available models from config (only for structured analysis)
        available_models = self.config.get('ai_pipeline.structured_analysis.available_models', {})
        default_model = self.config.get('ai_pipeline.structured_analysis.default_model')
        
        # Create models dict with display names for frontend
        models = {}
        
        for model_id, model_config in available_models.items():
            # Use display_name for the key that frontend shows
            display_name = model_config.get('display_name', model_id)
            models[model_id] = {
                "display_name": display_name,
                "temperature": model_config.get('temperature', 0.7),
                "seed": model_config.get('seed', 42),
                "streaming_enabled": self.config.get('ai_pipeline.structured_analysis.streaming.enabled', False)
            }
        
        return {
            "default_model": default_model,
            "models": models
        }
