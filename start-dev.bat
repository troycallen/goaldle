@echo off
REM GoalDle Development Startup Script for Windows
REM Starts both Next.js frontend and Python CV API

echo 🚀 Starting GoalDle Development Environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Install Python dependencies if needed
if not exist "cv-api\requirements.txt" (
    echo 📦 Installing Python dependencies...
    cd cv-api
    pip install -r requirements.txt
    cd ..
)

REM Start Python CV API in background
echo 🐍 Starting Python CV API on port 8000...
start "GoalDle CV API" cmd /k "cd cv-api && python main.py"

REM Wait a moment for CV API to start
timeout /t 3 /nobreak >nul

REM Start Next.js frontend
echo ⚛️ Starting Next.js frontend on port 3000...
start "GoalDle Frontend" cmd /k "npm run dev"

echo.
echo ✅ GoalDle is running!
echo    🌐 Frontend: http://localhost:3000
echo    🔧 CV API: http://localhost:8000
echo    📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup - close the started windows
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo 🛑 Services stopped.
pause 