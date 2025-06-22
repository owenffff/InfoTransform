#!/usr/bin/env python3
"""
Demo script showing how to use the InfoTransform processors directly
"""

import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from infotransform.processors import VisionProcessor, AudioProcessor

# Load environment variables
load_dotenv()

def demo_vision_processing():
    """Demo vision processing with a sample text file"""
    print("📸 Vision Processing Demo")
    print("-" * 40)
    
    # Create a sample text file to process
    sample_file = "sample_document.txt"
    with open(sample_file, 'w') as f:
        f.write("""
# Sample Document

This is a test document to demonstrate InfoTransform processing.

## Features
- Converts documents to Markdown
- Supports multiple file formats
- Easy to use

## Code Example
```python
def hello_world():
    print("Hello from InfoTransform!")
```

Visit https://github.com/microsoft/markitdown for more info.
""")
    
    try:
        # Initialize processor
        processor = VisionProcessor()
        
        # Process the file
        result = processor.process_file(sample_file)
        
        if result['success']:
            print(f"✅ Successfully processed: {result['filename']}")
            print(f"📄 Content preview (first 200 chars):")
            print(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        print("   Make sure you have set up your API credentials in .env")
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)

def main():
    print("🚀 InfoTransform Demo\n")
    
    # Check if API key is set
    if not os.getenv('API_KEY'):
        print("⚠️  API_KEY not found in environment!")
        print("   Please create a .env file with your API credentials:")
        print("   cp .env.example .env")
        print("   Then edit .env and add your API_KEY")
        return
    
    # Run vision demo
    demo_vision_processing()
    
    print("\n" + "="*50)
    print("✨ Demo complete!")
    print("\nTo use the web interface, run: python app.py")
    print("Then open http://localhost:8000 in your browser")

if __name__ == "__main__":
    main()
