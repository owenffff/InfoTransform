# Test Data Templates

This document provides templates for creating test data markdown files for different schema types.

## Flat Schema Test Data Template

Use this template when testing **flat schemas** (single instance extraction):

```markdown
# Test Document for [Schema Name]

**Field1**: Value for field 1
**Field2**: Value for field 2
**Field3**: Value for field 3

## Additional Context

This section provides additional context and detailed information that may be relevant
to the schema fields. The AI will extract structured data from this content based on
the field descriptions in the schema.

Include realistic data that matches the types and formats expected by the schema:
- Dates in the format specified in field descriptions
- Numbers in appropriate ranges
- Text that matches the semantic meaning of each field
```

**Example - Document Metadata Test Data:**

```markdown
# Annual Financial Report 2024

**Title**: Annual Financial Report 2024
**Author**: Jane Smith, CFO
**Date**: 2024-12-31

## Executive Summary

This comprehensive financial report provides a detailed overview of the company's
financial performance for fiscal year 2024. The report includes revenue analysis,
expense breakdown, and forward-looking statements.

Key Topics: Financial Performance, Revenue Growth, Cost Management, Strategic Initiatives,
Market Analysis

The document contains approximately 15,000 words across 50 pages, covering all major
financial metrics and operational highlights for the year.
```

## Nested Schema Test Data Template

Use this template when testing **nested schemas** (multiple instance extraction):

```markdown
# Test Document for [Schema Name]

This document contains multiple [items/instances] for testing the nested schema.

## Item 1: [Title/Name of First Instance]

**Field1**: Value for item 1 field 1
**Field2**: Value for item 1 field 2
**Field3**: Value for item 1 field 3

Detailed description or context for the first item...

## Item 2: [Title/Name of Second Instance]

**Field1**: Value for item 2 field 1
**Field2**: Value for item 2 field 2
**Field3**: Value for item 2 field 3

Detailed description or context for the second item...

## Item 3: [Title/Name of Third Instance]

**Field1**: Value for item 3 field 1
**Field2**: Value for item 3 field 2
**Field3**: Value for item 3 field 3

Detailed description or context for the third item...
```

**Example - Invoice Line Items Test Data:**

```markdown
# Invoice Test Data - Multiple Line Items

Invoice Number: INV-2024-001
Date: 2024-01-15
Customer: Acme Corporation
Currency: USD

## Line Item 1: Professional Services

- Description: Software development consulting services for Q4 2024
- Quantity: 120 hours
- Unit Price: $150.00
- Amount: $18,000.00
- Category: Services

## Line Item 2: Cloud Infrastructure

- Description: AWS hosting and infrastructure services for December 2024
- Quantity: 1 month
- Unit Price: $5,500.00
- Amount: $5,500.00
- Category: Infrastructure

## Line Item 3: Support & Maintenance

- Description: 24/7 technical support and system maintenance
- Quantity: 1 month
- Unit Price: $2,000.00
- Amount: $2,000.00
- Category: Support

Total Amount: $25,500.00
Payment Terms: Net 30 days
```

**Example - Report Summary Test Data:**

```markdown
# Quarterly Reports Summary - Q1-Q3 2024

## Q1 2024 Financial Performance Report

**Title**: Q1 2024 Financial Performance Report
**Summary**: The first quarter of 2024 showed strong revenue growth of 15% year-over-year,
driven by increased demand in the enterprise segment. Operating expenses remained controlled
at 68% of revenue, contributing to improved EBITDA margins. Key highlights include successful
product launches and expansion into three new markets.

## Q2 2024 Operational Excellence Report

**Title**: Q2 2024 Operational Excellence Report
**Summary**: Second quarter operations focused on efficiency improvements and process
optimization. The company achieved 98.5% uptime across all systems, reduced average
response time by 25%, and implemented automated workflows that saved 200 hours per week.
Customer satisfaction scores increased to 4.7/5.0.

## Q3 2024 Strategic Initiatives Report

**Title**: Q3 2024 Strategic Initiatives Report
**Summary**: Q3 strategic efforts centered on market expansion and product innovation.
Successfully launched two new product lines, established partnerships with five major
retailers, and completed the acquisition of TechStart Inc. Pipeline for Q4 includes
three additional product releases and expansion into the APAC region.
```

## Test Data Best Practices

### 1. Include Multiple Instances for Nested Schemas

Always include **at least 2-3 instances** when testing nested schemas:
- Tests the schema's ability to extract multiple items
- Validates that the `List[]` structure works correctly
- Ensures the AI can differentiate between instances

### 2. Cover All Schema Fields

Ensure test data includes content for **every field** in your schema:
- Required fields: Must have corresponding data
- Optional fields: Include data for at least some instances
- List fields: Provide multiple values when possible

### 3. Use Realistic Data

Use realistic, domain-appropriate data:
- Real-world values and formats
- Proper dates, currencies, and numbers
- Industry-specific terminology

### 4. Test Edge Cases

Include variations to test schema robustness:
- Minimum and maximum values
- Optional fields that are present vs. absent
- Different date formats (if applicable)
- Various string lengths

### 5. Provide Context

Add narrative context around the data:
- Helps the AI understand the document structure
- Provides semantic clues for field extraction
- Makes test data more representative of real documents

## Template Selection Guide

| Schema Type | Pattern | Template to Use | Example Use Case |
|------------|---------|-----------------|------------------|
| Single extraction | Flat Schema | Flat Template | Document metadata, Summary |
| Multiple extractions | Nested Schema | Nested Template | Multiple invoices, reports |
| Complex nested | Nested with Sub-items | Nested Template | Audit issues with recommendations |

## File Naming Conventions

Name test data files descriptively:
- `invoice_test.md` - For invoice schema testing
- `report_summary_test.md` - For report summary testing
- `audit_issues_test.md` - For audit schema testing
- `[schema_name]_test.md` - General pattern

Store test files in: `/Users/owen/Desktop/dev_projects/InfoTransform/backend/test_data/`
