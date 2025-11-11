"""
Vercel serverless function - Minimal API for Instagram Automation.
This is a lightweight version that doesn't include heavy dependencies.
For full functionality, deploy to Railway or Render instead.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os

# Create minimal app - no heavy dependencies
app = FastAPI(
    title="Instagram Automation API",
    description="Minimal API for Instagram Automation (Vercel-compatible)",
    version="1.0.0"
)


class URLRequest(BaseModel):
    """Request model for URL submission."""
    urls: List[str]
    auto_upload: bool = True
    auto_like_comments: bool = False


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Minimal web interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Automation - Vercel Deployment</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 { color: #333; margin-bottom: 20px; }
            .warning {
                background: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }
            .warning h2 { color: #856404; margin-bottom: 10px; }
            .info {
                background: #d1ecf1;
                border: 2px solid #0c5460;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }
            .info h3 { color: #0c5460; margin-bottom: 10px; }
            .info ul { margin-left: 20px; }
            .button {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                margin: 10px;
                font-weight: 600;
            }
            .button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Instagram Automation</h1>
            
            <div class="warning">
                <h2>⚠️ Vercel Deployment Limitations</h2>
                <p>This is a <strong>minimal version</strong> deployed on Vercel. Full functionality is not available due to:</p>
                <ul style="text-align: left; margin-top: 10px;">
                    <li>❌ 250 MB serverless function size limit</li>
                    <li>❌ No persistent storage for videos</li>
                    <li>❌ No long-running background tasks</li>
                    <li>❌ Heavy dependencies (instaloader, instagrapi) are too large</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>✅ Recommended: Deploy to Railway or Render</h3>
                <p>For <strong>full functionality</strong>, deploy to:</p>
                <ul>
                    <li><strong>Railway</strong> ⭐ (Recommended - Easy setup, persistent storage)</li>
                    <li><strong>Render</strong> (Free tier available, persistent storage)</li>
                    <li><strong>Fly.io</strong> (Good for long-running tasks)</li>
                </ul>
                <p style="margin-top: 15px;">
                    <strong>Why Railway/Render?</strong><br>
                    ✅ No size limits<br>
                    ✅ Persistent storage for videos<br>
                    ✅ Long-running background tasks<br>
                    ✅ All dependencies supported
                </p>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>📚 Documentation</h3>
                <p>See <code>DEPLOYMENT.md</code> for deployment instructions.</p>
                <p style="margin-top: 15px;">
                    <a href="https://railway.app" class="button" target="_blank">Deploy to Railway</a>
                    <a href="https://render.com" class="button" target="_blank">Deploy to Render</a>
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                <p style="color: #666; font-size: 14px;">
                    This minimal API is running on Vercel.<br>
                    For full automation features, please deploy to Railway or Render.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "limited",
        "platform": "vercel",
        "message": "Minimal API - Full functionality not available on Vercel",
        "recommendation": "Deploy to Railway or Render for full functionality"
    }


@app.post("/process")
async def process_urls(request: URLRequest):
    """Process URLs - Not available on Vercel."""
    raise HTTPException(
        status_code=503,
        detail={
            "error": "Feature not available on Vercel",
            "message": "Video download/upload requires heavy dependencies that exceed Vercel's 250MB limit",
            "recommendation": "Deploy to Railway or Render for full functionality",
            "railway": "https://railway.app",
            "render": "https://render.com"
        }
    )


@app.get("/status")
async def get_status():
    """Status endpoint."""
    return {
        "status": "limited",
        "platform": "vercel",
        "message": "Minimal API - Status tracking not available",
        "recommendation": "Deploy to Railway or Render"
    }


@app.get("/downloads")
async def list_downloads():
    """Downloads endpoint - Not available on Vercel."""
    return {
        "total": 0,
        "videos": [],
        "message": "Downloads not available on Vercel (no persistent storage)",
        "recommendation": "Deploy to Railway or Render"
    }


# Export for Vercel
__all__ = ["app"]
