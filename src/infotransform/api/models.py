"""
Pydantic models for API requests and responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TransformRequest(BaseModel):
    model_key: str = Field(description="Which analysis model to use")
    custom_instructions: Optional[str] = Field(default="", description="Additional instructions")
    ai_model: Optional[str] = Field(default=None, description="AI model to use (e.g., gpt-4o-mini, gpt-4)")


class TransformBatchRequest(BaseModel):
    model_key: str = Field(description="Which analysis model to use")
    custom_instructions: Optional[str] = Field(default="", description="Additional instructions")
    ai_model: Optional[str] = Field(default=None, description="AI model to use")


class FileTransformResult(BaseModel):
    filename: str
    status: str  # "success", "error"
    markdown_content: Optional[str] = None
    structured_data: Optional[dict] = None
    error: Optional[str] = None


class TransformResponse(BaseModel):
    model_used: str
    ai_model_used: str
    total_files: int
    successful: int
    failed: int
    results: List[FileTransformResult]
    summary: Optional[dict] = None
