#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量定义模块
统一管理项目中的常量
"""


class Constants:
    """常量类"""
    
    # 复习相关
    MIN_QUALITY = 0
    MAX_QUALITY = 5
    DEFAULT_EF = 2.5
    MIN_EF = 1.3
    
    # 界面相关
    DEFAULT_WINDOW_SIZE = "1200x800"
    MIN_WINDOW_SIZE = (1000, 700)
    
    # 性能相关
    PAGE_SIZE = 50
    CACHE_SIZE = 1000
    API_RATE_LIMIT = 0.5  # 秒
    REVIEW_LIMIT = 100  # 每次复习的最大单词数
    
    # 数据库相关
    DB_POOL_SIZE = 5
    DB_MAX_OVERFLOW = 10
    
    # 时间相关
    DEFAULT_REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]  # 天
    DEBOUNCE_DELAY = 300  # 毫秒

