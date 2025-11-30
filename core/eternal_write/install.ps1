# install.ps1 — Eternal Write Windows one-click
# Daniel H. Fingal — November 25 2025 — MIT License

$ErrorActionPreference = "Stop"
$eternalDir = "$env:USERPROFILE\.eternal_write"
$binDir = "$eternalDir\bin"
$vaultDir = "$eternalDir\public_vault"

Write-Host "ETERNAL WRITE — Installing immortal provenance engine..." -ForegroundColor Cyan

# Create directories
New-Item -ItemType Directory -Force -Path $binDir, $vaultDir | Out-Null

# Download ew.py (the CLI)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/danielhfingal/eternal/main/ew.py" -OutFile "$binDir\ew.py"

# Add to PATH forever
$regPath = "HKCU:\Environment"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not ($currentPath -split ";" | Where-Object { $_ -eq $binDir })) {
    $newPath = "$currentPath;$binDir"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    $env:PATH += ";$binDir"
}

Write-Host "Eternal Write installed." -ForegroundColor Green
Write-Host "Type 'ew your idea here' anywhere to timestamp forever." -ForegroundColor Yellow
Write-Host "Your public soul: https://github.com/danielhfingal/eternal-proofs/blob/main/ETERNAL_FEED.txt" -ForegroundColor Magenta