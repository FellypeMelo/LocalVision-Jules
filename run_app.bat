@echo off
REM LocalVision-Jules - Startup Script with Auto-Setup

echo =====================================
echo  LocalVision-Jules
echo =====================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\" (
    echo [SETUP] Virtual environment not found. Creating...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python is installed and in PATH
        echo.
        pause
        exit /b 1
    )
    echo [SETUP] Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo [2/3] Checking dependencies...
python -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo [SETUP] Dependencies not installed. Installing...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [SETUP] Dependencies installed successfully!
    echo.
)

REM Start the application
echo [3/3] Starting LocalVision-Jules...
echo.
echo =====================================
echo.
python main.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo =====================================
    echo Application exited with an error
    echo =====================================
) else (
    echo.
    echo =====================================
    echo Application closed successfully
    echo =====================================
)

echo.
pause
