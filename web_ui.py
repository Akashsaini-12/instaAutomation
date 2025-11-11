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
        logger.info(f"Starting background task: {len(urls)} URLs, auto_upload={auto_upload}, auto_like_comments={auto_like_comments}")
        automation_instance = Automation()
        
        # Temporarily update settings if auto_like_comments is enabled
        if auto_like_comments:
            from src.config import settings
            settings.auto_like_comments = True
            logger.info("Auto-like comments enabled")
        
        current_task_results = automation_instance.run(urls, auto_upload=auto_upload)
        logger.info(f"Background task completed: {len(current_task_results)} videos processed")
    except Exception as e:
        logger.error(f"Background task error: {str(e)}", exc_info=True)
        # Create error results for failed URLs
        current_task_results = []
        for url in urls:
            from src.models import VideoMetadata, VideoStatus
            error_meta = VideoMetadata(
                url=url,
                status=VideoStatus.DOWNLOAD_FAILED,
                error_message=str(e)
            )
            current_task_results.append(error_meta)


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
    """Enhanced modern HTML interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎬 Video Automation Hub</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            :root {
                --primary: #405DE6;
                --secondary: #5B51D8;
                --accent: #833AB4;
                --pink: #C13584;
                --red: #E1306C;
                --orange: #FD1D1D;
                --yellow: #FCAF45;
                --gradient: linear-gradient(45deg, #405DE6, #5B51D8, #833AB4, #C13584, #E1306C, #FD1D1D, #FCAF45);
                --bg-light: #FAFAFA;
                --bg-white: #FFFFFF;
                --text-primary: #262626;
                --text-secondary: #8E8E8E;
                --border: #DBDBDB;
                --success: #10B981;
                --error: #EF4444;
                --warning: #F59E0B;
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: var(--bg-light);
                color: var(--text-primary);
                line-height: 1.6;
                min-height: 100vh;
            }

            .header {
                background: var(--gradient);
                color: white;
                padding: 2rem 0;
                text-align: center;
                box-shadow: var(--shadow-md);
                margin-bottom: 2rem;
            }

            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }

            .header p {
                font-size: 1.1rem;
                opacity: 0.95;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 1.5rem;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }

            .stat-card {
                background: var(--bg-white);
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: var(--shadow-sm);
                border: 1px solid var(--border);
                transition: all 0.3s ease;
            }

            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }

            .stat-card .label {
                font-size: 0.875rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.5rem;
            }

            .stat-card .value {
                font-size: 2rem;
                font-weight: 700;
                background: var(--gradient);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .card {
                background: var(--bg-white);
                border-radius: 16px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: var(--shadow-sm);
                border: 1px solid var(--border);
                transition: all 0.3s ease;
            }

            .card:hover {
                box-shadow: var(--shadow-md);
            }

            .card-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            .form-group label {
                display: block;
                font-weight: 500;
                margin-bottom: 0.75rem;
                color: var(--text-primary);
                font-size: 0.95rem;
            }

            textarea {
                width: 100%;
                min-height: 150px;
                padding: 1rem;
                border: 2px solid var(--border);
                border-radius: 8px;
                font-size: 0.95rem;
                font-family: inherit;
                resize: vertical;
                transition: all 0.3s ease;
                background: var(--bg-white);
            }

            textarea:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(64, 93, 230, 0.1);
            }

            .checkbox-group {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin: 1.5rem 0;
            }

            .checkbox-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem;
                background: var(--bg-light);
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .checkbox-item:hover {
                background: #F0F0F0;
            }

            .checkbox-item input[type="checkbox"] {
                width: 20px;
                height: 20px;
                cursor: pointer;
                accent-color: var(--primary);
            }

            .checkbox-item label {
                cursor: pointer;
                font-weight: 500;
                margin: 0;
                flex: 1;
            }

            .btn {
                padding: 0.875rem 2rem;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                text-decoration: none;
            }

            .btn-primary {
                background: var(--gradient);
                color: white;
                box-shadow: var(--shadow-md);
            }

            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }

            .btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .btn-secondary {
                background: var(--bg-white);
                color: var(--text-primary);
                border: 2px solid var(--border);
            }

            .btn-secondary:hover {
                background: var(--bg-light);
                border-color: var(--primary);
            }

            .btn-success {
                background: var(--success);
                color: white;
            }

            .btn-danger {
                background: var(--error);
                color: white;
            }

            .btn-sm {
                padding: 0.5rem 1rem;
                font-size: 0.875rem;
            }

            .status-container {
                margin-top: 1.5rem;
                min-height: 60px;
            }

            .status-card {
                padding: 1.25rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                display: none;
                animation: slideIn 0.3s ease;
            }

            .status-card.show {
                display: block;
            }

            .status-card.info {
                background: #DBEAFE;
                color: #1E40AF;
                border-left: 4px solid #3B82F6;
            }

            .status-card.success {
                background: #D1FAE5;
                color: #065F46;
                border-left: 4px solid var(--success);
            }

            .status-card.error {
                background: #FEE2E2;
                color: #991B1B;
                border-left: 4px solid var(--error);
            }

            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .progress-container {
                margin-top: 1rem;
                display: none;
            }

            .progress-container.show {
                display: block;
            }

            .progress-bar {
                width: 100%;
                height: 8px;
                background: var(--bg-light);
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }

            .progress-fill {
                height: 100%;
                background: var(--gradient);
                border-radius: 4px;
                transition: width 0.3s ease;
                width: 0%;
            }

            .progress-text {
                font-size: 0.875rem;
                color: var(--text-secondary);
                text-align: center;
            }

            .videos-section {
                margin-top: 2rem;
            }

            .section-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }

            .videos-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 1.5rem;
            }

            .video-card {
                background: var(--bg-white);
                border-radius: 12px;
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                border: 1px solid var(--border);
                transition: all 0.3s ease;
                position: relative;
            }

            .video-card:hover {
                transform: translateY(-4px);
                box-shadow: var(--shadow-lg);
            }

            .video-thumbnail {
                width: 100%;
                height: 200px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                cursor: pointer;
            }

            .video-thumbnail video {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .play-overlay {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.7);
                border-radius: 50%;
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 24px;
                transition: all 0.3s ease;
            }

            .video-thumbnail:hover .play-overlay {
                background: rgba(0,0,0,0.9);
                transform: translate(-50%, -50%) scale(1.1);
            }

            .video-info {
                padding: 1rem;
            }

            .video-title {
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: var(--text-primary);
                font-size: 0.95rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .video-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-bottom: 1rem;
            }

            .video-actions {
                display: flex;
                gap: 0.5rem;
            }

            .video-actions .btn {
                flex: 1;
                justify-content: center;
            }

            .empty-state {
                text-align: center;
                padding: 3rem;
                color: var(--text-secondary);
            }

            .empty-state-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
                opacity: 0.5;
            }

            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .toast {
                background: var(--bg-white);
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: var(--shadow-xl);
                border-left: 4px solid var(--primary);
                min-width: 300px;
                animation: slideInRight 0.3s ease;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }

            .toast.success {
                border-left-color: var(--success);
            }

            .toast.error {
                border-left-color: var(--error);
            }

            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            @keyframes fadeOut {
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }

            .toast.fade-out {
                animation: fadeOut 0.3s ease forwards;
            }

            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                z-index: 2000;
                align-items: center;
                justify-content: center;
            }

            .modal.show {
                display: flex;
            }

            .modal-content {
                background: var(--bg-white);
                border-radius: 16px;
                max-width: 900px;
                width: 90%;
                max-height: 90vh;
                overflow: hidden;
                box-shadow: var(--shadow-xl);
            }

            .modal-header {
                padding: 1.5rem;
                border-bottom: 1px solid var(--border);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .modal-body {
                padding: 1.5rem;
                max-height: 70vh;
                overflow-y: auto;
            }

            .modal-body video {
                width: 100%;
                border-radius: 8px;
            }

            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2rem;
                }

                .container {
                    padding: 0 1rem;
                }

                .videos-grid {
                    grid-template-columns: 1fr;
                }

                .stats-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>🎬 Video Automation Hub</h1>
                <p>Download, manage, and upload videos with ease</p>
            </div>
        </div>

        <div class="container">
            <!-- Statistics Dashboard -->
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="label">Total Videos</div>
                    <div class="value" id="statTotal">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Total Size</div>
                    <div class="value" id="statSize">0 MB</div>
                </div>
                <div class="stat-card">
                    <div class="label">Last Updated</div>
                    <div class="value" id="statDate" style="font-size: 1.2rem;">Just now</div>
                </div>
            </div>

            <!-- Main Form Card -->
            <div class="card">
                <h2 class="card-title">📥 Add Video URLs</h2>
                <form id="urlForm">
                    <div class="form-group">
                        <label for="urls">Paste Instagram video URLs (one per line)</label>
                        <textarea 
                            id="urls" 
                            name="urls" 
                            placeholder="https://www.instagram.com/p/ABC123/&#10;https://www.instagram.com/reel/DEF456/&#10;..."></textarea>
                    </div>

                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="autoUpload" checked>
                            <label for="autoUpload">
                                <strong>Auto-upload</strong> - Automatically upload videos after download
                            </label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="autoLikeComments">
                            <label for="autoLikeComments">
                                <strong>Auto-like comments</strong> - Automatically like comments on uploaded posts
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary" id="submitBtn">
                        <span>🚀 Start Automation</span>
                    </button>
                </form>

                <div class="status-container">
                    <div id="statusCard" class="status-card"></div>
                    <div class="progress-container" id="progressContainer">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <div class="progress-text" id="progressText">Initializing...</div>
                    </div>
                </div>
            </div>

            <!-- Videos Section -->
            <div class="videos-section">
                <div class="section-header">
                    <h2 class="card-title">📹 Downloaded Videos</h2>
                    <button onclick="loadDownloads()" class="btn btn-secondary btn-sm">
                        🔄 Refresh
                    </button>
                </div>
                <div id="downloadsList" class="videos-grid">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No videos downloaded yet.</p>
                        <p style="margin-top: 0.5rem; font-size: 0.875rem;">Add URLs above to get started!</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Toast Container -->
        <div class="toast-container" id="toastContainer"></div>

        <!-- Video Modal -->
        <div class="modal" id="videoModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="modalTitle">Video Player</h3>
                    <button onclick="closeModal()" class="btn btn-secondary btn-sm">✕ Close</button>
                </div>
                <div class="modal-body" id="modalBody"></div>
            </div>
        </div>

        <script>
            let statusCheckInterval = null;
            let currentStats = { total: 0, size: 0 };

            // Toast notification system
            function showToast(message, type = 'info') {
                const container = document.getElementById('toastContainer');
                const toast = document.createElement('div');
                toast.className = `toast ${type}`;
                
                const icons = {
                    success: '✅',
                    error: '❌',
                    info: 'ℹ️'
                };
                
                toast.innerHTML = `
                    <span style="font-size: 1.5rem;">${icons[type] || icons.info}</span>
                    <span>${message}</span>
                `;
                
                container.appendChild(toast);
                
                setTimeout(() => {
                    toast.classList.add('fade-out');
                    setTimeout(() => toast.remove(), 300);
                }, 3000);
            }

            // Show status
            function showStatus(message, type = 'info') {
                const statusCard = document.getElementById('statusCard');
                statusCard.className = `status-card ${type} show`;
                statusCard.innerHTML = message;
            }

            // Update progress
            function updateProgress(percent, text) {
                const container = document.getElementById('progressContainer');
                const fill = document.getElementById('progressFill');
                const textEl = document.getElementById('progressText');
                
                container.classList.add('show');
                fill.style.width = percent + '%';
                textEl.textContent = text || `${percent}% complete`;
            }

            // Load downloads
            async function loadDownloads() {
                try {
                    const response = await fetch('/downloads');
                    const data = await response.json();
                    const listDiv = document.getElementById('downloadsList');
                    
                    // Update stats
                    currentStats.total = data.total;
                    currentStats.size = data.videos.reduce((sum, v) => sum + v.size_mb, 0);
                    
                    document.getElementById('statTotal').textContent = data.total;
                    document.getElementById('statSize').textContent = currentStats.size.toFixed(2) + ' MB';
                    
                    if (data.videos.length > 0) {
                        const latest = data.videos[0];
                        const date = new Date(latest.modified * 1000);
                        const now = new Date();
                        const diff = Math.floor((now - date) / 1000 / 60);
                        document.getElementById('statDate').textContent = diff < 1 ? 'Just now' : `${diff} min ago`;
                    }
                    
                    if (data.total === 0) {
                        listDiv.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-state-icon">📭</div>
                                <p>No videos downloaded yet.</p>
                                <p style="margin-top: 0.5rem; font-size: 0.875rem;">Add URLs above to get started!</p>
                            </div>
                        `;
                        return;
                    }
                    
                    let html = '';
                    data.videos.forEach(video => {
                        const date = new Date(video.modified * 1000);
                        const videoUrl = `/video/${encodeURIComponent(video.relative_path)}`;
                        const relativePath = encodeURIComponent(video.relative_path);
                        
                        html += `
                            <div class="video-card" id="card-${relativePath.replace(/[^a-zA-Z0-9]/g, '_')}">
                                <div class="video-thumbnail" onclick='playVideoModal("${videoUrl}", "${video.filename}")'>
                                    <video preload="metadata" muted>
                                        <source src="${videoUrl}" type="video/mp4">
                                    </video>
                                    <div class="play-overlay">▶</div>
                                </div>
                                <div class="video-info">
                                    <div class="video-title" title="${video.filename}">${video.filename}</div>
                                    <div class="video-meta">
                                        <span>📦 ${video.size_mb} MB</span>
                                        <span>📅 ${date.toLocaleDateString()}</span>
                                    </div>
                                    <div class="video-actions">
                                        <button class="btn btn-success btn-sm" onclick='playVideoModal("${videoUrl}", "${video.filename}")'>
                                            ▶️ Play
                                        </button>
                                        <button class="btn btn-danger btn-sm" onclick='deleteVideo("${relativePath}", "${video.filename}")'>
                                            🗑️ Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    
                    listDiv.innerHTML = html;
                    
                    // Load video thumbnails
                    listDiv.querySelectorAll('video[preload="metadata"]').forEach(video => {
                        video.addEventListener('loadedmetadata', function() {
                            this.currentTime = 1;
                        });
                    });
                } catch (error) {
                    showToast(`Error loading downloads: ${error.message}`, 'error');
                }
            }

            // Delete video
            async function deleteVideo(relativePath, filename) {
                if (!confirm(`Are you sure you want to delete "${filename}"?\\n\\nThis action cannot be undone!`)) {
                    return;
                }
                
                try {
                    const response = await fetch(`/video/${relativePath}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        const cardId = `card-${relativePath.replace(/[^a-zA-Z0-9]/g, '_')}`;
                        const card = document.getElementById(cardId);
                        if (card) {
                            card.style.transition = 'all 0.3s ease';
                            card.style.opacity = '0';
                            card.style.transform = 'scale(0.9)';
                            setTimeout(() => {
                                card.remove();
                                loadDownloads();
                            }, 300);
                        }
                        showToast(result.message, 'success');
                    } else {
                        throw new Error(result.detail || 'Failed to delete video');
                    }
                } catch (error) {
                    showToast(`Error: ${error.message}`, 'error');
                }
            }

            // Play video in modal
            function playVideoModal(videoUrl, filename) {
                const modal = document.getElementById('videoModal');
                const modalTitle = document.getElementById('modalTitle');
                const modalBody = document.getElementById('modalBody');
                
                modalTitle.textContent = filename;
                modalBody.innerHTML = `
                    <video controls autoplay style="width: 100%; border-radius: 8px;">
                        <source src="${videoUrl}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <div style="margin-top: 1rem; display: flex; gap: 1rem; justify-content: center;">
                        <a href="${videoUrl}" download class="btn btn-primary">
                            ⬇️ Download Video
                        </a>
                    </div>
                `;
                
                modal.classList.add('show');
            }

            // Close modal
            function closeModal() {
                const modal = document.getElementById('videoModal');
                const modalBody = document.getElementById('modalBody');
                modal.classList.remove('show');
                modalBody.innerHTML = '';
            }

            // Close modal on outside click
            document.getElementById('videoModal').addEventListener('click', function(e) {
                if (e.target === this) {
                    closeModal();
                }
            });

            // Form submission
            document.getElementById('urlForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const urls = document.getElementById('urls').value.split('\\n')
                    .map(url => url.trim())
                    .filter(url => url && url.length > 0);
                
                if (urls.length === 0) {
                    showToast('Please enter at least one URL', 'error');
                    return;
                }
                
                const autoUpload = document.getElementById('autoUpload').checked;
                const autoLikeComments = document.getElementById('autoLikeComments').checked;
                const submitBtn = document.getElementById('submitBtn');
                
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading"></span> Starting...';
                
                showStatus('🚀 Starting automation...', 'info');
                updateProgress(10, 'Initializing...');
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            urls: urls,
                            auto_upload: autoUpload,
                            auto_like_comments: autoLikeComments
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showStatus(`✅ Started processing ${data.total_urls} URL(s)`, 'success');
                        updateProgress(20, 'Processing started...');
                        showToast(`Processing ${data.total_urls} video(s)`, 'success');
                        
                        // Start polling for status
                        startStatusPolling();
                    } else {
                        throw new Error(data.detail || 'Failed to start automation');
                    }
                } catch (error) {
                    showStatus(`❌ Error: ${error.message}`, 'error');
                    showToast(`Error: ${error.message}`, 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<span>🚀 Start Automation</span>';
                    updateProgress(0, '');
                    document.getElementById('progressContainer').classList.remove('show');
                }
            });

            // Status polling
            function startStatusPolling() {
                if (statusCheckInterval) clearInterval(statusCheckInterval);
                
                let progress = 20;
                statusCheckInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/status');
                        const status = await response.json();
                        
                        if (status.total > 0) {
                            const total = status.total;
                            const completed = status.downloaded + status.uploaded;
                            progress = 20 + Math.floor((completed / total) * 70);
                            
                            updateProgress(progress, `Processing: ${completed}/${total} completed`);
                            
                            let statusText = `📊 Progress: ${status.downloaded} downloaded`;
                            if (status.uploaded > 0) {
                                statusText += `, ${status.uploaded} uploaded`;
                            }
                            if (status.failed > 0) {
                                statusText += `, ${status.failed} failed`;
                            }
                            showStatus(statusText, 'info');
                        }
                    } catch (error) {
                        console.error('Status check error:', error);
                    }
                }, 2000);
                
                // Stop polling after 5 minutes
                setTimeout(() => {
                    if (statusCheckInterval) {
                        clearInterval(statusCheckInterval);
                        statusCheckInterval = null;
                        updateProgress(100, 'Processing complete');
                        showStatus('✅ Processing complete! Refresh the videos list to see results.', 'success');
                        document.getElementById('submitBtn').disabled = false;
                        document.getElementById('submitBtn').innerHTML = '<span>🚀 Start Automation</span>';
                        loadDownloads();
                    }
                }, 300000); // 5 minutes
            }

            // Load downloads on page load
            loadDownloads();
            
            // Auto-refresh downloads every 30 seconds
            setInterval(loadDownloads, 30000);
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
    
    downloaded = sum(1 for v in current_task_results if v.status.value in ("downloaded", "uploading", "uploaded"))
    uploaded = sum(1 for v in current_task_results if v.status.value == "uploaded")
    failed = sum(1 for v in current_task_results if v.status.value in ("download_failed", "upload_failed"))
    
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


@app.delete("/video/{filename:path}")
async def delete_video(filename: str):
    """
    Delete a video file.
    
    Args:
        filename: Relative path to the video file from download directory
        
    Returns:
        Success or error message
    """
    from pathlib import Path
    from src.config import settings
    
    try:
        video_path = Path(settings.download_dir) / filename
        
        # Security check: ensure the path is within download directory
        try:
            video_path.resolve().relative_to(Path(settings.download_dir).resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid file path")
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        if not video_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Delete the file
        video_path.unlink()
        logger.info(f"Deleted video file: {video_path}")
        
        return {
            "success": True,
            "message": f"Video '{filename}' deleted successfully",
            "filename": filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video {filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting video: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for deployment platforms) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting web UI server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
