#!/bin/bash

echo "AI Video Analyzer - Installation Script"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 is installed"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✓ pip3 is installed"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. This is required for video processing."
    echo "Please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
    echo ""
    echo "After installing FFmpeg, run this script again."
    exit 1
fi

echo "✓ FFmpeg is installed"

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY environment variable is not set."
    echo "Please set your Gemini API key:"
    echo "export GEMINI_API_KEY='your_api_key_here'"
    echo ""
    echo "You can get an API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "After setting the API key, you can run the application with:"
    echo "python3 run.py"
else
    echo "✓ Gemini API key is configured"
    echo ""
    echo "🎉 Installation complete! You can now run the application with:"
    echo "python3 run.py"
fi
