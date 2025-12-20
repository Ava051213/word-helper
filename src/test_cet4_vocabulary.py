#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CET-4词汇功能的脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from dictionary_api import DictionaryAPI
import random

def test_cet4_vocabulary():
    """测试CET-4词汇功能"""
    print("测试CET-4词汇功能...")
    
    # 初始化词典API
    api = DictionaryAPI()
    
    # 测试获取随机单词信息
    print("\n获取1个随机单词的详细信息:")
    random_words_info = api.get_random_words_info(1)
    
    if random_words_info:
        word_info = random_words_info[0]
        print(f"单词: {word_info['word']}")
        print(f"音标: {word_info['phonetic']}")
        print("英文释义:")
        for meaning in word_info["meanings"][:3]:  # 只显示前3个释义
            print(f"  {meaning['part_of_speech']}: {meaning['definition']}")
        
        # 显示中文释义（如果有的话）
        if word_info["chinese_meanings"]:
            print("中文释义:")
            for meaning in word_info["chinese_meanings"][:3]:  # 只显示前3个释义
                print(f"  {meaning['part_of_speech']}: {meaning['definition']}")
        
        # 显示例句
        if word_info["examples"]:
            print("例句:")
            for example in word_info["examples"][:2]:  # 只显示前2个例句
                print(f"  {example}")
    else:
        print("未能获取随机单词信息")

def check_cet4_file():
    """检查CET-4词汇文件"""
    cet4_words_file = "data/cet4_words.txt"
    print(f"\n检查CET-4词汇文件: {cet4_words_file}")
    
    try:
        with open(cet4_words_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines() if line.strip()]
        
        print(f"成功读取CET-4词汇文件，共包含 {len(words)} 个单词")
        
        # 显示一些示例单词
        sample_words = random.sample(words, min(10, len(words)))
        print(f"示例单词: {', '.join(sample_words)}")
        
        # 检查是否包含一些典型的CET-4词汇
        cet4_examples = ['abandon', 'ability', 'academic', 'achieve', 'acquire']
        found_examples = [word for word in cet4_examples if word in words]
        print(f"CET-4示例词汇检查: {found_examples}")
        
    except FileNotFoundError:
        print(f"未找到CET-4词汇文件 {cet4_words_file}")

if __name__ == "__main__":
    check_cet4_file()
    test_cet4_vocabulary()