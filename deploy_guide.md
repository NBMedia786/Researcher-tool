# 🚀 Deployment Guide - AI Video Analyzer

## Quick Start (Railway - Recommended)

### 1. Prepare Your Code
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/yourusername/ai-video-analyzer.git
git push -u origin main
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variable: `GEMINI_API_KEY=your_actual_api_key`
6. Deploy!

### 3. Your app will be live at: `https://your-app-name.railway.app`

---

## Alternative: Render.com

### 1. Create Web Service
1. Go to [render.com](https://render.com)
2. Sign up and connect GitHub
3. Click "New" → "Web Service"
4. Connect your repository

### 2. Configure Settings
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
- **Environment Variables:** Add `GEMINI_API_KEY`

### 3. Deploy
Click "Create Web Service" and wait for deployment.

---

## Alternative: Heroku

### 1. Install Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# Or download from heroku.com
```

### 2. Deploy
```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variable
heroku config:set GEMINI_API_KEY=your_actual_api_key

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

---

## Environment Variables Required

Make sure to set these in your hosting platform:

- `GEMINI_API_KEY` - Your Google Gemini API key (required)

---

## Important Notes

1. **File Size Limits**: Most free tiers have file upload limits (usually 100MB)
2. **Memory Usage**: Video processing uses memory - free tiers may have limits
3. **Timeout**: Free tiers may have request timeout limits
4. **API Key**: Never commit your API key to GitHub - use environment variables

---

## Troubleshooting

### Port Issues
If you get port errors, the hosting platform will provide the correct port via `$PORT` environment variable.

### Memory Issues
For large videos, consider:
- Reducing `max_frames` in the code
- Using a paid tier with more memory
- Compressing videos before upload

### API Key Issues
Make sure your `GEMINI_API_KEY` is set correctly in the hosting platform's environment variables section.

---

## Cost Comparison

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| Railway | 500 hours/month | Sleeps after inactivity |
| Render | 750 hours/month | Sleeps after 15 min inactivity |
| Heroku | 550-1000 dyno hours/month | Sleeps after 30 min inactivity |
| PythonAnywhere | Always-on | Limited CPU seconds |

---

## Recommended: Railway
- Easiest setup
- Good free tier
- Automatic deployments
- Built-in environment variable management
