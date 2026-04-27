@echo off
title Vishnu Gita Launcher
color 5F

echo.
echo  ================================================
echo    Vishnu Gita - Starting...
echo  ================================================
echo.

echo  [1/2] Starting backend server...
start "Vishnu Gita Server" cmd /k "cd /d C:\Users\Admin-LFI\DivineGuide\backend && python main.py"

echo  Waiting for server to load (10 seconds)...
timeout /t 10 /nobreak > nul

echo  [2/2] Starting ngrok tunnel...
start "Vishnu Gita Ngrok" cmd /k "cd /d C:\Users\Admin-LFI\DivineGuide && ngrok.exe http 8000"

echo  Getting your public URL...
python C:\Users\Admin-LFI\DivineGuide\get_url.py

echo.
pause
