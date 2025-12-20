#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络中断恢复测试脚本
测试API在网络中断情况下的恢复能力
"""

import time
import sys
import os
import requests
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dictionary_api import DictionaryAPI


def test_network_interruption_recovery():
    """测试网络中断后的恢复能力"""
    print("=== 网络中断恢复测试 ===")
    
    # 模拟网络中断后恢复的情况
    call_count = 0
    
    def intermittent_failure_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        # 第一次调用模拟网络中断
        if call_count == 1:
            raise requests.exceptions.ConnectionError("模拟网络中断")
        
        # 第二次调用正常返回
        time.sleep(0.05)  # 很短的真实延迟
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [{
            "word": args[0].split('/')[-1],
            "phonetic": "/rɪˈkʌvər/",
            "meanings": [
                {
                    "partOfSpeech": "verb",
                    "definitions": [
                        {
                            "definition": "Return to a normal state of health, mind, or strength.",
                            "example": "The economy began to recover."
                        }
                    ]
                }
            ]
        }]
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=intermittent_failure_get):
        # 第一次尝试（应该失败）
        word_info_first = api.get_word_info("recover")
        
        # 第二次尝试（应该成功）
        word_info_second = api.get_word_info("recover")
    
    end_time = time.time()
    
    print(f"两次请求总耗时: {end_time - start_time:.2f} 秒")
    print(f"第一次请求结果: {'成功' if word_info_first else '失败'}")
    print(f"第二次请求结果: {'成功' if word_info_second else '失败'}")
    
    if word_info_first is None and word_info_second:
        print("✅ 正确处理了网络中断并成功恢复")
        return True
    else:
        print("❌ 未能正确处理网络中断恢复")
        return False


def test_retry_mechanism():
    """测试重试机制"""
    print("\n=== 重试机制测试 ===")
    
    # 模拟多次失败后成功的场景
    call_count = 0
    
    def retry_scenario_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        # 前两次调用模拟网络问题
        if call_count <= 2:
            raise requests.exceptions.ConnectionError(f"模拟网络问题 #{call_count}")
        
        # 第三次调用正常返回
        time.sleep(0.05)  # 很短的真实延迟
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [{
            "word": args[0].split('/')[-1],
            "phonetic": "/rɪˈtraɪ/",
            "meanings": [
                {
                    "partOfSpeech": "verb",
                    "definitions": [
                        {
                            "definition": "Make another attempt to achieve something.",
                            "example": "He retried the operation."
                        }
                    ]
                }
            ]
        }]
        return response
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=retry_scenario_get):
        word_info = api.get_word_info("retry")
    
    end_time = time.time()
    
    print(f"重试过程总耗时: {end_time - start_time:.2f} 秒")
    print(f"总共尝试了 {call_count} 次")
    
    if word_info and call_count == 3:
        print("✅ 成功实现了重试机制")
        return True
    else:
        print("❌ 重试机制未按预期工作")
        return False


def test_persistent_network_failure():
    """测试持续网络故障的处理"""
    print("\n=== 持续网络故障处理测试 ===")
    
    def persistent_failure_get(*args, **kwargs):
        # 持续模拟网络故障
        raise requests.exceptions.ConnectionError("持续网络故障")
    
    api = DictionaryAPI()
    start_time = time.time()
    
    with patch('requests.get', side_effect=persistent_failure_get):
        word_info = api.get_word_info("failure")
    
    end_time = time.time()
    
    print(f"处理耗时: {end_time - start_time:.2f} 秒")
    
    if word_info is None:
        print("✅ 正确处理了持续网络故障")
        return True
    else:
        print("❌ 未能正确处理持续网络故障")
        return False


def main():
    """主函数"""
    print("网络中断恢复能力测试")
    print("=" * 22)
    
    results = []
    
    # 运行各项测试
    results.append(("网络中断恢复", test_network_interruption_recovery()))
    results.append(("重试机制", test_retry_mechanism()))
    results.append(("持续故障处理", test_persistent_network_failure()))
    
    # 输出总结
    print("\n" + "=" * 22)
    print("测试结果总结:")
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"  {test_name}: {status}")
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    print(f"\n总体评估: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("✅ API在网络中断情况下具有良好的恢复能力")
    else:
        print("❌ API在网络中断恢复方面存在问题")


if __name__ == "__main__":
    main()