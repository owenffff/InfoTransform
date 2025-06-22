#!/usr/bin/env python3
"""
Example script to demonstrate the improved OCR functionality
"""

import os
from PIL import Image, ImageDraw, ImageFont
from processors import VisionProcessor

def create_sample_text_image():
    """Create a sample image with text for testing OCR"""
    # Create a white image
    width, height = 800, 400
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Add text content
    text_content = """
    Markitdown OCR Test
    
    This is a test document to demonstrate:
    • Text extraction from images
    • Bullet point preservation
    • Multiple line handling
    
    Code Example:
    def hello_world():
        print("Hello from Markitdown!")
    
    Visit https://github.com/microsoft/markitdown
    """
    
    # Try to use a better font, fallback to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    # Draw the text
    y_position = 20
    for line in text_content.strip().split('\n'):
        if line.strip():
            if 'def ' in line or 'print(' in line:
                # Code lines in monospace style
                draw.text((40, y_position), line, fill='darkgreen', font=small_font)
            else:
                draw.text((20, y_position), line, fill='black', font=font)
        y_position += 30
    
    # Save the image
    image_path = 'test_ocr_image.png'
    image.save(image_path)
    return image_path

def test_ocr():
    """Test the OCR functionality"""
    print("🧪 Testing OCR Functionality\n")
    
    # Create test image
    print("📝 Creating test image with text...")
    image_path = create_sample_text_image()
    print(f"✅ Test image created: {image_path}\n")
    
    # Process with vision processor
    print("🔍 Processing image with Markitdown...")
    try:
        processor = VisionProcessor()
        result = processor.process_file(image_path)
        
        if result['success']:
            print("✅ Successfully processed!\n")
            print("📄 Extracted Content:")
            print("-" * 50)
            print(result['content'])
            print("-" * 50)
        else:
            print(f"❌ Error: {result['error']}")
    
    except Exception as e:
        print(f"❌ Failed to process: {e}")
    
    finally:
        # Clean up
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"\n🧹 Cleaned up test image")

if __name__ == "__main__":
    # Check if PIL/Pillow is installed
    try:
        import PIL
        test_ocr()
    except ImportError:
        print("❌ This example requires Pillow. Install it with: pip install Pillow")
