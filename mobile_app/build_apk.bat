@echo off
echo Building Agriculture Mobile App APK...
echo.

REM Navigate to the mobile_app directory
cd /d "%~dp0"

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Flutter is not installed or not in PATH
    echo Please install Flutter and make sure it's accessible from command line
    pause
    exit /b 1
)

REM Get dependencies
echo Getting dependencies...
flutter pub get
if %errorlevel% neq 0 (
    echo Error: Failed to get dependencies
    pause
    exit /b 1
)

REM Build APK
echo Building APK...
flutter build apk
if %errorlevel% neq 0 (
    echo Error: Failed to build APK
    pause
    exit /b 1
)

echo.
echo APK built successfully!
echo You can find it at: build\app\outputs\flutter-apk\app-release.apk
echo.
pause
