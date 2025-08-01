# ⚽ Goaldle

A soccer/football player guessing game inspired by Wordle, where players guess the mystery player from a daily curated image.

## Features

### ✨ Core Gameplay
- **Daily Mystery Player**: Each day features a different pre-selected player
- **Blurred Images**: Players start with a blurred/obscured image to analyze
- **Progressive Hints**: Each wrong guess reveals more clues about the player
- **6 Attempts**: Wordle-style limited attempts with detailed similarity feedback

### 🏆 Game Modes
- **Free Play**: Practice with random players
- **Daily Challenge**: One daily player for all users to guess
- **Scoring System**: Points based on attempts, time, and hints used

### 📊 Player Feedback System
- **Color-coded Similarity**: Visual feedback for team, position, nationality, age, and height matches
- **Progressive Hints**: Each attempt unlocks career achievements and player facts
- **Detailed Statistics**: Track wins, streaks, and performance over time

### 🎯 Daily Challenge & Social Features
- **Consistent Daily Player**: Same player for all users each day
- **Score Sharing**: Share your results with emoji grids
- **Statistics Tracking**: Personal stats with streaks and averages
- **Local Storage**: All data saved locally (no account required)

## Installation & Setup

### Quick Start (Both Services)
```bash
# Windows
start-dev.bat

# macOS/Linux
chmod +x start-dev.sh
./start-dev.sh
```

### Manual Setup

1. **Install Node.js Dependencies**
   ```bash
   npm install
   ```

2. **Install Python Dependencies**
   ```bash
   cd cv-api
   pip install -r requirements.txt
   cd ..
   ```

3. **Start Both Services**
   ```bash
   # Terminal 1: Start Python CV API
   cd cv-api
   python main.py
   
   # Terminal 2: Start Next.js Frontend
   npm run dev
   ```

4. **Access the Application**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - CV API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Tech Stack

- **Next.js 15** with App Router and TypeScript
- **Tailwind CSS** for styling
- **Python FastAPI** for computer vision and image processing
- **OpenCV** for image analysis and enhancement
- **Curated Player Database** with high-quality images and hints
- **Next.js API Routes** for backend functionality

## How to Play

1. **Study the Mystery**: Look at the blurred image of today's mystery player
2. **Make Your Guess**: Type a player name with autocomplete suggestions  
3. **Get Feedback**: See how your guess compares across team, position, nationality, age, and height
4. **Unlock Hints**: Each wrong guess reveals more clues about the player's career
5. **Win or Learn**: Solve in 6 attempts or less to earn points!

## Game Features

- **10 Curated Players**: Each with professional photos and career facts
- **Smart Similarity System**: Detailed feedback on team, position, nationality, age, and height
- **Daily Challenges**: Same mystery player for all users each day
- **Progressive Hints**: Career achievements and facts unlock with each guess
- **Score & Stats**: Performance tracking with sharing capabilities

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Next.js API    │    │  Python CV API  │
│   (TypeScript)  │◄──►│   (TypeScript)  │◄──►│   (FastAPI)     │
│                 │    │                 │    │                 │
│ - Game UI       │    │ - Game State    │    │ - Image Analysis│
│ - Player Input  │    │ - Player Data   │    │ - Video Processing│
│ - Score Display │    │ - Authentication│    │ - AI Models     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Future Enhancements

- **Computer Vision Integration**: Real-time image analysis and enhancement
- **Machine Learning Models**: Custom trained models for player recognition
- **Video Processing**: Analyze player video clips for better hints
- **Expanded Database**: Real sports API integration with more players
- **Multiplayer Features**: Leaderboards and social features
- **Mobile App**: Native mobile application

Built with ❤️ for soccer fans who love a good challenge!
