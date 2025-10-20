---
name: document-schema-creator
description: Use this skill when adding new document schema models to the InfoTransform system. This skill should be used when the user requests to create schemas for extracting structured data from business documents (invoices, reports, contracts, financial statements, etc.), including schema design, implementation in document_schemas.py, test data creation, and API endpoint testing.
---

# Document Schema Creator

## Overview

Add new Pydantic document schema models to the InfoTransform system for extracting structured data from business documents. This skill guides through schema design, implementation, test data creation, and validation through API testing.

## When to Use This Skill

Invoke this skill when the user requests:
- "Add a new invoice schema to the system"
- "Create a document model for medical records"
- "I need a schema for extracting product information"
- "Build a schema for purchase orders"
- Any request to add a new document extraction schema to InfoTransform

## Core Workflow

Follow these steps sequentially when creating a new document schema:

### Step 1: Understand Requirements and Choose Pattern

First, clarify the extraction requirements with the user to determine the appropriate schema pattern:

**Key Question**: Will the schema extract ONE instance or MULTIPLE instances from documents?

- **ONE instance** → Use **Flat Schema Pattern** (Pattern 1)
  - Examples: Document metadata, overall summary, single compliance check

- **MULTIPLE instances** → Use **Nested Schema Pattern** (Pattern 2)
  - Examples: Multiple reports, multiple invoices, multiple audit issues

**Reference Material**: For detailed examples of both patterns, refer to `references/schema_examples.md` which contains comprehensive examples from the existing codebase.

### Step 2: Design the Schema Structure

Based on the requirements, design the schema fields:

1. **Identify all fields** to extract from the documents
2. **Choose appropriate field types**:
   - `str` for text fields
   - `int` or `float` for numeric values
   - `Optional[type]` for fields that may not be present
   - `List[type]` for multiple values
   - `Literal["option1", "option2"]` for constrained choices
   - `date` or `datetime` for date fields (or use `str` with format description)

3. **Write descriptive Field descriptions** - these help the AI understand what to extract:
   ```python
   title: str = Field(..., description="Concise title of the report")
   amount: float = Field(..., description="Total amount in full numbers without abbreviations")
   ```

4. **Add validation** when needed:
   - Use `ge=0` for non-negative numbers
   - Use `min_length=1` for required strings
   - Use custom `@field_validator` for complex validation

5. **Consider using OpenAICompatibleBaseModel** if OpenAI API compatibility is required

### Step 3: Implement the Schema

Locate and edit the schema file: `/Users/owen/Desktop/dev_projects/InfoTransform/config/document_schemas.py`

**For Flat Schema (Single Instance):**

```python
class YourModelName(BaseModel):
    """Clear description of what this schema extracts"""
    field1: str = Field(..., description="Description of field1")
    field2: Optional[int] = Field(None, description="Description of field2")
    field3: List[str] = Field(..., description="Description of field3")

# Register in AVAILABLE_MODELS at the bottom of the file
AVAILABLE_MODELS = {
    "your_model_key": YourModelName,
}
```

**For Nested Schema (Multiple Instances):**

```python
class YourModelItem(BaseModel):
    """Description of a single item"""
    field1: str = Field(..., description="Description of field1")
    field2: str = Field(..., description="Description of field2")

class YourModel_response(BaseModel):
    """Response wrapper for multiple items"""
    item: List[YourModelItem]  # MUST be named 'item'
    model_config = ConfigDict(critical_fields=[])

# Register the response wrapper in AVAILABLE_MODELS
AVAILABLE_MODELS = {
    "your_model_key": YourModel_response,  # Use _response, not _item
}
```

**Naming Conventions:**
- Item Classes: `YourModelItem` (e.g., `InvoiceItem`, `ReportItem`)
- Response Wrappers: `YourModel_response` (e.g., `Invoice_response`, `Report_response`)
- Model Keys: lowercase with underscores (e.g., `"invoice_schema"`, `"report_summary"`)

**Important**: Always add the import if using new types:
```python
from typing import Optional, List, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, field_validator
```

### Step 4: Create Test Data

Create markdown test files in `/Users/owen/Desktop/dev_projects/InfoTransform/backend/test_data/` that align with the schema structure.

**Test Data Requirements:**

1. **File naming**: Use descriptive names like `invoice_test.md`, `report_test.md`

2. **Content alignment**: Ensure the markdown content contains all fields defined in the schema

3. **For nested schemas**: Include MULTIPLE instances in the test data to properly test the list extraction
   - Example: If creating a report schema, include 2-3 different reports in the markdown
   - Example: If creating an invoice schema, include multiple line items

4. **Test data structure example** for a nested report schema:

```markdown
# Test Data for Report Schema

## Report 1: Q1 Financial Summary
This is the summary of Q1 financial performance showing strong growth...

## Report 2: Q2 Operational Review
The Q2 operations review indicates improved efficiency...

## Report 3: Annual Strategy Report
The annual strategy outlines three key initiatives for growth...
```

5. **Test data structure example** for a flat schema:

```markdown
# Document Metadata Test

Title: Annual Financial Report 2024
Author: John Smith
Date: 2024-01-15

This document provides a comprehensive overview of the company's financial performance...
```

### Step 5: Validate the Schema with API Testing

Use the test script to validate the schema implementation:

1. **Ensure the backend is running**:
   ```bash
   uv run python app.py
   ```

2. **Run the test script** located at `scripts/test_schema.py`:
   ```bash
   uv run python scripts/test_schema.py <schema_key> <test_data_file>
   ```

   Example:
   ```bash
   uv run python scripts/test_schema.py invoice_schema backend/test_data/invoice_test.md
   ```

3. **Review the test output**:
   - Check if all fields are extracted correctly
   - Verify that nested schemas extract multiple instances
   - Ensure data types match the schema definition
   - Look for any validation errors

4. **If issues are found**:
   - Adjust the schema Field descriptions for better AI understanding
   - Add validation constraints if needed
   - Modify test data to be more comprehensive
   - Re-run the test script

### Step 6: Verify in the UI (Optional)

For end-to-end validation:

1. Start the full development environment:
   ```bash
   npm run dev
   ```

2. Open the frontend at `http://localhost:3000`

3. Upload a test document or use the test markdown file

4. Select the new schema from the model dropdown

5. Process the document and verify the results display correctly

## Common Schema Patterns

### Invoice/Contract Schemas
- Use nested patterns for multiple line items
- Include: currency, dates, amounts, parties, terms
- Consider payment terms, credit terms, conditions

### Audit/Compliance Schemas
- Nested patterns for multiple issues/findings
- Include: categories, references, descriptions, risk statements
- Add recommendations and management responses

### Financial Schemas
- Flat pattern for single-period statements
- Use `float` for all monetary values
- Include proper field validation (`ge=0` for amounts)

### Report/Meeting Schemas
- Nested patterns for multiple items/topics
- Include metadata: dates, attendees, titles
- Add summary and detail fields for each item

## Troubleshooting

**Schema not appearing in UI:**
- Verify registration in `AVAILABLE_MODELS` dictionary
- Check that the key name follows lowercase_underscore convention
- Restart the backend server

**Fields not extracting correctly:**
- Improve Field descriptions to be more specific
- Check that field types match the data
- Consider using Optional for fields that may be missing

**Validation errors:**
- Review field constraints (min_length, ge, le)
- Check that date formats are specified in descriptions
- Ensure required fields are marked with `...` not `None`

**Test script failures:**
- Verify the schema key matches AVAILABLE_MODELS
- Check that test data file path is correct
- Ensure backend is running before testing

## Resources

### scripts/
- `test_schema.py` - Script for testing schema validation via API endpoint

### references/
- `schema_examples.md` - Comprehensive examples of flat and nested schemas from the existing codebase, including best practices for different document types

## Additional Notes

- Always test with realistic data that covers edge cases
- For nested schemas, test with varying numbers of instances (1, 2, many)
- Consider future extensibility when designing schemas
- Document complex validation logic with comments
- Follow the existing naming conventions in document_schemas.py
