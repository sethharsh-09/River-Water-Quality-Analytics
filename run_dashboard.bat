@echo off
title MindGraphNet - Clinical Analytics Dashboard
echo ========================================================
echo  Launching MindGraphNet Interactive Streamlit Portal
echo ========================================================
set PYTHONPATH=%~dp0
set PYTHONIOENCODING=utf-8
"%~dp0.venv\Scripts\streamlit.exe" run "%~dp0MindGraphNet\dashboard\streamlit_app.py" --server.port 8501
pause
