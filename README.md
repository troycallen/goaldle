# ⚽ Goaldle

A soccer/football player guessing game inspired by Wordle, featuring computer vision analysis of player images.

## Features

### ✨ Core Gameplay
- **Image Upload**: Drag & drop or click to upload soccer player photos
- **Computer Vision**: TensorFlow.js-powered analysis to extract visual clues
- **Smart Guessing**: Autocomplete player suggestions with similarity feedback
- **6 Attempts**: Wordle-style limited attempts with detailed feedback

### 🏆 Game Modes
- **Free Play**: Practice with random players
- **Daily Challenge**: One daily player for all users to guess
- **Scoring System**: Points based on attempts, time, and hints used

### 📊 Player Feedback System
- **Color-coded Similarity**: Visual feedback for team, position, nationality, age, and height matches
- **Progressive Hints**: Image analysis provides clues about jersey color, height, and physical features
- **Detailed Statistics**: Track wins, streaks, and performance over time

### 🎯 Daily Challenge & Social Features
- **Consistent Daily Player**: Same player for all users each day
- **Score Sharing**: Share your results with emoji grids
- **Statistics Tracking**: Personal stats with streaks and averages
- **Local Storage**: All data saved locally (no account required)

## Installation & Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Development Server**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000)

3. **Production Build**
   ```bash
   npm run build
   npm start
   ```

## Tech Stack

- **Next.js 15** with App Router and TypeScript
- **Tailwind CSS** for styling
- **TensorFlow.js** for computer vision
- **Next.js API Routes** for backend functionality

## How to Play

1. **Upload an Image**: Drag and drop or click to upload a soccer player photo
2. **Get Visual Clues**: The AI analyzes the image and provides hints about jersey color, height, etc.
3. **Make Your Guess**: Type a player name with autocomplete suggestions
4. **Get Feedback**: See how your guess compares across team, position, nationality, age, and height
5. **Win or Learn**: Solve in 6 attempts or less to earn points!

## Game Features

- 10 popular soccer players in the database
- Smart similarity matching system
- Daily challenges with consistent players
- Score calculation based on performance
- Statistics tracking and sharing

## Future Enhancements

- Expanded player database with real sports API integration
- Custom trained ML model for better player recognition
- Multiplayer modes and leaderboards
- Mobile app version
- Video clip analysis

Built with ❤️ for soccer fans who love a good challenge!
