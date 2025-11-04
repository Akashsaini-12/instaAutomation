"""
scheduler.py

Optional scheduler module for automatic posting at intervals.
Uses the schedule library to run automation at specified intervals.
"""

import schedule
import time
import logging
import json
import os
from pathlib import Path
from typing import List
from main import Automation, get_urls_from_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomationScheduler:
    """
    Scheduler for running  automation at regular intervals.
    """
    
    def __init__(self, config_path: str = "config.json", urls_file: str = None):
        """
        Initialize the scheduler.
        
        Args:
            config_path: Path to configuration file
            urls_file: Path to file containing URLs (optional, can be set later)
        """
        self.config_path = config_path
        self.urls_file = urls_file
        self.load_config()
        
        logger.info(" Automation Scheduler initialized")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            self.schedule_config = self.config.get("scheduling", {})
            self.enabled = self.schedule_config.get("enabled", False)
            self.interval_hours = self.schedule_config.get("interval_hours", 2)
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.enabled = False
    
    def run_automation_job(self):
        """
        Job function to run automation.
        Called by scheduler at intervals.
        """
        logger.info("=" * 60)
        logger.info("Scheduled automation job started")
        logger.info("=" * 60)
        
        # Get URLs
        urls = []
        if self.urls_file and os.path.exists(self.urls_file):
            urls = get_urls_from_file(self.urls_file)
        else:
            logger.warning("No URLs file specified or file not found")
            return
        
        if not urls:
            logger.warning("No URLs to process")
            return
        
        # Run automation
        try:
            automation = Automation(config_path=self.config_path)
            results = automation.run_automation(urls)
            
            if results.get("success"):
                logger.info("Scheduled automation completed successfully")
            else:
                logger.error("Scheduled automation completed with errors")
                
        except Exception as e:
            logger.error(f"Scheduled automation failed: {e}", exc_info=True)
    
    def start(self):
        """
        Start the scheduler.
        """
        if not self.enabled:
            logger.info("Scheduling is disabled in config. Enable it to use scheduler.")
            return
        
        logger.info(f"Starting scheduler with {self.interval_hours} hour interval")
        
        # Schedule the job
        schedule.every(self.interval_hours).hours.do(self.run_automation_job)
        
        # Run once immediately (optional)
        logger.info("Running initial automation job...")
        self.run_automation_job()
        
        # Keep scheduler running
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
    
    def set_urls_file(self, urls_file: str):
        """
        Set the URLs file for scheduled jobs.
        
        Args:
            urls_file: Path to file containing URLs
        """
        self.urls_file = urls_file
        logger.info(f"URLs file set to: {urls_file}")


def main():
    """
    Main entry point for scheduler.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description=" Automation Scheduler"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--urls-file",
        type=str,
        help="Path to file containing URLs (one per line)"
    )
    
    args = parser.parse_args()
    
    scheduler = AutomationScheduler(
        config_path=args.config,
        urls_file=args.urls_file
    )
    
    scheduler.start()


if __name__ == "__main__":
    main()
