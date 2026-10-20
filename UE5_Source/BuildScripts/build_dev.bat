@echo off
:: Noble Archimedes - Development Build Script
:: Compiles the editor target, then launches Unreal Editor.
:: Building first prevents the editor from loading a stale module DLL.

setlocal

set UE_ROOT=C:\Program Files\Epic Games\UE_5.8
set PROJECT=C:\Projects\NobleArchimedes\NobleArchimedes.uproject

echo ============================================
echo  Noble Archimedes - Development Build
echo ============================================
echo.

if not exist "%UE_ROOT%\Engine\Build\BatchFiles\Build.bat" (
    echo ERROR: UE5 not found at %UE_ROOT%
    echo Update UE_ROOT in this script.
    pause
    exit /b 1
)

if not exist "%PROJECT%" (
    echo ERROR: Project not found at %PROJECT%
    echo Update PROJECT in this script.
    pause
    exit /b 1
)

echo [1/2] Building NobleArchimedesEditor...
call "%UE_ROOT%\Engine\Build\BatchFiles\Build.bat" NobleArchimedesEditor Win64 Development -Project="%PROJECT%" -WaitMutex
if errorlevel 1 (
    echo.
    echo ERROR: Build failed. Fix the compile errors above, then run this script again.
    pause
    exit /b 1
)

echo.
echo [2/2] Launching Unreal Editor...
start "" "%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor.exe" "%PROJECT%"

echo.
echo Editor launched.
