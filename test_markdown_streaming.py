#!/usr/bin/env python3
"""
Test the streaming functionality with markdown files
"""

import requests
import json
from pathlib import Path

def test_streaming():
    # Create test markdown files
    test_dir = Path("test_md_files")
    test_dir.mkdir(exist_ok=True)
    
    test_files = {
        "test1.md": "# Test Document 1\nThis is a simple test document.",
        "test2.md": "# Test Document 2\nThis document has some **bold** text.",
        "test3.md": "# Test Document 3\nThis has a [link](https://example.com)."
    }
    
    for filename, content in test_files.items():
        (test_dir / filename).write_text(content)
    
    print("Created test markdown files in test_md_files/")
    print("\nNow you can:")
    print("1. Upload these .md files to test if streaming works")
    print("2. If .md files work but .docx don't, we know it's a DOCX processing issue")

if __name__ == "__main__":
    test_streaming()
