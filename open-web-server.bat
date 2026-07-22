@echo off
cd /d "%~dp0"
start "Student Management System Server" cmd /k "python app.py"
timeout /t 2 >nul
start "" http://127.0.0.1:5000
