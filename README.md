#  Automation Project

A complete Python-based automation system to download  videos from URLs and automatically post them to your  account.

## ⚠️ Important Disclaimer

**Please note**: This project is for educational purposes. 's Terms of Service prohibit automated posting and scraping. Use this at your own risk.  may temporarily or permanently suspend accounts that violate their terms.

## 🚀 Features

- **Batch Download**: Download multiple  videos from URLs
- **Automatic Posting**: Automatically upload videos to your  account
- **Metadata Tracking**: Store video metadata (title, path, timestamp, status)
- **Error Handling**: Robust error handling for download and upload failures
- **Logging**: Comprehensive logging for tracking operations
- **Queue Management**: Track download and upload status
- **CLI Interface**: Simple command-line interface
- **Web UI** (Optional): FastAPI-based web interface
- **Scheduling** (Optional): Schedule automatic posting

## 📋 Prerequisites

- Python 3.10 or higher
-  account credentials
- Stable internet connection

## 🔧 Installation

1. **Clone or download this project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up configuration**:
   - Copy `.env.example` to `.env`
   - Fill in your  credentials in `.env`:
   ```
   _USERNAME=your_username
   _PASSWORD=your_password
   ```

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
