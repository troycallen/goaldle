# Minimal GoalDle CV API
import subprocess
import sys
import os

# Auto-install dependencies if missing
def install_deps():
    try:
        import cv2
        import ultralytics
        import mediapipe
        import torch
        import fastapi
        print("✅ All dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                             "opencv-python", "ultralytics", "mediapipe", 
                             "torch", "fastapi", "uvicorn", "python-multipart"])

install_deps()

# Now import everything
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
import tempfile
from datetime import datetime
from ultralytics import YOLO
from collections import defaultdict

app = FastAPI(title="GoalDle CV API", version="1.0")

# CORS - Allow all origins including file:// URLs
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"],
    allow_credentials=False
)

class MinimalCV:
    def __init__(self):
        self.yolo = YOLO('yolov8n-seg.pt')  # Segmentation model for precise masks
        self.tracks = defaultdict(lambda: {'bbox': None, 'mask': None, 'centroid': None, 'frames': 0})
        self.next_id = 0
        self.max_disappeared = 15  # Keep tracks for 15 frames when not detected
    
    def detect_and_track(self, frame):
        # YOLOv8 segmentation (disable visualization)
        results = self.yolo(frame, classes=[0], verbose=False)  # person class
        detections = []
        
        for result in results:
            if result.boxes is not None and result.masks is not None:
                for i, (box, mask) in enumerate(zip(result.boxes, result.masks)):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    if conf > 0.5:
                        # Get segmentation mask
                        mask_data = mask.data[0].cpu().numpy()  # Shape: (H, W)
                        detections.append((x1, y1, x2, y2, conf, mask_data))
        
        # Improved tracking with centroids
        current_tracks = []
        for det in detections:
            x1, y1, x2, y2, conf, mask = det
            centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
            
            best_match = None
            best_distance = float('inf')
            
            for track_id, track in self.tracks.items():
                if track['centroid'] and track['frames'] < self.max_disappeared:
                    # Use both centroid distance and IOU
                    dist = ((centroid[0] - track['centroid'][0])**2 + (centroid[1] - track['centroid'][1])**2)**0.5
                    iou = self.iou((x1, y1, x2, y2), track['bbox']) if track['bbox'] else 0
                    
                    # Combined score: prefer close centroids with decent IOU
                    if dist < 100 and iou > 0.2 and dist < best_distance:
                        best_distance = dist
                        best_match = track_id
            
            if best_match:
                self.tracks[best_match]['bbox'] = (x1, y1, x2, y2)
                self.tracks[best_match]['mask'] = mask
                self.tracks[best_match]['centroid'] = centroid
                self.tracks[best_match]['frames'] = 0
                current_tracks.append((x1, y1, x2, y2, best_match, mask))
            else:
                track_id = self.next_id
                self.next_id += 1
                self.tracks[track_id] = {'bbox': (x1, y1, x2, y2), 'mask': mask, 'centroid': centroid, 'frames': 0}
                current_tracks.append((x1, y1, x2, y2, track_id, mask))
        
        # Clean stale tracks - but keep them longer to reduce blinking
        for track_id in list(self.tracks.keys()):
            if track_id not in [t[4] for t in current_tracks]:  # Not in current detections
                self.tracks[track_id]['frames'] += 1
                if self.tracks[track_id]['frames'] > self.max_disappeared:
                    del self.tracks[track_id]
        
        return current_tracks
    
    def iou(self, bbox1, bbox2):
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def blur_players(self, frame, tracks, effect_type="blur", color=(0, 0, 0), target_zone="all"):
        result = frame.copy()
        h, w = frame.shape[:2]
        
        for x1, y1, x2, y2, track_id, mask in tracks:
            # Resize mask to frame size if needed
            if mask.shape != (h, w):
                mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
            else:
                mask_resized = mask
            
            # Convert to binary mask with smoothing
            binary_mask = (mask_resized > 0.5).astype(np.uint8)
            
            # Smooth mask edges to reduce flickering
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
            binary_mask = cv2.GaussianBlur(binary_mask.astype(np.float32), (3, 3), 0)
            binary_mask = (binary_mask > 0.5).astype(np.uint8)
            
            # Check if player should be processed based on zone
            should_process = True
            if target_zone == "goal_area":
                # Only process players in goal area (roughly bottom 1/3 and sides)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                in_goal_area = (center_y > h * 0.6) or (center_x < w * 0.2) or (center_x > w * 0.8)
                should_process = in_goal_area
            elif target_zone == "center_field":
                # Only process players in center area
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                in_center = (w * 0.3 < center_x < w * 0.7) and (h * 0.3 < center_y < h * 0.7)
                should_process = in_center
            
            if not should_process:
                continue
                
            if effect_type == "blur":
                # Apply Gaussian blur
                blurred_frame = cv2.GaussianBlur(frame, (51, 51), 0)
                result = np.where(binary_mask[..., np.newaxis], blurred_frame, result)
            
            elif effect_type == "color":
                # Apply solid color
                colored_frame = result.copy()
                colored_frame[binary_mask == 1] = color  # BGR format
                result = colored_frame
            
            elif effect_type == "silhouette":
                # Black silhouette
                result[binary_mask == 1] = [0, 0, 0]
        
        return result
    
    def process_video(self, video_bytes):
        try:
            # Save video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                f.write(video_bytes)
                temp_path = f.name
            
            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                raise ValueError("Could not open video")
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            output_path = temp_path.replace('.mp4', '_blurred.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'H264')  # Better browser compatibility
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                tracks = self.detect_and_track(frame)
                processed_frame = self.blur_players(frame, tracks, "silhouette")
                out.write(processed_frame)
                
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Processed {frame_count} frames")
            
            cap.release()
            out.release()
            
            # Read result
            with open(output_path, 'rb') as f:
                result_bytes = f.read()
            
            # Cleanup
            os.unlink(temp_path)
            os.unlink(output_path)
            
            return {
                "success": True,
                "blurred_video": base64.b64encode(result_bytes).decode(),
                "video_info": {"fps": fps, "width": width, "height": height, "frames": frame_count}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

cv = MinimalCV()

@app.get("/")
async def root():
    return {"message": "GoalDle CV API", "status": "ready"}

@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Must be video file")
    
    contents = await file.read()
    result = cv.process_video(contents)
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GoalDle CV API...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 