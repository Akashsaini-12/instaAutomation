"""
Safety Manager for Instagram Automation
Tracks actions and enforces rate limits to prevent account bans.
Follows Instagram/Meta guidelines for safe automation.
"""
import time
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)


@dataclass
class ActionRecord:
    """Record of an action for rate limiting."""
    timestamp: float
    action_type: str
    details: Optional[Dict] = None


class SafetyManager:
    """
    Manages rate limiting and action tracking to prevent account bans.
    Implements Instagram/Meta guidelines for safe automation.
    """
    
    def __init__(self, state_file: str = "session/action_history.json"):
        """
        Initialize the safety manager.
        
        Args:
            state_file: Path to file storing action history
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.actions: List[ActionRecord] = []
        self.load_history()
        
        # Action type labels
        self.ACTION_POST = "post"
        self.ACTION_COMMENT = "comment"
        self.ACTION_LIKE = "like"
        self.ACTION_REPLY = "reply"
        
        logger.info("🛡️  Safety Manager initialized - Account protection enabled")
    
    def load_history(self):
        """Load action history from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.actions = [
                        ActionRecord(**record) for record in data.get('actions', [])
                    ]
                # Clean old records (older than 24 hours)
                self._clean_old_records()
                logger.info(f"📊 Loaded {len(self.actions)} action records")
        except Exception as e:
            logger.warning(f"Could not load action history: {e}")
            self.actions = []
    
    def save_history(self):
        """Save action history to file."""
        try:
            data = {
                'actions': [asdict(action) for action in self.actions],
                'last_updated': time.time()
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save action history: {e}")
    
    def _clean_old_records(self):
        """Remove action records older than 24 hours."""
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
        self.actions = [a for a in self.actions if a.timestamp > cutoff_time]
    
    def record_action(self, action_type: str, details: Optional[Dict] = None):
        """
        Record an action for rate limiting.
        
        Args:
            action_type: Type of action (post, comment, like, reply)
            details: Optional details about the action
        """
        action = ActionRecord(
            timestamp=time.time(),
            action_type=action_type,
            details=details or {}
        )
        self.actions.append(action)
        self._clean_old_records()
        self.save_history()
        logger.debug(f"📝 Recorded action: {action_type} at {datetime.fromtimestamp(action.timestamp)}")
    
    def get_action_count(self, action_type: str, hours: int = 1) -> int:
        """
        Get count of actions in the last N hours.
        
        Args:
            action_type: Type of action to count
            hours: Number of hours to look back
            
        Returns:
            Number of actions
        """
        cutoff_time = time.time() - (hours * 60 * 60)
        count = sum(
            1 for a in self.actions
            if a.action_type == action_type and a.timestamp > cutoff_time
        )
        return count
    
    def get_action_count_today(self, action_type: str) -> int:
        """Get count of actions today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_time = today_start.timestamp()
        count = sum(
            1 for a in self.actions
            if a.action_type == action_type and a.timestamp > cutoff_time
        )
        return count
    
    def can_perform_action(self, action_type: str):
        """
        Check if an action can be performed based on rate limits.
        
        Args:
            action_type: Type of action to check
            
        Returns:
            Tuple of (can_perform, reason_if_not)
        """
        limits = {
            self.ACTION_POST: {
                'per_hour': getattr(settings, 'max_posts_per_hour', 2),
                'per_day': getattr(settings, 'max_posts_per_day', 10)
            },
            self.ACTION_COMMENT: {
                'per_hour': getattr(settings, 'max_comments_per_hour', 20),
                'per_day': None  # No daily limit for comments
            },
            self.ACTION_LIKE: {
                'per_hour': getattr(settings, 'max_likes_per_hour', 50),
                'per_day': None  # No daily limit for likes
            },
            self.ACTION_REPLY: {
                'per_hour': getattr(settings, 'max_comments_per_hour', 20),  # Same as comments
                'per_day': None
            }
        }
        
        if action_type not in limits:
            return True, None
        
        limit = limits[action_type]
        
        # Check hourly limit
        hourly_count = self.get_action_count(action_type, hours=1)
        if limit['per_hour'] and hourly_count >= limit['per_hour']:
            return False, f"Hourly limit reached: {hourly_count}/{limit['per_hour']} {action_type}s"
        
        # Check daily limit
        if limit['per_day']:
            daily_count = self.get_action_count_today(action_type)
            if daily_count >= limit['per_day']:
                return False, f"Daily limit reached: {daily_count}/{limit['per_day']} {action_type}s"
        
        return True, None
    
    def get_random_delay(self, min_seconds: Optional[int] = None, max_seconds: Optional[int] = None) -> int:
        """
        Get a random delay to add human-like behavior.
        
        Args:
            min_seconds: Minimum delay (uses config default if None)
            max_seconds: Maximum delay (uses config default if None)
            
        Returns:
            Random delay in seconds
        """
        if min_seconds is None:
            min_seconds = getattr(settings, 'post_delay_random_min', 600)
        if max_seconds is None:
            max_seconds = getattr(settings, 'post_delay_random_max', 1800)
        
        # Add some randomness to make it more human-like
        delay = random.randint(min_seconds, max_seconds)
        # Add small random variation (±10%)
        variation = int(delay * 0.1)
        delay += random.randint(-variation, variation)
        
        return max(delay, min_seconds)  # Ensure minimum delay
    
    def wait_with_random_delay(self, base_delay: int, min_seconds: Optional[int] = None, max_seconds: Optional[int] = None):
        """
        Wait with randomized delay for human-like behavior.
        
        Args:
            base_delay: Base delay in seconds
            min_seconds: Minimum delay override
            max_seconds: Maximum delay override
        """
        if min_seconds is None and max_seconds is None:
            # Use base delay with small random variation
            delay = base_delay + random.randint(-int(base_delay * 0.1), int(base_delay * 0.2))
        else:
            delay = self.get_random_delay(min_seconds, max_seconds)
        
        logger.info(f"⏳ Waiting {delay} seconds (human-like delay)...")
        time.sleep(delay)
    
    def check_and_wait_if_needed(self, action_type: str) -> bool:
        """
        Check if action can be performed and wait if rate limit is approaching.
        
        Args:
            action_type: Type of action to check
            
        Returns:
            True if action can be performed, False if blocked
        """
        can_perform, reason = self.can_perform_action(action_type)
        
        if not can_perform:
            logger.warning(f"⚠️  Action blocked: {reason}")
            logger.warning("🛡️  This is a safety measure to protect your account from bans.")
            
            # Calculate wait time until next action is allowed
            if "Hourly limit" in reason:
                # Wait until next hour
                wait_time = 3600 - (time.time() % 3600)
                wait_minutes = int(wait_time / 60)
                logger.info(f"⏰ Please wait {wait_minutes} minutes before next {action_type}")
            elif "Daily limit" in reason:
                # Wait until next day
                tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                wait_time = (tomorrow.timestamp() - time.time())
                wait_hours = int(wait_time / 3600)
                logger.info(f"⏰ Daily limit reached. Please wait {wait_hours} hours (until tomorrow)")
            
            return False
        
        # Check if we're close to the limit and add extra delay
        limits = {
            self.ACTION_POST: getattr(settings, 'max_posts_per_hour', 2),
            self.ACTION_COMMENT: getattr(settings, 'max_comments_per_hour', 20),
            self.ACTION_LIKE: getattr(settings, 'max_likes_per_hour', 50),
            self.ACTION_REPLY: getattr(settings, 'max_comments_per_hour', 20),
        }
        
        if action_type in limits:
            hourly_count = self.get_action_count(action_type, hours=1)
            limit = limits[action_type]
            
            # If we're at 80% of limit, add extra delay
            if hourly_count >= int(limit * 0.8):
                extra_delay = 300  # 5 minutes extra delay
                logger.warning(f"⚠️  Approaching rate limit ({hourly_count}/{limit}). Adding {extra_delay}s safety delay.")
                time.sleep(extra_delay)
        
        return True
    
    def get_stats(self) -> Dict:
        """
        Get statistics about recent actions.
        
        Returns:
            Dictionary with action statistics
        """
        stats = {
            'today': {},
            'last_hour': {},
            'last_24_hours': {}
        }
        
        action_types = [self.ACTION_POST, self.ACTION_COMMENT, self.ACTION_LIKE, self.ACTION_REPLY]
        
        for action_type in action_types:
            stats['today'][action_type] = self.get_action_count_today(action_type)
            stats['last_hour'][action_type] = self.get_action_count(action_type, hours=1)
            stats['last_24_hours'][action_type] = self.get_action_count(action_type, hours=24)
        
        return stats
    
    def print_stats(self):
        """Print action statistics."""
        stats = self.get_stats()
        logger.info("📊 Action Statistics:")
        logger.info(f"  Today: {stats['today']}")
        logger.info(f"  Last Hour: {stats['last_hour']}")
        logger.info(f"  Last 24 Hours: {stats['last_24_hours']}")


# Global safety manager instance
_safety_manager: Optional[SafetyManager] = None


def get_safety_manager() -> SafetyManager:
    """Get or create the global safety manager instance."""
    global _safety_manager
    if _safety_manager is None:
        state_file = getattr(settings, 'session_file', 'session/action_history.json').replace('.json', '_history.json')
        _safety_manager = SafetyManager(state_file=state_file)
    return _safety_manager

