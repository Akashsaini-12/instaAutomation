#!/usr/bin/env python3
"""
Helper script to set up .env file for  Automation.
Prompts user for credentials and creates .env file.
"""
import os
from pathlib import Path


def setup_env():
    """Interactive setup for .env file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("=" * 60)
    print(" Automation - Environment Setup")
    print("=" * 60)
    print()
    
    # Get  credentials
    username = input("Enter your  username: ").strip()
    password = input("Enter your  password: ").strip()
    
    # Optional settings with defaults
    print("\nOptional settings (press Enter for defaults):")
    download_dir = input("Download directory [downloads]: ").strip() or "downloads"
    log_level = input("Log level [INFO]: ").strip() or "INFO"
    post_delay = input("Delay between posts in seconds [300]: ").strip() or "300"
    
    # Write .env file
    env_content = f"""#  Credentials
_USERNAME={username}
_PASSWORD={password}

# Configuration
DOWNLOAD_DIR={download_dir}
LOG_LEVEL={log_level}
POST_DELAY_SECONDS={post_delay}

# Optional: Scheduling (cron format or interval in hours)
AUTO_POST_ENABLED=false
POST_INTERVAL_HOURS=2
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print("\n✓ .env file created successfully!")
        print(f"✓ Credentials saved to {env_file.absolute()}")
        print("\n⚠️  IMPORTANT: Never commit .env file to version control!")
        print("   It contains your  credentials.")
        
    except Exception as e:
        print(f"\n✗ Error creating .env file: {str(e)}")


if __name__ == "__main__":
    setup_env()
