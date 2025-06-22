#!/usr/bin/env python3
"""
Test different file types to identify which ones work
"""

from pathlib import Path

def create_test_files():
    """Create various test files"""
    test_dir = Path("test_various_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create different file types
    files = {
        "test.txt": "This is a plain text file for testing.",
        "test.md": "# Markdown Test\n\nThis is a **markdown** file.",
        "test.html": "<html><body><h1>HTML Test</h1><p>This is an HTML file.</p></body></html>",
    }
    
    for filename, content in files.items():
        (test_dir / filename).write_text(content)
    
    print("Created test files in test_various_files/:")
    for filename in files:
        print(f"  - {filename}")
    
    print("\nTry uploading these files to see which ones work.")
    print("This will help identify if the issue is specific to DOCX files.")

if __name__ == "__main__":
    create_test_files()
