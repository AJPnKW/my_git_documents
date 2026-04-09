[CmdletBinding()]
param(
    [string]$Target = "C:\Users\andrew\PROJECTS\GitHub\my_git_documents\reports\packages\my_git_documents__package__20260408__164040.zip"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$before = (Get-PSDrive -Name C).Free

if (Test-Path -LiteralPath $Target) {
    Remove-Item -LiteralPath $Target -Force
}

$after = (Get-PSDrive -Name C).Free

[PSCustomObject]@{
    Deleted = -not (Test-Path -LiteralPath $Target)
    ReclaimedGB = [math]::Round(($after - $before) / 1GB, 2)
    FreeGB = [math]::Round($after / 1GB, 2)
} | Format-List
