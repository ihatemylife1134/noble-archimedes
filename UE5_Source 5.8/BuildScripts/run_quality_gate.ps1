<#
.SYNOPSIS
    Noble Archimedes quality gate.

.DESCRIPTION
    Runs every automated check in order and stops at the first failure:

      1. C++ build        (NobleArchimedesEditor Win64 Development)
      2. Content build    (Tools/ue5_build_content.py)
      3. Content QA       (Tools/ue5_verify_content.py)
      4. In-game smoke    (Tools/run_game_smoke_test.py)

    Exit code 0 means every gate passed. Run this before closing any milestone;
    a red gate means the milestone is not done.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File BuildScripts\run_quality_gate.ps1
    powershell -ExecutionPolicy Bypass -File BuildScripts\run_quality_gate.ps1 -SkipContent
#>
[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [switch]$SkipContent,
    [int]$SmokeSeconds = 45
)

$ErrorActionPreference = 'Stop'

$UE_ROOT = 'C:\Program Files\Epic Games\UE_5.8'
$PROJECT = 'C:\Projects\NobleArchimedes\NobleArchimedes.uproject'
$PROJECT_DIR = 'C:\Projects\NobleArchimedes'
$PROJECT_LOG = Join-Path $PROJECT_DIR 'Saved\Logs\NobleArchimedes.log'
$EDITOR_CMD = Join-Path $UE_ROOT 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$BUILD_BAT = Join-Path $UE_ROOT 'Engine\Build\BatchFiles\Build.bat'

$results = @()

function Write-Step {
    param([string]$Name)
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor Cyan
    Write-Host "  $Name" -ForegroundColor Cyan
    Write-Host ('=' * 70) -ForegroundColor Cyan
}

function Add-Result {
    param([string]$Name, [bool]$Passed, [string]$Detail = '')
    $script:results += [pscustomobject]@{ Step = $Name; Passed = $Passed; Detail = $Detail }
}

function Invoke-Commandlet {
    param([string]$Script)
    $logOut = Join-Path $env:TEMP ('gate_' + [IO.Path]::GetFileNameWithoutExtension($Script) + '.log')
    $args = @(
        $PROJECT, '-run=PythonScript', "-script=$Script",
        '-unattended', '-nosplash', '-nop4', '-nosound', '-stdout'
    )
    $proc = Start-Process -FilePath $EDITOR_CMD -ArgumentList $args -PassThru `
        -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError "$logOut.err"
    $proc.WaitForExit()

    # Display-level log lines are not captured on stdout, so read the project
    # log for the markers the scripts emit.
    $fromLog = ''
    if (Test-Path $PROJECT_LOG) {
        $fromLog = Get-Content $PROJECT_LOG -Tail 800 -ErrorAction SilentlyContinue | Out-String
    }
    return @{ ExitCode = $proc.ExitCode; Log = $logOut; Text = $fromLog }
}

# ---------------------------------------------------------------- 1. build
if (-not $SkipBuild) {
    Write-Step '1/4  C++ build (NobleArchimedesEditor Win64 Development)'
    $out = Join-Path $env:TEMP 'gate_build.log'
    $proc = Start-Process -FilePath $BUILD_BAT -PassThru -WindowStyle Hidden `
        -ArgumentList @('NobleArchimedesEditor', 'Win64', 'Development', "-Project=$PROJECT", '-WaitMutex') `
        -RedirectStandardOutput $out -RedirectStandardError "$out.err"
    $proc.WaitForExit()

    $text = Get-Content $out -Raw -ErrorAction SilentlyContinue
    $passed = ($text -match 'Result:\s*Succeeded') -or ($text -match 'Target is up to date')
    if ($passed) { Write-Host $text.Trim() -ForegroundColor DarkGray }
    if ($passed) { $detail = 'Succeeded' } else { $detail = "See $out" }
    Add-Result -Name 'C++ build' -Passed $passed -Detail $detail
    if (-not $passed) { $results | Format-Table -AutoSize; exit 1 }
}

# --------------------------------------------------------- 2/3. content + QA
if (-not $SkipContent) {
    Write-Step '2/4  Content build'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\ue5_build_content.py')
    $text = $r.Text
    $summary = ([regex]::Match($text, 'SUMMARY[^\r\n]*')).Value
    # UE reports a non-zero process code even on success, so trust the summary.
    $passed = ($summary -match 'errors=0')
    Write-Host ($summary.Trim()) -ForegroundColor DarkGray
    Add-Result -Name 'Content build' -Passed $passed -Detail ($summary.Trim())
    if (-not $passed) {
        Select-String -Path $PROJECT_LOG -Pattern 'NA-CONTENT\] ERROR|LogPython: Error' |
            ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
        $results | Format-Table -AutoSize; exit 1
    }

    Write-Step '3/4  Content QA'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\ue5_verify_content.py')
    $text = $r.Text
    $errors = ([regex]::Match($text, 'NA-QA\] errors=(\d+)')).Groups[1].Value
    $passed = ($errors -eq '0')
    Write-Host "NA-QA errors=$errors" -ForegroundColor DarkGray
    Add-Result -Name 'Content QA' -Passed $passed -Detail "errors=$errors"
    if (-not $passed) {
        Select-String -Path $PROJECT_LOG -Pattern 'NA-QA\] ERROR' |
            ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
        $results | Format-Table -AutoSize; exit 1
    }

    Write-Step '3b/4  Asset substance (no placeholders)'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\verify_assets_substance.py')
    $text = $r.Text
    $verdict = ([regex]::Match($text, 'NA-SUBSTANCE\] RESULT=(\w+)')).Groups[1].Value
    $passed = ($verdict -eq 'PASS')
    Write-Host "substance RESULT=$verdict" -ForegroundColor DarkGray
    Add-Result -Name 'Asset substance' -Passed $passed -Detail "RESULT=$verdict"
    if (-not $passed) {
        Select-String -Path $PROJECT_LOG -Pattern 'NA-SUBSTANCE\] FAILED' |
            ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
        $results | Format-Table -AutoSize; exit 1
    }
}
Write-Step '4/4  In-game smoke test'
& python (Join-Path $PROJECT_DIR 'Tools\run_game_smoke_test.py') --seconds $SmokeSeconds
$passed = ($LASTEXITCODE -eq 0)
Add-Result -Name 'In-game smoke' -Passed $passed -Detail ''
if (-not $passed) { $results | Format-Table -AutoSize; exit 1 }

Write-Step 'QUALITY GATE'
$results | Format-Table -AutoSize
Write-Host 'RESULT: PASS' -ForegroundColor Green
exit 0
