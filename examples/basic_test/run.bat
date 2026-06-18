@echo off
setlocal
cd /d "%~dp0"

start "Server Demo" cmd /k python serverdemo.py
start "Client Demo" cmd /k python clientdemo.py
start "Client2 Demo" cmd /k python clientdemo2.py

exit /b