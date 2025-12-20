#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本
用于测试各个模块的功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from word_manager import WordManager
from scheduler import Scheduler
from utils import show_menu, get_user_choice


def test_word_manager():
    """测试单词管理器"""
    print("=== 测试单词管理器 ===")
    
    # 创建临时数据文件进行测试
    manager = WordManager("../data/test_words.json")
    
    # 测试添加单词
    print("1. 测试添加单词...")
    test_word = "test"
    test_meaning = "测试"
    test_example = "This is a test."
    test_category = "学习"
    
    # 模拟添加单词的过程
    if test_word not in manager.words:
        manager.words[test_word] = {
            "meaning": test_meaning,
            "example": test_example,
            "category": test_category,
            "add_date": "2025-12-20T10:00:00",
            "last_reviewed": None,
            "next_review": None,
            "review_count": 0,
            "interval": 1,
            "difficulty": "normal"
        }
        print(f"   添加单词 '{test_word}' 成功")
    else:
        print(f"   单词 '{test_word}' 已存在")
    
    # 测试获取单词
    word_info = manager.get_word(test_word)
    if word_info:
        print(f"   获取单词信息成功: {word_info['meaning']}")
    else:
        print(f"   获取单词信息失败")
    
    # 测试搜索单词
    print("2. 测试搜索单词...")
    # 添加更多测试数据
    manager.words["example"] = {
        "meaning": "例子",
        "example": "This is an example.",
        "category": "学习",
        "add_date": "2025-12-20T10:00:00",
        "last_reviewed": None,
        "next_review": None,
        "review_count": 0,
        "interval": 1,
        "difficulty": "normal"
    }
    
    # 搜索包含"test"的单词
    found = False
    for word, info in manager.words.items():
        if "test" in word or "test" in info["meaning"]:
            print(f"   找到匹配单词: {word}")
            found = True
            break
    
    if not found:
        print("   未找到匹配单词")
    
    # 测试获取需要复习的单词
    print("3. 测试获取需要复习的单词...")
    review_words = manager.get_words_for_review()
    print(f"   需要复习的单词数量: {len(review_words)}")
    
    print("单词管理器测试完成!\n")


def test_scheduler():
    """测试调度器"""
    print("=== 测试调度器 ===")
    
    # 创建单词管理器和调度器
    manager = WordManager("../data/test_words.json")
    scheduler = Scheduler(manager)
    
    print("调度器初始化成功")
    print(f"艾宾浩斯记忆间隔: {scheduler.intervals}")
    
    print("调度器测试完成!\n")


def test_utils():
    """测试工具函数"""
    print("=== 测试工具函数 ===")
    
    # 测试菜单显示
    print("1. 测试菜单显示...")
    show_menu()
    
    print("工具函数测试完成!\n")


def main():
    """主测试函数"""
    print("开始测试单词记忆助手...")
    
    test_word_manager()
    test_scheduler()
    test_utils()
    
    print("所有测试完成!")


if __name__ == "__main__":
    main()