"""
Pydantic models for API requests and responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field




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
