#!/usr/bin/env python3
"""
Test script to verify environment configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment Configuration Test")
print("=" * 50)

# Check OpenAI configuration
openai_key = os.getenv('OPENAI_API_KEY')
openai_base = os.getenv('OPENAI_BASE_URL')

print(f"OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")
print(f"OPENAI_BASE_URL: {openai_base or 'Not set (will use default)'}")

# Check Azure Document Intelligence
azure_endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
print(f"AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: {'✓ Set' if azure_endpoint else '✗ Not set (optional)'}")

# Add the src directory to the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Test config module
print("\nTesting config module...")
try:
    from infotransform.config import config
    print(f"config.API_KEY: {'✓ Available' if config.API_KEY else '✗ Not available'}")
    print(f"config.BASE_URL: {config.BASE_URL}")
    print(f"config.DOCINTEL_ENDPOINT: {'✓ Set' if config.DOCINTEL_ENDPOINT else '✗ Not set (optional)'}")
    print("\n✓ Config module loaded successfully!")
except Exception as e:
    print(f"\n✗ Error loading config: {e}")

# Test processors
print("\nTesting processors...")
try:
    from infotransform.processors import VisionProcessor, AudioProcessor, StructuredAnalyzer
    
    # Test Vision Processor
    vision = VisionProcessor()
    print("✓ VisionProcessor initialized successfully")
    
    # Test Audio Processor  
    audio = AudioProcessor()
    print("✓ AudioProcessor initialized successfully")
    
    # Test Structured Analyzer
    analyzer = StructuredAnalyzer()
    print("✓ StructuredAnalyzer initialized successfully")
    
except Exception as e:
    print(f"✗ Error initializing processors: {e}")

print("\n" + "=" * 50)
print("Configuration test complete!")
