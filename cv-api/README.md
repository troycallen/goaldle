# GoalDle CV API

Blurs players in soccer videos using computer vision.

## Setup

```bash
python main.py
```

Dependencies install automatically on first run.

## Usage

POST video file to `http://localhost:8000/process-video`

Returns base64 encoded video with players as black silhouettes.

## What it does

- Detects players using YOLOv8
- Tracks them across frames  
- Applies black silhouette effect to player regions

Built for the GoalDle game.