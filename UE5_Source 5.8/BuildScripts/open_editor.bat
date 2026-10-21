@echo off
:: Noble Archimedes - open the project in the Unreal Engine 5.8 editor.
::
:: The editor must be launched detached. If it inherits this console, closing
:: the console sends QUIT_EDITOR and the editor exits immediately.

setlocal

set UE_ROOT=C:\Program Files\Epic Games\UE_5.8
set PROJECT=C:\Projects\NobleArchimedes\NobleArchimedes.uproject
set EDITOR=%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor.exe

if not exist "%EDITOR%" (
    echo ERROR: UnrealEditor.exe not found at %EDITOR%
    echo Update UE_ROOT in this script.
    exit /b 1
)

if not exist "%PROJECT%" (
    echo ERROR: Project not found at %PROJECT%
    exit /b 1
)

echo Opening %PROJECT% ...
start "" "%EDITOR%" "%PROJECT%"
exit /b 0
