#!/usr/bin/env python3
"""
test_schema.py

Script for testing document schema implementations via the InfoTransform API endpoint.

Usage:
    uv run python scripts/test_schema.py <schema_key> <test_data_file>

Example:
    uv run python scripts/test_schema.py invoice_schema backend/test_data/invoice_test.md

Requirements:
- Backend server must be running (uv run python app.py)
- Test data file must exist at the specified path
- Schema must be registered in AVAILABLE_MODELS in config/document_schemas.py
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any


def validate_args() -> tuple[str, Path]:
    """Validate command-line arguments."""
    if len(sys.argv) != 3:
        print("Usage: uv run python scripts/test_schema.py <schema_key> <test_data_file>")
        print("\nExample:")
        print("  uv run python scripts/test_schema.py invoice_schema backend/test_data/invoice_test.md")
        sys.exit(1)

    schema_key = sys.argv[1]
    test_file_path = Path(sys.argv[2])

    if not test_file_path.exists():
        print(f"❌ Error: Test data file not found: {test_file_path}")
        sys.exit(1)

    return schema_key, test_file_path


def check_backend() -> bool:
    """Check if the backend is running."""
    try:
        response = requests.get("http://localhost:8000/api/models", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_available_models() -> list[str]:
    """Fetch available models from the API."""
    try:
        response = requests.get("http://localhost:8000/api/models", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []


def test_schema(schema_key: str, test_file_path: Path) -> None:
    """Test the schema by calling the transform API endpoint."""
    print(f"\n{'='*70}")
    print(f"Testing Schema: {schema_key}")
    print(f"Test Data File: {test_file_path}")
    print(f"{'='*70}\n")

    # Check if backend is running
    if not check_backend():
        print("❌ Error: Backend is not running!")
        print("\nPlease start the backend first:")
        print("  uv run python app.py")
        sys.exit(1)

    print("✓ Backend is running")

    # Check if schema exists
    available_models = get_available_models()
    if schema_key not in available_models:
        print(f"\n❌ Error: Schema '{schema_key}' not found in available models!")
        print(f"\nAvailable models:")
        for model in sorted(available_models):
            print(f"  - {model}")
        print("\nPlease verify:")
        print("1. Schema is defined in config/document_schemas.py")
        print("2. Schema is registered in AVAILABLE_MODELS dictionary")
        print("3. Backend has been restarted after adding the schema")
        sys.exit(1)

    print(f"✓ Schema '{schema_key}' is registered")

    # Read test data
    with open(test_file_path, 'r', encoding='utf-8') as f:
        test_content = f.read()

    print(f"✓ Test data loaded ({len(test_content)} characters)")

    # Prepare the request
    url = "http://localhost:8000/api/transform"

    # Create a mock file upload
    files = {
        'files': (test_file_path.name, test_content, 'text/markdown')
    }

    data = {
        'selected_model': schema_key
    }

    print(f"\n{'─'*70}")
    print("Sending request to API...")
    print(f"{'─'*70}\n")

    try:
        # Make the request
        response = requests.post(url, files=files, data=data, timeout=120)

        if response.status_code != 200:
            print(f"❌ API Error (Status {response.status_code}):")
            print(response.text)
            sys.exit(1)

        # Parse SSE response
        results = []
        for line in response.text.strip().split('\n'):
            if line.startswith('data: '):
                try:
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        continue
                    event_data = json.loads(data_str)
                    if event_data.get('type') == 'result':
                        results.append(event_data.get('data'))
                except json.JSONDecodeError:
                    continue

        if not results:
            print("⚠️  Warning: No results extracted from the API response")
            print("\nThis could mean:")
            print("- The schema fields don't match the test data content")
            print("- The AI couldn't extract data based on field descriptions")
            print("- There was an error in the processing pipeline")
            sys.exit(1)

        print(f"✅ Success! Extracted {len(results)} result(s)\n")
        print(f"{'─'*70}")
        print("Extraction Results:")
        print(f"{'─'*70}\n")

        for idx, result in enumerate(results, 1):
            print(f"Result #{idx}:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print()

        print(f"{'─'*70}")
        print("Validation Summary:")
        print(f"{'─'*70}\n")

        # Analyze the results
        if results:
            first_result = results[0]

            # Check if it's a nested schema (has 'item' field with list)
            if isinstance(first_result, dict) and 'item' in first_result:
                items = first_result['item']
                if isinstance(items, list):
                    print(f"✓ Nested schema detected")
                    print(f"✓ Extracted {len(items)} item(s) from document")

                    if items:
                        print(f"✓ Fields in each item:")
                        for field_name in items[0].keys():
                            print(f"    - {field_name}")
                else:
                    print(f"⚠️  Warning: 'item' field is not a list")
            else:
                # Flat schema
                print(f"✓ Flat schema detected")
                if isinstance(first_result, dict):
                    print(f"✓ Extracted fields:")
                    for field_name in first_result.keys():
                        print(f"    - {field_name}")

        print(f"\n{'='*70}")
        print("✅ Schema test completed successfully!")
        print(f"{'='*70}\n")

        print("Next steps:")
        print("1. Review the extracted results above")
        print("2. Verify all expected fields are present and correct")
        print("3. Test with additional test data if needed")
        print("4. Optional: Test in the UI at http://localhost:3000")

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out (120s)")
        print("\nThe API processing took too long. This could mean:")
        print("- The test file is too large")
        print("- There's an issue with the AI processing")
        print("- The backend is overloaded")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Failed to connect to API: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    schema_key, test_file_path = validate_args()
    test_schema(schema_key, test_file_path)


if __name__ == "__main__":
    main()
