"""
upload_to_.py

This module handles uploading videos to  account.
Uses instagrapi library to authenticate and post videos.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, TwoFactorRequired, ChallengeRequired

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoUploader:
    """
    Handles uploading videos to  account.
    """
    
    def __init__(self, username: str, password: str, session_file: str = None):
        """
        Initialize the uploader.
        
        Args:
            username:  username
            password:  password
            session_file: Path to save session file (for login persistence)
        """
        self.username = username
        self.password = password
        self.session_file = session_file or "session/ig_session.json"
        self.client = Client()
        
        # Create session directory if it doesn't exist
        if self.session_file:
            session_dir = Path(self.session_file).parent
            session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized uploader for username: {username}")
    
    def login(self) -> bool:
        """
        Login to  account.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                try:
                    self.client.load_settings(self.session_file)
                    logger.info("Loaded existing session")
                except Exception as e:
                    logger.warning(f"Could not load session file: {e}")
            
            # Attempt login
            try:
                self.client.login(self.username, self.password)
                logger.info("Login successful")
                
                # Save session for future use
                if self.session_file:
                    self.client.dump_settings(self.session_file)
                
                return True
                
            except TwoFactorRequired:
                logger.error("Two-factor authentication is required. Please disable 2FA or use  Graph API.")
                return False
                
            except ChallengeRequired:
                logger.error(" challenge required. Please login manually via browser first.")
                return False
                
            except LoginRequired:
                logger.warning("Session expired, attempting new login...")
                self.client.login(self.username, self.password)
                
                if self.session_file:
                    self.client.dump_settings(self.session_file)
                
                logger.info("Login successful after session refresh")
                return True
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def upload_video(self, video_path: str, caption: str = "", thumbnail_path: str = None) -> Optional[Dict]:
        """
        Upload a single video to .
        
        Args:
            video_path: Path to video file
            caption: Caption for the post
            thumbnail_path: Optional thumbnail image path
            
        Returns:
            Dictionary with upload result or None if upload fails
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        try:
            logger.info(f"Uploading video: {video_path}")
            
            # Upload video with caption
            media = self.client.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=thumbnail_path
            )
            
            upload_result = {
                "video_path": video_path,
                "media_id": media.pk,
                "caption": caption,
                "timestamp": datetime.now().isoformat(),
                "status": "uploaded",
                "url": f"https://www..com/p/{media.code}/"
            }
            
            logger.info(f"Successfully uploaded video: {upload_result['url']}")
            return upload_result
            
        except LoginRequired:
            logger.error("Session expired. Please login again.")
            if self.login():
                # Retry upload after re-login
                return self.upload_video(video_path, caption, thumbnail_path)
            return None
            
        except Exception as e:
            logger.error(f"Upload failed for {video_path}: {e}")
            return {
                "video_path": video_path,
                "status": "upload_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def upload_multiple_videos(
        self, 
        videos: List[Dict], 
        delay_between_posts: int = 3600,
        caption_prefix: str = "",
        generate_captions: bool = False
    ) -> List[Dict]:
        """
        Upload multiple videos to .
        
        Args:
            videos: List of video metadata dictionaries
            delay_between_posts: Delay in seconds between posts (default: 1 hour)
            caption_prefix: Prefix to add to all captions
            generate_captions: Whether to generate captions from filename
            
        Returns:
            List of upload result dictionaries
        """
        # Filter only successfully downloaded videos
        videos_to_upload = [v for v in videos if v.get('status') == 'downloaded']
        
        if not videos_to_upload:
            logger.warning("No videos to upload")
            return []
        
        logger.info(f"Starting upload of {len(videos_to_upload)} videos")
        
        # Login first
        if not self.login():
            logger.error("Login failed. Cannot upload videos.")
            return []
        
        upload_results = []
        
        for index, video in enumerate(videos_to_upload):
            video_path = video.get('video_path')
            if not video_path or not os.path.exists(video_path):
                logger.warning(f"Skipping video (file not found): {video.get('url', 'unknown')}")
                upload_results.append({
                    **video,
                    "status": "upload_skipped",
                    "reason": "file_not_found"
                })
                continue
            
            # Generate caption
            caption = self._generate_caption(video, caption_prefix, generate_captions)
            
            # Upload video
            logger.info(f"Uploading video {index + 1}/{len(videos_to_upload)}")
            upload_result = self.upload_video(video_path, caption)
            
            if upload_result:
                # Merge original video metadata with upload result
                combined_result = {**video, **upload_result}
                upload_results.append(combined_result)
            else:
                upload_results.append({
                    **video,
                    "status": "upload_failed",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Delay between posts (except for the last one)
            if index < len(videos_to_upload) - 1:
                delay_minutes = delay_between_posts / 60
                logger.info(f"Waiting {delay_minutes:.1f} minutes before next upload...")
                time.sleep(delay_between_posts)
        
        logger.info(f"Upload complete. Successfully uploaded {len([r for r in upload_results if r.get('status') == 'uploaded'])}/{len(videos_to_upload)} videos")
        return upload_results
    
    def _generate_caption(self, video: Dict, prefix: str = "", generate: bool = False) -> str:
        """
        Generate caption for video.
        
        Args:
            video: Video metadata dictionary
            prefix: Prefix to add to caption
            generate: Whether to generate caption from metadata
            
        Returns:
            Generated caption string
        """
        caption_parts = []
        
        if prefix:
            caption_parts.append(prefix)
        
        if generate:
            # Generate caption from video metadata
            title = video.get('title', '')
            if title:
                caption_parts.append(title)
            
            # Add hashtags from filename or title
            filename = video.get('filename', '')
            if filename:
                # Extract meaningful words from filename
                words = filename.replace('_', ' ').replace('.mp4', '').split()
                if len(words) > 1:
                    caption_parts.append(' '.join(words))
        else:
            # Use existing title or create simple caption
            title = video.get('title', f"Video {video.get('shortcode', '')}")
            caption_parts.append(title)
        
        return ' '.join(caption_parts).strip()
    
    def save_upload_results(self, results: List[Dict], filename: str = "upload_results.json"):
        """
        Save upload results to JSON file.
        
        Args:
            results: List of upload result dictionaries
            filename: Output filename
        """
        results_dir = Path("downloads")
        results_dir.mkdir(parents=True, exist_ok=True)
        results_path = results_dir / filename
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved upload results to {results_path}")


def main():
    """
    Example usage of the uploader.
    """
    # Example usage (replace with actual credentials)
    username = "your_username"
    password = "your_password"
    
    uploader = VideoUploader(username, password)
    
    # Example videos (should come from download_videos.py output)
    example_videos = [
        {
            "video_path": "downloads/video_1_example.mp4",
            "title": "Example Video",
            "status": "downloaded"
        }
    ]
    
    uploader.upload_multiple_videos(example_videos)


if __name__ == "__main__":
    main()
