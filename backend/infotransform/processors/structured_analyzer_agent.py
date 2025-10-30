"""
Structured Analyzer for extracting structured data from markdown content using Pydantic AI
"""

from typing import Any, Type, Dict, Optional
from enum import Enum
import logging

from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from infotransform.config import config
from infotransform.utils.error_formatter import (
    format_validation_errors,
    create_user_friendly_error_message,
)

# Import from the correct path - add project root to path
import sys
from pathlib import Path

# Go up from structured_analyzer_agent.py -> processors -> infotransform -> backend -> project_root
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.document_schemas import AVAILABLE_MODELS  # noqa: E402

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
        ai_model_name: Optional[str] = None,
    ) -> Agent:
        """Get or create a Pydantic AI agent for the specified model"""
        # Use provided AI model or default
        if ai_model_name is None:
            ai_model_name = self.config.get(
                "ai_pipeline.structured_analysis.default_model", "azure.gpt-4o"
            )

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
        agent = Agent(model, output_type=model_class, system_prompt=system_prompt)

        # Cache the agent
        self.agents[cache_key] = agent

        return agent

    async def analyze_content_stream(
        self,
        content: str,
        model_key: str,
        custom_instructions: Optional[str] = None,
        ai_model: Optional[str] = None,
        file_path: Optional[str] = None,
        is_image: bool = False,
    ):
        """
        Analyze markdown content or image and stream partial structured data updates

        Args:
            content: Markdown content to analyze (None for images)
            model_key: Key of the document schema to use
            custom_instructions: Optional custom instructions
            ai_model: Optional AI model override
            file_path: Path to original file (for images)
            is_image: Flag indicating if this is an image file

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
            model_name = ai_model or self.config.get(
                "ai_pipeline.structured_analysis.default_model"
            )
            model_config = self.config.get_ai_model_config(model_name)

            # Build model settings with only temperature and seed
            model_settings = {}
            if "temperature" in model_config:
                model_settings["temperature"] = model_config["temperature"]
            if "seed" in model_config:
                model_settings["seed"] = model_config["seed"]

            # Prepare prompt - handle images vs. text content
            model_description = (
                model_class.__doc__ or f"Analysis using {model_class.__name__}"
            )

            if is_image and file_path:
                # For images: prepare prompt with image content
                from pydantic_ai.messages import BinaryImage
                import os
                import aiofiles

                # Read image file asynchronously (non-blocking)
                async with aiofiles.open(file_path, "rb") as f:
                    image_data = await f.read()

                # Determine media type from extension
                ext = os.path.splitext(file_path)[1].lower()
                media_type_map = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".bmp": "image/bmp",
                    ".webp": "image/webp",
                }
                media_type = media_type_map.get(ext, "image/jpeg")

                # Create BinaryImage
                binary_image = BinaryImage(data=image_data, media_type=media_type)

                # Create prompt with both text and image
                text_prompt = f"""Analyze this image and extract structured information.

Task: {model_description}

You should extract information according to the {model_class.__name__} schema.
{custom_instructions if custom_instructions else ""}

Please analyze the image thoroughly and extract all relevant information.
"""
                # Pydantic AI accepts a list of UserContent items
                prompt = [text_prompt, binary_image]
            else:
                # For text content: use template as before
                prompt_template = self.config.get_prompt_template("analysis_prompt")
                if prompt_template:
                    prompt = prompt_template.format(
                        model_description=model_description,
                        model_name=model_class.__name__,
                        custom_instructions=custom_instructions
                        if custom_instructions
                        else "",
                        content=content,
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
            async with agent.run_stream(
                prompt, model_settings=model_settings
            ) as result:
                async for message, last in result.stream_structured(debounce_by=0.01):
                    if last:
                        # Final validated result
                        validated_result = await result.validate_structured_output(
                            message
                        )
                        result_dict = validated_result.model_dump(mode="json")
                        result_dict = self._convert_enums_to_strings(result_dict)

                        # Capture usage information
                        usage = result.usage()
                        usage_dict = {
                            "input_tokens": usage.input_tokens or 0,
                            "output_tokens": usage.output_tokens or 0,
                            "cache_read_tokens": usage.cache_read_tokens or 0,
                            "cache_write_tokens": usage.cache_write_tokens or 0,
                            "total_tokens": (usage.input_tokens or 0)
                            + (usage.output_tokens or 0),
                            "requests": usage.requests or 0,
                        }

                        yield {
                            "success": True,
                            "model_used": model_class.__name__,
                            "ai_model_used": model_name,
                            "result": result_dict,
                            "usage": usage_dict,
                            "final": True,
                        }
                    else:
                        # Partial result - may have validation errors
                        try:
                            partial_result = await result.partial_structured_output(
                                message
                            )
                            if partial_result:
                                result_dict = partial_result.model_dump(mode="json")
                                result_dict = self._convert_enums_to_strings(
                                    result_dict
                                )

                                yield {
                                    "success": True,
                                    "model_used": model_class.__name__,
                                    "ai_model_used": model_name,
                                    "result": result_dict,
                                    "final": False,
                                }
                        except Exception as e:
                            # Skip partial results that fail validation
                            logger.debug(f"Partial result validation failed: {e}")
                            continue

        except ValidationError as e:
            # Handle Pydantic validation errors with user-friendly formatting
            logger.error(
                f"Validation error in structured analysis stream for {model_key}: {e}"
            )
            logger.debug(f"Validation error details: {e.errors()}")

            # Format errors for user display
            formatted = format_validation_errors(e.errors(), max_errors=10)
            user_message = create_user_friendly_error_message(e.errors(), model_key)

            yield {
                "success": False,
                "error": user_message,
                "error_type": "validation_error",
                "validation_errors": formatted["formatted_errors"],
                "error_summary": formatted["summary"],
                "raw_error": str(e),
                "model_used": model_key,
                "ai_model_used": ai_model
                or self.config.get("ai_pipeline.structured_analysis.default_model"),
                "final": True,
            }

        except Exception as e:
            logger.error(f"Error in structured analysis stream: {e}")
            yield {
                "success": False,
                "error": str(e),
                "error_type": "general_error",
                "model_used": model_key,
                "ai_model_used": ai_model
                or self.config.get("ai_pipeline.structured_analysis.default_model"),
                "final": True,
            }

    async def analyze_content(
        self,
        content: str,
        model_key: str,
        custom_instructions: Optional[str] = None,
        ai_model: Optional[str] = None,
        file_path: Optional[str] = None,
        is_image: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze markdown content or image file and extract structured data

        Args:
            content: Markdown content to analyze (None for images)
            model_key: Key of the document schema to use
            custom_instructions: Optional custom instructions
            ai_model: Optional AI model override
            file_path: Path to original file (for images)
            is_image: Flag indicating if this is an image file

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
            model_name = ai_model or self.config.get(
                "ai_pipeline.structured_analysis.default_model"
            )
            model_config = self.config.get_ai_model_config(model_name)

            # Build model settings with only temperature and seed
            model_settings = {}
            if "temperature" in model_config:
                model_settings["temperature"] = model_config["temperature"]
            if "seed" in model_config:
                model_settings["seed"] = model_config["seed"]

            # Prepare prompt - handle images vs. text content
            model_description = (
                model_class.__doc__ or f"Analysis using {model_class.__name__}"
            )

            if is_image and file_path:
                # For images: prepare prompt with image content
                from pydantic_ai.messages import BinaryImage
                import os
                import aiofiles

                # Read image file asynchronously (non-blocking)
                async with aiofiles.open(file_path, "rb") as f:
                    image_data = await f.read()

                # Determine media type from extension
                ext = os.path.splitext(file_path)[1].lower()
                media_type_map = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".bmp": "image/bmp",
                    ".webp": "image/webp",
                }
                media_type = media_type_map.get(ext, "image/jpeg")

                # Create BinaryImage
                binary_image = BinaryImage(data=image_data, media_type=media_type)

                # Create prompt with both text and image
                text_prompt = f"""Analyze this image and extract structured information.

Task: {model_description}

You should extract information according to the {model_class.__name__} schema.
{custom_instructions if custom_instructions else ""}

Please analyze the image thoroughly and extract all relevant information.
"""
                # Pydantic AI accepts a list of UserContent items
                prompt = [text_prompt, binary_image]
            else:
                # For text content: use template as before
                prompt_template = self.config.get_prompt_template("analysis_prompt")
                if prompt_template:
                    prompt = prompt_template.format(
                        model_description=model_description,
                        model_name=model_class.__name__,
                        custom_instructions=custom_instructions
                        if custom_instructions
                        else "",
                        content=content,
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
            streaming_enabled = self.config.is_feature_enabled("streaming_responses")

            if streaming_enabled:
                # Streaming mode
                async with agent.run_stream(
                    prompt, model_settings=model_settings
                ) as result:
                    async for message, last in result.stream_structured(
                        debounce_by=0.01
                    ):
                        if last:
                            validated_result = await result.validate_structured_output(
                                message
                            )
                            result_dict = validated_result.model_dump(mode="json")

                            # Convert Enums to strings
                            result_dict = self._convert_enums_to_strings(result_dict)

                            # Capture usage information
                            usage = result.usage()
                            usage_dict = {
                                "input_tokens": usage.input_tokens or 0,
                                "output_tokens": usage.output_tokens or 0,
                                "cache_read_tokens": usage.cache_read_tokens or 0,
                                "cache_write_tokens": usage.cache_write_tokens or 0,
                                "total_tokens": (usage.input_tokens or 0)
                                + (usage.output_tokens or 0),
                                "requests": usage.requests or 0,
                            }

                            return {
                                "success": True,
                                "model_used": model_class.__name__,
                                "ai_model_used": model_name,
                                "result": result_dict,
                                "usage": usage_dict,
                            }
            else:
                # Non-streaming mode
                result = await agent.run(prompt, model_settings=model_settings)
                result_dict = result.output.model_dump(mode="json")

                # Convert Enums to strings
                result_dict = self._convert_enums_to_strings(result_dict)

                # Capture usage information
                usage = result.usage()
                usage_dict = {
                    "input_tokens": usage.input_tokens or 0,
                    "output_tokens": usage.output_tokens or 0,
                    "cache_read_tokens": usage.cache_read_tokens or 0,
                    "cache_write_tokens": usage.cache_write_tokens or 0,
                    "total_tokens": (usage.input_tokens or 0)
                    + (usage.output_tokens or 0),
                    "requests": usage.requests or 0,
                }

                return {
                    "success": True,
                    "model_used": model_class.__name__,
                    "ai_model_used": model_name,
                    "result": result_dict,
                    "usage": usage_dict,
                }

        except ValidationError as e:
            # Handle Pydantic validation errors with user-friendly formatting
            logger.error(
                f"Validation error in structured analysis for {model_key}: {e}"
            )
            logger.debug(f"Validation error details: {e.errors()}")

            # Format errors for user display
            formatted = format_validation_errors(e.errors(), max_errors=10)
            user_message = create_user_friendly_error_message(e.errors(), model_key)

            return {
                "success": False,
                "error": user_message,
                "error_type": "validation_error",
                "validation_errors": formatted["formatted_errors"],
                "error_summary": formatted["summary"],
                "raw_error": str(e),
                "model_used": model_key,
                "ai_model_used": ai_model
                or self.config.get("ai_pipeline.structured_analysis.default_model"),
            }

        except Exception as e:
            logger.error(f"Error in structured analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error",
                "model_used": model_key,
                "ai_model_used": ai_model
                or self.config.get("ai_pipeline.structured_analysis.default_model"),
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

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available document schemas with detailed field info"""
        import typing
        from typing import get_origin, get_args

        models_info = {}

        for key, model_class in AVAILABLE_MODELS.items():
            # Check if this is a response wrapper model with just an 'item' field
            actual_model_class = model_class
            model_fields = model_class.model_fields

            if len(model_fields) == 1 and "item" in model_fields:
                # This looks like a wrapper response model
                item_field = model_fields["item"]

                # Check if the item field is a List type
                if hasattr(item_field.annotation, "__origin__"):
                    origin = get_origin(item_field.annotation)
                    if origin is list or (
                        hasattr(typing, "List") and origin is typing.List
                    ):
                        # Get the actual model class from the List type
                        args = get_args(item_field.annotation)
                        if args and hasattr(args[0], "model_fields"):
                            actual_model_class = args[0]
                            model_fields = actual_model_class.model_fields

            # Now extract fields from the actual model
            fields_info = {}
            for field_name, field in model_fields.items():
                # Get clean field type
                field_type = str(field.annotation).replace("typing.", "")

                # Extract constraints if it's a list field
                constraints = None
                if hasattr(field, "metadata"):
                    for meta in field.metadata:
                        if hasattr(meta, "min_length") or hasattr(meta, "max_length"):
                            constraints = f"{getattr(meta, 'min_length', 0)}-{getattr(meta, 'max_length', 'unlimited')} items"

                fields_info[field_name] = {
                    "type": field_type,
                    "description": field.description or "",
                    "required": field.is_required(),
                    "constraints": constraints,
                }

            # Use the original model class name for the response but actual model for description
            models_info[key] = {
                "name": model_class.__name__,
                "description": actual_model_class.__doc__
                or model_class.__doc__
                or "No description",
                "fields": fields_info,
            }

        return models_info

    def get_available_ai_models(self) -> Dict[str, Any]:
        """Get available AI models for structured analysis only"""
        # Get available models from config (only for structured analysis)
        available_models = self.config.get(
            "ai_pipeline.structured_analysis.available_models", {}
        )
        default_model = self.config.get("ai_pipeline.structured_analysis.default_model")

        # Create models dict with display names for frontend
        models = {}

        for model_id, model_config in available_models.items():
            # Use display_name for the key that frontend shows
            display_name = model_config.get("display_name", model_id)
            models[model_id] = {
                "display_name": display_name,
                "temperature": model_config.get("temperature", 0.7),
                "seed": model_config.get("seed", 42),
                "streaming_enabled": self.config.get(
                    "ai_pipeline.structured_analysis.streaming.enabled", False
                ),
            }

        return {"default_model": default_model, "models": models}
