#  Automation Project

A complete Python-based automation system to download  videos from URLs and automatically post them to your  account.

## ⚠️ Important Disclaimer

**Please note**: This project is for educational purposes. Instagram's Terms of Service prohibit automated posting and scraping. Use this at your own risk. Instagram may temporarily or permanently suspend accounts that violate their terms.

## 🛡️ Account Safety Features

This project includes **comprehensive safety measures** to protect your account:

- **Rate Limiting**: Enforces daily/hourly limits (10 posts/day, 2 posts/hour by default)
- **Randomized Delays**: Human-like behavior with random delays (10-30 minutes between posts)
- **Action Tracking**: Tracks all actions to prevent exceeding limits
- **Error Handling**: Exponential backoff on rate limit errors
- **Safety Manager**: Automatic blocking when limits are reached

**⚠️ IMPORTANT**: Read [SAFETY_GUIDELINES.md](SAFETY_GUIDELINES.md) before using this tool!

**Default Safety Settings**:
- Maximum 10 posts per day
- Maximum 2 posts per hour
- 15-30 minute delays between posts (randomized)
- Maximum 20 comments per hour
- Maximum 50 likes per hour

These settings can be adjusted in your `.env` file, but **we strongly recommend keeping them conservative** to avoid account bans.

## 🚀 Features

- **Batch Download**: Download multiple Instagram videos from URLs
- **Automatic Posting**: Automatically upload videos to your Instagram account
- **🛡️ Account Safety**: Comprehensive rate limiting and safety measures
- **Metadata Tracking**: Store video metadata (title, path, timestamp, status)
- **Error Handling**: Robust error handling with exponential backoff
- **Logging**: Comprehensive logging for tracking operations
- **Queue Management**: Track download and upload status
- **Web UI**: Modern FastAPI-based web interface
- **Auto-Interactions**: Auto-like comments, auto-comment, auto-reply (with safety limits)
- **Trending Hashtags**: Automatic hashtag generation based on video content

## 📋 Prerequisites

- Python 3.10 or higher
-  account credentials
- Stable internet connection

## 🔧 Installation

1. **Clone or download this project**

2. **Install dependencies**:

   For local development (full functionality):
   ```bash
   pip install -r requirements-full.txt
   ```

   For Vercel deployment (minimal - no video features):
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**:
   - Copy `env.example` to `.env`
   - Fill in your Instagram credentials in `.env`:
   ```
   _USERNAME=your_username
   _PASSWORD=your_password
   ```

## 🚀 Deployment

### Vercel Deployment (Limited)

⚠️ **Note**: Vercel has a 250 MB size limit. This project includes a minimal API for Vercel that explains limitations and guides users to Railway/Render.

- ✅ Minimal API deploys successfully
- ❌ Video download/upload not available
- 📄 Shows landing page with deployment instructions

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for details.

### Railway/Render Deployment (Recommended) ⭐

For **full functionality**, deploy to Railway or Render:

1. **Use full requirements**:
   ```bash
   cp requirements-full.txt requirements.txt
   ```

2. **Follow deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

3. **Platforms**:
   - **Railway** ⭐ (Recommended - Easy setup, persistent storage)
   - **Render** (Free tier, persistent storage)
   - **Fly.io** (Good for long-running tasks)

## 📁 Project Structure

```
-automation/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── download_videos.py     # Video downloading logic
│   ├── upload_to_.py #  upload logic
│   ├── models.py              # Data models for videos
│   └── utils.py               # Utility functions
├── main.py                    # Main automation script
├── cli.py                     # CLI interface
├── web_ui.py                  # Optional web UI (FastAPI)
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Usage

### Method 1: Command Line Interface

```bash
python cli.py --urls "https://www..com/p/ABC123/" "https://www..com/p/DEF456/"
```

### Method 2: Python Script

```python
from main import Automation

automation = Automation()
urls = [
    "https://www..com/p/ABC123/",
    "https://www..com/p/DEF456/"
]
automation.run(urls)
```

### Method 3: Web UI (Optional)

```bash
python web_ui.py
```

Then open your browser at `http://localhost:8000`

## ⚙️ Configuration

Edit `.env` file for credentials and settings:

```
_USERNAME=your_username
_PASSWORD=your_password
DOWNLOAD_DIR=downloads
LOG_LEVEL=INFO
POST_DELAY_SECONDS=300  # Delay between posts (5 minutes default)
```

## 📝 Logs

Logs are stored in `logs/` directory with timestamps.

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use strong passwords
- Consider using 's official API for production use
- Be aware of rate limits to avoid account suspension

## 📚 License

This project is for educational purposes only.
