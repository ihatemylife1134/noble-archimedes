@echo off
:: Noble Archimedes - Development Build Script
:: For iterative development and testing

setlocal enabledelayedexpansion

set UE_ROOT=C:\Program Files\Epic Games\UE_5.8
set PROJECT=C:\Projects\NobleArchimedes\NobleArchimedes.uproject
set PLATFORM=Win64

echo ============================================
echo  Noble Archimedes - Development Build
echo ============================================
echo.

echo [1/3] Launching Unreal Editor for development build...
echo This will open the UE5 editor. Use File > Package Project > Windows > Win64
echo to create a development build from within the editor.
echo.

"%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor.exe" "%PROJECT%"

echo.
echo Done.
pause