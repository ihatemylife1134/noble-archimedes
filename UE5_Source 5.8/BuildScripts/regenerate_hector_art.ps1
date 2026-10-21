param(
    [string]$Blender = ""
)

# Regenerate Hector's FBX art (mesh + 12 animation clips) with Blender.
# The UE content build imports from ArtSource/Hector/Export, so this must run
# before rebuilding content whenever hector_rig.py or hector_anims.py changes.

$ErrorActionPreference = 'Stop'
$ProjectDir = Split-Path -Parent $PSScriptRoot
$ArtDir = Join-Path $ProjectDir 'ArtSource\Hector'
$OutDir = Join-Path $ArtDir 'Export'

function Find-Blender {
    if ($Blender -and (Test-Path $Blender)) { return $Blender }

    $onPath = Get-Command blender -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }

    $roots = @(
        'C:\Program Files\Blender Foundation',
        'C:\Program Files (x86)\Blender Foundation',
        (Join-Path $env:LOCALAPPDATA 'Programs\Blender Foundation'),
        'C:\Program Files\Steam\steamapps\common\Blender'
    )
    foreach ($root in $roots) {
        if (-not (Test-Path $root)) { continue }
        $exe = Get-ChildItem $root -Recurse -Filter 'blender.exe' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($exe) { return $exe.FullName }
    }
    return $null
}

$exe = Find-Blender
if (-not $exe) {
    Write-Host 'Blender not found. Pass -Blender <path to blender.exe>.' -ForegroundColor Red
    exit 2
}
Write-Host "Blender: $exe" -ForegroundColor Cyan

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$before = @{}
Get-ChildItem $OutDir -Filter '*.fbx' -ErrorAction SilentlyContinue |
    ForEach-Object { $before[$_.Name] = $_.LastWriteTime }

Push-Location $ArtDir
try {
    & $exe -b -P (Join-Path $ArtDir 'generate_hector.py') -- $OutDir
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
}

Write-Host "blender exit=$code" -ForegroundColor DarkGray

$files = Get-ChildItem $OutDir -Filter '*.fbx' -ErrorAction SilentlyContinue
Write-Host "$($files.Count) FBX files in $OutDir" -ForegroundColor Cyan
foreach ($f in ($files | Sort-Object Name)) {
    $old = $before[$f.Name]
    $state = if (-not $old) { 'new' } elseif ($old -eq $f.LastWriteTime) { 'UNCHANGED' } else { 'updated' }
    Write-Host ("  {0,-26} {1,8:N1} KB  {2,-9} {3}" -f $f.Name, ($f.Length / 1KB), $state, $f.LastWriteTime.ToString('HH:mm:ss'))
}

if ($code -ne 0) { exit $code }
