$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "backup.ps1")
& (Join-Path $PSScriptRoot "export_json.ps1")
