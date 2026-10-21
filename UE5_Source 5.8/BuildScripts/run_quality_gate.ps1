<#
.SYNOPSIS
    Noble Archimedes quality gate.

.DESCRIPTION
    Runs every automated check in order and stops at the first failure:

      1.  C++ build            (NobleArchimedesEditor Win64 Development)
      2.  Content build        (Tools/ue5_build_content.py)
      3.  Content QA           (Tools/ue5_verify_content.py)
      3b. Asset substance      (Tools/verify_assets_substance.py)
      3c. Fidelity timings F2  (Tools/fidelity_timings.py)
      3d. Fidelity levels  F3  (Tools/fidelity_levels.py)
      3e. Asset coverage   F4  (Tools/fidelity_assets.py)
      4.  In-game smoke        (Tools/run_game_smoke_test.py)

    Exit code 0 means every gate passed. A red gate means the milestone is not
    done, so this is the definition of "done" for each milestone.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File BuildScripts\run_quality_gate.ps1
    powershell -ExecutionPolicy Bypass -File BuildScripts\run_quality_gate.ps1 -SkipBuild
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
    $callArgs = @(
        $PROJECT, '-run=PythonScript', "-script=$Script",
        '-unattended', '-nosplash', '-nop4', '-nosound', '-stdout'
    )
    $proc = Start-Process -FilePath $EDITOR_CMD -ArgumentList $callArgs -PassThru `
        -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError "$logOut.err"
    $proc.WaitForExit()

    # Display-level lines never reach stdout, so read the project log for the
    # markers the Python tools emit.
    $fromLog = ''
    if (Test-Path $PROJECT_LOG) {
        $fromLog = Get-Content $PROJECT_LOG -Tail 1200 -ErrorAction SilentlyContinue | Out-String
    }
    return @{ ExitCode = $proc.ExitCode; Log = $logOut; Text = $fromLog }
}

function Fail-Gate {
    param([string[]]$Patterns)
    foreach ($pattern in $Patterns) {
        Select-String -Path $PROJECT_LOG -Pattern $pattern -ErrorAction SilentlyContinue |
            ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
    }
    $results | Format-Table -AutoSize
    exit 1
}

# ------------------------------------------------------------------ 1. build
if (-not $SkipBuild) {
    Write-Step '1/4  C++ build (NobleArchimedesEditor Win64 Development)'
    $out = Join-Path $env:TEMP 'gate_build.log'
    $proc = Start-Process -FilePath $BUILD_BAT -PassThru -WindowStyle Hidden `
        -ArgumentList @('NobleArchimedesEditor', 'Win64', 'Development', "-Project=$PROJECT", '-WaitMutex') `
        -RedirectStandardOutput $out -RedirectStandardError "$out.err"
    $proc.WaitForExit()

    $text = Get-Content $out -Raw -ErrorAction SilentlyContinue
    $passed = ($text -match 'Result:\s*Succeeded') -or ($text -match 'Target is up to date')
    Add-Result -Name 'C++ build' -Passed $passed -Detail $(if ($passed) { 'Succeeded' } else { "See $out" })
    if (-not $passed) { Fail-Gate @('error C', 'error LNK') }
    Write-Host 'Result: Succeeded' -ForegroundColor DarkGray
}

if (-not $SkipContent) {
    Write-Step '2/4  Content build'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\ue5_build_content.py')
    $summary = ([regex]::Match($r.Text, 'SUMMARY[^\r\n]*')).Value
    $passed = ($summary -match 'errors=0')
    Add-Result -Name 'Content build' -Passed $passed -Detail $summary.Trim()
    Write-Host $summary.Trim() -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('NA-CONTENT\] ERROR', 'LogPython: Error') }

    # The content build regenerates the blockout, which removes every art-pass
    # actor. Re-apply the art pass before QA, otherwise level checks report
    # missing dais/shrine dressing that only exists in the presentation pass.
    Write-Step '2b/4  Art pass (materials and set dressing)'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\ue5_art_pass.py')
    $artErrors = ([regex]::Match($r.Text, 'Presentation pass complete')).Value
    $passed = ($artErrors -ne '')
    Add-Result -Name 'Art pass' -Passed $passed -Detail $(if ($passed) { 'applied' } else { 'did not complete' })
    Write-Host $(if ($passed) { 'art pass complete' } else { 'art pass FAILED' }) -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('LogPython: Error') }

    Write-Step '3/4  Content QA'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\ue5_verify_content.py')
    $errors = ([regex]::Match($r.Text, 'NA-QA\] errors=(\d+)')).Groups[1].Value
    $passed = ($errors -eq '0')
    Add-Result -Name 'Content QA' -Passed $passed -Detail "errors=$errors"
    Write-Host "NA-QA errors=$errors" -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('NA-QA\] ERROR') }

    Write-Step '3b/4  Asset substance (no placeholders)'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\verify_assets_substance.py')
    $verdict = ([regex]::Match($r.Text, 'NA-SUBSTANCE\] RESULT=(\w+)')).Groups[1].Value
    $passed = ($verdict -eq 'PASS')
    Add-Result -Name 'Asset substance' -Passed $passed -Detail "RESULT=$verdict"
    Write-Host "substance RESULT=$verdict" -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('NA-SUBSTANCE\] FAILED') }

    Write-Step '3c/4  Fidelity: mechanical timings (F2)'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\fidelity_timings.py')
    $m = [regex]::Match($r.Text, 'NA-FID2\] RESULT=(\w+) errors=(\d+) deviations=(\d+)')
    $f2Errors = $m.Groups[2].Value
    $f2Drift = $m.Groups[3].Value
    $passed = ($m.Groups[1].Value -eq 'PASS') -and ($f2Errors -eq '0')
    Add-Result -Name 'Fidelity timings' -Passed $passed -Detail "errors=$f2Errors clip_drift=$f2Drift"
    Write-Host "F2 verdict=$($m.Groups[1].Value) errors=$f2Errors clip_drift=$f2Drift" -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('NA-FID2\] FAILED') }

    Write-Step '3d/4  Fidelity: chapter structure (F3)'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\fidelity_levels.py')
    $m = [regex]::Match($r.Text, 'NA-FID3\] RESULT=(\w+) errors=(\d+)')
    $f3Errors = $m.Groups[2].Value
    $passed = ($m.Groups[1].Value -eq 'PASS') -and ($f3Errors -eq '0')
    Add-Result -Name 'Fidelity levels' -Passed $passed -Detail "errors=$f3Errors"
    Write-Host "F3 verdict=$($m.Groups[1].Value) errors=$f3Errors" -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('NA-FID3\] FAILED') }

    Write-Step '3e/4  Fidelity: asset coverage (F4)'
    $r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\fidelity_assets.py')
    $m = [regex]::Match($r.Text, 'NA-FID4\] RESULT=(\w+) errors=(\d+) gaps=(\d+)')
    $f4Errors = $m.Groups[2].Value
    $f4Gaps = $m.Groups[3].Value
    $coverage = [regex]::Match($r.Text, 'NA-FID4\] overall\s+(\S+)').Groups[1].Value
    $passed = ($m.Groups[1].Value -eq 'PASS') -and ($f4Errors -eq '0')
    Add-Result -Name 'Asset coverage' -Passed $passed -Detail "gaps=$f4Gaps coverage=$coverage"
    Write-Host "F4 verdict=$($m.Groups[1].Value) gaps=$f4Gaps coverage=$coverage" -ForegroundColor DarkGray
    if (-not $passed) { Fail-Gate @('NA-FID4\] FAILED') }
}

Write-Step '3f/4  Chapter 1 acceptance'
$r = Invoke-Commandlet -Script (Join-Path $PROJECT_DIR 'Tools\verify_chapter1.py')
$m = [regex]::Match($r.Text, 'NA-CH1\] RESULT=(\w+) errors=(\d+)')
$ch1Errors = $m.Groups[2].Value
$passed = ($m.Groups[1].Value -eq 'PASS') -and ($ch1Errors -eq '0')
Add-Result -Name 'Chapter 1 acceptance' -Passed $passed -Detail "errors=$ch1Errors"
Write-Host "Ch1 verdict=$($m.Groups[1].Value) errors=$ch1Errors" -ForegroundColor DarkGray
if (-not $passed) { Fail-Gate @('NA-CH1\] FAILED') }


Write-Step '4/4  In-game smoke test'
& python (Join-Path $PROJECT_DIR 'Tools\run_game_smoke_test.py') --seconds $SmokeSeconds
$passed = ($LASTEXITCODE -eq 0)
Add-Result -Name 'In-game smoke' -Passed $passed -Detail ''
if (-not $passed) { $results | Format-Table -AutoSize; exit 1 }

Write-Step 'QUALITY GATE'
$results | Format-Table -AutoSize
Write-Host 'RESULT: PASS' -ForegroundColor Green
exit 0
