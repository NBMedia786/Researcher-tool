#!/usr/bin/env python3
"""
Startup script for AI Video Analyzer
"""
import os
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import google.generativeai
        import cv2
        import PIL
        import requests
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if Gemini API key is set"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("✗ GEMINI_API_KEY environment variable not set")
        print("Please set your API key:")
        print("export GEMINI_API_KEY='your_api_key_here'")
        return False
    else:
        print("✓ Gemini API key is configured")
        return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg not found")
        print("Please install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return False

def main():
    """Main startup function"""
    print("AI Video Analyzer - Starting up...")
    print("=" * 40)
    
    # Check all requirements
    checks = [
        check_dependencies(),
        check_api_key(),
        check_ffmpeg()
    ]
    
    if not all(checks):
        print("\n❌ Some requirements are missing. Please fix the issues above.")
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting the application...")
    print("=" * 40)
    
    # Import and run the app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
