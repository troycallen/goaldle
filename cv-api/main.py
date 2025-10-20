# Goaldle CV API - Hybrid Approach (Best of Both) [Upgraded]
import subprocess
import sys
import os

# Dependencies are installed via requirements.txt

# import everything
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import tempfile
from datetime import datetime
from ultralytics import YOLO
from collections import defaultdict
from scipy.optimize import linear_sum_assignment
import torch  # NEW: for device + half
from game_logic import GoaldleGame
from simple_stats import SimpleStatsManager

# create app and add cors
app = FastAPI(title="GoalDle CV API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=False)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")
# Mount videos directory for fast streaming
app.mount("/videos", StaticFiles(directory="goals"), name="videos")


class HybridGoaldleCV:
    def __init__(self):
        # Slightly larger/better model; still fast
        self.yolo = YOLO('yolov8s-seg.pt')
        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.use_half = torch.cuda.is_available()

        self.tracks = {}
        self.next_id = 0
        self.max_disappeared = 45  # Increased from 30 - keep tracks alive longer
        self.min_confidence = 0.25  # Lowered from 0.30 - detect players more reliably
        # dynamic thresholds will be set per-frame based on resolution
        self.max_distance = 150
        self.min_iou = 0.05  # Lowered from 0.10 - allow more flexible matching

    # ---------- Utility & features ----------

    def _set_dynamic_thresholds(self, frame_shape):
        """Scale distance/IoU thresholds to video resolution."""
        h, w = frame_shape[:2]
        diag = (h ** 2 + w ** 2) ** 0.5
        # ~5% of image diagonal for assignment distance
        self.max_distance = 0.05 * diag
        # allow lower IoU on wide shots
        self.min_iou = 0.05

    def get_simple_features(self, bbox, mask, frame):
        """Feature extraction using ONLY the mask (avoids grass contamination)."""
        x1, y1, x2, y2 = bbox

        centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
        area = max(1, (x2 - x1) * (y2 - y1))
        aspect_ratio = (x2 - x1) / max(1, (y2 - y1))

        # mask is float [0..1] aligned to frame size
        m = (mask > 0.5).astype(np.uint8)

        roi = frame[y1:y2, x1:x2]
        m_crop = m[y1:y2, x1:x2]
        if roi.size > 0 and m_crop.any():
            # average BGR color inside the player only
            b, g, r, _ = cv2.mean(roi, mask=m_crop)
            avg_color = np.array([b, g, r], dtype=np.float32)
        else:
            avg_color = np.array([0, 0, 0], dtype=np.float32)

        return {
            'centroid': centroid,
            'area': area,
            'aspect_ratio': aspect_ratio,
            'avg_color': avg_color,
            'bbox': bbox
        }

    def iou(self, bbox1, bbox2):
        """IoU for xyxy bboxes."""
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
        return float(intersection) / float(union) if union > 0 else 0.0

    # ---------- Similarity & Assignment ----------

    def _predicted_centroid(self, track):
        """Predict next centroid using a tiny velocity model for stability."""
        c = track['features']['centroid']
        vx, vy = track.get('vel', (0.0, 0.0))
        return (c[0] + vx, c[1] + vy)

    def calculate_similarity(self, det_features, track):
        """Similarity with IoU + distance-to-predicted-center + color + area."""
        track_features = track['features']

        # predicted center for the track
        px, py = self._predicted_centroid(track)
        dx = det_features['centroid'][0] - px
        dy = det_features['centroid'][1] - py
        cent_dist = float(np.hypot(dx, dy))

        if cent_dist > self.max_distance:
            return 0.0

        # IoU check first
        iou = self.iou(det_features['bbox'], track_features['bbox'])
        if iou < self.min_iou:
            return 0.0

        # normalized center-distance similarity (0..1)
        cx_sim = 1.0 / (1.0 + (cent_dist / (self.max_distance + 1e-6)))

        # area similarity
        area_ratio = min(det_features['area'], track_features['area']) / max(det_features['area'], track_features['area'])

        # color similarity (gaussian on Euclidean BGR distance)
        color_dist = float(np.linalg.norm(det_features['avg_color'] - track_features['avg_color']))
        color_sim = float(np.exp(-(color_dist ** 2) / (2 * (35.0 ** 2))))  # sigma ~35

        # weight IoU & center more; then color; then area
        return 0.4 * iou + 0.3 * cx_sim + 0.2 * color_sim + 0.1 * area_ratio

    # ---------- Detection, Tracking, Compositing ----------

    def detect_and_track(self, frame):
        self._set_dynamic_thresholds(frame.shape)

        # Use predict() to pass params explicitly; retina_masks yields full-res masks
        results = self.yolo.predict(
            source=frame,
            classes=[0],                       # person
            conf=self.min_confidence,
            iou=0.6,
            imgsz=max(frame.shape[:2]),
            device=self.device,
            half=self.use_half,
            retina_masks=True,
            verbose=False
        )

        detections = []
        for r in results:
            if r.boxes is None or r.masks is None:
                continue

            boxes = r.boxes
            # masks at original frame size due to retina_masks=True
            masks = r.masks.data.cpu().numpy()  # (N, H, W)

            for i in range(len(boxes)):
                x1, y1, x2, y2 = map(int, boxes.xyxy[i].cpu().numpy())
                conf = float(boxes.conf[i].cpu().numpy())
                # basic size filtering
                if (x2 - x1) * (y2 - y1) <= 500:
                    continue

                mask = masks[i].astype(np.float32)  # [0..1]
                features = self.get_simple_features((x1, y1, x2, y2), mask, frame)
                detections.append((x1, y1, x2, y2, conf, mask, features))

        # Assign with Hungarian
        if detections and self.tracks:
            current_tracks = self.assign_with_hungarian(detections)
        else:
            current_tracks = self.initialize_tracks(detections)

        # Clean old tracks
        self.cleanup_tracks(current_tracks)
        return current_tracks

    def assign_with_hungarian(self, detections):
        track_ids = [tid for tid, t in self.tracks.items() if t['frames'] < self.max_disappeared]
        if not track_ids:
            return self.initialize_tracks(detections)

        sim = np.zeros((len(detections), len(track_ids)), dtype=np.float32)
        for i, det in enumerate(detections):
            dfeat = det[6]
            for j, tid in enumerate(track_ids):
                sim[i, j] = self.calculate_similarity(dfeat, self.tracks[tid])

        if sim.size > 0:
            rows, cols = linear_sum_assignment(-sim)  # maximize similarity
        else:
            rows, cols = [], []

        current_tracks = []
        assigned_dets = set()
        assigned_tids = set()

        for r_i, c_i in zip(rows, cols):
            if sim[r_i, c_i] > 0.25:  
                det = detections[r_i]
                tid = track_ids[c_i]
                x1, y1, x2, y2, conf, mask, features = det

                # update velocity 
                prev_c = self.tracks[tid]['features']['centroid']
                new_c = features['centroid']
                vel = (new_c[0] - prev_c[0], new_c[1] - prev_c[1])
                old_vx, old_vy = self.tracks[tid].get('vel', (0.0, 0.0))
                
                self.tracks[tid]['vel'] = (0.8 * old_vx + 0.2 * vel[0], 0.8 * old_vy + 0.2 * vel[1])

                # update features/frame age
                self.tracks[tid]['features'] = features
                self.tracks[tid]['frames'] = 0

                current_tracks.append((x1, y1, x2, y2, tid, mask))
                assigned_dets.add(r_i)
                assigned_tids.add(tid)

        # create new tracks for unassigned detections
        for i, det in enumerate(detections):
            if i in assigned_dets:
                continue
            x1, y1, x2, y2, conf, mask, features = det
            tid = self.next_id
            self.next_id += 1
            self.tracks[tid] = {'features': features, 'frames': 0, 'vel': (0.0, 0.0)}
            current_tracks.append((x1, y1, x2, y2, tid, mask))

        # age unassigned tracks
        for tid in track_ids:
            if tid not in assigned_tids:
                self.tracks[tid]['frames'] += 1

        return current_tracks

    def initialize_tracks(self, detections):
        current_tracks = []
        for det in detections:
            x1, y1, x2, y2, conf, mask, features = det
            tid = self.next_id
            self.next_id += 1
            self.tracks[tid] = {'features': features, 'frames': 0, 'vel': (0.0, 0.0)}
            current_tracks.append((x1, y1, x2, y2, tid, mask))
        return current_tracks

    def cleanup_tracks(self, current_tracks):
        to_del = []
        for tid in list(self.tracks.keys()):
            if self.tracks[tid]['frames'] > self.max_disappeared:
                to_del.append(tid)
        for tid in to_del:
            del self.tracks[tid]

    def blur_players(self, frame, tracks):
        """
        Colorized silhouette compositor.
        Each tracked player gets a unique tint instead of pure black blur.
        """
        result = frame.copy()
        h, w = frame.shape[:2]
        combined = np.zeros((h, w, 3), dtype=np.float32)

        for x1, y1, x2, y2, tid, mask in tracks:
            m = mask
            if m.shape != (h, w):
                m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
            m = m.astype(np.float32)
            if m.max() > 1.0:
                m /= 255.0

            # feather mask
            m = cv2.GaussianBlur(m, (21, 21), 6.0)

            # pick a pseudo-random color per track ID
            rng = np.random.default_rng(seed=tid)
            color = rng.random(3) * np.array([255, 255, 255])
            color = color.astype(np.float32)

            # expand mask to 3-channel
            m3 = np.repeat(m[:, :, None], 3, axis=2)

            # add tinted region
            combined += (m3 * color)

        # normalize combined mask intensity
        combined = np.clip(combined, 0, 255)

        # overlay color tint over blurred background
        blurred_bg = cv2.GaussianBlur(result, (71, 71), 30.0)
        alpha = 0.5  # how strong the color overlay is
        overlay = cv2.addWeighted(blurred_bg.astype(np.float32), 1 - alpha, combined, alpha, 0)

        # Blend back into frame using overall silhouette mask (for smooth edges)
        gray_mask = cv2.cvtColor((combined > 0).astype(np.uint8) * 255, cv2.COLOR_BGR2GRAY)
        gray_mask = cv2.GaussianBlur(gray_mask, (25, 25), 10.0)
        gray_mask = gray_mask.astype(np.float32) / 255.0
        gray_mask3 = np.repeat(gray_mask[:, :, None], 3, axis=2)

        result = (result * (1 - gray_mask3) + overlay * gray_mask3).astype(np.uint8)
        return result


    # ---------- Video pipeline ----------

    def process_video(self, video_bytes):
        try:
            # Save temp video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                f.write(video_bytes)
                temp_path = f.name

            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                raise ValueError("Could not open video")

            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0  # keep as float
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            output_path = temp_path.replace('.mp4', '_blurred.mp4')

            # Use H264 codec for browser compatibility
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                tracks = self.detect_and_track(frame)
                processed_frame = self.blur_players(frame, tracks)
                out.write(processed_frame)

                frame_count += 1
                if frame_count % 30 == 0:
                    active_tracks = len([t for t in self.tracks.values() if t['frames'] < 5])
                    print(f"Processed {frame_count} frames - Active tracks: {active_tracks}")

            cap.release()
            out.release()

            with open(output_path, 'rb') as f:
                result_bytes = f.read()

            os.unlink(temp_path)
            os.unlink(output_path)

            return {
                "success": True,
                "blurred_video": base64.b64encode(result_bytes).decode(),
                "video_info": {"fps": fps, "width": width, "height": height, "frames": frame_count}
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Initialize CV, Game, and Stats instances
import os
cv = HybridGoaldleCV()
db_path = os.path.join(os.path.dirname(__file__), "data/players_db.json")
print(f"Using device: {cv.device}, half: {cv.use_half}")
print(f"Looking for database at: {db_path}")
game = GoaldleGame(db_path)
stats = SimpleStatsManager()


# Pydantic models for API
class GuessRequest(BaseModel):
    player_name: str


class GameResult(BaseModel):
    player_name: str
    is_winner: bool
    total_guesses: int
    time_taken: int = None


@app.get("/", response_class=HTMLResponse)
async def root():
    from fastapi.responses import Response
    with open("goaldle-game.html", "r", encoding="utf-8") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/game", response_class=HTMLResponse)
async def serve_game():
    with open("goaldle-game.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/faq", response_class=HTMLResponse)
async def serve_faq():
    with open("faq.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/contact", response_class=HTMLResponse)
async def serve_contact():
    with open("contact.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/favicon.png")
async def serve_favicon():
    from fastapi.responses import FileResponse
    return FileResponse(
        "favicon.png",
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600"
        }
    )


@app.get("/favicon.ico")
async def serve_favicon_ico():
    from fastapi.responses import FileResponse
    return FileResponse("favicon.png", media_type="image/png")


@app.get("/sitemap.xml")
async def serve_sitemap():
    from fastapi.responses import FileResponse
    return FileResponse("sitemap.xml", media_type="application/xml")


@app.get("/robots.txt")
async def serve_robots():
    from fastapi.responses import FileResponse
    return FileResponse("robots.txt", media_type="text/plain")


@app.get("/googleb088480d1e6dc59e.html")
async def serve_google_verification():
    from fastapi.responses import FileResponse
    return FileResponse("googleb088480d1e6dc59e.html", media_type="text/html")


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


# Game endpoints
@app.post("/game/new")
async def new_game():
    """Start a new Goaldle game"""
    try:
        result = game.start_new_game()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/game/guess")
async def make_guess(request: GuessRequest):
    """Make a guess in the current game"""
    try:
        result = game.make_guess(request.player_name)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/state")
async def get_game_state():
    """Get current game state"""
    try:
        result = game.get_game_state()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/players")
async def get_players():
    """Get list of all available players for autocomplete"""
    try:
        players = game.get_available_players()
        return JSONResponse(content={"players": players})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/current-video")
async def get_current_video():
    """Get the current game's video (blurred version)"""
    try:
        video_data = game.get_current_video()
        if not video_data:
            raise HTTPException(status_code=404, detail="No active game or video not found")

        return JSONResponse(content={
            "success": True,
            "video_data": video_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/video-reveal")
async def get_video_reveal():
    """Get both original and blurred videos for reveal"""
    try:
        reveal_data = game.get_video_reveal()
        if not reveal_data:
            raise HTTPException(status_code=404, detail="No active game")

        return JSONResponse(content={
            "success": True,
            "reveal_data": reveal_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/game/start-with-video")
async def start_game_with_video():
    """Start a new game and get the video"""
    try:
        # Start new game
        game_result = game.start_new_game()

        # Get the video for this game
        video_data = game.get_current_video()

        if not video_data:
            raise HTTPException(status_code=500, detail="Failed to load video for game")

        return JSONResponse(content={
            "success": True,
            "game_state": game_result,
            "video_data": video_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/game/integrate-video")
async def integrate_video_with_game(file: UploadFile = File(...)):
    """Process video, blur players, and start a new game (legacy endpoint)"""
    try:
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Must be video file")

        # Process the video
        contents = await file.read()
        video_result = cv.process_video(contents)

        if not video_result["success"]:
            raise HTTPException(status_code=500, detail=f"Video processing failed: {video_result['error']}")

        # Start a new game
        game_result = game.start_new_game()

        return JSONResponse(content={
            "success": True,
            "video_result": {
                "blurred_video": video_result["blurred_video"],
                "video_info": video_result["video_info"]
            },
            "game_state": game_result,
            "hint": "Watch the blurred video and guess which player is performing the goal!"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === SIMPLE STATS ENDPOINTS ===

@app.get("/stats")
async def get_stats():
    """Get personal game statistics"""
    try:
        stats_summary = stats.get_stats_summary()
        return JSONResponse(content=stats_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/detailed")
async def get_detailed_stats():
    """Get detailed statistics with history"""
    try:
        detailed_stats = stats.get_detailed_stats()
        return JSONResponse(content=detailed_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stats/record-game")
async def record_game(game_result: GameResult):
    """Record a completed game"""
    try:
        stats.record_game(
            player_name=game_result.player_name,
            is_winner=game_result.is_winner,
            total_guesses=game_result.total_guesses,
            time_taken=game_result.time_taken
        )
        return JSONResponse(content={"success": True, "message": "Game recorded"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/export")
async def export_stats():
    """Export stats as formatted text"""
    try:
        export_text = stats.export_stats()
        return JSONResponse(content={"stats_text": export_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stats/reset")
async def reset_stats():
    """Reset all statistics"""
    try:
        stats.reset_stats()
        return JSONResponse(content={"success": True, "message": "Stats reset"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import os
    print("🚀 Starting GoalDle CV API - Now with Personal Stats!")
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
