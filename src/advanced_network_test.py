#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网络测试脚本
用于测试词典API在不同网络环境下的表现
"""

import time
import sys
import os
import threading
import requests
from unittest.mock import patch, MagicMock
import socket

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dictionary_api import DictionaryAPI


def simulate_network_delay(delay_seconds):
    """模拟网络延迟的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            time.sleep(delay_seconds)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def test_normal_conditions():
    """测试正常网络条件下的API表现"""
    print("\n=== 测试正常网络条件 ===")
    
    api = DictionaryAPI()
    start_time = time.time()
    word_info = api.get_word_info("hello")
    end_time = time.time()
    
    print(f"查询耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        print(f"成功获取单词信息: {word_info['word']}")
        return True
    else:
        print("未能获取单词信息")
        return False


def test_high_latency():
    """测试高延迟网络环境"""
    print("\n=== 测试高延迟网络环境 (模拟3秒延迟) ===")
    
    # 创建一个模拟高延迟的requests.get方法
    def delayed_get(*args, **kwargs):
        time.sleep(3)  # 模拟3秒延迟
        return requests.get(*args, **kwargs)
    
    api = DictionaryAPI()
    start_time = time.time()
    
    # 使用patch临时替换requests.get方法
    with patch('requests.get', side_effect=delayed_get):
        word_info = api.get_word_info("hello")
    
    end_time = time.time()
    
    print(f"查询耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        print(f"成功获取单词信息: {word_info['word']}")
        return True
    else:
        print("未能获取单词信息")
        return False


def test_timeout_condition():
    """测试超时情况"""
    print("\n=== 测试超时情况 (模拟15秒延迟, 超过10秒超时设置) ===")
    
    # 创建一个模拟超时的requests.get方法
    def timeout_get(*args, **kwargs):
        time.sleep(15)  # 超过10秒的超时设置
        return requests.get(*args, **kwargs)
    
    api = DictionaryAPI()
    start_time = time.time()
    
    # 使用patch临时替换requests.get方法
    with patch('requests.get', side_effect=timeout_get):
        word_info = api.get_word_info("hello")
    
    end_time = time.time()
    
    print(f"查询耗时: {end_time - start_time:.2f} 秒")
    if word_info is None:
        print("正确处理了超时情况")
        return True
    else:
        print("未能正确处理超时")
        return False


def test_connection_error():
    """测试连接错误情况"""
    print("\n=== 测试连接错误情况 ===")
    
    # 创建一个模拟连接错误的requests.get方法
    def connection_error_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError("模拟网络连接错误")
    
    api = DictionaryAPI()
    
    # 使用patch临时替换requests.get方法
    with patch('requests.get', side_effect=connection_error_get):
        word_info = api.get_word_info("hello")
    
    if word_info is None:
        print("正确处理了连接错误")
        return True
    else:
        print("未能正确处理连接错误")
        return False


def test_slow_bandwidth():
    """测试低带宽环境（通过限制响应大小）"""
    print("\n=== 测试低带宽环境 ===")
    
    # 创建一个模拟大数据响应的方法
    def slow_response_get(*args, **kwargs):
        # 模拟一个大的响应需要较长时间来传输
        response = MagicMock()
        response.status_code = 200
        # 模拟一个较大的JSON响应
        large_data = [{
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
                            "synonyms": []
                        }
                    ] * 50  # 多个定义来模拟大数据
                }
            ] * 20  # 多个词性来模拟大数据
        }]
        response.json.return_value = large_data
        time.sleep(2)  # 模拟传输时间
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    # 使用patch临时替换requests.get方法
    with patch('requests.get', side_effect=slow_response_get):
        word_info = api.get_word_info("hello")
    
    end_time = time.time()
    
    print(f"查询耗时: {end_time - start_time:.2f} 秒")
    if word_info:
        print(f"成功获取单词信息: {word_info['word']}")
        print(f"释义数量: {len(word_info['meanings'])}")
        return True
    else:
        print("未能获取单词信息")
        return False


def main():
    """主函数"""
    print("词典API网络环境测试工具")
    print("=" * 40)
    
    results = []
    
    # 测试正常网络条件
    results.append(("正常网络条件", test_normal_conditions()))
    
    # 测试高延迟
    results.append(("高延迟网络", test_high_latency()))
    
    # 测试超时
    results.append(("超时情况", test_timeout_condition()))
    
    # 测试连接错误
    results.append(("连接错误", test_connection_error()))
    
    # 测试低带宽
    results.append(("低带宽环境", test_slow_bandwidth()))
    
    # 输出总结
    print("\n" + "=" * 40)
    print("测试结果总结:")
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"  {test_name}: {status}")


if __name__ == "__main__":
    main()