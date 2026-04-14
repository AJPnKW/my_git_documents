param()
$ErrorActionPreference = 'Stop'
$overlayRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $overlayRoot 'my_git_documents'
$targetRoot = 'C:\Users\andrew\PROJECTS\GitHub\my_git_documents'
if (-not (Test-Path $sourceRoot)) { throw "Missing overlay folder: $sourceRoot" }
if (-not (Test-Path $targetRoot)) { throw "Missing target repo: $targetRoot" }
Copy-Item -Path (Join-Path $sourceRoot '*') -Destination $targetRoot -Recurse -Force
Write-Host 'Overlay copied.'
Write-Host 'Next:'
Write-Host 'Set-Location "C:\Users\andrew\PROJECTS\GitHub\my_git_documents"'
Write-Host 'python .\scripts\build_site_index.py'
Write-Host 'git status --short'
