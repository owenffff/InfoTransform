"""
Test script for Information Transformer functionality
"""

import asyncio
import os
from pathlib import Path

from processors.structured_analyzer import StructuredAnalyzer
from processors.vision import VisionProcessor
from config import config


async def test_transformer():
    """Test the Information Transformer pipeline"""
    print("🔄 Testing Information Transformer\n")
    
    # Initialize components
    print("1. Initializing components...")
    try:
        vision_processor = VisionProcessor()
        analyzer = StructuredAnalyzer()
        print("✅ Components initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # List available models
    print("2. Available Analysis Models:")
    models = analyzer.get_available_models()
    for key, info in models.items():
        print(f"   - {key}: {info['name']}")
        print(f"     Description: {info['description']}")
        print(f"     Fields: {', '.join(info['fields'])}\n")
    
    # List AI models
    print("3. Available AI Models:")
    ai_models = analyzer.get_available_ai_models()
    print(f"   Default: {ai_models['default_model']}")
    for name, cfg in ai_models['models'].items():
        print(f"   - {name}: {cfg['max_tokens']} tokens, temp={cfg['temperature']}")
    print()
    
    # Test with a sample image
    test_image = "test_ocr_example.py"  # Using existing test file
    if os.path.exists(test_image):
        print(f"4. Testing with file: {test_image}")
        
        # Step 1: Convert to markdown
        print("   Step 1: Converting to markdown...")
        result = vision_processor.process_file(test_image)
        
        if result['success']:
            markdown_content = result['content']
            print(f"   ✅ Converted to markdown ({len(markdown_content)} chars)")
            print(f"   Preview: {markdown_content[:200]}...\n")
            
            # Step 2: Extract structured data
            print("   Step 2: Extracting structured data...")
            
            # Test with document metadata model
            analysis_result = await analyzer.analyze_content(
                markdown_content,
                model_key="document_metadata",
                custom_instructions="Focus on extracting code-related metadata"
            )
            
            if analysis_result['success']:
                print(f"   ✅ Analysis successful!")
                print(f"   Model used: {analysis_result['model_used']}")
                print(f"   AI model: {analysis_result['ai_model_used']}")
                print("\n   Extracted Data:")
                
                data = analysis_result['result']
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"   - {key}: {', '.join(str(v) for v in value[:3])}...")
                    else:
                        print(f"   - {key}: {value}")
            else:
                print(f"   ❌ Analysis failed: {analysis_result.get('error')}")
        else:
            print(f"   ❌ Markdown conversion failed: {result.get('error')}")
    else:
        print(f"❌ Test file not found: {test_image}")
    
    print("\n✅ Test completed!")


async def test_batch_analysis():
    """Test batch analysis functionality"""
    print("\n5. Testing Batch Analysis...")
    
    analyzer = StructuredAnalyzer()
    
    # Create sample markdown contents
    contents = {
        "doc1.md": "# Technical Documentation\n\nThis is a guide about Python programming with async/await patterns.",
        "doc2.md": "# User Manual\n\nStep-by-step instructions for using the application.",
        "doc3.md": "# API Reference\n\nDetailed API documentation with code examples."
    }
    
    try:
        results = await analyzer.analyze_batch(
            contents,
            model_key="technical_analysis",
            custom_instructions="Assess the technical complexity"
        )
        
        print(f"   ✅ Batch analysis completed: {len(results)} files processed")
        
        for result in results:
            if result['success']:
                print(f"   - {result['filename']}: Success")
            else:
                print(f"   - {result['filename']}: Failed - {result.get('error')}")
                
    except Exception as e:
        print(f"   ❌ Batch analysis failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Information Transformer Test Suite")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_transformer())
    asyncio.run(test_batch_analysis())
    
    print("\n" + "=" * 60)
    print("All tests completed!")
