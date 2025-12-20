#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
低带宽环境测试脚本
测试API在低带宽环境下的性能表现
"""

import time
import sys
import os
import requests
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dictionary_api import DictionaryAPI


def test_large_response_handling():
    """测试大响应数据处理"""
    print("=== 大响应数据处理测试 ===")
    
    # 创建非常大的响应数据来模拟低带宽下的大数据传输
    large_meanings = []
    for i in range(100):  # 创建大量释义
        large_meanings.append({
            "partOfSpeech": "noun" if i % 2 == 0 else "verb",
            "definitions": [
                {
                    "definition": f"This is a sample definition number {i} for testing purposes.",
                    "example": f"This is a sample example sentence number {i} for testing large data handling.",
                    "synonyms": [f"synonym_{i}_1", f"synonym_{i}_2", f"synonym_{i}_3"]
                }
            ]
        })
    
    large_response_data = [{
        "word": "bandwidth",
        "phonetic": "/ˈbændwɪdθ/",
        "phonetics": [{"text": "/ˈbændwɪdθ/", "audio": ""}],
        "meanings": large_meanings,
        "sourceUrls": ["https://example.com"] * 50  # 添加大量URL
    }]
    
    def large_data_get(*args, **kwargs):
        time.sleep(0.1)  # 模拟传输延迟
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = large_response_data
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=large_data_get):
        word_info = api.get_word_info("bandwidth")
    
    end_time = time.time()
    
    print(f"处理大响应数据耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        meanings_count = len(word_info['meanings'])
        print(f"✅ 成功处理包含 {meanings_count} 个释义的大响应数据")
        return True
    else:
        print("❌ 未能处理大响应数据")
        return False


def test_small_response_performance():
    """测试小响应数据性能"""
    print("\n=== 小响应数据性能测试 ===")
    
    # 创建最小化的响应数据
    minimal_response_data = [{
        "word": "fast",
        "phonetic": "/fæst/",
        "meanings": [
            {
                "partOfSpeech": "adjective",
                "definitions": [
                    {
                        "definition": "Moving or capable of moving at high speed.",
                        "example": "The train was fast."
                    }
                ]
            }
        ]
    }]
    
    def minimal_data_get(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = minimal_response_data
        return response
    
    api = DictionaryAPI()
    
    # 多次执行测试性能
    start_time = time.time()
    results = []
    
    with patch('requests.get', side_effect=minimal_data_get):
        for i in range(10):  # 执行10次请求
            word_info = api.get_word_info("fast")
            results.append(word_info is not None)
    
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / 10
    
    print(f"10次请求总耗时: {total_time:.2f} 秒")
    print(f"平均每次请求耗时: {avg_time:.3f} 秒")
    
    successful_requests = sum(results)
    if successful_requests == 10:
        print("✅ 成功处理所有小响应数据请求")
        return True
    else:
        print(f"❌ 有 {10 - successful_requests} 个请求失败")
        return False


def test_memory_usage_with_large_data():
    """测试处理大数据时的内存使用情况"""
    print("\n=== 大数据内存使用测试 ===")
    
    # 创建极端大的响应数据
    extreme_meanings = []
    for i in range(500):  # 创建500个释义
        extreme_meanings.append({
            "partOfSpeech": "noun",
            "definitions": [
                {
                    "definition": f"Definition {i}: " + "This is a very long definition text that would consume more memory when processed. " * 10,
                    "example": f"Example {i}: " + "This is a very long example sentence that would also consume more memory when processed. " * 10,
                    "synonyms": [f"syn_{i}_{j}" for j in range(20)]  # 每个释义有20个同义词
                }
            ]
        })
    
    extreme_response_data = [{
        "word": "memory",
        "phonetic": "/ˈmeməri/",
        "phonetics": [{"text": "/ˈmeməri/", "audio": ""}] * 10,  # 多个音标
        "meanings": extreme_meanings,
        "sourceUrls": ["https://example.com/very/long/url/path/that/consumes/memory"] * 100
    }]
    
    def extreme_data_get(*args, **kwargs):
        time.sleep(0.2)  # 模拟更大的传输延迟
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = extreme_response_data
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=extreme_data_get):
        word_info = api.get_word_info("memory")
    
    end_time = time.time()
    
    print(f"处理极端大数据耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        meanings_count = len(word_info['meanings'])
        print(f"✅ 成功处理包含 {meanings_count} 个释义的极端大数据")
        return True
    else:
        print("❌ 未能处理极端大数据")
        return False


def main():
    """主函数"""
    print("低带宽环境性能测试")
    print("=" * 20)
    
    results = []
    
    # 运行各项测试
    results.append(("大响应数据处理", test_large_response_handling()))
    results.append(("小响应数据性能", test_small_response_performance()))
    results.append(("大数据内存使用", test_memory_usage_with_large_data()))
    
    # 输出总结
    print("\n" + "=" * 20)
    print("测试结果总结:")
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"  {test_name}: {status}")
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    print(f"\n总体评估: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("✅ API在低带宽环境下表现良好")
    else:
        print("❌ API在低带宽环境下存在问题")


if __name__ == "__main__":
    main()