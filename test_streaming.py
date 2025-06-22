#!/usr/bin/env python3
"""
Test script for the streaming table view functionality
"""

import asyncio
import aiohttp
import json
from pathlib import Path

async def test_streaming():
    """Test the streaming endpoint"""
    # Create some test markdown files
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create test files
    test_files = {
        "doc1.md": """# Technical Documentation
This is a Python tutorial for beginners.
```python
def hello_world():
    print("Hello, World!")
```
It covers basic programming concepts.
External links: https://python.org
""",
        "doc2.md": """# API Reference
Advanced API documentation for developers.
```javascript
const api = new API();
api.get('/users');
```
```python
import requests
response = requests.get('https://api.example.com')
```
Installation guide included.
Links: https://api.example.com, https://docs.example.com
""",
        "doc3.md": """# Getting Started Guide
Simple introduction to our product.
No code examples here.
Visit our website for more information.
"""
    }
    
    for filename, content in test_files.items():
        (test_dir / filename).write_text(content)
    
    print("Created test files in test_files/")
    print("\nTo test the streaming functionality:")
    print("1. Start the server: python app.py")
    print("2. Open http://localhost:8000 in your browser")
    print("3. Upload the test files from the test_files/ directory")
    print("4. Select 'Technical Documentation Analysis' model")
    print("5. Click Transform to see the streaming table view")
    print("\nThe table should update row by row as files are processed!")

if __name__ == "__main__":
    asyncio.run(test_streaming())
