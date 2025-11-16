@echo off
echo ========================================
echo MP4 to MP3 Converter - Build Script
echo ========================================
echo.

echo [1/3] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Done!
echo.

echo [2/3] Building executable with PyInstaller...
pyinstaller build.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please make sure PyInstaller is installed: pip install pyinstaller
    pause
    exit /b 1
)
echo Done!
echo.

echo [3/3] Cleaning up...
if exist build rmdir /s /q build
echo Done!
echo.

echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\MP4toMP3Converter.exe
echo.
pause
