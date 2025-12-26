#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典服务类
负责对接外部词典 API 和缓冲逻辑
"""

import logging
from .base_service import BaseService

# 导入词典API模块
try:
    from api.buffered_dictionary_api import BufferedDictionaryAPI
    DICTIONARY_API_AVAILABLE = True
except ImportError:
    try:
        from api.dictionary_api import DictionaryAPI
        DICTIONARY_API_AVAILABLE = True
    except ImportError:
        DICTIONARY_API_AVAILABLE = False

class DictionaryService(BaseService):
    """词典服务"""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.dictionary_api = None
        self._init_api()
    
    def _init_api(self):
        """初始化 API"""
        if DICTIONARY_API_AVAILABLE:
            try:
                # 优先使用缓冲 API
                from api.buffered_dictionary_api import BufferedDictionaryAPI
                self.dictionary_api = BufferedDictionaryAPI()
            except Exception as e:
                self.logger.warning(f"无法初始化缓冲词典API: {e}")
                try:
                    from api.dictionary_api import DictionaryAPI
                    self.dictionary_api = DictionaryAPI()
                except Exception as e2:
                    self.logger.error(f"无法初始化词典API: {e2}")
                    self.dictionary_api = None
    
    def get_word_info(self, word_text: str):
        """获取单词信息"""
        if not self.dictionary_api:
            return None
        try:
            return self.dictionary_api.get_word_info(word_text)
        except Exception as e:
            self.logger.error(f"查询单词 '{word_text}' 失败: {e}")
            return None
