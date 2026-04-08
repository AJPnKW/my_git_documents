param(
  [switch]$ValidateOnly
)

Set-Location $PSScriptRoot\..

if ($ValidateOnly) {
  python tests\run_all.py
  exit $LASTEXITCODE
}

Write-Host "Open http://localhost:8000/app/index.html after the server starts."
python -m http.server 8000
