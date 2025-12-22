#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓冲字典API模块
通过缓存机制优化字典API的性能，减少网络请求次数
"""

import json
import logging
import os
import threading
import time
from collections import deque
from typing import Dict, Optional, List
from .dictionary_api import DictionaryAPI
from core.constants import Constants

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BufferedDictionaryAPI:
    """带缓存的字典API客户端"""
    
    def __init__(self, cache_file: str = "data/dictionary_cache.json", max_cache_size: int = 1000):
        """初始化缓冲字典API客户端
        
        Args:
            cache_file: 缓存文件路径
            max_cache_size: 最大缓存大小
        """
        self.dictionary_api = DictionaryAPI()
        self.cache_file = cache_file
        self.max_cache_size = max_cache_size
        self.cache = {}
        self.cache_lock = threading.Lock()
        
        # API请求限流
        self.request_times = deque(maxlen=10)  # 记录最近10次请求时间
        self.min_interval = Constants.API_RATE_LIMIT  # 最小间隔
        self.rate_limit_lock = threading.Lock()
        
        # 加载缓存
        self._load_cache()
        
        # 预加载队列
        self.preload_queue = []
        self.preload_thread = None
        self.preload_running = False
        
        # 统计信息
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0
        }
    
    def _load_cache(self):
        """从文件加载缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"成功加载缓存，共 {len(self.cache)} 个单词")
            else:
                # 创建缓存目录
                os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
                logger.info("缓存文件不存在，创建新缓存")
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with self.cache_lock:
                cache_copy = dict(self.cache)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_copy, f, ensure_ascii=False, indent=2)
            logger.info("缓存已保存")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _clean_cache(self):
        """清理缓存，保留最近使用的单词"""
        if len(self.cache) > self.max_cache_size:
            # 按访问时间排序，保留最近使用的单词
            sorted_items = sorted(self.cache.items(), 
                                key=lambda x: x[1].get('last_accessed', 0), 
                                reverse=True)
            self.cache = dict(sorted_items[:self.max_cache_size])
            logger.info(f"缓存已清理，保留 {len(self.cache)} 个单词")
    
    def _rate_limit_check(self):
        """API请求限流检查"""
        with self.rate_limit_lock:
            now = time.time()
            if self.request_times and now - self.request_times[-1] < self.min_interval:
                sleep_time = self.min_interval - (now - self.request_times[-1])
                time.sleep(sleep_time)
            self.request_times.append(time.time())
    
    def get_word_info(self, word: str) -> Optional[Dict]:
        """获取单词信息（带缓存和限流）
        
        Args:
            word: 要查询的单词
            
        Returns:
            包含单词信息的字典，如果查询失败则返回None
        """
        self.stats['total_requests'] += 1
        
        # 检查缓存
        cache_key = word.lower()
        with self.cache_lock:
            if cache_key in self.cache:
                # 更新访问时间
                self.cache[cache_key]['last_accessed'] = time.time()
                self.stats['cache_hits'] += 1
                logger.info(f"缓存命中: {word}")
                return self.cache[cache_key]['data']
        
        # 缓存未命中，从API获取（限流检查）
        self.stats['cache_misses'] += 1
        logger.info(f"缓存未命中，从API获取: {word}")
        
        # 限流检查
        self._rate_limit_check()
        
        word_info = self.dictionary_api.get_word_info(word)
        
        if word_info:
            # 保存到缓存
            with self.cache_lock:
                self.cache[cache_key] = {
                    'data': word_info,
                    'last_accessed': time.time(),
                    'cached_at': time.time()
                }
                self._clean_cache()
                # 异步保存缓存
                threading.Thread(target=self._save_cache, daemon=True).start()
        
        return word_info
    
    def get_random_words_info(self, count: int = 10, vocabulary_level: str = "cet6") -> List[Dict]:
        """获取随机单词的信息列表（带缓存优化）
        
        Args:
            count: 要获取的随机单词数量
            vocabulary_level: 词汇级别
            
        Returns:
            包含单词信息的字典列表
        """
        import random
        
        # 根据词汇级别选择对应的词汇文件
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        vocabulary_files = {
            "cet4": os.path.join(base_dir, "data", "cet4_words.txt"),
            "cet6": os.path.join(base_dir, "data", "cet6_words.txt"), 
            "gre": os.path.join(base_dir, "data", "gre_words.txt")
        }
        
        # 默认词汇级别为cet6
        if vocabulary_level not in vocabulary_files:
            logger.warning(f"未知的词汇级别: {vocabulary_level}，使用默认级别: cet6")
            vocabulary_level = "cet6"
        
        vocabulary_file = vocabulary_files[vocabulary_level]
        
        try:
            # 尝试读取指定级别的词汇文件
            with open(vocabulary_file, 'r', encoding='utf-8') as f:
                vocabulary_words = [line.strip() for line in f.readlines() if line.strip()]
            logger.info(f"成功加载 {vocabulary_level.upper()} 词汇，共 {len(vocabulary_words)} 个单词")
            
        except FileNotFoundError:
            # 如果找不到指定级别的词汇文件，尝试使用其他级别的文件作为备选
            logger.warning(f"未找到 {vocabulary_level.upper()} 词汇文件: {vocabulary_file}")
            
            # 备选方案：按优先级尝试其他词汇文件
            fallback_levels = ["cet6", "cet4", "gre"]
            vocabulary_words = None
            
            for level in fallback_levels:
                if level != vocabulary_level:
                    fallback_file = vocabulary_files[level]
                    try:
                        with open(fallback_file, 'r', encoding='utf-8') as f:
                            vocabulary_words = [line.strip() for line in f.readlines() if line.strip()]
                        logger.info(f"使用备选词汇级别: {level.upper()}，共 {len(vocabulary_words)} 个单词")
                        break
                    except FileNotFoundError:
                        continue
            
            # 如果所有词汇文件都找不到，使用默认词汇列表
            if vocabulary_words is None:
                logger.warning("未找到任何词汇文件，使用默认词汇列表")
                vocabulary_words = [
                    "ability", "able", "about", "above", "accept", "according", "account", "across", "act", "action"
                ]
        
        # 随机选择指定数量的单词
        selected_words = random.sample(vocabulary_words, min(count, len(vocabulary_words)))
        
        # 优化：先检查缓存中已有的单词
        cached_words = []
        uncached_words = []
        
        for word in selected_words:
            cache_key = word.lower()
            with self.cache_lock:
                if cache_key in self.cache:
                    self.cache[cache_key]['last_accessed'] = time.time()
                    cached_words.append(self.cache[cache_key]['data'])
                else:
                    uncached_words.append(word)
        
        # 并行获取未缓存的单词信息
        word_infos = cached_words.copy()
        
        if uncached_words:
            logger.info(f"需要从API获取 {len(uncached_words)} 个单词的信息")
            
            # 使用线程池并行获取
            import concurrent.futures
            
            def fetch_word_info(word):
                return self.get_word_info(word)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_word = {executor.submit(fetch_word_info, word): word for word in uncached_words}
                
                for future in concurrent.futures.as_completed(future_to_word):
                    word_info = future.result()
                    if word_info:
                        word_infos.append(word_info)
        
        return word_infos
    
    def start_preloading(self, words: List[str]):
        """开始预加载单词信息
        
        Args:
            words: 要预加载的单词列表
        """
        if self.preload_thread and self.preload_thread.is_alive():
            # 如果已有预加载线程在运行，停止它
            self.preload_running = False
            self.preload_thread.join(timeout=1.0)
        
        self.preload_queue = words.copy()
        self.preload_running = True
        self.preload_thread = threading.Thread(target=self._preload_worker, daemon=True)
        self.preload_thread.start()
        
        logger.info(f"开始预加载 {len(words)} 个单词")
    
    def stop_preloading(self):
        """停止预加载"""
        self.preload_running = False
        if self.preload_thread:
            self.preload_thread.join(timeout=1.0)
        logger.info("预加载已停止")
    
    def _preload_worker(self):
        """预加载工作线程"""
        while self.preload_running and self.preload_queue:
            word = self.preload_queue.pop(0)
            
            # 检查是否已在缓存中
            cache_key = word.lower()
            with self.cache_lock:
                if cache_key in self.cache:
                    continue
            
            # 预加载单词信息
            try:
                self.get_word_info(word)
                time.sleep(0.1)  # 避免过于频繁的请求
            except Exception as e:
                logger.error(f"预加载单词 '{word}' 时发生错误: {e}")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        stats = self.stats.copy()
        stats['cache_size'] = len(self.cache)
        stats['cache_hit_rate'] = (stats['cache_hits'] / stats['total_requests'] * 100 
                                  if stats['total_requests'] > 0 else 0)
        return stats
    
    def clear_cache(self):
        """清空缓存"""
        with self.cache_lock:
            self.cache.clear()
            try:
                if os.path.exists(self.cache_file):
                    os.remove(self.cache_file)
                logger.info("缓存已清空")
            except Exception as e:
                logger.error(f"清空缓存文件失败: {e}")


def demo():
    """演示函数"""
    api = BufferedDictionaryAPI()
    
    # 测试查询单词
    word = "hello"
    print(f"查询单词: {word}")
    info = api.get_word_info(word)
    
    if info:
        print(f"单词: {info['word']}")
        print(f"音标: {info['phonetic']}")
        print("英文释义:")
        for meaning in info["meanings"]:
            print(f"  {meaning['part_of_speech']}: {meaning['definition']}")
    
    # 测试缓存功能
    print("\n第二次查询（应该从缓存获取）:")
    info2 = api.get_word_info(word)
    
    # 显示统计信息
    stats = api.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"总请求数: {stats['total_requests']}")
    print(f"缓存命中: {stats['cache_hits']}")
    print(f"缓存未命中: {stats['cache_misses']}")
    print(f"缓存命中率: {stats['cache_hit_rate']:.1f}%")
    print(f"缓存大小: {stats['cache_size']}")


if __name__ == "__main__":
    demo()
