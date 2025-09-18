# 🥅 Goaldle

**Play now at [goaldle.com](https://goaldle.com)**

A daily soccer goal guessing game. Watch famous goals with players blurred out and guess who scored in 6 tries or less.

## How to Play

1. 🎥 Watch the blurred goal video
2. 🔍 Use context clues (stadium, teammates, celebration style)
3. ⌨️ Type a player name and submit your guess
4. 📊 Get feedback and try again (max 6 attempts)
5. 🔄 Share your results and come back tomorrow!

## Features

- 🎯 Daily challenges with iconic goals
- 📊 Personal stats tracking (win rate, streaks, guess distribution)
- 🔥 Streak counter
- 📱 Mobile-friendly
- 🎮 Shareable results
- 💡 Player name autocomplete
- 📈 Game history and export

## How It Works

1. **Player Detection**: Uses YOLOv8 to detect players in soccer videos
2. **Player Masking**: Applies black silhouettes to tracked players while keeping everything else visible
3. **Game Logic**: Manages guessing, scoring, and player database
4. **Stats Tracking**: Records your performance locally

You get context from the stadium, teammates, celebration style, etc. - just not the scorer's identity.

## Technology Stack

**Backend**: FastAPI, OpenCV, PyTorch, YOLOv8
**Frontend**: HTML/CSS/JavaScript
**Stats**: JSON file storage
**Computer Vision**: YOLO object detection with Hungarian algorithm tracking

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