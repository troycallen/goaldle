# Goaldle CV API - Hybrid Approach (Best of Both)
import subprocess
import sys
import os

# install dependencies
def install_deps():
    try:
        import cv2
        import ultralytics
        import mediapipe
        import torch
        import fastapi
        import scipy
        print("✅ All dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                             "opencv-python", "ultralytics", "mediapipe", 
                             "torch", "fastapi", "uvicorn", "python-multipart", "scipy"])

install_deps()

# import everything
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
from scipy.optimize import linear_sum_assignment

# create app and add cors
app = FastAPI(title="GoalDle CV API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=False)

class HybridGoaldleCV:
    def __init__(self):
        # Use medium model for better accuracy (you can switch back to 'yolov8n-seg.pt' if too slow)
        self.yolo = YOLO('yolov8n-seg.pt')  # Use smaller model to avoid GitHub file size limits  
        self.tracks = {}
        self.next_id = 0
        self.max_disappeared = 30  # Your good parameter
        self.min_confidence = 0.3  # Your parameter - keeps more detections
        self.max_distance = 150    # Your parameter - more lenient matching
        self.min_iou = 0.1        # Your parameter
        
    def get_simple_features(self, bbox, mask, frame):
        """Simplified feature extraction - faster than full histogram"""
        x1, y1, x2, y2 = bbox
        
        # Basic features
        centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
        area = (x2 - x1) * (y2 - y1)
        aspect_ratio = (x2 - x1) / max(y2 - y1, 1)
        
        # Simple color feature - just average color in bbox
        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            avg_color = np.mean(roi.reshape(-1, 3), axis=0)
        else:
            avg_color = np.array([0, 0, 0])
        
        return {
            'centroid': centroid,
            'area': area,
            'aspect_ratio': aspect_ratio,
            'avg_color': avg_color,
            'bbox': bbox
        }
    
    def calculate_similarity(self, det_features, track_features):
        """Lightweight similarity calculation"""
        # Distance check first (early exit)
        cent_dist = np.sqrt((det_features['centroid'][0] - track_features['centroid'][0])**2 + 
                           (det_features['centroid'][1] - track_features['centroid'][1])**2)
        
        if cent_dist > self.max_distance:
            return 0  # Too far apart
        
        # IoU check
        iou = self.iou(det_features['bbox'], track_features['bbox'])
        if iou < self.min_iou:
            return 0  # Not enough overlap
        
        # Area similarity
        area_ratio = min(det_features['area'], track_features['area']) / max(det_features['area'], track_features['area'])
        
        # Color similarity (simple Euclidean distance)
        color_dist = np.linalg.norm(det_features['avg_color'] - track_features['avg_color'])
        color_sim = max(0, 1 - color_dist / 100)  # Normalize to 0-1
        
        # Combined score
        similarity = (
            (1 / (1 + cent_dist/50)) * 0.5 +  # Distance (most important)
            iou * 0.3 +                        # Overlap
            area_ratio * 0.1 +                 # Size consistency
            color_sim * 0.1                    # Color consistency
        )
        
        return similarity
    
    def detect_and_track(self, frame):
        # YOLOv8 detection with your parameters
        results = self.yolo(frame, classes=[0], verbose=False, conf=self.min_confidence)
        detections = []
        
        for result in results:
            if result.boxes is not None and result.masks is not None:
                for i, (box, mask) in enumerate(zip(result.boxes, result.masks)):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    
                    # Basic size filtering
                    bbox_area = (x2 - x1) * (y2 - y1)
                    if bbox_area > 500:  # Minimum reasonable size
                        mask_data = mask.data[0].cpu().numpy()
                        features = self.get_simple_features((x1, y1, x2, y2), mask_data, frame)
                        detections.append((x1, y1, x2, y2, conf, mask_data, features))
        
        # Use Hungarian algorithm for assignment (prevents blinking)
        if len(detections) > 0 and len(self.tracks) > 0:
            current_tracks = self.assign_with_hungarian(detections)
        else:
            # Initialize tracks for first frame or when no existing tracks
            current_tracks = self.initialize_tracks(detections)
        
        # Clean up old tracks
        self.cleanup_tracks(current_tracks)
        
        return current_tracks
    
    def assign_with_hungarian(self, detections):
        """Hungarian algorithm assignment"""
        track_ids = [tid for tid, track in self.tracks.items() if track['frames'] < self.max_disappeared]
        
        if not track_ids:
            return self.initialize_tracks(detections)
        
        # Build similarity matrix
        similarity_matrix = np.zeros((len(detections), len(track_ids)))
        
        for i, det in enumerate(detections):
            features = det[6]
            for j, track_id in enumerate(track_ids):
                similarity = self.calculate_similarity(features, self.tracks[track_id]['features'])
                similarity_matrix[i, j] = similarity
        
        # Hungarian assignment (maximize similarity)
        if similarity_matrix.size > 0:
            row_indices, col_indices = linear_sum_assignment(-similarity_matrix)
        else:
            row_indices, col_indices = [], []
        
        # Process assignments
        current_tracks = []
        assigned_detections = set()
        assigned_tracks = set()
        
        for row, col in zip(row_indices, col_indices):
            if similarity_matrix[row, col] > 0.2:  # Minimum threshold
                det = detections[row]
                track_id = track_ids[col]
                x1, y1, x2, y2, conf, mask, features = det
                
                # Update track
                self.tracks[track_id]['features'] = features
                self.tracks[track_id]['frames'] = 0
                
                current_tracks.append((x1, y1, x2, y2, track_id, mask))
                assigned_detections.add(row)
                assigned_tracks.add(track_id)
        
        # Create new tracks for unassigned detections
        for i, det in enumerate(detections):
            if i not in assigned_detections:
                x1, y1, x2, y2, conf, mask, features = det
                track_id = self.next_id
                self.next_id += 1
                
                self.tracks[track_id] = {
                    'features': features,
                    'frames': 0
                }
                
                current_tracks.append((x1, y1, x2, y2, track_id, mask))
        
        # Update frames for unassigned tracks
        for track_id in track_ids:
            if track_id not in assigned_tracks:
                self.tracks[track_id]['frames'] += 1
        
        return current_tracks
    
    def initialize_tracks(self, detections):
        """Initialize tracks for first frame"""
        current_tracks = []
        for det in detections:
            x1, y1, x2, y2, conf, mask, features = det
            track_id = self.next_id
            self.next_id += 1
            
            self.tracks[track_id] = {
                'features': features,
                'frames': 0
            }
            
            current_tracks.append((x1, y1, x2, y2, track_id, mask))
        
        return current_tracks
    
    def cleanup_tracks(self, current_tracks):
        """Remove old tracks"""
        tracks_to_remove = []
        for track_id in list(self.tracks.keys()):
            if self.tracks[track_id]['frames'] > self.max_disappeared:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
    
    def iou(self, bbox1, bbox2):
        """Your IoU function"""
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
    
    def blur_players(self, frame, tracks):
        """Your improved mask processing"""
        result = frame.copy()
        h, w = frame.shape[:2]
        
        for x1, y1, x2, y2, track_id, mask in tracks:
            # Resize mask to frame size if needed
            if mask.shape != (h, w):
                mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
            else:
                mask_resized = mask
            
            # Your tight mask processing
            binary_mask = (mask_resized > 0.5).astype(np.uint8)  # Higher threshold
            
            # Minimal morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
            
            # Light smoothing
            binary_mask = cv2.GaussianBlur(binary_mask.astype(np.float32), (3, 3), 0)
            binary_mask = (binary_mask > 0.5).astype(np.uint8)
            
            # Apply black silhouette
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
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                tracks = self.detect_and_track(frame)
                processed_frame = self.blur_players(frame, tracks)
                out.write(processed_frame)
                
                frame_count += 1
                if frame_count % 30 == 0:
                    active_tracks = len([t for t in self.tracks.values() if t['frames'] < 5])
                    print(f"Processed {frame_count} frames - Active tracks: {active_tracks}")
            
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

cv = HybridGoaldleCV()

@app.get("/")
async def root():
    return {"message": "GoalDle CV API - Hybrid Approach", "status": "ready"}

@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Must be video file")
    
    contents = await file.read()
    result = cv.process_video(contents)
    return JSONResponse(content=result)

@app.post("/reset-tracking")
async def reset_tracking():
    """Reset tracking state for new video"""
    global cv
    cv = HybridGoaldleCV()
    return {"message": "Tracking reset successfully"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GoalDle CV API - Hybrid Approach...")
    uvicorn.run(app, host="0.0.0.0", port=8000)