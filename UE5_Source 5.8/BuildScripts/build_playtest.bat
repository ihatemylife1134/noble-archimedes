@echo off
:: Noble Archimedes - Playtest Build Script
:: Run this on your Windows GPU machine after setting up the UE5 project

setlocal enabledelayedexpansion

set UE_ROOT=C:\Program Files\Epic Games\UE_5.8
set PROJECT=C:\Projects\NobleArchimedes\NobleArchimedes.uproject
set CONFIG=Shipping
set PLATFORM=Win64

echo ============================================
echo  Noble Archimedes - Playtest Build Script
echo ============================================
echo.

echo [1/4] Validating UE5 installation...
if not exist "%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat" (
    echo ERROR: UE5 not found at %UE_ROOT%
    echo Please update UE_ROOT in this script.
    pause
    exit /b 1
)
echo OK: UE5 found at %UE_ROOT%

echo.
echo [2/4] Validating project file...
if not exist "%PROJECT%" (
    echo ERROR: Project not found at %PROJECT%
    echo Please update PROJECT path in this script.
    pause
    exit /b 1
)
echo OK: Project found at %PROJECT%

echo.
echo [3/4] Building project...
echo Running: RunUAT.bat BuildCookRun
echo This may take 10-30 minutes depending on your hardware.
echo.

"%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun ^
    -project="%PROJECT%" ^
    -platform=%PLATFORM% ^
    -clientconfig=%CONFIG% ^
    -serverconfig=%CONFIG% ^
    -cook ^
    -stage ^
    -package ^
    -prerequisites ^
    -build

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Build failed with code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [4/4] Build complete!
echo Output: C:\Projects\NobleArchimedes\Saved\StagedBuilds\Windows\NobleArchimedes\NobleArchimedes.exe
echo.
pause