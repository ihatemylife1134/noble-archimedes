# Noble Archimedes - Project Setup Script (PowerShell)
# Run this on Windows after creating the UE5 project

$projectRoot = "C:\Projects\NobleArchimedes"
$ueRoot = "C:\Program Files\Epic Games\UE_5.5"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Noble Archimedes - Project Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check UE5 installation
if (-not (Test-Path "$ueRoot\Engine\Build\BatchFiles\RunUAT.bat")) {
    Write-Host "ERROR: UE5 not found at $ueRoot" -ForegroundColor Red
    Write-Host "Please install UE5.5+ or update \$ueRoot in this script." -ForegroundColor Red
    exit 1
}
Write-Host "OK: UE5 found at $ueRoot" -ForegroundColor Green

# Check project exists
$projectFile = "$projectRoot\NobleArchimedes.uproject"
if (-not (Test-Path $projectFile)) {
    Write-Host "ERROR: Project not found at $projectFile" -ForegroundColor Red
    Write-Host "Create the UE5 project first, then run this script." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Project found at $projectFile" -ForegroundColor Green

# Copy source files
Write-Host ""
Write-Host "Copying source files..." -ForegroundColor Cyan
$sourceRoot = "$PSScriptRoot\.."

# Copy Config
Copy-Item "$sourceRoot\Config\*" "$projectRoot\Config\" -Recurse -Force
Write-Host "  Config files copied"

# Copy Source
Copy-Item "$sourceRoot\NobleArchimedes\*" "$projectRoot\Source\NobleArchimedes\" -Recurse -Force
Write-Host "  Source files copied"

# Copy uproject
Copy-Item "$sourceRoot\NobleArchimedes.uproject" "$projectRoot\" -Force
Write-Host "  Project file copied"

# Generate Visual Studio project files
Write-Host ""
Write-Host "Generating Visual Studio project files..." -ForegroundColor Cyan
& "$ueRoot\Engine\Build\BatchFiles\GenerateProjectFiles.bat" -project="$projectFile"

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Project files generated" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to generate project files" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open NobleArchimedes.sln in Visual Studio 2022"
Write-Host "  2. Build > Build Solution"
Write-Host "  3. Open NobleArchimedes.uproject in UE5 Editor"
Write-Host "  4. Create Blueprints and assets per TRANSFER_GUIDE.md"
Write-Host ""
pause