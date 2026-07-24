[CmdletBinding()]
param(
    [string]$CodexHome
)

$ErrorActionPreference = 'Stop'
$skillName = 'document-extractor-lite'
if (-not $CodexHome) {
    $CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
}
$source = Join-Path $PSScriptRoot ('skills\' + $skillName)
$skillsRoot = Join-Path ([IO.Path]::GetFullPath($CodexHome)) 'skills'
$target = Join-Path $skillsRoot $skillName
if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md') -PathType Leaf)) {
    throw "Skill source is missing: $source"
}
if (Test-Path -LiteralPath $target) {
    throw "Skill already exists: $target"
}
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Recurse
[pscustomobject]@{
    status = 'ok'
    skill = $skillName
    target = $target
}
