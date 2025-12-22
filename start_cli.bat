@echo off
setlocal
cd /d "%~dp0"
python "%~dp0src\cli\main.py"
endlocal
