#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词记忆助手主程序
基于艾宾浩斯记忆曲线的智能单词记忆系统
"""

import sys
import os

# 将src目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from word_manager import WordManager
from scheduler import Scheduler
from utils import show_menu, get_user_choice


def main():
    """主函数"""
    print("=" * 50)
    print("欢迎使用单词记忆助手!")
    print("基于艾宾浩斯记忆曲线的智能单词记忆系统")
    print("=" * 50)
    
    # 初始化单词管理器和调度器
    word_manager = WordManager()
    scheduler = Scheduler(word_manager)
    
    while True:
        # 显示主菜单
        show_menu()
        
        # 获取用户选择
        choice = get_user_choice()
        
        if choice == '1':
            # 添加单词
            word_manager.add_word()
        elif choice == '2':
            # 查看单词
            word_manager.view_words()
        elif choice == '3':
            # 复习单词
            scheduler.review_words()
        elif choice == '4':
            # 搜索单词
            word_manager.search_word()
        elif choice == '5':
            # 删除单词
            word_manager.delete_word()
        elif choice == '6':
            # 显示学习统计
            word_manager.show_statistics()
        elif choice == '0':
            # 退出程序
            print("感谢使用单词记忆助手，再见！")
            break
        else:
            print("无效的选择，请重新输入！")


if __name__ == "__main__":
    main()