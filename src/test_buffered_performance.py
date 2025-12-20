#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试模块
用于测试带缓冲区和不带缓冲区的随机单词生成性能对比
"""

import time
import threading
from typing import List, Dict
from dictionary_api import DictionaryAPI
from buffered_dictionary_api import BufferedDictionaryAPI


def test_performance_without_buffer(count: int = 5) -> float:
    """
    测试不带缓冲区的随机单词生成性能
    
    Args:
        count: 要获取的随机单词数量
        
    Returns:
        执行时间（秒）
    """
    api = DictionaryAPI()
    
    start_time = time.time()
    try:
        random_words_info = api.get_random_words_info(count)
        if not random_words_info:
            print(f"未能获取到 {count} 个随机单词")
    except Exception as e:
        print(f"获取随机单词时发生错误: {e}")
    
    end_time = time.time()
    return end_time - start_time


def test_performance_with_buffer(buffered_api: BufferedDictionaryAPI, count: int = 5) -> float:
    """
    测试带缓冲区的随机单词生成性能
    
    Args:
        buffered_api: 带缓冲区的词典API实例
        count: 要获取的随机单词数量
        
    Returns:
        执行时间（秒）
    """
    start_time = time.time()
    try:
        random_words_info = buffered_api.get_random_words_info(count)
        if not random_words_info:
            print(f"未能获取到 {count} 个随机单词")
    except Exception as e:
        print(f"从缓冲区获取随机单词时发生错误: {e}")
    
    end_time = time.time()
    return end_time - start_time


def test_concurrent_performance_without_buffer(thread_count: int = 3, words_per_thread: int = 3) -> List[float]:
    """
    测试不带缓冲区的并发随机单词生成性能
    
    Args:
        thread_count: 并发线程数量
        words_per_thread: 每个线程获取的单词数量
        
    Returns:
        各线程的执行时间列表
    """
    def worker(results: List[float], index: int):
        duration = test_performance_without_buffer(words_per_thread)
        results[index] = duration
    
    threads = []
    results = [0.0] * thread_count
    
    # 创建并启动线程
    for i in range(thread_count):
        thread = threading.Thread(target=worker, args=(results, i))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    return results


def test_concurrent_performance_with_buffer(buffered_api: BufferedDictionaryAPI, thread_count: int = 3, 
                                          words_per_thread: int = 3) -> List[float]:
    """
    测试带缓冲区的并发随机单词生成性能
    
    Args:
        buffered_api: 带缓冲区的词典API实例
        thread_count: 并发线程数量
        words_per_thread: 每个线程获取的单词数量
        
    Returns:
        各线程的执行时间列表
    """
    def worker(results: List[float], index: int):
        duration = test_performance_with_buffer(buffered_api, words_per_thread)
        results[index] = duration
    
    threads = []
    results = [0.0] * thread_count
    
    # 创建并启动线程
    for i in range(thread_count):
        thread = threading.Thread(target=worker, args=(results, i))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    return results


def test_performance():
    """测试随机单词生成性能"""
    print("测试随机单词生成性能...")
    
    # 创建带缓冲区的词典API实例
    buffered_api = BufferedDictionaryAPI(buffer_size=10, preload_count=5)
    
    # 等待缓冲区预加载
    print("等待缓冲区预加载...")
    time.sleep(2)
    print(f"初始缓冲区大小: {buffered_api.buffer_queue.qsize()}")
    
    # 测试单次获取性能
    print("\n=== 单次获取性能测试 ===")
    
    # 测试不带缓冲区的性能
    print("\n测试不带缓冲区获取5个随机单词:")
    duration_without_buffer = test_performance_without_buffer(5)
    print(f"耗时: {duration_without_buffer:.2f} 秒")
    
    # 测试带缓冲区的性能
    print("\n测试带缓冲区获取5个随机单词:")
    duration_with_buffer = test_performance_with_buffer(buffered_api, 5)
    print(f"耗时: {duration_with_buffer:.2f} 秒")
    
    # 计算性能提升
    if duration_without_buffer > 0:
        improvement = (duration_without_buffer - duration_with_buffer) / duration_without_buffer * 100
        print(f"性能提升: {improvement:.1f}%")
    
    # 测试并发性能
    print("\n=== 并发性能测试 ===")
    
    # 测试不带缓冲区的并发性能
    print("\n测试不带缓冲区3个并发线程，每个线程获取3个随机单词:")
    concurrent_times_without_buffer = test_concurrent_performance_without_buffer(3, 3)
    avg_time_without_buffer = sum(concurrent_times_without_buffer) / len(concurrent_times_without_buffer)
    print(f"各线程耗时: {[f'{t:.2f}s' for t in concurrent_times_without_buffer]}")
    print(f"平均耗时: {avg_time_without_buffer:.2f} 秒")
    
    # 测试带缓冲区的并发性能
    print("\n测试带缓冲区3个并发线程，每个线程获取3个随机单词:")
    concurrent_times_with_buffer = test_concurrent_performance_with_buffer(buffered_api, 3, 3)
    avg_time_with_buffer = sum(concurrent_times_with_buffer) / len(concurrent_times_with_buffer)
    print(f"各线程耗时: {[f'{t:.2f}s' for t in concurrent_times_with_buffer]}")
    print(f"平均耗时: {avg_time_with_buffer:.2f} 秒")
    
    # 计算并发性能提升
    if avg_time_without_buffer > 0:
        concurrent_improvement = (avg_time_without_buffer - avg_time_with_buffer) / avg_time_without_buffer * 100
        print(f"并发性能提升: {concurrent_improvement:.1f}%")
    
    # 停止缓冲区预加载线程
    buffered_api.stop()
    
    print("\n性能测试完成!")


if __name__ == "__main__":
    test_performance()