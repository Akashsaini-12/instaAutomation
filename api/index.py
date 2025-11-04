"""
Vercel serverless function entry point for Instagram Automation API.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_ui import app

# Export the app for Vercel
__all__ = ["app"]
