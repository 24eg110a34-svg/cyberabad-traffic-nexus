@echo off
title CYBERABAD TRAFFIC NEXUS - Starting Server
color 0A

echo.
echo ============================================
echo    CYBERABAD TRAFFIC NEXUS
echo    Hyderabad Metro Command Center
echo ============================================
echo.

cd /d "%~dp0"

echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [+] Python found
echo.

echo [*] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [!] Installing dependencies...
    pip install -r requirements.txt
)

echo [+] Dependencies ready
echo.

echo [*] Initializing database...
python -c "import database; print('[+] Database initialized')"
echo.

echo.
echo ============================================
echo    Starting Services...
echo ============================================
echo.
echo [1] Flask API Server - http://127.0.0.1:5000
echo [2] Streamlit Dashboard - http://127.0.0.1:8501
echo [3] Socket Server - ws://127.0.0.1:5555
echo.
echo ============================================
echo.

choice /C:123 /N /M "Select option (1=Flask, 2=Streamlit, 3=Both): "

if errorlevel 3 goto both
if errorlevel 2 goto streamlit
if errorlevel 1 goto flask

:flask
echo.
echo [+] Starting Flask API Server...
echo.
python app.py
goto end

:streamlit
echo.
echo [+] Starting Streamlit Dashboard...
echo.
streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1
goto end

:both
echo.
echo [+] Starting Flask API Server...
echo.
start "Flask API" cmd /c "python app.py"
timeout /t 3 /nobreak >nul
echo.
echo [+] Starting Streamlit Dashboard...
echo.
streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1
goto end

:end
pause
