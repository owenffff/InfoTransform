#!/usr/bin/env python3
"""
Entry point for the InfoTransform application
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Setup enhanced logging configuration
from infotransform.utils.logging_config import setup_logging, enable_quiet_mode

# Check for quiet mode environment variable
if os.getenv('QUIET_MODE', '').lower() in ('true', '1', 'yes'):
    setup_logging()
    enable_quiet_mode()
    print("[QUIET] Quiet mode enabled - reduced logging output")
else:
    setup_logging()

# Import and run the FastAPI app

if __name__ == "__main__":
    import uvicorn
    from infotransform.config import config
    
    print(f"[START] Starting server on http://localhost:{config.PORT}")
    print(f"[DOCS] API documentation available at http://localhost:{config.PORT}/docs")
    
    uvicorn.run(
        "infotransform.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        log_level="info"
    )
