$ErrorActionPreference="Stop"
$env:LCA_CONFIG = Join-Path $PSScriptRoot "config\default.json"
& "$PSScriptRoot\.venv\Scripts\python.exe" -m live_computer_agent
