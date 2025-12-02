"""
Vercel serverless function entry point for Flask app.
This file is used when deploying to Vercel.
"""
from app import app

# Export the Flask app for Vercel
handler = app

