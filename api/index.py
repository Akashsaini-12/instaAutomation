"""
Vercel serverless function entry point for Instagram Automation API.
Note: Due to Vercel's 250MB size limit, full functionality may not be available.
For best results, deploy to Railway or Render instead.
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import, but handle missing dependencies gracefully
try:
    from web_ui import app
except ImportError as e:
    # Create a minimal app if dependencies are missing
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Instagram Automation API")
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "status": "error",
            "message": "Full dependencies not available on Vercel. Deploy to Railway/Render for full functionality.",
            "error": str(e)
        })
    
    @app.get("/health")
    async def health():
        return {"status": "limited", "platform": "vercel"}

# Export the app for Vercel
__all__ = ["app"]
