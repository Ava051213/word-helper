#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试随机单词生成性能的脚本
"""

import sys
import os
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from dictionary_api import DictionaryAPI

def test_performance():
    """测试随机单词生成性能"""
    print("测试随机单词生成性能...")
    
    # 初始化词典API
    api = DictionaryAPI()
    
    # 测试生成1个随机单词的性能
    print("\n测试生成1个随机单词:")
    start_time = time.time()
    
    random_words_info = api.get_random_words_info(1)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if random_words_info:
        word_info = random_words_info[0]
        print(f"单词: {word_info['word']}")
        print(f"耗时: {elapsed_time:.2f} 秒")
    else:
        print("未能获取随机单词信息")
        print(f"耗时: {elapsed_time:.2f} 秒")

def test_multiple_calls():
    """测试多次调用的性能"""
    print("\n测试多次调用性能:")
    
    # 初始化词典API
    api = DictionaryAPI()
    
    total_time = 0
    successful_calls = 0
    
    for i in range(5):
        print(f"第 {i+1} 次调用:")
        start_time = time.time()
        
        random_words_info = api.get_random_words_info(1)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        
        if random_words_info:
            word_info = random_words_info[0]
            print(f"  单词: {word_info['word']}")
            print(f"  耗时: {elapsed_time:.2f} 秒")
            successful_calls += 1
        else:
            print(f"  未能获取随机单词信息")
            print(f"  耗时: {elapsed_time:.2f} 秒")
    
    print(f"\n总计:")
    print(f"  成功调用次数: {successful_calls}/5")
    print(f"  平均耗时: {total_time/5:.2f} 秒")
    print(f"  总耗时: {total_time:.2f} 秒")

if __name__ == "__main__":
    test_performance()
    test_multiple_calls()