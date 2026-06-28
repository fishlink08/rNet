@echo off
setlocal
cd /d "%~dp0"

start "Server Demo" cmd /k python server.py
start "Client Demo" cmd /k python client.py

exit /b