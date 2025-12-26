#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词服务类
负责单词的 CRUD 操作
"""

import datetime
from typing import List, Optional, Dict
from sqlalchemy import or_
from .base_service import BaseService
from core.models import Word, ReviewHistory

class WordService(BaseService):
    """单词服务"""
    
    def add_word(self, word_text: str, meaning: str, example: str = "", phonetic: str = "", category: str = "默认") -> bool:
        """添加新单词"""
        if not word_text or not meaning:
            return False
        
        word_text = word_text.strip().lower()
        session = self.get_session()
        try:
            existing = session.query(Word).filter_by(word=word_text).first()
            if existing:
                return False
            
            new_word = Word(
                word=word_text,
                meaning=meaning,
                example=example,
                phonetic=phonetic,
                category=category,
                next_review=datetime.datetime.now()
            )
            session.add(new_word)
            session.commit()
            return True
        except Exception as e:
            self.logger.error(f"添加单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete_word(self, word_text: str) -> bool:
        """删除单词"""
        session = self.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            if word:
                session.delete(word)
                session.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"删除单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_word(self, word_text: str, **kwargs) -> bool:
        """更新单词信息"""
        session = self.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            if not word:
                return False
            
            for key, value in kwargs.items():
                if hasattr(word, key) and value is not None:
                    setattr(word, key, value)
                
            session.commit()
            return True
        except Exception as e:
            self.logger.error(f"更新单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_word(self, word_text: str) -> Optional[Dict]:
        """获取单个单词"""
        session = self.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            return word.to_dict() if word else None
        finally:
            session.close()

    def get_all_words(self) -> List[Dict]:
        """获取所有单词"""
        session = self.get_session()
        try:
            words = session.query(Word).all()
            return [w.to_dict() for w in words]
        finally:
            session.close()

    def clear_all_words(self) -> bool:
        """清空所有单词和复习记录"""
        session = self.get_session()
        try:
            session.query(ReviewHistory).delete()
            session.query(Word).delete()
            session.commit()
            return True
        except Exception as e:
            self.logger.error(f"清空数据失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def search_words(self, keyword: str) -> List[Dict]:
        """搜索单词"""
        session = self.get_session()
        try:
            search_pattern = f"%{keyword}%"
            words = session.query(Word).filter(
                or_(
                    Word.word.like(search_pattern),
                    Word.meaning.like(search_pattern),
                    Word.example.like(search_pattern)
                )
            ).all()
            return [w.to_dict() for w in words]
        finally:
            session.close()
