"""
download_videos.py

This module handles downloading videos from  URLs.
Uses instaloader library to fetch and download  videos.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import instaloader
from urllib.parse import urlparse
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Handles downloading  videos from URLs.
    """
    
    def __init__(self, download_dir: str = "downloads", max_retries: int = 3, retry_delay: int = 5):
        """
        Initialize the downloader.
        
        Args:
            download_dir: Directory to save downloaded videos
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (seconds)
        """
        self.download_dir = Path(download_dir)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Create download directory if it doesn't exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize instaloader
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        logger.info(f"Initialized downloader with directory: {self.download_dir}")
    
    def extract_shortcode_from_url(self, url: str) -> Optional[str]:
        """
        Extract  post shortcode from URL.
        
        Args:
            url:  post URL
            
        Returns:
            Shortcode if found, None otherwise
        """
        try:
            # Handle different  URL formats
            # https://www..com/p/SHORTCODE/
            # https://www..com/reel/SHORTCODE/
            # https://.com/p/SHORTCODE/
            
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            
            if len(path_parts) >= 2:
                # Get the part after 'p' or 'reel'
                if path_parts[0] in ['p', 'reel']:
                    return path_parts[1].split('?')[0]  # Remove query parameters
            
            logger.warning(f"Could not extract shortcode from URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting shortcode from {url}: {e}")
            return None
    
    def download_video(self, url: str, video_index: int = 0) -> Optional[Dict]:
        """
        Download a single video from  URL.
        
        Args:
            url:  post/reel URL
            video_index: Index of video in the batch (for naming)
            
        Returns:
            Dictionary with video metadata or None if download fails
        """
        shortcode = self.extract_shortcode_from_url(url)
        
        if not shortcode:
            logger.error(f"Invalid URL format: {url}")
            return None
        
        logger.info(f"Downloading video {video_index + 1}: {shortcode}")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Get post from 
                post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                
                # Check if post has video
                if not post.is_video:
                    logger.warning(f"Post {shortcode} is not a video")
                    return None
                
                # Prepare metadata
                timestamp = datetime.now().isoformat()
                filename = f"video_{video_index + 1}_{shortcode}.mp4"
                video_path = self.download_dir / filename
                
                # Download the video
                self.loader.download_post(post, target=str(self.download_dir))
                
                # Find the downloaded video file (instaloader names it with shortcode)
                # Instaloader saves as: {shortcode}.mp4
                downloaded_file = self.download_dir / f"{shortcode}.mp4"
                
                if not downloaded_file.exists():
                    # Try alternative naming
                    downloaded_file = self.download_dir / f"{shortcode}.mp4"
                    for file in self.download_dir.glob(f"{shortcode}*"):
                        if file.suffix == '.mp4':
                            downloaded_file = file
                            break
                
                if downloaded_file.exists():
                    # Rename to our standard format if needed
                    if downloaded_file.name != filename:
                        final_path = self.download_dir / filename
                        downloaded_file.rename(final_path)
                        video_path = final_path
                    else:
                        video_path = downloaded_file
                    
                    # Prepare metadata
                    video_metadata = {
                        "url": url,
                        "shortcode": shortcode,
                        "title": post.caption[:100] if post.caption else f"Video {shortcode}",
                        "video_path": str(video_path.absolute()),
                        "filename": filename,
                        "timestamp": timestamp,
                        "status": "downloaded",
                        "file_size": os.path.getsize(video_path),
                        "duration": post.video_duration if hasattr(post, 'video_duration') else None,
                        "owner_username": post.owner_username,
                        "download_index": video_index
                    }
                    
                    logger.info(f"Successfully downloaded: {filename} ({video_metadata['file_size']} bytes)")
                    return video_metadata
                else:
                    logger.error(f"Video file not found after download: {shortcode}")
                    
            except instaloader.exceptions.InstaloaderException as e:
                logger.error(f"Instaloader error (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error downloading {url} (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
        
        logger.error(f"Failed to download video after {self.max_retries} attempts: {url}")
        return None
    
    def download_multiple_videos(self, urls: List[str]) -> List[Dict]:
        """
        Download multiple videos from a list of URLs.
        
        Args:
            urls: List of  video URLs
            
        Returns:
            List of video metadata dictionaries
        """
        logger.info(f"Starting download of {len(urls)} videos")
        downloaded_videos = []
        
        for index, url in enumerate(urls):
            logger.info(f"Processing video {index + 1}/{len(urls)}")
            video_metadata = self.download_video(url, index)
            
            if video_metadata:
                downloaded_videos.append(video_metadata)
            else:
                # Add failed entry with error status
                downloaded_videos.append({
                    "url": url,
                    "status": "download_failed",
                    "timestamp": datetime.now().isoformat(),
                    "download_index": index
                })
            
            # Small delay between downloads to avoid rate limiting
            if index < len(urls) - 1:
                time.sleep(2)
        
        logger.info(f"Download complete. Successfully downloaded {len([v for v in downloaded_videos if v.get('status') == 'downloaded'])}/{len(urls)} videos")
        return downloaded_videos
    
    def save_metadata(self, videos: List[Dict], filename: str = "video_metadata.json"):
        """
        Save video metadata to JSON file.
        
        Args:
            videos: List of video metadata dictionaries
            filename: Output filename
        """
        metadata_path = self.download_dir / filename
        with open(metadata_path, 'w') as f:
            json.dump(videos, f, indent=2)
        logger.info(f"Saved metadata to {metadata_path}")


def main():
    """
    Example usage of the downloader.
    """
    # Example URLs (replace with actual  URLs)
    test_urls = [
        "https://www..com/p/EXAMPLE_SHORTCODE_1/",
        "https://www..com/reel/EXAMPLE_SHORTCODE_2/"
    ]
    
    downloader = VideoDownloader(download_dir="downloads")
    videos = downloader.download_multiple_videos(test_urls)
    downloader.save_metadata(videos)


if __name__ == "__main__":
    main()
