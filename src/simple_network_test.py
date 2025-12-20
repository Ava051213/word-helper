#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版网络测试脚本
用于快速测试词典API在不同网络环境下的表现
"""

import time
import sys
import os
import requests
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dictionary_api import DictionaryAPI


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


def test_timeout_scenario():
    """测试超时处理"""
    print("\n=== 测试超时处理 ===")
    
    api = DictionaryAPI()
    
    # 使用mock模拟超时
    with patch('requests.get', side_effect=requests.exceptions.Timeout("模拟超时")):
        start_time = time.time()
        word_info = api.get_word_info("hello")
        end_time = time.time()
    
    print(f"处理耗时: {end_time - start_time:.2f} 秒")
    if word_info is None:
        print("正确处理了超时情况")
        return True
    else:
        print("未能正确处理超时")
        return False


def test_connection_error():
    """测试连接错误处理"""
    print("\n=== 测试连接错误处理 ===")
    
    api = DictionaryAPI()
    
    # 使用mock模拟连接错误
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("模拟连接错误")):
        word_info = api.get_word_info("hello")
    
    if word_info is None:
        print("正确处理了连接错误")
        return True
    else:
        print("未能正确处理连接错误")
        return False


def test_invalid_response():
    """测试无效响应处理"""
    print("\n=== 测试无效响应处理 ===")
    
    api = DictionaryAPI()
    
    # 使用mock模拟无效JSON响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("模拟JSON解析错误")
    
    with patch('requests.get', return_value=mock_response):
        word_info = api.get_word_info("hello")
    
    if word_info is None:
        print("正确处理了无效响应")
        return True
    else:
        print("未能正确处理无效响应")
        return False


def main():
    """主函数"""
    print("词典API网络环境快速测试工具")
    print("=" * 35)
    
    results = []
    
    # 运行各项测试
    results.append(("正常网络条件", test_normal_conditions()))
    results.append(("超时处理", test_timeout_scenario()))
    results.append(("连接错误处理", test_connection_error()))
    results.append(("无效响应处理", test_invalid_response()))
    
    # 输出总结
    print("\n" + "=" * 35)
    print("测试结果总结:")
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"  {test_name}: {status}")
    
    # 总体评估
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    print(f"\n总体评估: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("✅ 所有网络环境测试均已通过，API具有良好的容错性")
    else:
        print("❌ 部分测试未通过，请检查API的错误处理机制")


if __name__ == "__main__":
    main()