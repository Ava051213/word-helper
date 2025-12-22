#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块
包含通用的工具函数
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def show_menu() -> None:
    """显示主菜单"""
    print("\n" + "=" * 40)
    print("单词记忆助手 - 主菜单")
    print("=" * 40)
    print("1. 添加单词")
    print("2. 查看单词")
    print("3. 复习单词")
    print("4. 搜索单词")
    print("5. 删除单词")
    print("6. 学习统计")
    print("0. 退出程序")
    print("-" * 40)


def get_user_choice() -> str:
    """获取用户选择"""
    choice = input("请选择操作 (0-6): ").strip()
    return choice


def confirm_action(prompt: str) -> bool:
    """确认操作"""
    while True:
        response = input(f"{prompt} (y/N): ").strip().lower()
        if response in ['', 'n', 'no']:
            return False
        elif response in ['y', 'yes']:
            return True
        else:
            print("请输入 y(是) 或 n(否)")


def init_logging(level: int = logging.INFO) -> None:
    """初始化统一的日志系统（控制台 + 轮转文件）"""
    logger = logging.getLogger()
    if logger.handlers:
        return
    
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "app.log")
    
    file_handler = RotatingFileHandler(file_path, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
