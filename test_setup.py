#!/usr/bin/env python3
"""
Test script to verify Markitdown MVP setup
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment setup...\n")
    
    # Check Python version
    python_version = sys.version_info
    print(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print("  ⚠️  Warning: Python 3.11+ is required")
    
    # Check required packages
    print("\n📦 Checking required packages:")
    packages = {
        'markitdown': 'Markitdown',
        'openai': 'OpenAI',
        'flask': 'Flask',
        'dotenv': 'python-dotenv'
    }
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name} is installed")
        except ImportError:
            print(f"  ❌ {name} is NOT installed")
    
    # Check environment variables
    print("\n🔐 Checking environment variables:")
    api_key = os.getenv('API_KEY')
    base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
    
    if api_key:
        print(f"  ✓ API_KEY is set (length: {len(api_key)} chars)")
    else:
        print("  ❌ API_KEY is NOT set")
    
    print(f"  ℹ️  BASE_URL: {base_url}")
    print(f"  ℹ️  MODEL_NAME: {os.getenv('MODEL_NAME', 'gpt-4-vision-preview')}")
    print(f"  ℹ️  WHISPER_MODEL: {os.getenv('WHISPER_MODEL', 'whisper-1')}")
    
    vision_prompt = os.getenv('VISION_PROMPT')
    if vision_prompt:
        print(f"  ℹ️  VISION_PROMPT: Custom prompt set ({len(vision_prompt)} chars)")
    else:
        print(f"  ℹ️  VISION_PROMPT: Using default (optimized for OCR + descriptions)")
    
    # Check directories
    print("\n📁 Checking directories:")
    dirs = ['uploads', 'templates', 'static', 'processors']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ❌ {dir_name}/ is missing")
    
    # Summary
    print("\n" + "="*50)
    if api_key and all(os.path.exists(d) for d in dirs):
        print("✅ Setup looks good! You can run: python app.py")
    else:
        print("⚠️  Please complete the setup:")
        if not api_key:
            print("   1. Copy .env.example to .env")
            print("   2. Add your API_KEY to .env")
        if not all(os.path.exists(d) for d in dirs):
            print("   3. Make sure all directories exist")

if __name__ == "__main__":
    check_environment()
