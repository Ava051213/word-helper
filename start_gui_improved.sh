#!/bin/bash

# 单词记忆助手启动脚本 (改进版GUI)
# 适用于 macOS 和 Linux 系统

echo "========================================"
echo "     单词记忆助手 (改进版GUI)"
echo "========================================"
echo ""

# 检查Python是否已安装
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python解释器"
    echo "请先安装Python 3.6或更高版本"
    echo "下载地址: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# 启动改进版GUI
echo "正在启动单词记忆助手(改进版)..."
python3 src/gui_main_improved.py

if [ $? -ne 0 ]; then
    echo ""
    echo "程序运行出现错误！"
    exit $?
fi

echo ""
echo "程序已退出。"