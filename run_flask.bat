@echo off
echo =============================================================================
echo CRATA AI - Growth Intelligence Dashboard (Flask)
echo =============================================================================
echo.

REM Activate virtual environment if exists
if exist "venv_flask\Scripts\activate.bat" (
    call venv_flask\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo No virtual environment found. Creating one...
    python -m venv venv_flask
    call venv_flask\Scripts\activate.bat
    pip install Flask google-analytics-data pandas python-dotenv
)

echo.
echo Starting Flask server...
echo Open your browser at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server.
echo =============================================================================
echo.

python app_flask.py

pause

