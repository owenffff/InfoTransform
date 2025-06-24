#!/usr/bin/env python3
"""
Integration test for token counting in the processing pipeline
"""

import sys
import os
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from infotransform.processors.vision import VisionProcessor
from infotransform.api.streaming_v2 import OptimizedStreamingProcessor
import asyncio

async def test_token_counting():
    """Test token counting in the processing pipeline"""
    
    # Test 1: Direct VisionProcessor test
    print("\n=== Test 1: VisionProcessor Token Counting ===")
    vision = VisionProcessor()
    
    # Create a test file
    test_content = """# Test Document

This is a test document with some content to verify token counting is working properly.

## Section 1
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Section 2
The quick brown fox jumps over the lazy dog.
"""
    
    test_file = "test_doc.md"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Process the file
        result = vision.process_file(test_file)
        print(f"Processing result: {result['success']}")
        print(f"Content preview: {result.get('content', '')[:100]}...")
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    # Test 2: Streaming processor test
    print("\n=== Test 2: Streaming Processor Token Counting ===")
    processor = OptimizedStreamingProcessor()
    await processor.start()
    
    # Create test file info
    test_file2 = "test_doc2.docx"
    with open(test_file2, 'w') as f:
        f.write("Test content for streaming processor")
    
    try:
        file_infos = [{
            'file_path': test_file2,
            'filename': test_file2
        }]
        
        # Process through streaming
        print("Processing through streaming pipeline...")
        async for event in processor.process_files_optimized(
            file_infos,
            'document_metadata',
            '',
            None
        ):
            # Just consume the events
            pass
        
        print("Streaming processing complete")
    finally:
        # Clean up
        if os.path.exists(test_file2):
            os.remove(test_file2)
        await processor.stop()

if __name__ == "__main__":
    print("Testing token counting integration...")
    print("You should see INFO log messages with token counts")
    asyncio.run(test_token_counting())
    print("\nTest complete!")
