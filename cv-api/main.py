from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Optional
import os
from datetime import datetime
import tempfile

app = FastAPI(
    title="GoalDle CV API",
    description="Computer Vision API for GoalDle soccer player video blurring and processing",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoProcessor:
    def __init__(self):
        # Load person detection (HOG descriptor for full body detection)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    def process_video(self, video_bytes: bytes, blur_strength: int = 50) -> dict:
        """Process goal-scoring video and blur the scoring player"""
        try:
            # Save video bytes to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                temp_video.write(video_bytes)
                temp_video_path = temp_video.name
            
            # Open video
            cap = cv2.VideoCapture(temp_video_path)
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create output video writer
            output_path = temp_video_path.replace('.mp4', '_blurred.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            processed_frames = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply blurring to frame - focus on full player detection
                blurred_frame = self.apply_player_blur_to_frame(frame, blur_strength)
                out.write(blurred_frame)
                processed_frames += 1
                
                frame_count += 1
                if frame_count % 30 == 0:  # Log every 30 frames
                    print(f"Processed {frame_count}/{total_frames} frames")
            
            cap.release()
            out.release()
            
            # Read the blurred video back as bytes
            with open(output_path, 'rb') as f:
                blurred_video_bytes = f.read()
            
            # Clean up temporary files
            os.unlink(temp_video_path)
            os.unlink(output_path)
            
            return {
                "success": True,
                "blurred_video": base64.b64encode(blurred_video_bytes).decode(),
                "video_info": {
                    "fps": fps,
                    "width": width,
                    "height": height,
                    "total_frames": total_frames,
                    "processed_frames": processed_frames,
                    "blur_strength": blur_strength
                },
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Clean up temp files on error
            if 'temp_video_path' in locals():
                try:
                    os.unlink(temp_video_path)
                except:
                    pass
            if 'output_path' in locals():
                try:
                    os.unlink(output_path)
                except:
                    pass
            
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def apply_player_blur_to_frame(self, frame: np.ndarray, blur_strength: int = 50) -> np.ndarray:
        """Apply blurring to full players in the frame"""
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Create a copy of the frame for blurring
        blurred_frame = frame.copy()
        
        # Detect players using HOG (full body detection)
        players, _ = self.hog.detectMultiScale(
            gray, 
            winStride=(8, 8), 
            padding=(4, 4), 
            scale=1.05,
            hitThreshold=0
        )
        
        # Blur detected players (full body)
        for (x, y, w, h) in players:
            # Expand the region to include the full player
            # This ensures we blur the entire player, not just the detected region
            x = max(0, x - 30)  # Expand left
            y = max(0, y - 30)  # Expand up
            w = min(frame.shape[1] - x, w + 60)  # Expand width
            h = min(frame.shape[0] - y, h + 60)  # Expand height
            
            # Ensure we have a valid region
            if w > 0 and h > 0:
                player_roi = blurred_frame[y:y+h, x:x+w]
                if player_roi.size > 0:  # Check if ROI is valid
                    # Apply strong blur to the entire player
                    blurred_player = cv2.GaussianBlur(player_roi, (blur_strength, blur_strength), 0)
                    blurred_frame[y:y+h, x:x+w] = blurred_player
        
        return blurred_frame

# Initialize video processor
processor = VideoProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "GoalDle CV API is running!",
        "version": "1.0.0",
        "endpoints": [
            "/process-video",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/process-video")
async def process_video(file: UploadFile = File(...), blur_strength: int = 50):
    """Process goal-scoring video and blur the scoring player"""
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    try:
        contents = await file.read()
        result = processor.process_video(contents, blur_strength)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 