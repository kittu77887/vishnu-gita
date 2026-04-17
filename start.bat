@echo off
echo ================================================
echo   DivineGuide - Starting...
echo ================================================

REM Check if database exists
if not exist "backend\divine_db" (
    echo.
    echo [!] Database not found. Running setup first...
    echo.
    echo [Step 1/2] Downloading scripture data...
    cd data
    python download_data.py
    echo.
    echo [Step 2/2] Building vector database...
    python build_database.py
    cd ..
)

echo.
echo [✓] Starting DivineGuide server...
echo [✓] Open your browser at: http://localhost:8000
echo.
cd backend
python main.py
pause
