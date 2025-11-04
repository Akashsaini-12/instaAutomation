"""
Main automation script for  video download and upload.
Orchestrates the complete flow: download videos -> upload to .
"""
import sys
from typing import List, Optional

from src.config import settings
from src.download_videos import VideoDownloader
from src.models import VideoMetadata, VideoStatus
from src.upload_to_instagram import Uploader
from src.utils import setup_logger, validate__url

logger = setup_logger(__name__)


class Automation:
    """
    Main automation class that handles the complete workflow:
    1. Download videos from  URLs
    2. Upload downloaded videos to  account
    """
    
    def __init__(self):
        """Initialize automation with downloader and uploader."""
        self.downloader = VideoDownloader()
        self.uploader = Uploader(
            username=settings.instagram_username,
            password=settings.instagram_password
        )
        self.videos: List[VideoMetadata] = []
    
    def validate_urls(self, urls: List[str]) -> tuple[List[str], List[str]]:
        """
        Validate  URLs.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Tuple of (valid_urls, invalid_urls)
        """
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            if validate__url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
                logger.warning(f"Invalid  URL: {url}")
        
        return valid_urls, invalid_urls
    
    def download_videos(self, urls: List[str]) -> List[VideoMetadata]:
        """
        Download videos from  URLs.
        
        Args:
            urls: List of  post/reel URLs
            
        Returns:
            List of VideoMetadata objects
        """
        logger.info("=" * 60)
        logger.info("STEP 1: DOWNLOADING VIDEOS")
        logger.info("=" * 60)
        
        # Validate URLs first
        valid_urls, invalid_urls = self.validate_urls(urls)
        
        if invalid_urls:
            logger.warning(f"Skipping {len(invalid_urls)} invalid URLs")
        
        if not valid_urls:
            logger.error("No valid URLs to download")
            return []
        
        # Download videos
        metadata_list = self.downloader.download_multiple_videos(valid_urls)
        self.videos = metadata_list
        
        # Log summary
        successful_downloads = [
            m for m in metadata_list if m.status == VideoStatus.DOWNLOADED
        ]
        failed_downloads = [
            m for m in metadata_list if m.status == VideoStatus.DOWNLOAD_FAILED
        ]
        
        logger.info(f"\nDownload Summary:")
        logger.info(f"  ✓ Successful: {len(successful_downloads)}")
        logger.info(f"  ✗ Failed: {len(failed_downloads)}")
        
        if failed_downloads:
            logger.info("\nFailed downloads:")
            for meta in failed_downloads:
                logger.info(f"  - {meta.url}: {meta.error_message}")
        
        return metadata_list
    
    def upload_videos(self, videos: Optional[List[VideoMetadata]] = None) -> List[VideoMetadata]:
        """
        Upload videos to  account.
        
        Args:
            videos: List of VideoMetadata objects (uses self.videos if None)
            
        Returns:
            List of updated VideoMetadata objects
        """
        logger.info("=" * 60)
        logger.info("STEP 2: UPLOADING VIDEOS TO ")
        logger.info("=" * 60)
        
        videos_to_upload = videos or self.videos
        
        if not videos_to_upload:
            logger.error("No videos to upload")
            return []
        
        # Check if we have any downloaded videos
        downloaded_videos = [
            v for v in videos_to_upload if v.status == VideoStatus.DOWNLOADED
        ]
        
        if not downloaded_videos:
            logger.error("No videos in DOWNLOADED status. Cannot upload.")
            return videos_to_upload
        
        # Login to 
        logger.info("Authenticating with ...")
        if not self.uploader.login():
            logger.error("Failed to login to . Cannot proceed with uploads.")
            # Mark all videos as upload failed
            for video in downloaded_videos:
                video.status = VideoStatus.UPLOAD_FAILED
                video.error_message = "Authentication failed"
            return videos_to_upload
        
        # Upload videos with auto-like feature if enabled
        auto_like = getattr(settings, 'auto_like_comments', False)
        if auto_like:
            logger.info("✓ Auto-like comments feature is ENABLED")
        updated_videos = self.uploader.upload_multiple_videos(
            downloaded_videos,
            auto_like_comments=auto_like
        )
        self.videos = updated_videos
        
        # Log summary
        successful_uploads = [
            v for v in updated_videos if v.status == VideoStatus.UPLOADED
        ]
        failed_uploads = [
            v for v in updated_videos if v.status == VideoStatus.UPLOAD_FAILED
        ]
        
        logger.info(f"\nUpload Summary:")
        logger.info(f"  ✓ Successful: {len(successful_uploads)}")
        logger.info(f"  ✗ Failed: {len(failed_uploads)}")
        
        if failed_uploads:
            logger.info("\nFailed uploads:")
            for meta in failed_uploads:
                logger.info(f"  - {meta.url}: {meta.error_message}")
        
        # Logout
        self.uploader.logout()
        
        return updated_videos
    
    def run(self, urls: List[str], auto_upload: bool = True) -> List[VideoMetadata]:
        """
        Run complete automation: download and upload videos.
        
        Args:
            urls: List of  post/reel URLs
            auto_upload: Whether to automatically upload after download
            
        Returns:
            List of VideoMetadata objects with final status
        """
        logger.info("=" * 60)
        logger.info(" AUTOMATION - STARTING")
        logger.info("=" * 60)
        logger.info(f"Processing {len(urls)} URLs")
        
        try:
            # Step 1: Download videos
            downloaded_videos = self.download_videos(urls)
            
            if not downloaded_videos:
                logger.error("No videos were downloaded. Exiting.")
                return []
            
            # Step 2: Upload videos (if enabled and we have successful downloads)
            if auto_upload:
                uploaded_videos = self.upload_videos(downloaded_videos)
                
                logger.info("=" * 60)
                logger.info("AUTOMATION COMPLETE")
                logger.info("=" * 60)
                
                return uploaded_videos
            else:
                logger.info("Auto-upload disabled. Videos downloaded but not uploaded.")
                return downloaded_videos
                
        except KeyboardInterrupt:
            logger.warning("\nProcess interrupted by user")
            return self.videos
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return self.videos
    
    def get_status_summary(self) -> dict:
        """
        Get summary of all processed videos.
        
        Returns:
            Dictionary with status counts
        """
        status_counts = {}
        for status in VideoStatus:
            status_counts[status.value] = sum(
                1 for v in self.videos if v.status == status
            )
        
        return {
            "total": len(self.videos),
            "by_status": status_counts
        }


def main():
    """Main entry point for the automation script."""
    # Example usage - you can modify this or use CLI/web UI
    if len(sys.argv) < 2:
        print("Usage: python main.py <url1> [url2] [url3] ...")
        print("\nExample:")
        print("  python main.py https://www..com/p/ABC123/ https://www..com/p/DEF456/")
        sys.exit(1)
    
    urls = sys.argv[1:]
    
    # Create automation instance
    automation = Automation()
    
    # Run automation
    results = automation.run(urls, auto_upload=True)
    
    # Print final summary
    summary = automation.get_status_summary()
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total videos processed: {summary['total']}")
    for status, count in summary['by_status'].items():
        if count > 0:
            print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
