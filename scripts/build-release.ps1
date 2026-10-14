$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $repoRoot 'blender_manifest.toml'
$sourcePath = Join-Path $repoRoot '__init__.py'
$licensePath = Join-Path $repoRoot 'LICENSE'
$manifestText = Get-Content -LiteralPath $manifestPath -Raw
$sourceText = Get-Content -LiteralPath $sourcePath -Raw
$manifestVersionMatch = [regex]::Match($manifestText, '(?m)^version\s*=\s*"([^"]+)"')
$codeVersionMatch = [regex]::Match($sourceText, '"version"\s*:\s*\((\d+),\s*(\d+),\s*(\d+)\)')
if (-not $manifestVersionMatch.Success -or -not $codeVersionMatch.Success) {
    throw 'Could not read the version from the manifest and bl_info.'
}
$codeVersion = '{0}.{1}.{2}' -f $codeVersionMatch.Groups[1].Value, $codeVersionMatch.Groups[2].Value, $codeVersionMatch.Groups[3].Value
if ($manifestVersionMatch.Groups[1].Value -ne $codeVersion) {
    throw "Version mismatch: manifest is $($manifestVersionMatch.Groups[1].Value), bl_info is $codeVersion."
}
$version = $manifestVersionMatch.Groups[1].Value
$dist = Join-Path $repoRoot 'dist'
New-Item -ItemType Directory -Path $dist -Force | Out-Null
$archivePath = Join-Path $dist "Home_Model_Workshop_Blender_5_2_2_v$($version.Replace('.', '_')).zip"
Compress-Archive -LiteralPath $sourcePath,$manifestPath,$licensePath -DestinationPath $archivePath -CompressionLevel Optimal -Force
Write-Output "Created $archivePath"
