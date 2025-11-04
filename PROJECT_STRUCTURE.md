# Project Structure

## Directory Layout

```
-automation/
├── src/                          # Source code package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management (environment variables)
│   ├── models.py                # Data models (VideoMetadata, VideoStatus)
│   ├── utils.py                 # Utility functions (logging, URL validation, etc.)
│   ├── download_videos.py       # Video downloading logic using instaloader
│   └── upload_to_.py   #  upload logic using instagrapi
│
├── main.py                      # Main automation orchestrator script
├── cli.py                       # Command-line interface
├── web_ui.py                    # Optional FastAPI web interface
├── setup_env.py                 # Interactive .env setup script
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick start guide
├── PROJECT_STRUCTURE.md         # This file
│
├── downloads/                   # Downloaded videos (created automatically)
└── logs/                        # Log files (created automatically)
```

## Core Modules

### `src/config.py`
- **Purpose**: Configuration management
- **Features**:
  - Loads settings from `.env` file
  - Creates necessary directories
  - Handles missing credentials gracefully
  - Uses Pydantic for validation

### `src/models.py`
- **Purpose**: Data models for video metadata
- **Classes**:
  - `VideoStatus`: Enum for tracking video processing status
  - `VideoMetadata`: Dataclass for storing video information

### `src/utils.py`
- **Purpose**: Utility functions
- **Functions**:
  - `setup_logger()`: Configure colored console and file logging
  - `validate__url()`: Validate  URLs
  - `extract_post_id_from_url()`: Extract post shortcode from URL
  - `get_file_size()`: Get file size in bytes
  - `sanitize_filename()`: Clean filenames for filesystem
  - `format_file_size()`: Human-readable file size formatting

### `src/download_videos.py`
- **Purpose**: Download  videos
- **Class**: `VideoDownloader`
- **Methods**:
  - `download_video(url)`: Download single video
  - `download_multiple_videos(urls)`: Batch download
  - `_find_downloaded_video(post_id)`: Locate downloaded file

### `src/upload_to_.py`
- **Purpose**: Upload videos to 
- **Class**: `Uploader`
- **Methods**:
  - `login()`: Authenticate with 
  - `upload_video()`: Upload single video
  - `upload_video_metadata()`: Upload using metadata object
  - `upload_multiple_videos()`: Batch upload with delays
  - `logout()`: Cleanup session

### `main.py`
- **Purpose**: Main automation orchestrator
- **Class**: `Automation`
- **Methods**:
  - `download_videos()`: Download videos from URLs
  - `upload_videos()`: Upload videos to 
  - `run()`: Complete automation workflow
  - `validate_urls()`: URL validation
  - `get_status_summary()`: Get processing summary

## Entry Points

### `cli.py`
- Command-line interface
- Supports:
  - `--urls`: Direct URL input
  - `--file`: Read URLs from file
  - `--no-upload`: Download only mode

### `web_ui.py`
- FastAPI web interface
- Endpoints:
  - `GET /`: Web form for URL submission
  - `POST /process`: Submit URLs for processing
  - `GET /status`: Check processing status
  - `GET /health`: Health check

### `setup_env.py`
- Interactive setup script
- Creates `.env` file with credentials

## Data Flow

```
User Input (URLs)
    ↓
Automation.run()
    ↓
1. Validate URLs
    ↓
2. VideoDownloader.download_multiple_videos()
    ├─→ For each URL:
    │   ├─→ Extract post ID
    │   ├─→ Load post via instaloader
    │   ├─→ Download video
    │   └─→ Create VideoMetadata
    ↓
3. Store VideoMetadata list
    ↓
4. Uploader.upload_multiple_videos()
    ├─→ Login to 
    ├─→ For each downloaded video:
    │   ├─→ Upload via instagrapi
    │   ├─→ Update metadata status
    │   └─→ Wait (delay between uploads)
    ↓
5. Return results with status
```

## Configuration

Configuration is managed via `.env` file:

```env
_USERNAME=your_username
_PASSWORD=your_password
DOWNLOAD_DIR=downloads
LOG_LEVEL=INFO
POST_DELAY_SECONDS=300
AUTO_POST_ENABLED=false
POST_INTERVAL_HOURS=2
```

## Logging

Logs are written to:
- **Console**: Colored output with timestamps
- **File**: `logs/_automation_YYYYMMDD.log`

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Error Handling

- **Download failures**: VideoMetadata status set to `DOWNLOAD_FAILED` with error message
- **Upload failures**: VideoMetadata status set to `UPLOAD_FAILED` with error message
- **Authentication errors**: Clear error messages with troubleshooting hints
- **Rate limiting**: Automatic delay and retry logic

## Dependencies

See `requirements.txt` for complete list. Key dependencies:
- `instaloader`:  video downloading
- `instagrapi`:  API client for uploading
- `fastapi`: Web framework (optional)
- `pydantic`: Configuration validation
- `colorlog`: Colored logging
