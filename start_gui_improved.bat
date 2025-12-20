@echo off
title 单词记忆助手 (改进版)
echo ========================================
echo      单词记忆助手 (改进版GUI)
echo ========================================
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python解释器
    echo 请先安装Python 3.6或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 启动改进版GUI
echo 正在启动单词记忆助手(改进版)...
python src/gui_main_improved.py

if %errorlevel% neq 0 (
    echo.
    echo 程序运行出现错误！
    pause
    exit /b %errorlevel%
)

echo.
echo 程序已退出。
pause