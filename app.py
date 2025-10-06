from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import tempfile
import requests
from werkzeug.utils import secure_filename
import google.generativeai as genai
import cv2
import base64
from io import BytesIO
from PIL import Image
import json
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Configure Gemini Pro
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Default prompt for specific investigative categories
DEFAULT_PROMPT = """Analyze this video and extract timestamps for the following specific categories:

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

Format each timestamp as: [MM:SS] - [CATEGORY] - Description

After extracting all timestamps, provide a comprehensive SUMMARY AND STORYLINE section that explains:
- The overall narrative of the video
- Key events and their significance
- Timeline of important developments
- Main characters or subjects involved
- Conclusion or outcome

Be thorough in identifying moments that fit these specific categories."""

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
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        custom_prompt = request.form.get('custom_prompt', '').strip()
        
        if 'video_file' in request.files:
            # Handle file upload
            file = request.files['video_file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file:
                filename = secure_filename(file.filename)
                temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                file.save(temp_path.name)
                video_path = temp_path.name
        else:
            # Handle URL input
            video_url = request.form.get('video_url', '').strip()
            if not video_url:
                return jsonify({'error': 'No video URL provided'}), 400
            
            video_path = download_video_from_url(video_url)
        
        # Extract frames
        frames, duration = extract_frames_from_video(video_path)
        
        if not frames:
            return jsonify({'error': 'Could not extract frames from video'}), 400
        
        # Analyze with Gemini
        analysis = analyze_video_with_gemini(frames, custom_prompt)
        
        # Clean up temporary file
        try:
            os.unlink(video_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'duration': duration,
            'frames_analyzed': len(frames)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY environment variable not set!")
        print("Please set your Gemini API key: export GEMINI_API_KEY='your_api_key_here'")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
