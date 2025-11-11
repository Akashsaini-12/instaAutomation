"""
Configuration management for  Automation Project.
Handles loading settings from environment variables and .env file.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    #  Credentials (required, but will prompt if not found)
    # Note: Using os.getenv manually since _USERNAME/_PASSWORD with underscore prefix need special handling
    instagram_username: str = Field(default_factory=lambda: os.getenv("_USERNAME", "") or os.getenv("INSTAGRAM_USERNAME", ""))
    instagram_password: str = Field(default_factory=lambda: os.getenv("_PASSWORD", "") or os.getenv("INSTAGRAM_PASSWORD", ""))
    
    # Directories
    download_dir: str = Field(default="downloads", env="DOWNLOAD_DIR")
    log_dir: str = Field(default="logs", env="LOG_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Posting Configuration - SAFETY FIRST: Following Instagram Guidelines
    # Minimum delay between posts: 10-15 minutes (recommended: 15-30 minutes)
    post_delay_seconds: int = Field(default=900, env="POST_DELAY_SECONDS")  # 15 minutes default (safer)
    post_delay_random_min: int = Field(default=600, env="POST_DELAY_RANDOM_MIN")  # 10 minutes minimum
    post_delay_random_max: int = Field(default=1800, env="POST_DELAY_RANDOM_MAX")  # 30 minutes maximum
    
    # Daily/Hourly Limits - CRITICAL for account safety
    max_posts_per_day: int = Field(default=10, env="MAX_POSTS_PER_DAY")  # Maximum 10 posts per day (very safe)
    max_posts_per_hour: int = Field(default=2, env="MAX_POSTS_PER_HOUR")  # Maximum 2 posts per hour
    max_comments_per_hour: int = Field(default=20, env="MAX_COMMENTS_PER_HOUR")  # Maximum 20 comments per hour
    max_likes_per_hour: int = Field(default=50, env="MAX_LIKES_PER_HOUR")  # Maximum 50 likes per hour
    
    # Optional Scheduling
    auto_post_enabled: bool = Field(default=False, env="AUTO_POST_ENABLED")
    post_interval_hours: int = Field(default=2, env="POST_INTERVAL_HOURS")
    
    # Auto-like comments feature - WITH SAFETY LIMITS
    auto_like_comments: bool = Field(default=False, env="AUTO_LIKE_COMMENTS")
    auto_like_comment_delay: int = Field(default=180, env="AUTO_LIKE_COMMENT_DELAY")  # 3 minutes delay after upload (safer)
    auto_like_max_per_post: int = Field(default=10, env="AUTO_LIKE_MAX_PER_POST")  # Max likes per post
    auto_like_delay_between: int = Field(default=5, env="AUTO_LIKE_DELAY_BETWEEN")  # 5 seconds between likes
    
    # Auto-comment feature - WITH SAFETY LIMITS
    auto_comment_enabled: bool = Field(default=False, env="AUTO_COMMENT_ENABLED")
    auto_comment_text: str = Field(default="Thanks for watching! 🙌", env="AUTO_COMMENT_TEXT")
    auto_comment_delay: int = Field(default=60, env="AUTO_COMMENT_DELAY")  # 1 minute delay after upload (safer)
    
    # Auto-reply to comments feature - WITH SAFETY LIMITS
    auto_reply_enabled: bool = Field(default=False, env="AUTO_REPLY_ENABLED")
    auto_reply_text: str = Field(default="Thanks for your comment! 🙏", env="AUTO_REPLY_TEXT")
    auto_reply_delay: int = Field(default=300, env="AUTO_REPLY_DELAY")  # 5 minutes delay after upload
    auto_reply_check_interval: int = Field(default=600, env="AUTO_REPLY_CHECK_INTERVAL")  # Check every 10 minutes
    auto_reply_max_per_post: int = Field(default=5, env="AUTO_REPLY_MAX_PER_POST")  # Max replies per post
    auto_reply_delay_between: int = Field(default=30, env="AUTO_REPLY_DELAY_BETWEEN")  # 30 seconds between replies
    
    # Rate limit handling
    enable_exponential_backoff: bool = Field(default=True, env="ENABLE_EXPONENTIAL_BACKOFF")
    max_retry_attempts: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    retry_base_delay: int = Field(default=60, env="RETRY_BASE_DELAY")  # Base delay for retries (1 minute)
    
    # Session safety
    session_save_enabled: bool = Field(default=True, env="SESSION_SAVE_ENABLED")
    session_file: str = Field(default="session/ig_session.json", env="SESSION_FILE")
    
    # Trending hashtags with video analysis
    use_trending_hashtags: bool = Field(default=True, env="USE_TRENDING_HASHTAGS")
    hashtag_count: int = Field(default=10, env="HASHTAG_COUNT")  # Number of hashtags to add
    base_hashtags: str = Field(default="#viral #trending #fyp", env="BASE_HASHTAGS")  # Base hashtags to always include
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file
    
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        
        # Create download directory if it doesn't exist
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        
        # Create log directory if it doesn't exist
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)


# Global settings instance
# Settings will be initialized, but credentials should be checked before use
try:
    settings = Settings()
except Exception as e:
    # If settings fail to load, create a minimal instance
    # This allows the module to be imported even if .env is missing
    import sys
    print(f"\n⚠️  Configuration warning: {str(e)}", file=sys.stderr)
    print("Please run 'python setup_env.py' to set up your configuration.", file=sys.stderr)
    # Create a minimal settings object to prevent import errors
    # Actual credential validation will happen when uploader tries to login
    settings = type('Settings', (), {
        'instagram_username': '',
        'instagram_password': '',
        'download_dir': 'downloads',
        'log_dir': 'logs',
        'log_level': 'INFO',
        'post_delay_seconds': 300,
        'auto_post_enabled': False,
        'post_interval_hours': 2,
        'auto_like_comments': False,
        'auto_like_comment_delay': 60,
        'auto_comment_enabled': False,
        'auto_comment_text': 'Thanks for watching! 🙌',
        'auto_comment_delay': 30,
        'auto_reply_enabled': False,
        'auto_reply_text': 'Thanks for your comment! 🙏',
        'auto_reply_delay': 120,
        'auto_reply_check_interval': 300,
        'use_trending_hashtags': True,
        'hashtag_count': 10,
        'base_hashtags': '#viral #trending #fyp'
    })()
