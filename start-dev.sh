#!/bin/bash

# GoalDle Development Startup Script
# Starts both Next.js frontend and Python CV API

echo "🚀 Starting GoalDle Development Environment..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check ports
echo "🔍 Checking ports..."
if ! check_port 3000; then
    echo "   Next.js frontend port 3000 is busy"
fi

if ! check_port 8000; then
    echo "   Python CV API port 8000 is busy"
fi

# Install Python dependencies if needed
if [ ! -d "cv-api/venv" ] && [ ! -f "cv-api/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    cd cv-api
    pip install -r requirements.txt
    cd ..
fi

# Start Python CV API in background
echo "🐍 Starting Python CV API on port 8000..."
cd cv-api
python main.py &
CV_API_PID=$!
cd ..

# Wait a moment for CV API to start
sleep 3

# Start Next.js frontend
echo "⚛️  Starting Next.js frontend on port 3000..."
npm run dev &
NEXT_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $CV_API_PID 2>/dev/null
    kill $NEXT_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "✅ GoalDle is running!"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 CV API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait 