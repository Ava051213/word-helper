#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调度器模块
实现艾宾浩斯记忆曲线算法，安排单词复习时间
"""

import datetime
import random
from typing import List
from word_manager import WordManager


def calculate_next_review_interval(current_interval: int, is_correct: bool) -> int:
    """计算下次复习间隔
    
    Args:
        current_interval: 当前间隔天数
        is_correct: 是否回答正确
    
    Returns:
        下次复习间隔天数
    """
    if is_correct:
        # 回答正确，间隔时间乘以3
        return current_interval * 3
    else:
        # 回答错误，间隔时间重置为1天
        return 1


class Scheduler:
    """复习调度器"""
    
    def __init__(self, word_manager: WordManager):
        """初始化调度器"""
        self.word_manager = word_manager
        # 艾宾浩斯记忆间隔 (天)
        self.intervals = [1, 2, 4, 7, 15, 30]
    
    def review_words(self) -> None:
        """复习单词"""
        print("\n--- 单词复习 ---")
        
        # 获取需要复习的单词
        review_words = self.word_manager.get_words_for_review()
        
        if not review_words:
            print("暂无需要复习的单词。")
            return
        
        print(f"共有 {len(review_words)} 个单词需要复习。")
        
        # 随机打乱单词顺序
        random.shuffle(review_words)
        
        correct_count = 0
        total_count = len(review_words)
        
        for i, word in enumerate(review_words):
            info = self.word_manager.get_word(word)
            print(f"\n[{i+1}/{total_count}] 单词: {word}")
            print(f"释义: {info['meaning']}")
            if info.get('example'):
                print(f"例句: {info['example']}")
            
            # 获取用户反馈
            while True:
                feedback = input("是否认识这个单词? (y/n, q退出复习): ").strip().lower()
                if feedback in ['y', 'n', 'q']:
                    break
                print("请输入 y(认识)、n(不认识) 或 q(退出复习)")
            
            if feedback == 'q':
                print("退出复习模式。")
                break
            
            # 更新单词信息
            self._update_word_schedule(word, info, feedback == 'y')
            correct_count += 1 if feedback == 'y' else 0
        
        print(f"\n本次复习完成: {correct_count}/{total_count} 正确")
    
    def schedule_new_word(self, word: str) -> None:
        """为新单词安排复习计划"""
        info = self.word_manager.get_word(word)
        if info:
            now = datetime.datetime.now()
            # 设置初次复习时间为1天后
            next_review = now + datetime.timedelta(days=1)
            info['next_review'] = next_review.isoformat()
            info['interval'] = 1
            self.word_manager.update_word(word, info)
    
    def _update_word_schedule(self, word: str, info: dict, is_correct: bool) -> None:
        """更新单词的复习计划"""
        now = datetime.datetime.now()
        
        # 更新复习次数
        info['review_count'] = info.get('review_count', 0) + 1
        info['last_reviewed'] = now.isoformat()
        
        if is_correct:
            # 回答正确，延长复习间隔
            current_interval_idx = self.intervals.index(info['interval']) if info['interval'] in self.intervals else 0
            if current_interval_idx < len(self.intervals) - 1:
                next_interval = self.intervals[current_interval_idx + 1]
            else:
                next_interval = info['interval'] * 2  # 超出预设间隔后翻倍
        else:
            # 回答错误，缩短复习间隔
            next_interval = 1
        
        # 设置下次复习时间
        next_review = now + datetime.timedelta(days=next_interval)
        info['next_review'] = next_review.isoformat()
        info['interval'] = next_interval
        
        # 更新单词信息
        self.word_manager.update_word(word, info)