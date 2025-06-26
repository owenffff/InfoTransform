"""
analysis_schemas.py

Schema definitions for structured data analysis models.
These Pydantic models define the structure of data extracted by the analysis system.

HOW TO ADD A NEW ANALYSIS MODEL:
1. Create a new Pydantic model class below (inherit from BaseModel)
2. Add descriptive docstring and Field descriptions
3. Register it in AVAILABLE_MODELS at the bottom of this file
   Example: "your_model_key": YourModelClass
   - Choose a descriptive key (this is what users will see)
   - The key can be different from the class name


Note: The key you use in AVAILABLE_MODELS will be the model_key users select in the UI.
"""


from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Category(str, Enum):
    violence = "violence"
    sexual = "sexual" 
    self_harm = "self_harm"


class ContentCompliance_response(BaseModel):
    """Content compliance analysis for policy violations"""
    is_violating: bool = Field(description="Whether content violates policies")
    category: Optional[Category] = Field(description="Violation category if applicable")
    explanation_if_violating: Optional[str] = Field(description="Explanation of violation")


class DocumentMetadata(BaseModel):
    """Document metadata extraction"""
    title: str = Field(description="Main title of the document")
    author: Optional[str] = Field(description="Author if mentioned")
    summary: str = Field(description="Brief summary of content")
    word_count: int = Field(description="Approximate word count", ge=0)
    key_topics: List[str] = Field(description="3-5 main topics", min_length=1, max_length=5)


class TechnicalDocAnalysis(BaseModel):
    """Technical documentation analysis"""
    programming_languages: List[str] = Field(description="Programming languages mentioned")
    code_snippets_count: int = Field(description="Number of code blocks", ge=0)
    has_installation_guide: bool = Field(description="Whether it has installation instructions")
    has_api_reference: bool = Field(description="Whether it contains API documentation")
    complexity_level: str = Field(description="Beginner, Intermediate, or Advanced")
    external_links_count: int = Field(description="Number of external links", ge=0)


# Model registry - just the models
AVAILABLE_MODELS = {
    #"UI displayed name": actual pydantic model name,
    "content_compliance": ContentCompliance_response,   
    "document_metadata": DocumentMetadata,
    "technical_analysis": TechnicalDocAnalysis,
}
