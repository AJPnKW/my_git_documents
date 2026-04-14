param()
$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = 'C:\Users\andrew\PROJECTS\GitHub\my_git_documents'

$items = @(
  'app\shared\viewer\viewer.html',
  'app\shared\viewer\viewer.js',
  'app\assets\css\app.css',
  'web\shared\viewer\viewer.html',
  'web\shared\viewer\viewer.js',
  'web\assets\css\app.css'
)

foreach ($item in $items) {
  $src = Join-Path $sourceRoot $item
  $dst = Join-Path $repoRoot $item
  if (-not (Test-Path $src)) { throw "Missing overlay file: $src" }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
  Copy-Item -Path $src -Destination $dst -Force
  Write-Host "UPDATED: $dst"
}

Write-Host ''
Write-Host 'Next:'
Write-Host 'Set-Location "C:\Users\andrew\PROJECTS\GitHub\my_git_documents"'
Write-Host 'python .\scripts\build_site_index.py'
Write-Host 'git status --short'
