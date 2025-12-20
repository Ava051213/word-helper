#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CET-6词汇功能的脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from word_manager import WordManager
import random

def test_cet6_vocabulary():
    """测试CET-6词汇功能"""
    print("测试CET-6词汇功能...")
    
    # 初始化单词管理器
    word_manager = WordManager("data/words.json")
    
    # 测试生成随机单词
    print("\n生成10个随机单词:")
    random_words = word_manager.generate_random_words(10)
    
    if random_words:
        print(f"成功生成 {len(random_words)} 个随机单词:")
        for i, word in enumerate(random_words, 1):
            print(f"  {i}. {word}")
    else:
        print("未能生成随机单词")

def check_cet6_file():
    """检查CET-6词汇文件"""
    cet6_words_file = "data/cet6_words.txt"
    print(f"\n检查CET-6词汇文件: {cet6_words_file}")
    
    try:
        with open(cet6_words_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines() if line.strip()]
        
        print(f"成功读取CET-6词汇文件，共包含 {len(words)} 个单词")
        
        # 显示一些示例单词
        sample_words = random.sample(words, min(10, len(words)))
        print(f"示例单词: {', '.join(sample_words)}")
        
        # 检查是否包含一些典型的CET-6词汇
        cet6_examples = ['abandon', 'abdomen', 'abide', 'abnormal', 'abolish']
        found_examples = [word for word in cet6_examples if word in words]
        print(f"CET-6示例词汇检查: {found_examples}")
        
    except FileNotFoundError:
        print(f"未找到CET-6词汇文件 {cet6_words_file}")

def test_word_difficulty():
    """测试生成的单词难度"""
    print("\n测试生成的单词难度...")
    
    # 初始化单词管理器
    word_manager = WordManager("data/words.json")
    
    # 生成多个随机单词来评估难度
    print("生成50个随机单词以评估难度:")
    random_words = word_manager.generate_random_words(50)
    
    if random_words:
        print(f"成功生成 {len(random_words)} 个随机单词")
        
        # 统计单词长度分布（简单评估难度的一种方式）
        short_words = [w for w in random_words if len(w) <= 5]
        medium_words = [w for w in random_words if 6 <= len(w) <= 10]
        long_words = [w for w in random_words if len(w) > 10]
        
        print(f"短单词 (≤5字符): {len(short_words)} 个 ({len(short_words)/len(random_words)*100:.1f}%)")
        print(f"中等单词 (6-10字符): {len(medium_words)} 个 ({len(medium_words)/len(random_words)*100:.1f}%)")
        print(f"长单词 (>10字符): {len(long_words)} 个 ({len(long_words)/len(random_words)*100:.1f}%)")
        
        # 显示一些较长的单词作为示例
        if long_words:
            sample_long = random.sample(long_words, min(5, len(long_words)))
            print(f"长单词示例: {', '.join(sample_long)}")
    else:
        print("未能生成随机单词进行难度评估")

if __name__ == "__main__":
    check_cet6_file()
    test_cet6_vocabulary()
    test_word_difficulty()