# Deployment Guide

This guide explains how to deploy the Instagram Automation project to various platforms.

## ⚠️ Important Considerations

### Vercel Limitations

**Vercel is NOT recommended for this project** due to the following limitations:

1. **No Persistent Storage**: Downloaded videos are stored in the `downloads/` directory, which is ephemeral on Vercel
2. **Serverless Functions**: Long-running background tasks may timeout (max 60 seconds on free tier, 300s on Pro)
3. **File System**: Writable file system is limited - files may be deleted between requests
4. **Session Storage**: Instagram session files won't persist across function invocations

### Better Alternatives

For this type of application, consider these platforms instead:

1. **Railway** ⭐ Recommended
2. **Render**
3. **Fly.io**
4. **Heroku** (paid)
5. **DigitalOcean App Platform**
6. **AWS EC2 / Lightsail**
7. **Google Cloud Run** (with Cloud Storage)

---

## 🚂 Deployment to Railway (Recommended)

Railway is ideal because it provides:
- Persistent storage
- Always-on containers
- Easy environment variable management
- Free tier available

### Steps:

1. **Install Railway CLI**:
```bash
npm i -g @railway/cli
```

2. **Login**:
```bash
railway login
```

3. **Initialize Project**:
```bash
railway init
```

4. **Set Environment Variables**:
```bash
railway variables set _USERNAME=your_username
railway variables set _PASSWORD=your_password
railway variables set AUTO_LIKE_COMMENTS=true
railway variables set USE_TRENDING_HASHTAGS=true
```

5. **Deploy**:
```bash
railway up
```

6. **Create `Procfile`** (if not exists):
```
web: python web_ui.py
```

---

## 🌐 Deployment to Render

### Steps:

1. **Create `render.yaml`**:
```yaml
services:
  - type: web
    name: instagram-automation
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python web_ui.py
    envVars:
      - key: _USERNAME
        value: your_username
      - key: _PASSWORD
        value: your_password
      - key: PORT
        value: 8000
```

2. **Deploy via Render Dashboard**:
   - Connect your GitHub repository
   - Select the `render.yaml` file
   - Add environment variables in the dashboard

---

## ✈️ Deployment to Fly.io

### Steps:

1. **Install Fly CLI**:
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Create `fly.toml`**:
```toml
app = "instagram-automation"
primary_region = "iad"

[build]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

3. **Deploy**:
```bash
fly launch
fly secrets set _USERNAME=your_username
fly secrets set _PASSWORD=your_password
fly deploy
```

---

## 📦 Deployment to Vercel (Limited Functionality)

**Note**: This will NOT work fully due to Vercel's serverless limitations. Use only for testing the web UI without file operations.

### Steps:

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel
```

3. **Set Environment Variables** in Vercel Dashboard:
   - Go to your project settings
   - Add environment variables:
     - `_USERNAME`
     - `_PASSWORD`
     - `AUTO_LIKE_COMMENTS`
     - etc.

### Known Issues on Vercel:
- ❌ Downloaded videos will not persist
- ❌ Background tasks may timeout
- ❌ File operations are limited
- ❌ Instagram sessions won't persist

---

## 🐳 Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories for downloads and logs
RUN mkdir -p downloads logs

EXPOSE 8000

CMD ["python", "web_ui.py"]
```

Build and run:
```bash
docker build -t instagram-automation .
docker run -p 8000:8000 --env-file .env instagram-automation
```

---

## 🔐 Environment Variables

Make sure to set these in your deployment platform:

```bash
# Required
_USERNAME=your_instagram_username
_PASSWORD=your_instagram_password

# Optional
DOWNLOAD_DIR=downloads
LOG_DIR=logs
LOG_LEVEL=INFO
POST_DELAY_SECONDS=300
AUTO_POST_ENABLED=false
POST_INTERVAL_HOURS=2

# Auto-features
AUTO_LIKE_COMMENTS=true
AUTO_LIKE_COMMENT_DELAY=60
AUTO_COMMENT_ENABLED=true
AUTO_COMMENT_TEXT=Thanks for watching! 🙌
AUTO_COMMENT_DELAY=30
AUTO_REPLY_ENABLED=true
AUTO_REPLY_TEXT=Thanks for your comment! 🙏
AUTO_REPLY_DELAY=120

# Hashtags
USE_TRENDING_HASHTAGS=true
HASHTAG_COUNT=15
BASE_HASHTAGS=#viral #trending #fyp #explore
```

---

## ✅ Recommended Platform: Railway

For the best experience with this application, **Railway is recommended** because:

1. ✅ Persistent file storage
2. ✅ Long-running processes supported
3. ✅ Simple deployment
4. ✅ Free tier available
5. ✅ Easy environment variable management
6. ✅ Automatic HTTPS

---

## 📝 Post-Deployment Checklist

- [ ] Environment variables configured
- [ ] Test video download functionality
- [ ] Test video upload functionality
- [ ] Verify auto-like comments works
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Set up monitoring/alerting

---

## 🔒 Security Notes

- Never commit `.env` files to git
- Use platform secrets management for credentials
- Enable HTTPS only
- Regularly rotate Instagram credentials
- Monitor for suspicious activity

---

## 🆘 Troubleshooting

### Videos not persisting
- **Solution**: Use a platform with persistent storage (Railway, Render, etc.)

### Background tasks timing out
- **Solution**: Use always-on containers, not serverless functions

### Instagram login failing
- **Solution**: Check credentials and disable 2FA or handle it manually

### High memory usage
- **Solution**: Increase container memory or optimize video processing

---

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs/)
- [Vercel Docs](https://vercel.com/docs)
