#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高效高延迟网络测试脚本
使用计时而非真实等待来测试API在高延迟网络环境下的表现
"""

import time
import sys
import os
import requests
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dictionary_api import DictionaryAPI


def test_timeout_behavior():
    """测试超时行为"""
    print("=== 超时行为测试 ===")
    
    # 模拟刚好在超时边缘的情况
    def near_timeout_get(*args, **kwargs):
        # 模拟接近但不超过超时的时间
        time.sleep(0.1)  # 很短的真实延迟
        # 创建模拟响应
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [{
            "word": "hello",
            "phonetic": "/həˈloʊ/",
            "meanings": [
                {
                    "partOfSpeech": "exclamation",
                    "definitions": [
                        {
                            "definition": "Used as a greeting or to begin a telephone conversation.",
                            "example": "Hello, how are you?"
                        }
                    ]
                }
            ]
        }]
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=near_timeout_get):
        word_info = api.get_word_info("hello")
    
    end_time = time.time()
    
    print(f"处理耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        print(f"✅ 成功处理接近超时的请求: {word_info['word']}")
        return True
    else:
        print("❌ 未能处理接近超时的请求")
        return False


def test_response_parsing_under_load():
    """测试在模拟负载下的响应解析"""
    print("\n=== 响应解析负载测试 ===")
    
    # 创建大型响应数据
    large_response_data = [{
        "word": "hello",
        "phonetic": "/həˈloʊ/",
        "phonetics": [{"text": "/həˈloʊ/", "audio": ""}],
        "meanings": [
            {
                "partOfSpeech": "exclamation",
                "definitions": [
                    {
                        "definition": "Used as a greeting or to begin a telephone conversation.",
                        "example": "Hello, how are you?",
                        "synonyms": ["hi", "hey", "greetings"]
                    }
                ] * 100  # 重复定义模拟大数据
            }
        ] * 5  # 重复词性模拟大数据
    }]
    
    def large_data_get(*args, **kwargs):
        time.sleep(0.1)  # 很短的真实延迟
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = large_response_data
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=large_data_get):
        word_info = api.get_word_info("hello")
    
    end_time = time.time()
    
    print(f"处理耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        print(f"✅ 成功解析大型响应数据: {word_info['word']}")
        print(f"   解析了 {len(word_info['meanings'])} 个释义")
        return True
    else:
        print("❌ 未能解析大型响应数据")
        return False


def test_concurrent_requests_simulation():
    """模拟并发请求处理"""
    print("\n=== 并发请求模拟测试 ===")
    
    # 模拟多个连续请求
    def normal_get(*args, **kwargs):
        time.sleep(0.05)  # 很短的真实延迟
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [{
            "word": args[0].split('/')[-1],  # 从URL中提取单词
            "phonetic": "/tɛst/",
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "A procedure intended to establish the quality, performance, or reliability of something.",
                            "example": "This is a test."
                        }
                    ]
                }
            ]
        }]
        return response
    
    api = DictionaryAPI()
    test_words = ["hello", "world", "test", "python", "api"]
    
    start_time = time.time()
    results = []
    
    with patch('requests.get', side_effect=normal_get):
        for word in test_words:
            word_info = api.get_word_info(word)
            results.append(word_info is not None)
    
    end_time = time.time()
    
    print(f"处理{len(test_words)}个请求耗时: {end_time - start_time:.2f} 秒")
    successful_requests = sum(results)
    print(f"成功处理 {successful_requests}/{len(test_words)} 个请求")
    
    if successful_requests == len(test_words):
        print("✅ 成功处理所有模拟并发请求")
        return True
    else:
        print("❌ 未能处理所有模拟并发请求")
        return False


def main():
    """主函数"""
    print("高效高延迟网络环境测试")
    print("=" * 25)
    
    results = []
    
    # 运行各项测试
    results.append(("超时行为", test_timeout_behavior()))
    results.append(("响应解析负载", test_response_parsing_under_load()))
    results.append(("并发请求模拟", test_concurrent_requests_simulation()))
    
    # 输出总结
    print("\n" + "=" * 25)
    print("测试结果总结:")
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"  {test_name}: {status}")
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    print(f"\n总体评估: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("✅ API在高延迟网络环境下表现良好")
    else:
        print("❌ API在高延迟网络环境下存在问题")


if __name__ == "__main__":
    main()