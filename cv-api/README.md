# GoalDle Computer Vision API

This is the Python FastAPI backend for GoalDle's computer vision features, specifically designed for processing goal-scoring videos and blurring the scoring player for the guessing game.

## Features

- **Goal Video Processing**: Process goal-scoring videos and blur the scoring player
- **Full Player Detection**: Detect and blur entire players
- **Single Blur Level**: Simple, consistent blurring for all videos
- **Player Tracking**: Focus on full-body player detection for goal videos

## Setup

1. **Install Python dependencies**:
   ```bash
   cd cv-api
   pip install -r requirements.txt
   ```

2. **Start the API server**:
   ```bash
   python main.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /health` - Check API status

### Video Processing
- `POST /process-video` - Process goal video and blur the scoring player

## How It Works

### Goal Video Blurring Process
1. **Upload Goal Video**: Send goal-scoring video to the API
2. **Player Detection**: Process each frame to detect full players
3. **Full Player Blurring**: Apply Gaussian blur to entire player bodies
4. **Video Output**: Return blurred video for guessing game

### Blur Settings
- **Default Blur Strength**: 50 (balanced obscuring)
- **Customizable**: Can adjust blur strength via parameter
- **Full Player Coverage**: Expands detection areas to ensure complete blurring

### Detection Features
- **Full Player Detection**: Uses HOG (Histogram of Oriented Gradients) for complete body detection
- **Expanded Regions**: Automatically expands detection areas to ensure full player coverage
- **Goal-Specific**: Optimized for goal-scoring video analysis

## Game Integration

### Goal Video Guessing Game
1. **Upload Goal Video**: Player uploads a goal-scoring video
2. **Player Detection**: CV API detects all players in the video
3. **Full Player Blur**: Blurs the entire scoring player
4. **Player Guessing**: Users guess who scored the goal
5. **Reveal Answer**: Show clear video when game ends

## Integration with Next.js Frontend

The CV API is designed to work alongside the Next.js frontend:

1. **CORS enabled** for localhost:3000
2. **Video upload support** for MP4 goal videos
3. **Base64 responses** for easy frontend integration

## Example Usage

```javascript
// From your Next.js frontend
const processGoalVideo = async (goalVideoFile) => {
  const formData = new FormData();
  formData.append('file', goalVideoFile);
  formData.append('blur_strength', '50');
  
  const response = await fetch('http://localhost:8000/process-video', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

## Game Flow

### Daily Goal Challenge
1. **Select Goal Video**: Choose a goal-scoring video for the day
2. **Process Video**: Use CV API to blur the scoring player
3. **Start Game**: Show blurred video to players
4. **Player Guessing**: Users guess who scored the goal
5. **Final Reveal**: Show clear video when game ends

## Development

- **Hot reload**: Use `uvicorn main:app --reload`
- **API docs**: Visit http://localhost:8000/docs for interactive documentation
- **Testing**: Use the `/health` endpoint to verify the API is running
- **Video testing**: Upload goal videos to test player blurring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Next.js API    │    │  Python CV API  │
│   (TypeScript)  │◄──►│   (TypeScript)  │◄──►│   (FastAPI)     │
│                 │    │                 │    │                 │
│ - Game UI       │    │ - Game State    │    │ - Video Processing│
│ - Video Display │    │ - Player Data   │    │ - Player Detection│
│ - Guess Input   │    │ - Authentication│    │ - Full Body Blur │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Future Enhancements

- [ ] Advanced player tracking across frames
- [ ] Jersey number detection and blurring
- [ ] Team color-based blurring strategies
- [ ] Real-time video processing
- [ ] Machine learning for better player detection
- [ ] Custom blur effects (pixelation, black bars)
- [ ] Video compression optimization 