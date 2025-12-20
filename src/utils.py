#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块
包含通用的工具函数
"""

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