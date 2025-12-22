#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调度器模块
实现 SM-2 算法调度逻辑
"""

import datetime
import random
import logging
from typing import List
from .word_manager import WordManager

logger = logging.getLogger(__name__)

class Scheduler:
    """复习调度器"""
    
    def __init__(self, word_manager: WordManager):
        """初始化调度器"""
        self.word_manager = word_manager
    
    def review_words(self) -> None:
        """CLI复习逻辑"""
        print("\n--- 单词复习 (SM-2 模式) ---")
        
        # 获取需要复习的单词
        review_words = self.word_manager.get_words_for_review()
        
        if not review_words:
            print("目前没有需要复习的单词。")
            return
        
        print(f"共有 {len(review_words)} 个单词需要复习。")
        
        # 随机打乱单词顺序
        random.shuffle(review_words)
        
        total_count = len(review_words)
        
        for i, word_text in enumerate(review_words):
            info = self.word_manager.get_word(word_text)
            print(f"\n[{i+1}/{total_count}] 单词: {word_text}")
            if info.get('phonetic'):
                print(f"音标: [{info['phonetic']}]")
            
            input("按回车显示释义...")
            print(f"释义: {info['meaning']}")
            if info.get('example'):
                print(f"例句: {info['example']}")
            
            # 获取用户反馈 (0-5)
            print("\n请评估记忆程度:")
            print("5: 非常容易 (秒答)")
            print("4: 比较容易 (短暂思考后想起)")
            print("3: 一般 (费劲想起)")
            print("2: 困难 (看了释义才想起)")
            print("1: 模糊 (觉得眼熟但想不起释义)")
            print("0: 完全忘记")
            
            while True:
                choice = input("评分 (0-5, q退出): ").strip().lower()
                if choice == 'q':
                    print("已中途退出复习。")
                    return
                if choice in ['0', '1', '2', '3', '4', '5']:
                    quality = int(choice)
                    break
                print("无效输入，请输入 0-5 之间的数字")
            
            # 更新复习状态
            self.word_manager.update_review_status(word_text, quality)
        
        print(f"\n本次复习任务已全部完成！")

    def schedule_new_word(self, word: str) -> None:
        """为新单词安排复习计划 (在 WordManager.add_word_direct 中已处理)"""
        pass
