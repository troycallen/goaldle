@echo off
echo 🚀 Starting GoalDle...

echo 🐍 Starting CV API...
start "CV API" cmd /k "cd cv-api && python main.py"

timeout /t 3 /nobreak >nul

echo 🌐 Opening Frontend...
start "GoalDle Frontend" index.html

echo ✅ GoalDle is running!
echo 🌐 Frontend: index.html (opened in browser)
echo 🔧 CV API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs 