@echo off
setlocal
cd /d "%~dp0"
title NetGuard Pro Installer
where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  echo Install Python 3.13 or newer, then run this file again.
  pause
  exit /b 1
)
echo Installing required components...
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Dependency installation failed.
  pause
  exit /b 1
)
set "APP=%~dp0start_netguard.bat"
set "LNK=%USERPROFILE%\Desktop\NetGuard Pro.lnk"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell;$s=$w.CreateShortcut([Environment]::ExpandEnvironmentVariables('%LNK%'));$s.TargetPath='%APP%';$s.WorkingDirectory='%~dp0';$s.IconLocation='%~dp0assets\netguard_pro_icon.ico';$s.Save()"
echo.
echo Installation complete. A NetGuard Pro shortcut was created on your Desktop.
start "" "%APP%"
exit /b 0
