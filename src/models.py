"""
Data models for  video metadata and status tracking.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class VideoStatus(Enum):
    """Enumeration for video processing status."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    DOWNLOAD_FAILED = "download_failed"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    UPLOAD_FAILED = "upload_failed"
    PROCESSING = "processing"


@dataclass
class VideoMetadata:
    """
    Metadata structure for downloaded  videos.
    
    Attributes:
        url: Original  URL
        title: Video title or post caption
        file_path: Local file path where video is stored
        timestamp: When the video was downloaded
        status: Current processing status
        _post_id:  post ID after successful upload
        error_message: Error message if operation failed
        file_size: Size of video file in bytes
        duration: Video duration in seconds (if available)
    """
    url: str
    title: Optional[str] = None
    file_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: VideoStatus = VideoStatus.PENDING
    _post_id: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert metadata to dictionary format."""
        return {
            "url": self.url,
            "title": self.title,
            "file_path": self.file_path,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status.value,
            "_post_id": self._post_id,
            "error_message": self.error_message,
            "file_size": self.file_size,
            "duration": self.duration
        }
