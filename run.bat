@echo off
echo Starting MP4 to MP3 Converter...
python main.py
if errorlevel 1 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
)
