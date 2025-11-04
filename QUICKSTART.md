# Quick Start Guide

Get up and running with  Automation in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Credentials

Run the interactive setup script:

```bash
python setup_env.py
```

Or manually create a `.env` file from `.env.example`:

```bash
cp .env.example .env
# Then edit .env with your  credentials
```

## Step 3: Run the Automation

### Option A: Using CLI

```bash
python cli.py --urls "https://www..com/p/ABC123/" "https://www..com/p/DEF456/"
```

### Option B: Using Python Script

```python
from main import Automation

automation = Automation()
urls = [
    "https://www..com/p/ABC123/",
    "https://www..com/p/DEF456/"
]
automation.run(urls)
```

### Option C: Using Web UI

```bash
python web_ui.py
```

Then open `http://localhost:8000` in your browser.

## Step 4: Check Results

- **Downloaded videos**: Check the `downloads/` directory
- **Logs**: Check the `logs/` directory for detailed logs
- **Status**: The CLI will show a summary at the end

## Troubleshooting

### Login Issues

- Verify your credentials in `.env`
- Make sure 2FA is disabled (or handle it manually)
- Check if  requires account verification

### Download Failures

- Ensure the URLs are valid  video posts
- Videos must be public (private videos require authentication)
- Check your internet connection

### Upload Failures

- Verify videos exist in `downloads/` directory
- Check  rate limits (wait between uploads)
- Ensure videos meet  requirements (format, size, duration)

## Important Notes

⚠️ **Rate Limiting**:  has strict rate limits. The default delay between uploads is 5 minutes (300 seconds). Adjust `POST_DELAY_SECONDS` in `.env` if needed.

⚠️ **Account Safety**: Using automation may violate 's Terms of Service. Use at your own risk.

⚠️ **2FA**: If you have Two-Factor Authentication enabled, you may need to disable it or handle verification manually.

## Need Help?

Check the main [README.md](README.md) for detailed documentation.
