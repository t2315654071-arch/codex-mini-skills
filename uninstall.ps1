[CmdletBinding()]
param(
    [string]$CodexHome
)

$ErrorActionPreference = 'Stop'
$skillName = 'document-extractor-lite'
if (-not $CodexHome) {
    $CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
}
$skillsRoot = Join-Path ([IO.Path]::GetFullPath($CodexHome)) 'skills'
$target = Join-Path $skillsRoot $skillName
$targetFull = [IO.Path]::GetFullPath($target)
if (-not $targetFull.StartsWith([IO.Path]::GetFullPath($skillsRoot).TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Resolved target is outside the Codex skills directory.'
}
if ((Split-Path -Leaf $targetFull) -ne $skillName) {
    throw 'Resolved target does not match the expected skill ID.'
}
if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
}
[pscustomobject]@{
    status = 'ok'
    skill = $skillName
    removed = -not (Test-Path -LiteralPath $target)
}
