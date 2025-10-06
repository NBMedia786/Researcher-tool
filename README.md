# AI Video Analyzer - Researcher Tool

An intelligent video analysis tool powered by Google's Gemini Pro that extracts timestamps and analyzes video content with a focus on investigative and research applications.

## Features

- **Investigative Analysis Categories**: Extracts timestamps specifically for:
  - 911 Calls - Emergency calls and distress signals
  - CCTV Footage - Surveillance activities and security incidents
  - Interrogation - Questioning sessions and confessions
  - Bodycam Footage - Police interactions and evidence collection
  - Investigation - Case development and evidence discovery
  - Summary & Storyline - Complete narrative analysis

- **Flexible Input Options**:
  - Upload video files directly (MP4, AVI, MOV, etc.)
  - Enter video URLs for remote analysis
  - Support for YouTube and other video platforms

- **Custom Prompts**: Add specific requirements for focused analysis

- **Modern UI**: Clean, responsive interface built with Tailwind CSS

- **Export Results**: Download analysis reports as text files

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- FFmpeg (for video processing)

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (required for video processing):
   
   **On macOS**:
   ```bash
   brew install ffmpeg
   ```
   
   **On Ubuntu/Debian**:
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **On Windows**:
   Download from https://ffmpeg.org/download.html

4. **Set up your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```
   
   Or create a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

## Running the Application

### Development Mode
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Usage

1. **Open the application** in your web browser
2. **Select analysis type** from the predefined options or use custom prompts
3. **Upload a video file** or **enter a video URL**
4. **Click "Analyze Video"** to start the analysis
5. **View results** with timestamps and detailed analysis
6. **Download the report** if needed

## API Endpoints

- `GET /` - Main application interface
- `POST /upload` - Video analysis endpoint
- `GET /health` - Health check endpoint

## Configuration

The application supports the following environment variables:

- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `MAX_CONTENT_LENGTH` - Maximum file upload size (default: 500MB)

## Deployment

### Heroku
1. Create a `Procfile`:
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

2. Set environment variables in Heroku dashboard:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Deploy using Heroku CLI or GitHub integration

### Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### VPS/Cloud Server
1. Install dependencies on your server
2. Set up a reverse proxy (nginx) if needed
3. Use a process manager like PM2 or systemd
4. Configure SSL certificates for HTTPS

## File Structure

```
Researcher tool/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/
    └── index.html        # Web interface template
```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set" error**:
   - Make sure you've set the environment variable correctly
   - Check that your API key is valid and has proper permissions

2. **Video processing errors**:
   - Ensure FFmpeg is installed and accessible
   - Check that the video format is supported
   - Verify the video file isn't corrupted

3. **Memory issues with large videos**:
   - The application extracts frames for analysis to reduce memory usage
   - For very large videos, consider compressing them first

4. **URL download failures**:
   - Some video URLs may be protected or require authentication
   - YouTube videos may have restrictions
   - Try downloading the video manually and uploading the file instead

## Security Notes

- The application processes videos temporarily and deletes them after analysis
- No video data is stored permanently on the server
- API keys should be kept secure and not committed to version control
- Consider using HTTPS in production environments

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your API key and dependencies
3. Check the application logs for detailed error messages

## License

This project is for educational and research purposes. Please ensure you have proper rights to analyze any videos you process with this tool.
# Researcher-tool
