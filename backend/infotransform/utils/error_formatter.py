"""
Error formatting utilities for user-friendly error messages.

Converts technical Pydantic validation errors into human-readable messages.
"""

import re
from typing import List, Dict, Any, Optional


def humanize_field_name(field_name: str) -> str:
    """
    Convert snake_case or camelCase field names to Title Case.

    Examples:
        income_capitalisation_method → Income Capitalisation Method
        walkthrough_datetime → Walkthrough Datetime
        comparable_sales_method → Comparable Sales Method
    """
    # Replace underscores with spaces
    humanized = field_name.replace("_", " ")

    # Convert to title case
    humanized = humanized.title()

    return humanized


def extract_row_number(location: List[Any]) -> Optional[int]:
    """
    Extract row number from Pydantic error location path.

    Examples:
        ['item', 0, 'income_capitalisation_method'] → 1 (display as row 1)
        ['item', 5, 'fair_value'] → 6
        ['title'] → None
    """
    for loc_part in location:
        if isinstance(loc_part, int):
            return loc_part + 1  # Convert 0-index to 1-index for user display
    return None


def simplify_error_message(error_type: str, error_msg: str, input_value: Any) -> str:
    """
    Convert technical Pydantic error messages into user-friendly text.

    Args:
        error_type: Pydantic error type (e.g., 'float_type', 'string_type')
        error_msg: Original error message
        input_value: The invalid input value

    Returns:
        Simplified, user-friendly error message
    """
    # Type conversion errors
    if error_type in ["float_type", "int_type", "number_type"]:
        if input_value is None:
            return "Expected a number, but got no value"
        return f"Expected a number, but got: {input_value}"

    if error_type in ["string_type", "str_type"]:
        if input_value is None:
            return "Expected text, but got no value"
        return f"Expected text, but got: {type(input_value).__name__}"

    if error_type in ["bool_type", "boolean_type"]:
        return f"Expected true/false, but got: {input_value}"

    if error_type == "list_type":
        return f"Expected a list, but got: {type(input_value).__name__}"

    # Date/time errors
    if "datetime" in error_type or "date" in error_type:
        return f"Invalid date/time format: {input_value}"

    # Missing required field
    if error_type == "missing":
        return "This required field is missing"

    # Value errors
    if error_type == "value_error":
        if "enum" in error_msg.lower() or "literal" in error_msg.lower():
            # Extract allowed values if present
            allowed_match = re.search(r"permitted: (.*?)(?:\]|$)", error_msg)
            if allowed_match:
                return f"Invalid value. Allowed values: {allowed_match.group(1)}"
            return "Invalid value for this field"
        return error_msg

    # String constraints
    if "min_length" in error_type:
        return "Value is too short"
    if "max_length" in error_type:
        return "Value is too long"

    # Literal errors (specific allowed values)
    if "literal_error" in error_type:
        return "Value must be one of the specified options"

    # Default fallback
    return error_msg


def format_single_validation_error(error: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a single Pydantic validation error into a user-friendly structure.

    Args:
        error: Pydantic error dict with 'loc', 'msg', 'type', 'input' keys

    Returns:
        Formatted error dict with 'field', 'message', 'row', 'technical_details'
    """
    location = error.get("loc", [])
    error_type = error.get("type", "")
    error_msg = error.get("msg", "")
    input_value = error.get("input")

    # Extract field name (last non-integer element in location)
    field_name = None
    for loc_part in reversed(location):
        if isinstance(loc_part, str) and loc_part != "item":
            field_name = loc_part
            break

    # Get row number if present
    row_num = extract_row_number(location)

    # Humanize field name
    field_display = humanize_field_name(field_name) if field_name else "Unknown Field"

    # Simplify error message
    simple_msg = simplify_error_message(error_type, error_msg, input_value)

    # Build formatted error
    formatted = {
        "field": field_display,
        "message": simple_msg,
        "row": row_num,
        "technical_details": {
            "location": location,
            "type": error_type,
            "original_message": error_msg,
        },
    }

    return formatted


def format_validation_errors(
    errors: List[Dict[str, Any]], max_errors: int = 10, include_summary: bool = True
) -> Dict[str, Any]:
    """
    Format multiple Pydantic validation errors into user-friendly structure.

    Args:
        errors: List of Pydantic error dicts
        max_errors: Maximum number of errors to format (rest are truncated)
        include_summary: Whether to include a summary section

    Returns:
        Dict with 'formatted_errors', 'total_count', 'truncated', 'summary'
    """
    total_count = len(errors)
    errors_to_format = errors[:max_errors]
    truncated = total_count > max_errors

    # Format each error
    formatted_errors = [format_single_validation_error(err) for err in errors_to_format]

    # Group errors by row for summary
    rows_with_errors = set()
    fields_with_errors = set()
    for formatted_err in formatted_errors:
        if formatted_err["row"]:
            rows_with_errors.add(formatted_err["row"])
        fields_with_errors.add(formatted_err["field"])

    # Build summary
    summary = None
    if include_summary:
        if rows_with_errors:
            rows_text = (
                f"{len(rows_with_errors)} row(s)"
                if len(rows_with_errors) > 1
                else "1 row"
            )
            summary = f"{total_count} validation issue(s) found across {rows_text}"
        else:
            summary = f"{total_count} validation issue(s) found"

    # Build response
    response = {
        "formatted_errors": formatted_errors,
        "total_count": total_count,
        "truncated": truncated,
        "summary": summary,
        "affected_rows": sorted(rows_with_errors) if rows_with_errors else [],
        "affected_fields": sorted(fields_with_errors),
    }

    if truncated:
        response["truncation_message"] = (
            f"Showing first {max_errors} of {total_count} errors"
        )

    return response


def create_user_friendly_error_message(
    errors: List[Dict[str, Any]], model_name: str = "document schema"
) -> str:
    """
    Create a concise, user-friendly error message from validation errors.

    Args:
        errors: List of Pydantic error dicts
        model_name: Name of the schema/model that failed validation

    Returns:
        User-friendly error string suitable for display
    """
    formatted = format_validation_errors(errors, max_errors=3, include_summary=True)

    lines = []
    lines.append(f"Schema validation failed for {model_name}:")
    lines.append(formatted["summary"])
    lines.append("")

    # Show first few errors
    for err in formatted["formatted_errors"]:
        if err["row"]:
            lines.append(f"  • Row {err['row']}, {err['field']}: {err['message']}")
        else:
            lines.append(f"  • {err['field']}: {err['message']}")

    if formatted["truncated"]:
        lines.append(f"  ... and {formatted['total_count'] - 3} more errors")

    lines.append("")
    lines.append(
        "Tip: The document structure didn't match the expected format. Try using a different schema or ensure the document contains the required information."
    )

    return "\n".join(lines)


def get_helpful_tips(error_types: List[str]) -> List[str]:
    """
    Generate helpful tips based on common error patterns.

    Args:
        error_types: List of Pydantic error types encountered

    Returns:
        List of helpful tip strings
    """
    tips = []

    if any("type" in et for et in error_types):
        tips.append(
            "Ensure numeric fields contain valid numbers, not text or empty values"
        )

    if any("missing" in et for et in error_types):
        tips.append("Some required fields are missing from the document")

    if any("date" in et or "datetime" in et for et in error_types):
        tips.append("Check that dates are in the correct format (YYYY-MM-DD)")

    if any("literal" in et or "enum" in et for et in error_types):
        tips.append(
            "Some fields have invalid values - check they match the expected options"
        )

    if not tips:
        tips.append(
            "Review the document to ensure it matches the expected schema structure"
        )

    return tips
