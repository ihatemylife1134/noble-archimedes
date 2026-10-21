@echo off
:: Noble Archimedes - play the game in UE5 with the in-game smoke test.
::
:: Useful for a quick manual look at Chapter 1 with the -NATestCombat smoke
:: test running. For the automated pass/fail version use:
::     python Tools\run_game_smoke_test.py

setlocal

set UE_ROOT=C:\Program Files\Epic Games\UE_5.8
set PROJECT=C:\Projects\NobleArchimedes\NobleArchimedes.uproject
set EDITOR=%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor.exe
set MAP=/Game/Maps/Chap_01_AbandonedCastle

if not exist "%EDITOR%" (
    echo ERROR: UnrealEditor.exe not found at %EDITOR%
    exit /b 1
)

echo Playing %MAP% ...
start "" "%EDITOR%" "%PROJECT%" %MAP% -game -windowed -resx=1600 -resy=900 -NATestCombat
exit /b 0
