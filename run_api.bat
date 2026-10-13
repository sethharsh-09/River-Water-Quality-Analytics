@echo off
title MindGraphNet - FastAPI Microservice
echo ========================================================
echo  Starting MindGraphNet FastAPI Microservice
echo ========================================================
set PYTHONPATH=%~dp0
set PYTHONIOENCODING=utf-8
"%~dp0.venv\Scripts\uvicorn.exe" MindGraphNet.api.app:app --host 127.0.0.1 --port 8000 --reload
pause
