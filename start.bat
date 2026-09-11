@echo off
echo ===================================================
echo   Starting FINMITRA — Your Everyday Financial Companion
echo   Track: UN SDG 1 No Poverty
echo ===================================================

set VENV_PYTHON=C:\Users\Rehankhan\.gemini\antigravity\scratch\sou-ai-assistant\.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" run.py
) else (
    python run.py
)
pause
