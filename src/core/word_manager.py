#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词管理模块 (Facade 模式)
通过委托给具体的 Service 层实现业务逻辑，保持向后兼容性
"""

import logging
from typing import Dict, List, Optional

from .database import Database
from services.word_service import WordService
from services.review_service import ReviewService
from services.stats_service import StatsService
from services.dictionary_service import DictionaryService
from services.tts_service import TTSService

logger = logging.getLogger(__name__)

class WordManager:
    """单词管理器 (Facade)"""
    
    def __init__(self, db_path: str = None):
        """初始化单词管理器，并注入具体服务"""
        self.db = Database(db_path)
        
        # 实例化各个服务
        self.word_service = WordService(self.db)
        self.review_service = ReviewService(self.db)
        self.stats_service = StatsService(self.db)
        self.dict_service = DictionaryService(self.db)
        self.tts_service = TTSService()
        
        # 为了兼容旧代码，保留 dictionary_api 引用
        self.dictionary_api = self.dict_service.dictionary_api
    
    def speak(self, text: str):
        """语音播放"""
        self.tts_service.speak(text)
    
    def add_word_direct(self, word_text: str, meaning: str, example: str = "", phonetic: str = "") -> bool:
        """委托给 WordService"""
        return self.word_service.add_word(word_text, meaning, example, phonetic)

    def delete_word(self, word_text: str) -> bool:
        """委托给 WordService"""
        return self.word_service.delete_word(word_text)

    def update_word(self, word_text: str, **kwargs) -> bool:
        """委托给 WordService"""
        return self.word_service.update_word(word_text, **kwargs)

    def get_word(self, word_text: str) -> Optional[Dict]:
        """委托给 WordService"""
        return self.word_service.get_word(word_text)

    def get_all_words(self) -> List[Dict]:
        """委托给 WordService"""
        return self.word_service.get_all_words()

    def search_words(self, keyword: str) -> List[Dict]:
        """委托给 WordService"""
        return self.word_service.search_words(keyword)

    def get_words_for_review(self, limit: int = 100) -> List[str]:
        """委托给 ReviewService，并提取 word 列表"""
        review_dicts = self.review_service.get_words_for_review(limit)
        return [w['word'] for w in review_dicts]

    def update_review_status(self, word_text: str, quality: int) -> bool:
        """委托给 ReviewService"""
        return self.review_service.update_review_status(word_text, quality)

    def get_statistics(self) -> Dict:
        """委托给 StatsService"""
        return self.stats_service.get_overview_stats()

    def get_recent_activity(self, days: int = 30) -> Dict:
        """委托给 StatsService"""
        return self.stats_service.get_recent_activity(days)

    def get_future_review_stats(self, days: int = 7) -> Dict:
        """委托给 ReviewService"""
        return self.review_service.get_future_review_stats(days)

    def clear_all_words(self) -> bool:
        """委托给 WordService"""
        return self.word_service.clear_all_words()
