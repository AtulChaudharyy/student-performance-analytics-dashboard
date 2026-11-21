@echo off
echo ========================================================
echo  Student Performance Analytics Dashboard (SPAD)
echo  Building and Running inside Docker...
echo ========================================================
echo [1/2] Building Docker image...
docker build -t student-dashboard .
if errorlevel 1 (
    echo [ERROR] Docker build failed. Please ensure Docker Desktop is running.
    pause
    exit /b %errorlevel%
)
echo [2/2] Running Docker container on port 5000...
echo Access application at: http://localhost:5000
docker run --rm -p 5000:5000 --name student-dashboard-app student-dashboard
pause
