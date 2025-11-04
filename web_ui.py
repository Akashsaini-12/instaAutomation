"""
Optional Web UI for  Automation using FastAPI.
Provides a simple web interface to submit URLs and monitor progress.
"""
import asyncio
from typing import List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from main import Automation
from src.models import VideoMetadata
from src.utils import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title=" Automation API", version="1.0.0")

# Global automation instance
automation_instance: Automation = None
current_task_results: List[VideoMetadata] = []


class URLRequest(BaseModel):
    """Request model for URL submission."""
    urls: List[str]
    auto_upload: bool = True
    auto_like_comments: bool = False


class StatusResponse(BaseModel):
    """Response model for status check."""
    total: int
    downloaded: int
    uploaded: int
    failed: int
    videos: List[dict]


def run_automation_background(urls: List[str], auto_upload: bool, auto_like_comments: bool = False):
    """
    Run automation in background task.
    
    Args:
        urls: List of URLs to process
        auto_upload: Whether to auto-upload
        auto_like_comments: Whether to auto-like comments
    """
    global automation_instance, current_task_results
    
    try:
        automation_instance = Automation()
        # Temporarily update settings if auto_like_comments is enabled
        if auto_like_comments:
            from src.config import settings
            settings.auto_like_comments = True
        current_task_results = automation_instance.run(urls, auto_upload=auto_upload)
    except Exception as e:
        logger.error(f"Background task error: {str(e)}", exc_info=True)


@app.get("/video/{filename:path}")
async def serve_video(filename: str):
    """Serve video files for playback."""
    from fastapi.responses import FileResponse
    from pathlib import Path
    from src.config import settings
    
    video_path = Path(settings.download_dir) / filename
    if video_path.exists() and video_path.is_file():
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=video_path.name
        )
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Video not found")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Simple HTML interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title> Automation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            h2 {
                color: #555;
                margin-top: 30px;
            }
            textarea {
                width: 100%;
                height: 150px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                box-sizing: border-box;
            }
            button {
                background-color: #405DE6;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 10px;
                margin-right: 10px;
            }
            button:hover {
                background-color: #5B51D8;
            }
            button.secondary {
                background-color: #6c757d;
            }
            button.secondary:hover {
                background-color: #5a6268;
            }
            .checkbox {
                margin: 15px 0;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            tr:hover {
                background-color: #f8f9fa;
            }
            .video-container {
                margin: 20px 0;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            video {
                width: 100%;
                max-width: 800px;
                border-radius: 8px;
                background-color: #000;
            }
            .video-info {
                margin-top: 10px;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
            }
            .play-btn {
                background-color: #28a745;
                padding: 8px 16px;
                font-size: 14px;
            }
            .play-btn:hover {
                background-color: #218838;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬  Automation</h1>
            <p>Enter  video URLs (one per line):</p>
            <form id="urlForm">
                <textarea id="urls" name="urls" placeholder="https://www..com/p/ABC123/&#10;https://www..com/p/DEF456/"></textarea>
                <div class="checkbox">
                    <label>
                        <input type="checkbox" id="autoUpload" checked>
                        Auto-upload after download
                    </label>
                </div>
                <div class="checkbox">
                    <label>
                        <input type="checkbox" id="autoLikeComments">
                        Auto-like comments on uploaded posts
                    </label>
                </div>
                <button type="submit">Start Automation</button>
            </form>
            <div id="status" class="status" style="display:none;"></div>
            <div style="margin-top: 30px;">
                <h2>📥 Downloaded Videos</h2>
                <button onclick="loadDownloads()" style="margin-bottom: 10px;">Refresh List</button>
                <div id="downloadsList"></div>
            </div>
        </div>
        <script>
            async function loadDownloads() {
                try {
                    const response = await fetch('/downloads');
                    const data = await response.json();
                    const listDiv = document.getElementById('downloadsList');
                    
                    if (data.total === 0) {
                        listDiv.innerHTML = '<p>No videos downloaded yet.</p>';
                        return;
                    }
                    
                    let html = `<p><strong>Total: ${data.total} video(s)</strong></p>`;
                    html += '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">';
                    html += '<tr style="background-color: #f0f0f0;"><th style="padding: 8px; text-align: left;">File</th><th style="padding: 8px; text-align: left;">Size</th><th style="padding: 8px; text-align: left;">Date</th></tr>';
                    
                    data.videos.forEach(video => {
                        const date = new Date(video.modified * 1000).toLocaleString();
                        const videoUrl = `/video/${encodeURIComponent(video.relative_path)}`;
                        html += `<tr>`;
                        html += `<td>📹 ${video.filename}</td>`;
                        html += `<td>${video.size_mb} MB</td>`;
                        html += `<td>${date}</td>`;
                        html += `<td><button class="play-btn" onclick='playVideo("${videoUrl}", "${video.filename}")'>▶️ Play</button></td>`;
                        html += `</tr>`;
                    });
                    
                    html += '</table>';
                    listDiv.innerHTML = html;
                } catch (error) {
                    document.getElementById('downloadsList').innerHTML = `<p>Error loading downloads: ${error.message}</p>`;
                }
            }
            
            // Load downloads on page load
            loadDownloads();
            
            function playVideo(videoUrl, filename) {
                // Remove existing video player if any
                const existing = document.getElementById('videoPlayerContainer');
                if (existing) {
                    existing.remove();
                }
                
                // Create video player container
                const container = document.createElement('div');
                container.id = 'videoPlayerContainer';
                container.className = 'video-container';
                container.innerHTML = `
                    <h3>📹 ${filename}</h3>
                    <video controls autoplay>
                        <source src="${videoUrl}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <div class="video-info">
                        <p><strong>File:</strong> ${filename}</p>
                        <p><a href="${videoUrl}" download style="color: #405DE6;">⬇️ Download Video</a></p>
                        <button onclick="this.closest('.video-container').remove()" class="secondary">Close Player</button>
                    </div>
                `;
                
                // Insert after downloads section
                const downloadsDiv = document.getElementById('downloadsList').parentElement;
                downloadsDiv.insertAdjacentElement('afterend', container);
                
                // Scroll to video player
                container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            
            document.getElementById('urlForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const urls = document.getElementById('urls').value.split('\\n').filter(u => u.trim());
                const autoUpload = document.getElementById('autoUpload').checked;
                const autoLikeComments = document.getElementById('autoLikeComments').checked;
                
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = 'Processing... Please wait.';
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({urls: urls, auto_upload: autoUpload, auto_like_comments: autoLikeComments})
                    });
                    const data = await response.json();
                    statusDiv.innerHTML = `Started processing ${data.total_urls} URL(s). Check status at /status`;
                } catch (error) {
                    statusDiv.innerHTML = `Error: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/process")
async def process_urls(request: URLRequest, background_tasks: BackgroundTasks):
    """
    Submit URLs for processing.
    
    Args:
        request: URLRequest with URLs and settings
        background_tasks: FastAPI background tasks
        
    Returns:
        Confirmation message
    """
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    # Start background task
    background_tasks.add_task(run_automation_background, request.urls, request.auto_upload, request.auto_like_comments)
    
    return {
        "message": "Processing started",
        "total_urls": len(request.urls),
        "auto_upload": request.auto_upload,
        "auto_like_comments": request.auto_like_comments
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get current processing status.
    
    Returns:
        StatusResponse with current progress
    """
    global current_task_results
    
    if not current_task_results:
        return StatusResponse(
            total=0,
            downloaded=0,
            uploaded=0,
            failed=0,
            videos=[]
        )
    
    downloaded = sum(1 for v in current_task_results if v.status.value == "downloaded")
    uploaded = sum(1 for v in current_task_results if v.status.value == "uploaded")
    failed = sum(1 for v in current_task_results if "failed" in v.status.value)
    
    return StatusResponse(
        total=len(current_task_results),
        downloaded=downloaded,
        uploaded=uploaded,
        failed=failed,
        videos=[v.to_dict() for v in current_task_results]
    )


@app.get("/downloads")
async def list_downloads():
    """
    List all downloaded video files.
    
    Returns:
        List of downloaded video files with metadata
    """
    from pathlib import Path
    from src.config import settings
    import os
    
    download_dir = Path(settings.download_dir)
    videos = []
    
    # Find all MP4 files recursively
    for video_file in download_dir.rglob("*.mp4"):
        if video_file.is_file():
            stat = video_file.stat()
            videos.append({
                "filename": video_file.name,
                "path": str(video_file),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": video_file.stat().st_mtime,
                "relative_path": str(video_file.relative_to(download_dir))
            })
    
    # Sort by modification time (newest first)
    videos.sort(key=lambda x: x["modified"], reverse=True)
    
    return {
        "total": len(videos),
        "download_dir": str(download_dir.absolute()),
        "videos": videos
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting web UI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
