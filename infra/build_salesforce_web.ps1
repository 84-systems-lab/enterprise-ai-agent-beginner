# One locked build path for all Python ZIP functions.
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
& (Join-Path $projectRoot '.venv/Scripts/python.exe') (Join-Path $projectRoot 'tools/build_packages.py') --install
if ($LASTEXITCODE -ne 0) { throw 'Pinned Lambda package build failed.' }
