@echo off
echo Yu-Gi-Oh! Card Database Generator Web Server Launcher
echo ==================================================
echo.

REM Check if Flask is installed
python -c "import flask" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Installing Flask...
    pip install flask
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Flask. Please install it manually.
        pause
        exit /b 1
    )
)

echo Starting web server...
echo The server will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server.
echo.

python -m yugioh_db_generator.web.web_ui

echo.
echo Server has been stopped.
pause