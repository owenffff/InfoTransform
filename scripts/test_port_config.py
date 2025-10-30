#!/usr/bin/env python3
"""
Test script to verify port configuration is properly read from .env file
This tests the scenario where ports are swapped from defaults.

Test scenario:
- PORT=8501 (Frontend)
- BACKEND_PORT=8502 (Backend)
- NEXT_PUBLIC_BACKEND_PORT=8502 (Must match BACKEND_PORT)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if not env_path.exists():
    print(f"❌ ERROR: .env file not found at {env_path}")
    print("Please copy .env.example to .env and configure it")
    sys.exit(1)

load_dotenv(env_path)

print("=" * 70)
print("PORT CONFIGURATION TEST")
print("=" * 70)

# Read environment variables
port = os.getenv("PORT")
backend_port = os.getenv("BACKEND_PORT")
next_public_backend_port = os.getenv("NEXT_PUBLIC_BACKEND_PORT")

print("\n📋 Environment Variables from .env:")
print(f"   PORT                     = {port}")
print(f"   BACKEND_PORT             = {backend_port}")
print(f"   NEXT_PUBLIC_BACKEND_PORT = {next_public_backend_port}")

# Validation checks
errors = []
warnings = []

if not port:
    warnings.append("PORT is not set (will default to 3000)")
else:
    print(f"\n✅ PORT is set to {port}")

if not backend_port:
    errors.append("BACKEND_PORT is not set (required)")
else:
    print(f"✅ BACKEND_PORT is set to {backend_port}")

if not next_public_backend_port:
    errors.append("NEXT_PUBLIC_BACKEND_PORT is not set (required)")
else:
    print(f"✅ NEXT_PUBLIC_BACKEND_PORT is set to {next_public_backend_port}")

if backend_port and next_public_backend_port:
    if backend_port != next_public_backend_port:
        errors.append(
            f"❌ BACKEND_PORT ({backend_port}) does NOT match "
            f"NEXT_PUBLIC_BACKEND_PORT ({next_public_backend_port})\n"
            f"   These MUST be the same value!"
        )
    else:
        print(f"\n✅ BACKEND_PORT matches NEXT_PUBLIC_BACKEND_PORT ({backend_port})")

# Test backend config loading
print("\n" + "=" * 70)
print("TESTING BACKEND PORT CONFIGURATION")
print("=" * 70)

try:
    # Add backend to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
    from infotransform.config import config

    backend_config_port = config.PORT
    print(f"\n✅ Backend config.PORT = {backend_config_port}")

    if backend_port and int(backend_port) != backend_config_port:
        errors.append(
            f"❌ Backend config.PORT ({backend_config_port}) does NOT match "
            f"BACKEND_PORT env var ({backend_port})"
        )
    else:
        print("✅ Backend correctly reads BACKEND_PORT from .env")

except Exception as e:
    errors.append(f"❌ Failed to load backend config: {e}")

# Test frontend config
print("\n" + "=" * 70)
print("TESTING FRONTEND CONFIGURATION")
print("=" * 70)

frontend_next_config = Path(__file__).parent.parent / "frontend" / "next.config.js"
if frontend_next_config.exists():
    print("✅ next.config.js found")
    print(f"   Location: {frontend_next_config}")
    print("   ℹ️  next.config.js exposes NEXT_PUBLIC_BACKEND_PORT to browser")
    print(f"   ℹ️  Frontend will use: http://<hostname>:{next_public_backend_port}")
else:
    errors.append(f"❌ next.config.js not found at {frontend_next_config}")

api_url_util = (
    Path(__file__).parent.parent / "frontend" / "lib" / "utils" / "api-url.ts"
)
if api_url_util.exists():
    print("✅ api-url.ts utility found")
    print(f"   Location: {api_url_util}")
    print(
        "   ℹ️  This utility dynamically constructs API URLs using NEXT_PUBLIC_BACKEND_PORT"
    )
else:
    errors.append(f"❌ api-url.ts not found at {api_url_util}")

# Print summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if warnings:
    print("\n⚠️  WARNINGS:")
    for warning in warnings:
        print(f"   {warning}")

if errors:
    print("\n❌ ERRORS FOUND:")
    for error in errors:
        print(f"   {error}")
    print("\n💡 Fix these issues before running the application!")
    sys.exit(1)
else:
    print("\n✅ ALL CHECKS PASSED!")
    print("\n📌 Configuration Summary:")
    print(f"   Frontend will run on port:        {port or '3000 (default)'}")
    print(f"   Backend will run on port:         {backend_port}")
    print(
        f"   Frontend will call backend on:    http://<hostname>:{next_public_backend_port}"
    )
    print("\n💡 To test with swapped ports, set in .env:")
    print("   PORT=8501")
    print("   BACKEND_PORT=8502")
    print("   NEXT_PUBLIC_BACKEND_PORT=8502")
    print("\n🚀 You can now run: npm run dev")
    sys.exit(0)
