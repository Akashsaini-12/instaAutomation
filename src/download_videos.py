"""
 video downloading module using instaloader.
Handles downloading videos from  URLs with metadata extraction.
"""
import os
import time
import requests
from pathlib import Path
from typing import List, Optional

import instaloader
from instaloader import Post, Instaloader

from src.config import settings
from src.models import VideoMetadata, VideoStatus
from src.utils import (
    setup_logger,
    validate__url,
    extract_post_id_from_url,
    get_file_size,
    sanitize_filename
)

logger = setup_logger(__name__)


class VideoDownloader:
    """Class to handle downloading  videos."""
    
    def __init__(self):
        """Initialize the video downloader with instaloader instance."""
        self.loader = Instaloader(
            download_videos=False,  # We'll download manually
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            max_connection_attempts=3
        )
        self.download_dir = Path(settings.download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, url: str) -> VideoMetadata:
        """
        Download a single video from  URL.
        
        Args:
            url:  post/reel URL
            
        Returns:
            VideoMetadata object with download information
        """
        metadata = VideoMetadata(url=url, status=VideoStatus.PENDING)
        
        try:
            # Validate URL
            if not validate__url(url):
                raise ValueError(f"Invalid  URL: {url}")
            
            logger.info(f"Starting download for URL: {url}")
            metadata.status = VideoStatus.DOWNLOADING
            
            # Extract post shortcode from URL
            post_id = extract_post_id_from_url(url)
            if not post_id:
                raise ValueError(f"Could not extract post ID from URL: {url}")
            
            logger.info(f"Extracted post ID: {post_id}")
            
            # Load post
            try:
                post = Post.from_shortcode(self.loader.context, post_id)
            except Exception as e:
                raise Exception(f"Failed to load post: {str(e)}")
            
            # Check if post has video
            if not post.is_video:
                raise ValueError(f"Post {url} does not contain a video")
            
            # Get video title/caption
            caption = post.caption if post.caption else f"Post_{post_id}"
            metadata.title = caption[:200] if caption else None  # Limit caption length
            
            # Get video URL
            if not hasattr(post, 'video_url') or not post.video_url:
                raise ValueError("Video URL not available for this post")
            
            video_url = post.video_url
            logger.info(f"Video URL obtained, starting download...")
            
            # Download video directly using requests
            logger.info(f"Downloading video from URL to: {self.download_dir}")
            
            # Create filename
            timestamp = int(time.time())
            filename = f"{post_id}_{timestamp}.mp4"
            video_path = self.download_dir / filename
            
            # Download the video file
            response = requests.get(video_url, stream=True, timeout=60, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Get file size from headers
            total_size = int(response.headers.get('content-length', 0))
            
            # Write video to file
            downloaded_size = 0
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            if downloaded_size % (1024 * 1024) < 8192:  # Log every MB
                                logger.info(f"Downloaded: {downloaded_size / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({percent:.1f}%)")
            
            # Verify file was downloaded
            if not video_path.exists() or video_path.stat().st_size == 0:
                raise FileNotFoundError(f"Downloaded file is empty or doesn't exist: {video_path}")
            
            # Update metadata
            metadata.file_path = str(video_path.absolute())
            metadata.file_size = get_file_size(metadata.file_path)
            metadata.duration = getattr(post, 'video_duration', None)
            metadata.status = VideoStatus.DOWNLOADED
            
            logger.info(
                f"✓ Successfully downloaded video: {metadata.file_path} "
                f"({metadata.file_size / (1024*1024):.2f} MB)"
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to download video from {url}: {error_msg}")
            metadata.status = VideoStatus.DOWNLOAD_FAILED
            metadata.error_message = error_msg
        
        return metadata
    
    def download_multiple_videos(self, urls: List[str]) -> List[VideoMetadata]:
        """
        Download multiple videos from  URLs.
        
        Args:
            urls: List of  post/reel URLs
            
        Returns:
            List of VideoMetadata objects
        """
        logger.info(f"Starting batch download for {len(urls)} videos")
        results = []
        
        for idx, url in enumerate(urls, 1):
            logger.info(f"Processing video {idx}/{len(urls)}")
            metadata = self.download_video(url)
            results.append(metadata)
            
            # Log status
            if metadata.status == VideoStatus.DOWNLOADED:
                logger.info(f"✓ Video {idx}/{len(urls)} downloaded successfully")
            else:
                logger.warning(f"✗ Video {idx}/{len(urls)} failed: {metadata.error_message}")
        
        # Summary
        successful = sum(1 for m in results if m.status == VideoStatus.DOWNLOADED)
        failed = len(results) - successful
        logger.info(f"Download complete: {successful} successful, {failed} failed")
        
        return results
    
    def _find_downloaded_video(self, post_id: str) -> Optional[Path]:
        """
        Find the downloaded video file by searching in download directory.
        
        Args:
            post_id:  post shortcode/ID
            
        Returns:
            Path to video file if found, None otherwise
        """
        # Get all .mp4 files recursively, sorted by modification time (newest first)
        all_mp4_files = sorted(
            self.download_dir.rglob("*.mp4"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )
        
        # First, try to find files with post_id in the name/path
        for file_path in all_mp4_files:
            if file_path.is_file() and post_id in str(file_path):
                return file_path
        
        # If no match found, return the most recently modified .mp4 file
        # (assuming it's the one we just downloaded)
        if all_mp4_files:
            most_recent = all_mp4_files[0]
            # Only return if it was modified recently (within last 5 minutes)
            file_age = time.time() - most_recent.stat().st_mtime
            if file_age < 300:  # 5 minutes
                return most_recent
        
        return None
    
    def cleanup(self):
        """Cleanup resources (if needed)."""
        pass  # Instaloader doesn't require explicit cleanup
