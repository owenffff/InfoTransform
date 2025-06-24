"""
Test script to verify token counting functionality
"""

import logging
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.infotransform.utils.token_counter import count_tokens, log_token_count

# Configure logging to see INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_token_counting():
    """Test the token counting functionality"""
    
    # Test 1: Simple text
    text1 = "Hello, this is a simple test of the token counting functionality."
    tokens1 = count_tokens(text1)
    print(f"Test 1 - Simple text: {tokens1} tokens")
    
    # Test 2: Markdown content
    text2 = """
# Document Title

This is a **markdown** document with various formatting.

## Section 1
- Item 1
- Item 2
- Item 3

## Section 2
Here's some code:
```python
def hello_world():
    print("Hello, World!")
```

And a table:
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
    tokens2 = count_tokens(text2)
    print(f"Test 2 - Markdown content: {tokens2} tokens")
    
    # Test 3: Using log_token_count
    print("\nTest 3 - Testing log_token_count (check logs above):")
    log_token_count("test_document.md", text2)
    
    # Test 4: Large text
    large_text = "This is a test sentence. " * 100
    tokens3 = count_tokens(large_text)
    print(f"\nTest 4 - Large text (100 repetitions): {tokens3} tokens")
    log_token_count("large_document.txt", large_text)
    
    # Test 5: Empty text
    empty_text = ""
    tokens4 = count_tokens(empty_text)
    print(f"\nTest 5 - Empty text: {tokens4} tokens")
    
    # Test 6: Special characters and emojis
    special_text = "Special chars: @#$%^&*() and emojis: 😀🎉🚀"
    tokens5 = count_tokens(special_text)
    print(f"\nTest 6 - Special characters and emojis: {tokens5} tokens")
    
    print("\n✅ All token counting tests completed!")

if __name__ == "__main__":
    test_token_counting()
