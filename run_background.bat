@echo off
REM Chay Task_Manager.py nen (khong cua so console). Working dir = thu muc chua file .env
cd /d "%~dp0"

where pythonw >nul 2>&1
if %errorlevel% equ 0 (
  pythonw "%~dp0Task_Manager.py"
  exit /b %ERRORLEVEL%
)

where pyw >nul 2>&1
if %errorlevel% equ 0 (
  pyw "%~dp0Task_Manager.py"
  exit /b %ERRORLEVEL%
)

echo Khong tim thay pythonw hoac pyw. Cai Python tu python.org va tich "Add to PATH".
pause
exit /b 1
