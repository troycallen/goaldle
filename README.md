# 🥅 Goaldle

**Play now at [goaldle.com](https://goaldle.com)**

A daily soccer goal guessing game. Watch famous goals with players blurred out and guess who scored.

## How to Play

1. 🎥 Watch the blurred goal video
2. 🔍 Use context clues 
3. ⌨️ Type a player name and submit your guess
4. 📊 Get feedback and try again (max 6 attempts)

## Technology Stack

**Backend**: Python, FastAPI, PyTorch

**Frontend**: HTML/CSS/JavaScript

**Computer Vision**: YOLOv8, OpenCV, Hungarian algorithm

## Local Development

```bash
cd cv-api
python main.py
```

Dependencies install automatically. Then open `goaldle-game.html` in your browser.

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