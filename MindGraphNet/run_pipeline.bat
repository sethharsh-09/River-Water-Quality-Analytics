@echo off
title MindGraphNet - Multi-Hybrid Pipeline Execution
echo ========================================================
echo  Executing MindGraphNet 9-Stage ML Pipeline
echo ========================================================
set PYTHONPATH=%~dp0
set PYTHONIOENCODING=utf-8
"%~dp0.venv\Scripts\python.exe" "%~dp0MindGraphNet\MindGraphNet_Enhanced_Pipeline.py"
pause
