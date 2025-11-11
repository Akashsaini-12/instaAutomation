# 🚀 Vercel Deployment Guide

## ⚠️ Important: Vercel Limitations

**Vercel has a 250 MB serverless function size limit.** This project's dependencies (`instaloader`, `instagrapi`, `pillow`) exceed this limit.

## ✅ Solution: Minimal API Deployment

This repository includes a **minimal API version** optimized for Vercel that:
- ✅ Stays under the 250 MB limit
- ✅ Provides a landing page with deployment instructions
- ✅ Explains why full functionality isn't available
- ✅ Guides users to Railway/Render for full features

## 📦 What's Included in Vercel Deployment

The Vercel deployment includes:
- ✅ FastAPI web framework
- ✅ Minimal dependencies (pydantic, python-dotenv, colorlog)
- ✅ Information page explaining limitations
- ✅ Links to Railway/Render deployment guides

**Excluded** (too large for Vercel):
- ❌ `instaloader` (~50-80 MB)
- ❌ `instagrapi` (~30-50 MB)
- ❌ `pillow` (~20-40 MB)
- ❌ Video download/upload functionality

## 🔧 Deployment Steps

### 1. Connect to Vercel

1. Go to [Vercel Dashboard](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the Python project

### 2. Configure Build Settings

Vercel will automatically:
- ✅ Detect `api/index.py` as the serverless function
- ✅ Use `requirements.txt` (minimal version)
- ✅ Set Python version to 3.12

### 3. Set Environment Variables (Optional)

Even though full functionality isn't available, you can set:
```
_USERNAME=your_username
_PASSWORD=your_password
```

These won't be used in the Vercel deployment, but they're kept for reference.

### 4. Deploy

Click "Deploy" - the minimal API will be deployed successfully!

## 🌐 What Users Will See

When users visit your Vercel deployment, they'll see:
1. A beautiful landing page explaining Vercel limitations
2. Information about why full functionality isn't available
3. Links to deploy to Railway or Render for full features
4. Clear instructions on how to get full functionality

## 🚂 Recommended: Deploy to Railway

For **full functionality**, deploy to Railway:

### Quick Start:

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   railway init
   railway up
   ```

4. **Use Full Requirements**:
   - Rename `requirements-full.txt` to `requirements.txt`
   - Or set Railway to use `requirements-full.txt`

5. **Set Environment Variables**:
   ```bash
   railway variables set _USERNAME=your_username
   railway variables set _PASSWORD=your_password
   railway variables set POST_DELAY_SECONDS=900
   railway variables set MAX_POSTS_PER_DAY=10
   ```

## 📊 File Structure

```
├── api/
│   └── index.py              # Minimal Vercel API (no heavy dependencies)
├── requirements.txt          # Minimal requirements (for Vercel)
├── requirements-full.txt     # Full requirements (for Railway/Render)
├── vercel.json              # Vercel configuration
└── DEPLOYMENT.md            # Full deployment guide
```

## 🔍 Why Vercel Doesn't Work for Full Features

1. **Size Limit**: 250 MB unzipped limit
   - `instaloader`: ~50-80 MB
   - `instagrapi`: ~30-50 MB
   - `pillow`: ~20-40 MB
   - **Total**: ~100-170 MB (before other dependencies)

2. **No Persistent Storage**: Videos can't be stored permanently

3. **Serverless Functions**: Long-running tasks timeout (60s free, 300s pro)

4. **File System**: Ephemeral - files deleted between requests

## ✅ Alternative Platforms

### Railway (Recommended) ⭐
- ✅ No size limits
- ✅ Persistent storage
- ✅ Always-on containers
- ✅ Free tier available
- ✅ Easy environment variable management

### Render
- ✅ No size limits
- ✅ Persistent storage
- ✅ Free tier available
- ✅ Good for web services

### Fly.io
- ✅ No size limits
- ✅ Persistent storage
- ✅ Good for long-running tasks
- ✅ Global deployment

## 📝 Summary

- **Vercel**: Minimal API only (landing page with instructions)
- **Railway/Render**: Full functionality (video download/upload)
- **Recommendation**: Use Railway for production deployment

## 🆘 Troubleshooting

### Build Fails with Size Error

If you see "exceeded 250 MB" error:
1. ✅ Ensure `requirements.txt` is the minimal version
2. ✅ Check that `api/index.py` doesn't import heavy dependencies
3. ✅ Verify `.vercelignore` excludes large files

### Function Times Out

Vercel functions have timeout limits:
- Free: 60 seconds
- Pro: 300 seconds

**Solution**: Deploy to Railway/Render for long-running tasks.

## 📚 Additional Resources

- [Railway Deployment Guide](DEPLOYMENT.md#railway)
- [Render Deployment Guide](DEPLOYMENT.md#render)
- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Railway Documentation](https://docs.railway.app)

---

**Remember**: Vercel is great for APIs, but this project needs persistent storage and large dependencies. Use Railway or Render for the best experience! 🚀
