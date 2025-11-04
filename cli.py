#!/usr/bin/env python3
"""
Command-line interface for  Automation.
Provides easy way to run the automation from terminal.
"""
import argparse
import sys
from typing import List

from main import Automation
from src.utils import setup_logger

logger = setup_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=" Automation - Download and upload videos automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and upload multiple videos
  python cli.py --urls "https://www..com/p/ABC123/" "https://www..com/p/DEF456/"
  
  # Download only (no upload)
  python cli.py --urls "https://www..com/p/ABC123/" --no-upload
  
  # Read URLs from file
  python cli.py --file urls.txt
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--urls",
        nargs="+",
        help=" video URLs to process"
    )
    group.add_argument(
        "--file",
        type=str,
        help="Path to file containing URLs (one per line)"
    )
    
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Only download videos, do not upload"
    )
    
    parser.add_argument(
        "--delay",
        type=int,
        help="Delay in seconds between uploads (overrides config)"
    )
    
    return parser.parse_args()


def read_urls_from_file(file_path: str) -> List[str]:
    """
    Read URLs from a text file (one URL per line).
    
    Args:
        file_path: Path to file containing URLs
        
    Returns:
        List of URLs
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        return urls
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Get URLs
    if args.urls:
        urls = args.urls
    elif args.file:
        urls = read_urls_from_file(args.file)
    else:
        logger.error("No URLs provided")
        sys.exit(1)
    
    if not urls:
        logger.error("No valid URLs found")
        sys.exit(1)
    
    logger.info(f"Processing {len(urls)} URL(s)")
    
    # Create automation instance
    automation = Automation()
    
    # Run automation
    auto_upload = not args.no_upload
    results = automation.run(urls, auto_upload=auto_upload)
    
    # Exit with appropriate code
    uploaded = sum(1 for r in results if r.status.value == "uploaded")
    if auto_upload and uploaded == 0 and len(results) > 0:
        sys.exit(1)  # Failed if we tried to upload but none succeeded
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
