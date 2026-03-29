@echo off
title SIGNAL COMMAND PRO v2.0 - Hyderabad Traffic Intelligence
color 0A
echo.
echo ================================================
echo   SIGNAL COMMAND PRO v2.0
echo   Hyderabad Traffic Intelligence Dashboard
echo ================================================
echo.
echo Features:
echo   - 26 Junctions (Including Ghatkesar & Uppal)
echo   - 30 Road Segments with 7 Hotspots
echo   - 8,928 Traffic Records
echo   - Random Forest ML (92.89%% Accuracy)
echo   - Holiday/Event Engine
echo   - Ambulance Green Corridor Mode
echo   - Weather & VIP Modes
echo   - Biryani Index
echo.
echo Starting Flask server...
echo.
cd /d "%~dp0"
python app.py
pause
