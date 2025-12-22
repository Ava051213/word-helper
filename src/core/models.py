#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型模块
定义数据库表结构
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Word(Base):
    """单词模型"""
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), unique=True, nullable=False, index=True)
    phonetic = Column(String(100))
    meaning = Column(Text)
    example = Column(Text)
    category = Column(String(100))  # 单词分类
    added_date = Column(DateTime, default=datetime.datetime.now, index=True)  # 添加索引用于时间范围查询
    
    # 复习相关
    last_review = Column(DateTime)
    next_review = Column(DateTime, index=True)
    review_count = Column(Integer, default=0, index=True)  # 添加索引用于统计查询
    mastery_level = Column(Integer, default=0, index=True)  # 添加索引用于筛选 0-5
    
    # SM-2 算法参数
    easiness_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)  # 天数
    
    # 关联复习历史
    history = relationship("ReviewHistory", back_populates="word_ref", cascade="all, delete-orphan")

    def to_dict(self):
        """转为字典格式，保持与旧代码兼容"""
        return {
            "word": self.word,
            "phonetic": self.phonetic,
            "meaning": self.meaning,
            "example": self.example,
            "category": self.category,
            "added_date": self.added_date.strftime("%Y-%m-%d %H:%M:%S") if self.added_date else None,
            "last_review": self.last_review.strftime("%Y-%m-%d %H:%M:%S") if self.last_review else None,
            "next_review": self.next_review.strftime("%Y-%m-%d %H:%M:%S") if self.next_review else None,
            "review_count": self.review_count,
            "mastery_level": self.mastery_level,
            "easiness_factor": self.easiness_factor,
            "interval": self.interval
        }

class ReviewHistory(Base):
    """复习历史记录模型"""
    __tablename__ = 'review_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False, index=True)  # 添加索引
    review_date = Column(DateTime, default=datetime.datetime.now, index=True)  # 添加索引用于时间查询
    quality = Column(Integer)  # 用户选择的掌握程度 (0-5)
    
    word_ref = relationship("Word", back_populates="history")
