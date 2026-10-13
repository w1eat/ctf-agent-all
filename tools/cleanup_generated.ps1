param([switch]$Apply)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\')
$knowledgeRoot = Join-Path $projectRoot '.runtime\knowledge'
$snapshotRoot = Join-Path $knowledgeRoot 'snapshots'
$candidates = [System.Collections.Generic.List[string]]::new()

function Add-Candidate([string]$relativePath) {
    $path = Join-Path $projectRoot $relativePath
    if (Test-Path -LiteralPath $path) {
        $candidates.Add($path)
    }
}

# Only generated caches and one-off exports belong in this list. Logs, challenge
# packages, browser login profiles, installed MCP tools, and .venv are retained.
Add-Candidate '.pytest_cache'
Add-Candidate '.ruff_cache'
$playwrightActive = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'playwright-mcp'
}).Count -gt 0
if (-not $playwrightActive) {
    Add-Candidate '.playwright-mcp'
} else {
    Write-Output 'Keeping .playwright-mcp while Playwright MCP processes are running.'
}

foreach ($name in @(
    'caculate_detail.json', 'challenges.json', 'challenges_api.json',
    'challenges_list.json', 'challenges_parsed.json', 'leaderboard.json',
    'leaderboard_challenges.json', 'platform-challenges.json',
    'platform-details.json', 'fmt-challenge.yml', 'snap1.yml',
    'js-scan.txt', 'rev_local.exe', 'unpacked.bin'
)) {
    Add-Candidate $name
}

if (Test-Path -LiteralPath $snapshotRoot) {
    $currentPath = Join-Path $knowledgeRoot 'current.json'
    if (-not (Test-Path -LiteralPath $currentPath)) {
        throw 'Knowledge current.json is missing; refusing snapshot cleanup.'
    }
    $current = (Get-Content -LiteralPath $currentPath -Raw | ConvertFrom-Json).snapshot_id
    if (-not $current -or -not (Test-Path -LiteralPath (Join-Path $snapshotRoot $current))) {
        throw 'Current knowledge snapshot is missing; refusing snapshot cleanup.'
    }
    $pinned = @()
    $runsPath = Join-Path $knowledgeRoot 'runs'
    if (Test-Path -LiteralPath $runsPath) {
        $pinned = @(Get-ChildItem -LiteralPath $runsPath -File | ForEach-Object {
            (Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json).snapshot_id
        })
    }
    foreach ($snapshot in Get-ChildItem -LiteralPath $snapshotRoot -Directory) {
        if ($snapshot.Name -ne $current -and $snapshot.Name -notin $pinned) {
            $candidates.Add($snapshot.FullName)
        }
    }
}

$totalBytes = 0L
foreach ($candidate in $candidates) {
    $absolute = (Resolve-Path -LiteralPath $candidate).Path
    $prefix = $projectRoot + [IO.Path]::DirectorySeparatorChar
    if (-not $absolute.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing path outside project: $absolute"
    }
    if ($absolute -eq $projectRoot -or $absolute -eq $snapshotRoot -or $absolute -eq $knowledgeRoot) {
        throw "Refusing directory root: $absolute"
    }
    $item = Get-Item -LiteralPath $absolute
    $bytes = if ($item.PSIsContainer) {
        (Get-ChildItem -LiteralPath $absolute -Recurse -File -Force | Measure-Object Length -Sum).Sum
    } else { $item.Length }
    $totalBytes += [long]$bytes
    $sizeMb = [math]::Round($bytes / 1MB, 1)
    Write-Output "$sizeMb MB  $absolute"
    if ($Apply) {
        Remove-Item -LiteralPath $absolute -Recurse -Force -ErrorAction Stop
    }
}

$mode = if ($Apply) { 'Removed' } else { 'Preview only' }
Write-Output "$mode`: $($candidates.Count) paths, $([math]::Round($totalBytes / 1MB, 1)) MB"
