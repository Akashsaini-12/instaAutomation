"""
Utility functions for logging, file operations, and URL validation.
"""
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import colorlog
from colorlog import ColoredFormatter

from src.config import settings


def setup_logger(name: str = "_automation") -> logging.Logger:
    """
    Set up a colored logger with file and console handlers.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(asctime)s%(reset)s "
        "%(yellow)s%(name)s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        }
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    log_file = Path(settings.log_dir) / f"_automation_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(levelname)-8s %(asctime)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def validate__url(url: str) -> bool:
    """
    Validate if a URL is a valid  post/reel URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid  URL, False otherwise
    """
    _pattern = r'https?://(www\.)?(\.com|instagr\.am)/.*'
    return bool(re.match(_pattern, url))


def extract_post_id_from_url(url: str) -> Optional[str]:
    """
    Extract post ID from  URL.
    
    Args:
        url:  post URL
        
    Returns:
        Post ID if found, None otherwise
    """
    # Pattern for  post URLs like /p/POST_ID/ or /reel/POST_ID/
    pattern = r'/(?:p|reel)/([A-Za-z0-9_-]+)/?'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, None if file doesn't exist
    """
    try:
        path = Path(file_path)
        if path.exists():
            return path.stat().st_size
    except Exception:
        pass
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters for filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", filename)
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def generate_trending_hashtags(video_path: Optional[str] = None, caption: Optional[str] = None, count: int = 10) -> List[str]:
    """
    Generate trending hashtags based on video analysis.
    
    Args:
        video_path: Path to video file (for future video analysis)
        caption: Video caption or title to analyze
        count: Number of hashtags to generate
        
    Returns:
        List of hashtag strings
    """
    from src.config import settings
    
    # Base trending hashtags
    base_tags = settings.base_hashtags.split() if hasattr(settings, 'base_hashtags') else ["#viral", "#trending", "#fyp"]
    
    # Extract keywords from caption/filename
    keywords = []
    text_to_analyze = ""
    
    if caption:
        text_to_analyze += caption.lower() + " "
    if video_path:
        filename = Path(video_path).stem.lower()
        text_to_analyze += filename + " "
    
    # Common trending hashtag categories
    trending_categories = {
        "video": ["#video", "#videos", "#videography", "#videocontent"],
        "trending": ["#trending", "#trend", "#viral", "#fyp", "#foryou"],
        "entertainment": ["#entertainment", "#funny", "#comedy", "#meme", "#humor"],
        "lifestyle": ["#lifestyle", "#life", "#daily", "#lifestyleblogger"],
        "motivation": ["#motivation", "#inspiration", "#motivational", "#success"],
        "music": ["#music", "#musician", "#song", "#beat", "#audio"],
        "dance": ["#dance", "#dancing", "#dancer", "#choreography"],
        "food": ["#food", "#foodie", "#cooking", "#recipe", "#delicious"],
        "fitness": ["#fitness", "#workout", "#gym", "#health", "#fit"],
        "travel": ["#travel", "#wanderlust", "#adventure", "#explore"],
        "fashion": ["#fashion", "#style", "#ootd", "#outfit"],
        "beauty": ["#beauty", "#makeup", "#skincare", "#beautiful"],
        "art": ["#art", "#artist", "#creative", "#artwork"],
        "photography": ["#photography", "#photo", "#photographer", "#pic"],
        "nature": ["#nature", "#outdoors", "#landscape", "#naturelovers"],
        "animals": ["#animals", "#pets", "#dog", "#cat", "#wildlife"],
        "sports": ["#sports", "#football", "#basketball", "#soccer"],
        "gaming": ["#gaming", "#gamer", "#game", "#twitch"],
        "tech": ["#tech", "#technology", "#innovation", "#gadgets"],
        "cars": ["#cars", "#car", "#automotive", "#vehicle"],
    }
    
    # Analyze text and match categories
    matched_hashtags = []
    text_lower = text_to_analyze.lower()
    
    for category, tags in trending_categories.items():
        if category in text_lower:
            matched_hashtags.extend(tags[:2])  # Take max 2 from each category
    
    # Add generic trending hashtags if we have space
    generic_trending = [
        "#viral", "#trending", "#fyp", "#foryou", "#foryoupage",
        "#explore", "#explorepage", "#like", "#follow", "#share",
        "#instagram", "#instagood", "#love", "#photooftheday",
        "#beautiful", "#happy", "#cute", "#picoftheday", "#selfie"
    ]
    
    # Combine all hashtags
    all_hashtags = base_tags + matched_hashtags + generic_trending
    
    # Remove duplicates and limit count
    unique_hashtags = []
    seen = set()
    for tag in all_hashtags:
        tag_normalized = tag.lower().replace("#", "")
        if tag_normalized not in seen and len(unique_hashtags) < count:
            unique_hashtags.append(tag if tag.startswith("#") else f"#{tag}")
            seen.add(tag_normalized)
    
    # Fill remaining slots with generic trending
    while len(unique_hashtags) < count and len(generic_trending) > 0:
        for tag in generic_trending:
            tag_normalized = tag.lower().replace("#", "")
            if tag_normalized not in seen:
                unique_hashtags.append(tag)
                seen.add(tag_normalized)
                break
    
    return unique_hashtags[:count]
