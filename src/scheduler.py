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
    """计算下次复习间隔（基于标准艾宾浩斯遗忘曲线）
    
    Args:
        current_interval: 当前间隔天数
        is_correct: 是否回答正确
    
    Returns:
        下次复习间隔天数
    """
    # 标准艾宾浩斯遗忘曲线间隔（天）
    eb_intervals = [1, 2, 4, 7, 15, 30]
    
    if is_correct:
        # 回答正确，按标准艾宾浩斯曲线递进到下一个间隔
        try:
            current_idx = eb_intervals.index(current_interval)
            if current_idx < len(eb_intervals) - 1:
                return eb_intervals[current_idx + 1]
            else:
                # 超出预设间隔后，按指数增长（乘以2）
                return current_interval * 2
        except ValueError:
            # 如果当前间隔不在标准列表中，按指数增长
            return current_interval * 2
    else:
        # 回答错误，重置为1天
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
            # 新单词立即可以复习，设置next_review为当前时间
            # 这样新单词会被get_words_for_review方法正确识别
            info['next_review'] = now.isoformat()
            info['interval'] = 1
            info['review_count'] = 0  # 确保新单词的复习次数为0
            self.word_manager.update_word(word, info)
    
    def _update_word_schedule(self, word: str, info: dict, is_correct: bool) -> None:
        """更新单词的复习计划"""
        now = datetime.datetime.now()
        
        # 更新复习次数
        info['review_count'] = info.get('review_count', 0) + 1
        info['last_reviewed'] = now.isoformat()
        
        # 使用标准艾宾浩斯遗忘曲线计算下次复习间隔
        current_interval = info.get('interval', 1)
        next_interval = calculate_next_review_interval(current_interval, is_correct)
        
        # 设置下次复习时间
        next_review = now + datetime.timedelta(days=next_interval)
        info['next_review'] = next_review.isoformat()
        info['interval'] = next_interval
        
        # 更新单词信息
        self.word_manager.update_word(word, info)