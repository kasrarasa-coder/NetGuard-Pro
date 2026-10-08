@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Run NetGuardPro_Install.bat first.
  pause
  exit /b 1
)
py netguard_pro.py
if errorlevel 1 (
  echo.
  echo NetGuard Pro closed because an error occurred.
  pause
)
