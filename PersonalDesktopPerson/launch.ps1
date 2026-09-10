$env:PDP_CONFIG=Join-Path $PSScriptRoot 'config\default.json'
& "$PSScriptRoot\.venv\Scripts\python.exe" -m personal_desktop_person
