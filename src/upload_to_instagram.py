"""
 video uploading module using instagrapi.
Handles uploading videos to  account with proper authentication and error handling.
"""
import time
import random
from pathlib import Path
from typing import List, Optional

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, TwoFactorRequired, PleaseWaitFewMinutes
import time

from src.config import settings
from src.models import VideoMetadata, VideoStatus
from src.utils import setup_logger, generate_trending_hashtags
from src.safety_manager import get_safety_manager

logger = setup_logger(__name__)


class Uploader:
    """Class to handle uploading videos to ."""
    
    def __init__(self, username: str, password: str):
        """
        Initialize the  uploader with credentials.
        
        Args:
            username:  username
            password:  password
        """
        self.username = username
        self.password = password
        self.client = Client()
        # Increased delay range for safer automation (2-5 seconds)
        self.client.delay_range = [2, 5]
        self._authenticated = False
        self.safety_manager = get_safety_manager()
        self._retry_count = 0
        
        logger.info("🛡️  Uploader initialized with safety manager - Account protection enabled")
    
    def login(self) -> bool:
        """
        Authenticate with  account.
        
        Returns:
            True if login successful, False otherwise
        """
        if self._authenticated:
            logger.info("Already authenticated")
            return True
        
        # Validate credentials are provided
        if not self.username or not self.password:
            logger.error(" credentials not provided. Please set up .env file.")
            logger.error("Run 'python setup_env.py' to configure credentials.")
            return False
        
        try:
            logger.info(f"Attempting to login as {self.username}")
            
            # Try to login
            self.client.login(self.username, self.password)
            self._authenticated = True
            logger.info("✓ Successfully logged in to ")
            return True
            
        except TwoFactorRequired as e:
            logger.error("Two-factor authentication required. Please handle 2FA manually.")
            logger.error(f"Error: {str(e)}")
            return False
            
        except PleaseWaitFewMinutes as e:
            logger.error(f"⚠️  Rate limit exceeded. Please wait: {str(e)}")
            logger.error("🛡️  This is Instagram's rate limiting. Your account is being protected.")
            logger.error("💡 Recommendation: Wait 1-2 hours before trying again.")
            return False
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Login failed: {error_msg}")
            
            # Check for common errors
            if "challenge_required" in error_msg.lower():
                logger.error("Challenge required. Please verify your account manually.")
            elif "checkpoint" in error_msg.lower():
                logger.error("Account checkpoint required. Please verify via  app.")
            
            return False
    
    def upload_video(
        self,
        video_path: str,
        caption: Optional[str] = None,
        thumbnail_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload a single video to  with safety checks.
        
        Args:
            video_path: Path to video file
            caption: Caption for the post
            thumbnail_path: Optional thumbnail image path
            
        Returns:
             media ID if successful, None otherwise
        """
        if not self._authenticated:
            logger.error("Not authenticated. Please login first.")
            return None
        
        # SAFETY CHECK: Check rate limits before uploading
        can_upload, reason = self.safety_manager.can_perform_action(self.safety_manager.ACTION_POST)
        if not can_upload:
            logger.error(f"❌ Upload blocked: {reason}")
            logger.error("🛡️  This is a safety measure to prevent account bans.")
            logger.error("💡 Please wait before uploading more videos.")
            return None
        
        video_file = Path(video_path)
        if not video_file.exists():
            logger.error(f"Video file not found: {video_path}")
            return None
        
        try:
            logger.info(f"Uploading video: {video_file.name}")
            
            # Prepare caption with trending hashtags
            if not caption:
                caption = f"Uploaded via automation - {video_file.stem}"
            
            # Add trending hashtags if enabled
            if getattr(settings, 'use_trending_hashtags', True):
                try:
                    hashtags = generate_trending_hashtags(
                        video_path=str(video_file.absolute()),
                        caption=caption,
                        count=getattr(settings, 'hashtag_count', 10)
                    )
                    if hashtags:
                        caption += "\n\n" + " ".join(hashtags)
                        logger.info(f"📌 Added {len(hashtags)} trending hashtags to caption")
                except Exception as e:
                    logger.warning(f"⚠️  Could not generate hashtags: {str(e)}")
            
            # Upload video
            # Try clip_upload first (for reels/IGTV), fallback to video_upload for regular posts
            # clip_upload supports longer videos, video_upload is for feed posts
            try:
                # Try clip_upload (supports reels and longer videos)
                media = self.client.clip_upload(
                    path=str(video_file.absolute()),
                    caption=caption,
                    thumbnail=thumbnail_path if thumbnail_path else None
                )
            except Exception as clip_error:
                # Fallback to video_upload for regular feed posts
                logger.info("clip_upload failed, trying video_upload...")
                try:
                    media = self.client.video_upload(
                        path=str(video_file.absolute()),
                        caption=caption,
                        thumbnail=thumbnail_path if thumbnail_path else None
                    )
                except Exception as video_error:
                    # If both fail, raise the original clip error
                    raise clip_error
            
            # Extract media ID - instagrapi Media objects have pk attribute
            media_id = getattr(media, 'pk', None) or getattr(media, 'id', None)
            if not media_id:
                # Try to get from dict representation
                try:
                    media_dict = media.dict() if hasattr(media, 'dict') else {}
                    media_id = media_dict.get("id") or media_dict.get("pk")
                except:
                    pass
            
            media_id = str(media_id) if media_id else "uploaded"
            logger.info(f"✓ Successfully uploaded video. Media ID: {media_id}")
            
            # Record the action for rate limiting
            self.safety_manager.record_action(
                self.safety_manager.ACTION_POST,
                details={'media_id': media_id, 'video_path': str(video_file)}
            )
            
            # Reset retry count on success
            self._retry_count = 0
            
            return media_id
            
        except LoginRequired:
            logger.error("Login required. Attempting to re-authenticate...")
            if self.login():
                return self.upload_video(video_path, caption, thumbnail_path)
            return None
            
        except PleaseWaitFewMinutes as e:
            logger.error(f"⚠️  Rate limit exceeded: {str(e)}")
            logger.error("🛡️  Instagram has rate-limited your account. Please wait before uploading again.")
            
            # Record the rate limit event
            self.safety_manager.record_action(
                'rate_limit',
                details={'error': str(e), 'action': 'upload'}
            )
            
            # Exponential backoff if enabled
            if getattr(settings, 'enable_exponential_backoff', True):
                backoff_delay = getattr(settings, 'retry_base_delay', 60) * (2 ** self._retry_count)
                logger.info(f"⏳ Waiting {backoff_delay} seconds before retry (exponential backoff)...")
                time.sleep(min(backoff_delay, 3600))  # Max 1 hour
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to upload video {video_file.name}: {error_msg}")
            
            # Check for rate limit indicators in error message
            if any(keyword in error_msg.lower() for keyword in ['rate limit', 'too many', 'wait', 'try again later']):
                logger.warning("🛡️  Rate limit detected in error message. Adding safety delay.")
                time.sleep(300)  # Wait 5 minutes
            
            return None
    
    def like_comments_on_post(self, media_id: str, max_comments: int = 10) -> int:
        """
        Auto-like comments on a specific post.
        
        Args:
            media_id:  media ID
            max_comments: Maximum number of comments to like
            
        Returns:
            Number of comments liked
        """
        if not self._authenticated:
            logger.error("Not authenticated. Cannot like comments.")
            return 0
        
        try:
            # Convert media_id to appropriate format for instagrapi
            # instagrapi uses media_id in format: {media_id}_{user_id} or just media_id
            # First, try using the media_id directly, or extract PK if it contains underscore
            media_pk = media_id.split('_')[0] if '_' in media_id else media_id
            
            # Try to convert to int if possible (instagrapi expects int)
            try:
                media_pk_int = int(media_pk)
            except (ValueError, TypeError):
                media_pk_int = media_pk
            
            logger.info(f"🔍 Fetching comments for media ID: {media_pk_int}")
            
            # Get media info first to verify the post exists and get proper ID
            try:
                media_info = self.client.media_info(media_pk_int)
                actual_media_pk = media_info.pk
                logger.debug(f"✓ Media info retrieved. Actual PK: {actual_media_pk}")
            except Exception as info_error:
                logger.warning(f"⚠️  Could not fetch media info: {str(info_error)}, using provided ID directly")
                actual_media_pk = media_pk_int
            
            # Get comments for the post
            logger.info(f"📥 Attempting to fetch comments for media PK: {actual_media_pk}")
            comments = self.client.media_comments(actual_media_pk, amount=max_comments)
            
            if not comments or len(comments) == 0:
                logger.info(f"ℹ️  No comments found on this post yet (checked after {settings.auto_like_comment_delay}s delay)")
                logger.info(f"💡 Tip: Comments may appear later. Auto-like will only work when comments exist.")
                return 0
            
            liked_count = 0
            logger.info(f"✅ Found {len(comments)} comment(s), starting to like...")
            
            max_likes = min(len(comments), getattr(settings, 'auto_like_max_per_post', 10))
            like_delay = getattr(settings, 'auto_like_delay_between', 5)
            
            for idx, comment in enumerate(comments[:max_likes], 1):
                try:
                    # SAFETY CHECK: Check rate limits before liking
                    can_like, reason = self.safety_manager.can_perform_action(self.safety_manager.ACTION_LIKE)
                    if not can_like:
                        logger.warning(f"⚠️  Like blocked: {reason}. Stopping auto-like.")
                        break
                    
                    # Like the comment
                    self.client.comment_like(comment.pk)
                    liked_count += 1
                    username = getattr(comment.user, 'username', 'unknown')
                    logger.info(f"  [{idx}/{max_likes}] ❤️  Liked comment by @{username}")
                    
                    # Record the action
                    self.safety_manager.record_action(
                        self.safety_manager.ACTION_LIKE,
                        details={'comment_id': comment.pk, 'username': username}
                    )
                    
                    # Random delay between likes (human-like behavior)
                    delay = like_delay + random.randint(-1, 2)
                    time.sleep(max(delay, 3))  # Minimum 3 seconds
                    
                except Exception as e:
                    username = getattr(comment.user, 'username', 'unknown') if hasattr(comment, 'user') else 'unknown'
                    logger.warning(f"  [{idx}/{len(comments)}] ✗ Failed to like comment by @{username}: {str(e)}")
                    continue
            
            logger.info(f"🎉 Successfully liked {liked_count} out of {len(comments)} comment(s) on this post!")
            return liked_count
            
        except Exception as e:
            logger.error(f"❌ Error while liking comments: {str(e)}", exc_info=True)
            logger.error(f"   Media ID used: {media_id}")
            return 0
    
    def comment_on_post(self, media_id: str, comment_text: str) -> bool:
        """
        Post a comment on a specific post.
        
        Args:
            media_id:  media ID
            comment_text: Text of the comment to post
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        if not self._authenticated:
            logger.error("Not authenticated. Cannot post comment.")
            return False
        
        if not comment_text or not comment_text.strip():
            logger.warning("Comment text is empty. Skipping auto-comment.")
            return False
        
        try:
            # Convert media_id to appropriate format for instagrapi
            media_pk = media_id.split('_')[0] if '_' in media_id else media_id
            
            # Try to convert to int if possible (instagrapi expects int or str)
            try:
                media_pk_int = int(media_pk)
            except (ValueError, TypeError):
                media_pk_int = media_pk
            
            # SAFETY CHECK: Check rate limits before commenting
            can_comment, reason = self.safety_manager.can_perform_action(self.safety_manager.ACTION_COMMENT)
            if not can_comment:
                logger.warning(f"⚠️  Comment blocked: {reason}")
                return False
            
            logger.info(f"💬 Posting comment on media ID: {media_pk_int}")
            logger.info(f"   Comment text: \"{comment_text}\"")
            
            # Post the comment
            comment = self.client.media_comment(media_pk_int, comment_text)
            
            # Record the action
            if comment:
                self.safety_manager.record_action(
                    self.safety_manager.ACTION_COMMENT,
                    details={'media_id': media_pk_int, 'comment_id': getattr(comment, 'pk', None)}
                )
            
            if comment:
                logger.info(f"✅ Successfully posted comment on the post!")
                return True
            else:
                logger.warning("⚠️  Comment posting returned no result")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error while posting comment: {str(e)}", exc_info=True)
            logger.error(f"   Media ID used: {media_id}")
            return False
    
    def reply_to_comments(self, media_id: str, reply_text: str, max_comments: int = 10) -> int:
        """
        Auto-reply to comments on a specific post.
        
        Args:
            media_id:  media ID
            reply_text: Text to reply with
            max_comments: Maximum number of comments to reply to
            
        Returns:
            Number of comments replied to
        """
        if not self._authenticated:
            logger.error("Not authenticated. Cannot reply to comments.")
            return 0
        
        if not reply_text or not reply_text.strip():
            logger.warning("Reply text is empty. Skipping auto-reply.")
            return 0
        
        try:
            # Convert media_id to appropriate format
            media_pk = media_id.split('_')[0] if '_' in media_id else media_id
            
            try:
                media_pk_int = int(media_pk)
            except (ValueError, TypeError):
                media_pk_int = media_pk
            
            logger.info(f"💬 Checking for comments to reply on media ID: {media_pk_int}")
            
            # Get media info
            try:
                media_info = self.client.media_info(media_pk_int)
                actual_media_pk = media_info.pk
            except Exception as info_error:
                logger.warning(f"⚠️  Could not fetch media info: {str(info_error)}")
                actual_media_pk = media_pk_int
            
            # Get comments
            comments = self.client.media_comments(actual_media_pk, amount=max_comments)
            
            if not comments or len(comments) == 0:
                logger.info("ℹ️  No comments found to reply to")
                return 0
            
            replied_count = 0
            logger.info(f"✅ Found {len(comments)} comment(s), checking which ones need replies...")
            
            for idx, comment in enumerate(comments, 1):
                try:
                    # Check if we already replied to this comment (avoid duplicate replies)
                    # Get replies to this comment
                    try:
                        replies = self.client.comment_replies(comment.pk, amount=5)
                        # Check if we already replied
                        already_replied = False
                        for reply in replies:
                            if hasattr(reply, 'user') and reply.user.username == self.username:
                                already_replied = True
                                break
                    except:
                        # If we can't check replies, try to reply anyway
                        already_replied = False
                    
                    if already_replied:
                        logger.debug(f"  [{idx}] Already replied to comment by @{comment.user.username}")
                        continue
                    
                    # SAFETY CHECK: Check rate limits before replying
                    can_reply, reason = self.safety_manager.can_perform_action(self.safety_manager.ACTION_REPLY)
                    if not can_reply:
                        logger.warning(f"⚠️  Reply blocked: {reason}. Stopping auto-reply.")
                        break
                    
                    max_replies = getattr(settings, 'auto_reply_max_per_post', 5)
                    if replied_count >= max_replies:
                        logger.info(f"⚠️  Reached maximum replies per post ({max_replies}). Stopping.")
                        break
                    
                    # Reply to the comment
                    self.client.media_comment(actual_media_pk, reply_text, replied_to_comment_id=comment.pk)
                    replied_count += 1
                    username = getattr(comment.user, 'username', 'unknown')
                    logger.info(f"  [{idx}/{len(comments)}] 💬 Replied to comment by @{username}")
                    
                    # Record the action
                    self.safety_manager.record_action(
                        self.safety_manager.ACTION_REPLY,
                        details={'comment_id': comment.pk, 'username': username}
                    )
                    
                    # Random delay between replies (human-like behavior)
                    reply_delay = getattr(settings, 'auto_reply_delay_between', 30)
                    delay = reply_delay + random.randint(-5, 10)
                    time.sleep(max(delay, 20))  # Minimum 20 seconds
                    
                except Exception as e:
                    username = getattr(comment.user, 'username', 'unknown') if hasattr(comment, 'user') else 'unknown'
                    logger.warning(f"  [{idx}/{len(comments)}] ✗ Failed to reply to comment by @{username}: {str(e)}")
                    continue
            
            logger.info(f"✅ Successfully replied to {replied_count} out of {len(comments)} comment(s)")
            return replied_count
            
        except Exception as e:
            logger.error(f"❌ Error while replying to comments: {str(e)}", exc_info=True)
            return 0
    
    def upload_video_metadata(self, metadata: VideoMetadata, auto_like_comments: bool = False, auto_comment: bool = False) -> VideoMetadata:
        """
        Upload a video using its metadata.
        
        Args:
            metadata: VideoMetadata object with file path and caption
            auto_like_comments: Whether to auto-like comments after upload
            
        Returns:
            Updated VideoMetadata object with upload status
        """
        if metadata.status != VideoStatus.DOWNLOADED:
            logger.warning(f"Video {metadata.url} not in downloaded status. Current: {metadata.status}")
            metadata.status = VideoStatus.UPLOAD_FAILED
            metadata.error_message = f"Video not ready for upload. Status: {metadata.status.value}"
            return metadata
        
        try:
            metadata.status = VideoStatus.UPLOADING
            logger.info(f"Starting upload for: {metadata.file_path}")
            
            # Upload video
            media_id = self.upload_video(
                video_path=metadata.file_path,
                caption=metadata.title or f"Reposted video"
            )
            
            if media_id:
                metadata._post_id = media_id
                metadata.status = VideoStatus.UPLOADED
                logger.info(f"✓ Video uploaded successfully. Post ID: {metadata._post_id}")
                
                # Auto-comment if enabled
                if getattr(settings, 'auto_comment_enabled', False):
                    comment_text = getattr(settings, 'auto_comment_text', 'Thanks for watching! 🙌')
                    comment_delay = getattr(settings, 'auto_comment_delay', 30)
                    logger.info(f"💬 Auto-comment enabled. Waiting {comment_delay} seconds before posting comment...")
                    time.sleep(comment_delay)
                    comment_success = self.comment_on_post(media_id, comment_text)
                    if comment_success:
                        logger.info(f"✅ Auto-comment posted successfully!")
                
                # Auto-reply to comments if enabled
                if getattr(settings, 'auto_reply_enabled', False):
                    reply_delay = getattr(settings, 'auto_reply_delay', 120)
                    reply_text = getattr(settings, 'auto_reply_text', 'Thanks for your comment! 🙏')
                    logger.info(f"💬 Auto-reply enabled. Waiting {reply_delay} seconds before checking for comments to reply...")
                    time.sleep(reply_delay)
                    replied_count = self.reply_to_comments(media_id, reply_text)
                    if replied_count > 0:
                        logger.info(f"✅ Auto-replied to {replied_count} comment(s)")
                
                # Auto-like comments if enabled
                if auto_like_comments:
                    logger.info(f"💬 Auto-like comments enabled. Waiting {settings.auto_like_comment_delay} seconds before checking comments...")
                    logger.info(f"⏳ Please wait... (Post ID: {media_id})")
                    time.sleep(settings.auto_like_comment_delay)
                    logger.info(f"⏱️  Delay complete. Now checking for comments...")
                    liked_count = self.like_comments_on_post(media_id)
                    if liked_count > 0:
                        logger.info(f"✅ Auto-liked {liked_count} comment(s) on this post")
                    else:
                        logger.info(f"ℹ️  No comments to like yet (checked {settings.auto_like_comment_delay}s after upload)")
            else:
                metadata.status = VideoStatus.UPLOAD_FAILED
                metadata.error_message = "Upload failed - no media ID returned"
                logger.error(f"✗ Failed to upload video: {metadata.url}")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Exception during upload: {error_msg}")
            metadata.status = VideoStatus.UPLOAD_FAILED
            metadata.error_message = error_msg
        
        return metadata
    
    def upload_multiple_videos(
        self,
        videos: List[VideoMetadata],
        delay_seconds: Optional[int] = None,
        auto_like_comments: bool = False
    ) -> List[VideoMetadata]:
        """
        Upload multiple videos sequentially with delay between uploads.
        
        Args:
            videos: List of VideoMetadata objects
            delay_seconds: Delay between uploads (uses config default if None)
            
        Returns:
            List of updated VideoMetadata objects
        """
        delay = delay_seconds or settings.post_delay_seconds
        
        # Filter only downloaded videos
        videos_to_upload = [v for v in videos if v.status == VideoStatus.DOWNLOADED]
        
        if not videos_to_upload:
            logger.warning("No videos ready for upload (all must be in DOWNLOADED status)")
            return videos
        
        logger.info(f"Starting batch upload for {len(videos_to_upload)} videos")
        logger.info(f"Delay between uploads: {delay} seconds")
        
        results = []
        
        for idx, metadata in enumerate(videos_to_upload, 1):
            logger.info(f"Uploading video {idx}/{len(videos_to_upload)}")
            
            # Upload video
            updated_metadata = self.upload_video_metadata(metadata, auto_like_comments=auto_like_comments)
            results.append(updated_metadata)
            
            # Update original list
            for i, v in enumerate(videos):
                if v.url == updated_metadata.url:
                    videos[i] = updated_metadata
                    break
            
            # Wait before next upload (except for the last one) with randomized delay
            if idx < len(videos_to_upload):
                # Use safety manager's random delay for human-like behavior
                random_delay = self.safety_manager.get_random_delay(
                    min_seconds=getattr(settings, 'post_delay_random_min', 600),
                    max_seconds=getattr(settings, 'post_delay_random_max', 1800)
                )
                logger.info(f"⏳ Waiting {random_delay} seconds before next upload (randomized for safety)...")
                self.safety_manager.wait_with_random_delay(random_delay)
                
                # Print safety stats
                self.safety_manager.print_stats()
        
        # Summary
        successful = sum(1 for m in results if m.status == VideoStatus.UPLOADED)
        failed = len(results) - successful
        logger.info(f"Upload complete: {successful} successful, {failed} failed")
        
        return videos
    
    def logout(self):
        """Logout from  (cleanup)."""
        try:
            if self._authenticated:
                self.client.logout()
                self._authenticated = False
                logger.info("Logged out from ")
        except Exception as e:
            logger.warning(f"Error during logout: {str(e)}")
