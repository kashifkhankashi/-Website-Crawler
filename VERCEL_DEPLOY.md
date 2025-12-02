# Vercel Deployment Guide

## Important Notes

⚠️ **Vercel Limitations for This App:**

1. **Execution Time Limits:**
   - Free tier: 10 seconds per function
   - Pro tier: 60 seconds per function
   - Scrapy crawls can take much longer than this!

2. **Serverless Functions:**
   - Each request spawns a new function instance
   - No persistent state between requests
   - `active_crawls` dictionary is in-memory and will be lost

3. **SocketIO Limitations:**
   - WebSocket connections may not work reliably on Vercel
   - Real-time progress updates might not work

## Deployment Steps

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Set Environment Variables (if needed):**
   ```bash
   vercel env add SECRET_KEY
   ```

## Alternative Solutions

For production use, consider:

1. **Railway.app** - Better for long-running processes
2. **Render.com** - Supports persistent processes
3. **Heroku** - Traditional hosting (paid)
4. **DigitalOcean App Platform** - Good for Flask apps
5. **AWS/GCP** - Full control, more complex setup

## Current Configuration

- `vercel.json` - Routes all requests to Flask app
- `api/index.py` - Serverless function entry point
- Error handling improved for JSON responses

## Troubleshooting

If you see "Unexpected token '<'" error:
- Check Vercel function logs
- Ensure all API routes return JSON
- Check that routes are properly configured in `vercel.json`

