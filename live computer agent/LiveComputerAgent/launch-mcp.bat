@echo off
set LCA_CONFIG=%~dp0config\default.json
"%~dp0.venv\Scripts\python.exe" -m live_computer_agent
