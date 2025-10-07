from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
import os
import tempfile
import requests
import google.generativeai as genai
import cv2
import base64
from io import BytesIO
from PIL import Image
import json
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configure Gemini Pro
genai.configure(api_key=os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'))

# Default prompt for specific investigative categories
DEFAULT_PROMPT = """Analyze this video and extract the following information:

## METADATA EXTRACTION (Extract from any visible text, audio, or context):
- **DATE**: Any dates, times, or timestamps visible or mentioned
- **ADDRESS/LOCATION**: Street addresses, building names, landmarks, or location references
- **CITY/STATE/COUNTY**: Geographic location information
- **POLICE DEPARTMENT**: Agency names, officer badges, department identifiers, or jurisdiction

## TIMESTAMP ANALYSIS (Extract timestamps for these categories):

1. 911 CALLS:
   - Emergency calls being made or received
   - Distress signals or calls for help
   - Emergency dispatcher communications
   - Critical emergency moments

2. CCTV FOOTAGE:
   - Suspicious activities or behaviors
   - People entering or leaving areas
   - Vehicle movements and activities
   - Security incidents or breaches
   - Unusual or notable events

3. INTERROGATION:
   - Questioning sessions or interviews
   - Confessions or admissions
   - Denials or evasive responses
   - Important statements or testimony
   - Emotional reactions during questioning

4. BODYCAM FOOTAGE:
   - Police officer interactions with civilians
   - Use of force incidents
   - Evidence collection moments
   - Procedural compliance or violations
   - Important statements or commands

5. INVESTIGATION:
   - Evidence discovery and collection
   - Crime scene analysis
   - Witness interviews
   - Key findings or breakthroughs
   - Case development moments

6. INTERROGATION (Additional):
   - Follow-up questioning sessions
   - Cross-examinations
   - Additional confessions or statements
   - Legal proceedings or hearings

## FORMAT:
**METADATA:**
- Date: [extracted date/time information]
- Address/Location: [extracted location details]
- City/State/County: [extracted geographic information]
- Police Department: [extracted agency information]

**TIMESTAMPS:**
Format each timestamp as: [MM:SS] - [CATEGORY] - Description

**SUMMARY AND STORYLINE:**
After extracting all timestamps, provide a comprehensive summary that explains:
- The overall narrative of the video
- Key events and their significance
- Timeline of important developments
- Main characters or subjects involved
- Conclusion or outcome

Be thorough in identifying moments that fit these specific categories and extract all visible metadata."""

def download_video_from_url(url):
    """Download video from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        
        temp_file.close()
        return temp_file.name
    except Exception as e:
        raise Exception(f"Failed to download video: {str(e)}")

def extract_frames_from_video(video_path, max_frames=20):
    """Extract frames from video for analysis"""
    # Check if file exists and get file size
    if not os.path.exists(video_path):
        raise Exception(f"Video file not found: {video_path}")
    
    file_size = os.path.getsize(video_path)
    if file_size == 0:
        raise Exception("Video file is empty or corrupted")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        # Check if it's a codec issue or file corruption
        raise Exception(
            f"Failed to open video file. File size: {file_size} bytes. "
            f"This often happens when codecs are missing or the video file is corrupted. "
            f"Try uploading a different video file or ensure it's a valid MP4/H.264 format. "
            f"On Railway, set NIXPACKS_PKGS=ffmpeg,ffmpeg-full and redeploy."
        )
    frames = []
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if fps is None or fps <= 0:
        cap.release()
        raise Exception(
            f"Invalid video properties detected. FPS: {fps}, Total frames: {total_frames}, "
            f"Resolution: {width}x{height}. This usually indicates a corrupted video file or missing codecs. "
            f"Try uploading a different video file or ensure it's a valid MP4/H.264 format."
        )
    duration = total_frames / fps if fps > 0 else 0
    
    # Calculate frame interval
    frame_interval = max(1, total_frames // max_frames)
    
    frame_count = 0
    extracted_count = 0
    
    while cap.isOpened() and extracted_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize frame for better processing
            frame_rgb = cv2.resize(frame_rgb, (640, 360))
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Convert to base64
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            timestamp = frame_count / fps if fps > 0 else 0
            frames.append({
                'timestamp': timestamp,
                'image': img_str,
                'frame_number': frame_count
            })
            extracted_count += 1
        
        frame_count += 1
    
    cap.release()
    return frames, duration

def analyze_video_with_gemini(frames, custom_prompt):
    """Analyze video frames using Gemini Pro"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Use custom prompt or default comprehensive prompt
        if custom_prompt.strip():
            prompt = f"{DEFAULT_PROMPT}\n\nADDITIONAL USER REQUIREMENTS:\n{custom_prompt}\n\nPlease ensure you address the user's specific requirements while maintaining comprehensive coverage of all significant events."
        else:
            prompt = DEFAULT_PROMPT
        
        # Prepare content for Gemini
        content_parts = [prompt]
        
        # Add frames with timestamps
        for frame in frames:
            content_parts.append(f"Timestamp: {frame['timestamp']:.2f}s")
            content_parts.append({
                "mime_type": "image/jpeg",
                "data": frame['image']
            })
        
        # Generate analysis
        response = model.generate_content(content_parts)
        return response.text
        
    except Exception as e:
        raise Exception(f"Gemini analysis failed: {str(e)}")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    # Return no content to prevent 404 log spam when browsers request favicon
    return Response(status_code=204)

@app.post("/upload")
async def upload_video(
    request: Request,
    video_file: UploadFile | None = File(None),
    video_url: str = Form("") ,
    custom_prompt: str = Form("")
):
    try:
        custom_prompt = (custom_prompt or "").strip()

        if video_file is not None and video_file.filename:
            # Validate file extension - only allow MP4 files
            file_extension = os.path.splitext(video_file.filename)[1].lower()
            if file_extension not in ['.mp4']:
                return JSONResponse({
                    "error": f"Invalid file format. Only MP4 files are accepted. Received: {file_extension}"
                }, status_code=400)
            
            # Validate MIME type (be more flexible with curl uploads)
            if video_file.content_type and video_file.content_type not in ['video/mp4', 'application/octet-stream']:
                return JSONResponse({
                    "error": f"Invalid file type. Only MP4 videos are accepted. Received: {video_file.content_type}"
                }, status_code=400)
            
            suffix = ".mp4"  # Force MP4 extension
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            content = await video_file.read()
            with open(temp_path.name, "wb") as f:
                f.write(content)
            video_path = temp_path.name
        else:
            video_url = (video_url or "").strip()
            if not video_url:
                return JSONResponse({"error": "No video URL provided"}, status_code=400)
            video_path = download_video_from_url(video_url)

        # Extract frames
        frames, duration = extract_frames_from_video(video_path)

        if not frames:
            return JSONResponse({"error": "Could not extract frames from video"}, status_code=400)

        # Analyze with Gemini
        analysis = analyze_video_with_gemini(frames, custom_prompt)

        # Clean up temporary file
        try:
            os.unlink(video_path)
        except Exception:
            pass

        return JSONResponse({
            "success": True,
            "analysis": analysis,
            "duration": duration,
            "frames_analyzed": len(frames)
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    # Optional local run support via uvicorn
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY environment variable not set!")
        print("Please set your Gemini API key: export GEMINI_API_KEY='your_api_key_here'")
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=False)
