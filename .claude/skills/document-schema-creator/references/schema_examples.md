# Document Schema Examples

This reference provides examples of well-structured document schemas from the InfoTransform system.

## Pattern 1: Flat Schema (Single Instance Extraction)

Use flat schemas when extracting ONE set of information from a document.

### Example: Document Metadata

```python
class DocumentMetadata(BaseModel):
    """Document metadata extraction"""
    title: str = Field(description="Main title of the document")
    author: Optional[str] = Field(description="Author if mentioned")
    summary: str = Field(description="Brief summary of content")
    word_count: int = Field(description="Approximate word count", ge=0)
    key_topics: List[str] = Field(description="3-5 main topics", min_length=1, max_length=5)

# Register directly in AVAILABLE_MODELS
AVAILABLE_MODELS = {
    "document_metadata": DocumentMetadata,
}
```

**When to use**: Document summaries, metadata extraction, compliance checks, single-entity extraction.

### Example: Content Compliance Check

```python
class Category(str, Enum):
    violence = "violence"
    sexual = "sexual"
    self_harm = "self_harm"

class ContentCompliance_response(BaseModel):
    """Content compliance analysis for policy violations"""
    is_violating: bool = Field(description="Whether content violates policies")
    category: Optional[Category] = Field(description="Violation category if applicable")
    explanation_if_violating: Optional[str] = Field(description="Explanation of violation")

# Register in AVAILABLE_MODELS
AVAILABLE_MODELS = {
    "content_compliance": ContentCompliance_response,
}
```

## Pattern 2: Nested Schema (Multiple Instance Extraction)

Use nested schemas when extracting MULTIPLE instances from a document.

### Example: Report Summary (Simple Nested)

```python
class report_item(BaseModel):
    """data model for report item"""
    title: str = Field(..., description="title of the content")
    summary: str = Field(..., description="summary of the content")

class report_response(BaseModel):
    item: List[report_item]
    model_config = ConfigDict(critical_fields=[])

# Register the response wrapper in AVAILABLE_MODELS
AVAILABLE_MODELS = {
    "report_summary": report_response,  # Use _response, not _item
}
```

**When to use**: Multiple reports, multiple invoices, multiple audit issues, multiple contracts.

### Example: IT Audit Issues (Complex Nested with Sub-items)

```python
class Recommendation(BaseModel):
    """A specific recommendation with management response"""
    recommendation: str = Field(..., description="Actionable recommendation for addressing the audit issue.")
    management_comment: str = Field(..., description="Management's response to the recommendation.")

class Issue(BaseModel):
    """Represents a single audit issue/risk/finding"""
    agency: str = Field(..., description="Agency or ministry where the issue was identified.")
    category: str = Field(..., description="Category or type of audit issue (e.g., Procurement, Data Security).")
    reference: str = Field(..., description="Unique identifier for the issue (e.g., Finding 1, Finding 2).")
    title: str = Field(..., description="Concise, descriptive title of the issue.")
    description: str = Field(..., description="Detailed description of the audit finding.")
    risk_statement: str = Field(..., description="Potential negative consequences if not addressed.")
    root_cause: str = Field(..., description="Underlying reason or cause of the issue.")
    root_cause_category: Literal["People", "Process", "System"] = Field(..., description="Categorization of the root cause.")
    recommendations: List[Recommendation] = Field(..., description="List of recommendations and management comments.")

class ITAudit_response(BaseModel):
    """The complete structured response, containing all extracted issues"""
    item: List[Issue] = Field(..., description="List of all individual audit issues extracted from the report.")
    model_config = ConfigDict(extra="forbid")

# Register in AVAILABLE_MODELS
AVAILABLE_MODELS = {
    "it_audit": ITAudit_response,
}
```

**Key points for nested schemas**:
- Always use `item: List[YourItemClass]` as the field name in the response wrapper
- Always include `model_config = ConfigDict(critical_fields=[])` in response wrappers
- Register the `_response` class, not the `_item` class
- Sub-items (like Recommendation) can be nested within items (like Issue)

## Pattern 3: OpenAI Compatible Schemas

Use `OpenAICompatibleBaseModel` for better compatibility with OpenAI API constraints.

```python
class ValuationReportItem(OpenAICompatibleBaseModel):
    """Data model for Valuation Report extraction"""
    company_name: str = Field(None, description="Full Name of the company being valuated")
    valuation_company: str = Field(None, description="Name of the valuation company")
    currency: str = Field(..., description="currency used for this report, output in ISO4217 format")
    fair_value: float = Field(..., description="Fair value/concluded value. Express as full numbers without abbreviations.")

    @field_validator("currency")
    def validate_currency_format(cls, v):
        if v is None:
            return "Not Specified"
        return v.upper()

class ValuationReport_response(OpenAICompatibleBaseModel):
    item: List[ValuationReportItem]

# Register in AVAILABLE_MODELS
AVAILABLE_MODELS = {
    "valuation_report": ValuationReport_response,
}
```

**When to use**: When working with OpenAI API that has strict schema requirements.

## Field Type Best Practices

### String Fields
```python
title: str = Field(..., description="Concise title")
summary: str = Field(..., min_length=1, strip_whitespace=True, description="Detailed summary")
```

### Optional Fields
```python
author: Optional[str] = Field(None, description="Author if mentioned")
subtitle: Optional[str] = Field(None, description="Optional subtitle for context")
```

### Numeric Fields with Validation
```python
amount: float = Field(..., description="Amount in full numbers")
score: int = Field(ge=0, le=10, description="Score between 0-10")
word_count: int = Field(ge=0, description="Word count, must be non-negative")
```

### Date Fields
```python
contract_date: str = Field(..., description="Date in YYYY-MM-DD format")
report_date: date = Field(..., description="Date of the report")
```

### Enum/Literal Fields
```python
asset_type: Literal["Retail", "Office", "Industrial"] = Field(..., description="Type of asset")
root_cause_category: Literal["People", "Process", "System"] = Field(..., description="Root cause category")
```

### List Fields
```python
attendees: List[str] = Field(..., description="List of attendees with roles")
key_topics: List[str] = Field(min_length=1, max_length=5, description="3-5 main topics")
```

### Nested List Fields
```python
recommendations: List[Recommendation] = Field(..., description="List of recommendations")
comparables: List[Comparables] = Field(default_factory=list, description="List of comparable properties")
```

## Field Validators

Custom validators ensure data quality:

```python
@field_validator("discount_rate_percentage", "capitalisation_rate_percentage")
def validate_percentage_format(cls, v):
    if v is None:
        return "Not Specified"
    v_str = str(v).strip()
    if v_str.lower() in {"not specified", "n/a", ""}:
        return "Not Specified"
    if not v_str.endswith("%"):
        return f"{v_str}%"
    return v_str
```

## Common Patterns by Use Case

### Invoice/Contract Schemas
- Use nested patterns for multiple line items
- Include currency, dates, amounts, parties involved
- Consider payment terms, credit terms, conditions

### Audit/Compliance Schemas
- Nested patterns for multiple issues/findings
- Include categories, references, descriptions
- Add risk statements, recommendations, management responses

### Financial Statement Schemas
- Flat pattern for single period statements
- Nested pattern for multi-period or multi-entity
- Use float for all monetary values

### Legal Document Schemas
- Include parties, dates, terms, conditions
- Consider using Optional fields for clauses that may not exist
- Add validation for date formats

### Meeting/Report Schemas
- Nested patterns for multiple items/topics
- Include metadata: dates, attendees, titles
- Summary and detail fields for each item
