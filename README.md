# GoalDle

A soccer goal guessing game where players watch blurred videos of famous goals and try to identify the scorer.

## Overview

GoalDle combines computer vision with an interactive web game. Players are shown videos where the goal scorer appears as a black silhouette, and they must guess who scored the goal. The game includes famous goals from players like Messi, Drogba, Salah, Son Heung-min, and others.

## Components

- **CV API**: FastAPI backend with computer vision processing (`cv-api/`)
- **Web Game**: HTML/CSS/JS frontend (`goaldle-game.html`)
- **Goal Database**: Pre-processed videos with original and blurred versions

## Setup

```bash
cd cv-api
python main.py
```

Dependencies install automatically on first run. Then open `goaldle-game.html` in your browser.

## API Endpoints

### Game Endpoints
- `POST /game/new` - Start a new game
- `POST /game/guess` - Make a player guess
- `GET /game/state` - Get current game state
- `GET /game/players` - Get available players for autocomplete
- `GET /game/current-video` - Get blurred video for current game

### Video Processing
- `POST /process-video` - Process and blur a new video
- `POST /reset-tracking` - Reset tracking state

## How It Works

1. **Player Detection**: Uses YOLOv8 to detect players in soccer videos
2. **Player Tracking**: Hungarian algorithm assigns consistent IDs across frames
3. **Silhouette Effect**: Applies black silhouette masks to tracked players
4. **Game Logic**: Manages game state, scoring, and player database

## Technology Stack

- **Backend**: FastAPI, OpenCV, PyTorch, YOLOv8
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Computer Vision**: YOLO object detection, Hungarian algorithm tracking