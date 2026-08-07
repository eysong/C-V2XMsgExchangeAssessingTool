@echo off
title Installing Packages from Pip Freeze
cd /d "%~dp0"

echo Upgrading pip first...
python -m pip install --upgrade pip

echo.
echo Installing libraries from your pip freeze file...
pip install -r requirements.txt

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] All libraries installed perfectly!
) else (
    echo [ERROR] Something went wrong during installation. Check the messages above.
)

echo.
pause
