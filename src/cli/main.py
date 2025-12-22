#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词记忆助手主程序 (CLI)
已升级为 SQLite + SM-2 算法
"""

import sys
import os

# 将src目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.word_manager import WordManager
from core.scheduler import Scheduler
from utils.common import show_menu, get_user_choice, init_logging

def interactive_add_word(word_manager: WordManager):
    """交互式添加单词"""
    print("\n--- 添加单词 ---")
    word_text = input("请输入单词: ").strip().lower()
    if not word_text:
        return
    
    # 尝试从词典API获取
    meaning = ""
    example = ""
    phonetic = ""
    
    if word_manager.dictionary_api:
        print(f"正在查询 '{word_text}'...")
        info = word_manager.dictionary_api.get_word_info(word_text)
        if info:
            print(f"找到释义: {info['meanings'][0]['definition']}")
            phonetic = info.get('phonetic', '')
            use_it = input("是否使用该释义? (Y/n): ").strip().lower()
            if use_it != 'n':
                meaning = info['meanings'][0]['definition']
                example = info['examples'][0] if info.get('examples') else ""
    
    if not meaning:
        meaning = input("请输入释义: ").strip()
    
    if not example:
        example = input("请输入例句 (可选): ").strip()
        
    if word_manager.add_word_direct(word_text, meaning, example, phonetic):
        print(f"成功添加单词: {word_text}")
    else:
        print(f"添加失败 (单词可能已存在)")

def main():
    """主函数"""
    init_logging()
    
    # 初始化
    word_manager = WordManager()
    scheduler = Scheduler(word_manager)
    
    while True:
        show_menu()
        choice = get_user_choice()
        
        if choice == '1':
            interactive_add_word(word_manager)
        elif choice == '2':
            # 查看单词
            words = word_manager.get_all_words()
            print("\n--- 单词列表 ---")
            for w in words:
                print(f"{w['word']:<15} {w['meaning'][:30]}")
        elif choice == '3':
            scheduler.review_words()
        elif choice == '4':
            keyword = input("搜索关键词: ").strip()
            results = word_manager.search_words(keyword)
            for w in results:
                print(f"{w['word']:<15} {w['meaning']}")
        elif choice == '5':
            word_text = input("要删除的单词: ").strip()
            if word_manager.delete_word(word_text):
                print("删除成功")
            else:
                print("未找到单词")
        elif choice == '6':
            stats = word_manager.get_statistics()
            print(f"\n--- 统计信息 ---")
            print(f"总单词数: {stats['total_words']}")
            print(f"已复习数: {stats['reviewed_words']}")
            print(f"掌握数: {stats['mastered_words']}")
        elif choice == '0':
            print("再见！")
            break

if __name__ == "__main__":
    main()
