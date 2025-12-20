#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典API测试脚本
用于测试词典API在不同网络环境下的表现
"""

import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dictionary_api import DictionaryAPI


def test_word_lookup(word):
    """测试单词查询功能"""
    print(f"\n=== 测试查询单词: {word} ===")
    
    start_time = time.time()
    api = DictionaryAPI()
    word_info = api.get_word_info(word)
    end_time = time.time()
    
    print(f"查询耗时: {end_time - start_time:.2f} 秒")
    
    if word_info:
        print(f"单词: {word_info['word']}")
        if word_info['phonetic']:
            print(f"音标: {word_info['phonetic']}")
        if word_info['meanings']:
            print("释义:")
            for i, meaning_info in enumerate(word_info['meanings'][:3]):
                print(f"  {i+1}. {meaning_info['part_of_speech']}: {meaning_info['definition']}")
        if word_info['examples']:
            print("例句:")
            for i, ex in enumerate(word_info['examples'][:2]):
                print(f"  {i+1}. {ex}")
    else:
        print(f"未找到单词 '{word}' 的定义")


def main():
    """主函数"""
    print("词典API测试工具")
    print("=" * 30)
    
    # 测试常见单词
    test_words = [
        "hello",
        "world",
        "computer",
        "python",
        "dictionary",
        "nonexistentword123"  # 测试不存在的单词
    ]
    
    for word in test_words:
        test_word_lookup(word)
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()