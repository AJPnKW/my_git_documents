param(
    [string]$Group = "venuiti",
    [switch]$SkipRepoValidation
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

Push-Location $RepoRoot
try {
    $ArgsList = @("scripts/company_research/run_company_research_production.py", "--group", $Group)
    if ($SkipRepoValidation) {
        $ArgsList += "--skip-repo-validation"
    }
    python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
