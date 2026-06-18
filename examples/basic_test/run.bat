@echo off
setlocal
cd /d "%~dp0"
start "Server Demo" python serverdemo.py
start "Client Demo" python clientdemo.py
start "Client2 Demo" python clientdemo2.py
exit /b
