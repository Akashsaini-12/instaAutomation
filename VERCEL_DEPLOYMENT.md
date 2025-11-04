# Vercel Deployment Guide - Size Optimization

## ⚠️ Important: Size Limitations

Vercel has a **250 MB unzipped limit** for serverless functions. This project's dependencies (`instaloader`, `instagrapi`, `pillow`) can easily exceed this limit.

## 🔧 Solutions

### Option 1: Use Minimal Requirements (Recommended for Vercel)

1. **Create a minimal version for Vercel** that only includes the web UI:

```bash
# Use requirements-vercel.txt instead
cp requirements-vercel.txt requirements.txt
```

2. **Note**: This version will only show the web UI. Download/upload features won't work.

### Option 2: Deploy to Railway/Render Instead (Best Solution)

This application is **NOT suitable for Vercel** due to:
- ❌ Large dependencies (instaloader, instagrapi)
- ❌ Need for persistent storage (videos)
- ❌ Long-running background tasks

**Recommended**: Deploy to Railway or Render instead. See `DEPLOYMENT.md`.

### Option 3: Optimize Dependencies

1. **Exclude unnecessary packages**:
   - Remove `instaloader` and `instagrapi` if you only need the UI
   - Use `pillow-simd` instead of `pillow` (if available)

2. **Update `.vercelignore`** to exclude large files:
   ```
   venv/**
   *.pyc
   __pycache__/**
   downloads/**
   ```

3. **Use Vercel's dependency caching**:
   - Vercel will cache dependencies between builds
   - Ensure `requirements.txt` is optimized

### Option 4: Split into Multiple Functions

Split the application into separate functions:
- `/api/web` - Web UI only (lightweight)
- `/api/download` - Download functionality (deploy separately)

## 📝 Minimal Vercel Deployment Steps

1. **Use minimal requirements**:
   ```bash
   cp requirements-vercel.txt requirements.txt
   ```

2. **Update `api/index.py`** to handle missing dependencies gracefully:
   ```python
   try:
       from main import Automation
   except ImportError as e:
       # Handle missing dependencies
       pass
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Set environment variables** (even if features are disabled):
   ```
   _USERNAME=your_username
   _PASSWORD=your_password
   ```

## 🚀 Recommended: Railway Deployment

For **full functionality**, deploy to Railway:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Railway supports:
- ✅ Large dependencies
- ✅ Persistent storage
- ✅ Background tasks
- ✅ No size limits

## 🔍 Debugging Size Issues

Check your function size:

```bash
# Install vercel-cli
npm i -g vercel

# Check build output
vercel build

# Inspect function size in Vercel dashboard
# Go to: Project → Functions → View logs
```

## 📊 Dependency Sizes (Approximate)

- `instaloader`: ~50-80 MB
- `instagrapi`: ~30-50 MB  
- `pillow`: ~20-40 MB
- `fastapi` + `uvicorn`: ~5-10 MB
- **Total**: Often exceeds 250 MB

## ✅ Quick Fix

The fastest solution is to use **Railway** or **Render** instead of Vercel. They have no such size limits and support all features of this application.

See `DEPLOYMENT.md` for Railway deployment instructions.
