#!/usr/bin/env python3
"""
Entry point for the InfoTransform application
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Import and run the FastAPI app
from infotransform.main import app

if __name__ == "__main__":
    import uvicorn
    from infotransform.config import config
    
    print(f"🚀 Starting server on http://localhost:{config.PORT}")
    print(f"📚 API documentation available at http://localhost:{config.PORT}/docs")
    
    uvicorn.run(
        "infotransform.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        log_level="info"
    )
