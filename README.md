# Goaldle

A soccer goal guessing game where players watch blurred videos and try to identify the scorer.

## Overview

Goaldle is like Wordle but for soccer goals. Watch famous goal clips where the players are blacked out and guess who scored. You get 6 attempts and context clues from the stadium, crowd, and other players.

**Features:**
- Daily challenges with different goals
- Personal stats tracking (win rate, streaks, guess distribution)
- Player name autocomplete
- Game history and export

## Setup

```bash
cd cv-api
python main.py
```

Dependencies install automatically. Then open `goaldle-game.html` in your browser.

## How It Works

1. **Player Detection**: Uses YOLOv8 to detect players in soccer videos
2. **Player Masking**: Applies black silhouettes to tracked players while keeping everything else visible
3. **Game Logic**: Manages guessing, scoring, and player database
4. **Stats Tracking**: Records your performance in a local JSON file

You get context from the stadium, teammates, celebration style, etc. - just not the scorer's identity.

## Technology Stack

**Backend**: FastAPI, OpenCV, PyTorch, YOLOv8  
**Frontend**: HTML/CSS/JavaScript  
**Stats**: JSON file storage  
**Computer Vision**: YOLO object detection with Hungarian algorithm tracking  

## API Endpoints

**Game:**
- `POST /game/guess` - Submit a player guess
- `GET /game/players` - Get available players for autocomplete
- `GET /game/current-video` - Get blurred video for current game

**Stats:**
- `GET /stats` - Get personal statistics
- `POST /stats/record-game` - Record a completed game
- `GET /stats/export` - Export stats as text

**Video Processing:**
- `POST /process-video` - Process and blur new videos