@echo off
REM Quick start script for Streamlit deployment on Windows

echo ============================================================
echo  AI Output Evaluation Tool - Streamlit Deployment Helper
echo ============================================================
echo.

REM Check if streamlit is installed
python -m streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Streamlit not found. Installing...
    pip install streamlit
)

echo.
echo [✓] Streamlit is installed
echo.
echo Starting Streamlit app...
echo.
echo Main file: streamlit_app.py
echo.
echo The app will be available at:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
