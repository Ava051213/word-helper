#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
负责 SQLite 连接和 Session 管理
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

class Database:
    """数据库管理类"""
    
    def __init__(self, db_path=None):
        """初始化数据库"""
        if db_path is None:
            # 默认存储在项目根目录的 data 文件夹下
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "words.db")
        
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """获取一个新的 Session"""
        return self.Session()
    
    def close(self):
        """关闭数据库连接"""
        self.Session.remove()
