#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础服务类
提供数据库 Session 管理等通用功能
"""

import logging
from core.database import Database

class BaseService:
    """所有服务的基类"""
    
    def __init__(self, db: Database = None):
        """初始化服务"""
        self.db = db or Database()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_session(self):
        """获取数据库会话"""
        return self.db.get_session()
