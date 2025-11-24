@echo off
echo.
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

echo.
echo Starting the application...
REM The 'lms' command should be available in your PATH now.
REM If you still get an 'lms not found' error, please restart your terminal or your computer.
python main.py

echo.
echo The application has closed. Press any key to exit.
pause
