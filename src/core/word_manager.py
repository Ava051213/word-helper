#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词管理模块
负责单词的增删改查等基本操作，使用 SQLite 数据库存储
"""

import os
import datetime
import logging
from typing import Dict, List, Optional
from sqlalchemy import or_, func, case

from .database import Database
from .models import Word, ReviewHistory

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
        print("警告: 无法导入词典API模块，自动获取单词信息功能将不可用")

logger = logging.getLogger(__name__)

class WordManager:
    """单词管理器 (基于 SQLite)"""
    
    def __init__(self, db_path: str = None):
        """初始化单词管理器"""
        self.db = Database(db_path)
        
        # 初始化词典API
        if DICTIONARY_API_AVAILABLE:
            try:
                self.dictionary_api = BufferedDictionaryAPI()
            except Exception as e:
                logger.warning(f"无法初始化缓冲词典API: {e}，回退到普通词典API")
                try:
                    from ..api.dictionary_api import DictionaryAPI
                    self.dictionary_api = DictionaryAPI()
                except Exception as e2:
                    logger.error(f"无法初始化普通词典API: {e2}")
                    self.dictionary_api = None
        else:
            self.dictionary_api = None
    
    def add_word_direct(self, word_text: str, meaning: str, example: str = "", phonetic: str = "") -> bool:
        """直接添加新单词（编程接口）"""
        if not word_text or not meaning:
            return False
        
        word_text = word_text.strip().lower()
        session = self.db.get_session()
        try:
            # 检查是否已存在
            existing = session.query(Word).filter_by(word=word_text).first()
            if existing:
                return False
            
            new_word = Word(
                word=word_text,
                meaning=meaning,
                example=example,
                phonetic=phonetic,
                next_review=datetime.datetime.now() # 新单词立即可以复习
            )
            session.add(new_word)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"添加单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete_word(self, word_text: str) -> bool:
        """删除单词"""
        session = self.db.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            if word:
                session.delete(word)
                session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"删除单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_word(self, word_text: str, meaning: str = None, example: str = None, category: str = None, phonetic: str = None) -> bool:
        """更新单词信息"""
        session = self.db.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            if not word:
                return False
            
            if meaning is not None:
                word.meaning = meaning
            if example is not None:
                word.example = example
            if category is not None:
                word.category = category
            if phonetic is not None:
                word.phonetic = phonetic
                
            session.commit()
            return True
        except Exception as e:
            logger.error(f"更新单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_word(self, word_text: str) -> Optional[Dict]:
        """获取单词信息"""
        session = self.db.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            return word.to_dict() if word else None
        finally:
            session.close()

    def get_all_words(self) -> List[Dict]:
        """获取所有单词"""
        session = self.db.get_session()
        try:
            words = session.query(Word).all()
            return [w.to_dict() for w in words]
        finally:
            session.close()

    def search_words(self, keyword: str) -> List[Dict]:
        """搜索单词"""
        session = self.db.get_session()
        try:
            keyword = f"%{keyword}%"
            words = session.query(Word).filter(
                or_(
                    Word.word.like(keyword),
                    Word.meaning.like(keyword),
                    Word.example.like(keyword)
                )
            ).all()
            return [w.to_dict() for w in words]
        finally:
            session.close()

    def get_words_for_review(self, limit: int = 100) -> List[str]:
        """获取需要复习的单词列表（优化：添加限制数量）"""
        session = self.db.get_session()
        try:
            now = datetime.datetime.now()
            # 查询 next_review 小于等于现在的，或者从未复习过的
            words = session.query(Word).filter(
                or_(
                    Word.next_review <= now,
                    Word.next_review == None
                )
            ).order_by(Word.next_review.asc()).limit(limit).all()
            return [w.word for w in words]
        finally:
            session.close()

    def update_review_status(self, word_text: str, quality: int):
        """更新复习状态 (SM-2 算法逻辑将在这里调用)"""
        session = self.db.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            if not word:
                return
            
            # 记录复习历史
            history = ReviewHistory(word_id=word.id, quality=quality)
            session.add(history)
            
            # SM-2 算法更新
            self._update_sm2(word, quality)
            
            session.commit()
        except Exception as e:
            logger.error(f"更新复习状态失败: {e}")
            session.rollback()
        finally:
            session.close()

    def _update_sm2(self, word: Word, quality: int):
        """SM-2 算法核心逻辑
        quality: 0-5 (0: 完全忘记, 5: 非常容易)
        """
        if quality < 3:
            # 如果掌握不好，重新开始
            word.interval = 1
            word.review_count = 0
        else:
            if word.review_count == 0:
                word.interval = 1
            elif word.review_count == 1:
                word.interval = 6
            else:
                word.interval = int(word.interval * word.easiness_factor)
            
            word.review_count += 1
            
        # 更新容易度因子 (Easiness Factor)
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        word.easiness_factor = max(1.3, word.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # 设置下一次复习时间
        word.last_review = datetime.datetime.now()
        word.next_review = word.last_review + datetime.timedelta(days=word.interval)
        word.mastery_level = quality

    def get_statistics(self) -> Dict:
        """获取学习统计"""
        session = self.db.get_session()
        try:
            total = session.query(Word).count()
            reviewed = session.query(Word).filter(Word.review_count > 0).count()
            mastered = session.query(Word).filter(Word.mastery_level >= 4).count()
            
            return {
                "total_words": total,
                "reviewed_words": reviewed,
                "mastered_words": mastered,
                "review_rate": (reviewed / total * 100) if total > 0 else 0
            }
        finally:
            session.close()

    def clear_all_words(self) -> bool:
        """清空所有单词数据"""
        session = self.db.get_session()
        try:
            session.query(ReviewHistory).delete()
            session.query(Word).delete()
            session.commit()
            return True
        except Exception as e:
            logger.error(f"清空单词失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_recent_activity(self, days: int = 30) -> Dict:
        """获取最近活动统计"""
        session = self.db.get_session()
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # 新增单词数
            new_words = session.query(Word).filter(
                Word.added_date >= cutoff_date
            ).count()
            
            # 复习会话数（通过ReviewHistory统计）
            review_sessions = session.query(
                func.date(ReviewHistory.review_date).distinct()
            ).filter(
                ReviewHistory.review_date >= cutoff_date
            ).count()
            
            # 每日统计
            daily_stats = {}
            words_added = session.query(
                func.date(Word.added_date).label('date'),
                func.count(Word.id).label('count')
            ).filter(
                Word.added_date >= cutoff_date
            ).group_by(func.date(Word.added_date)).all()
            
            for date, count in words_added:
                daily_stats[date.strftime('%Y-%m-%d')] = {'new': count, 'review': 0}
            
            # 每日复习统计
            reviews = session.query(
                func.date(ReviewHistory.review_date).label('date'),
                func.count(ReviewHistory.id).label('count')
            ).filter(
                ReviewHistory.review_date >= cutoff_date
            ).group_by(func.date(ReviewHistory.review_date)).all()
            
            for date, count in reviews:
                date_str = date.strftime('%Y-%m-%d')
                if date_str not in daily_stats:
                    daily_stats[date_str] = {'new': 0, 'review': 0}
                daily_stats[date_str]['review'] = count
            
            return {
                'new_words': new_words,
                'review_sessions': review_sessions,
                'daily_stats': daily_stats
            }
        finally:
            session.close()
    
    def get_future_review_stats(self, days: int = 7) -> Dict:
        """获取未来复习计划统计"""
        session = self.db.get_session()
        try:
            now = datetime.datetime.now().date()
            future_stats = {}
            
            for i in range(days):
                target_date = now + datetime.timedelta(days=i)
                count = session.query(Word).filter(
                    func.date(Word.next_review) == target_date
                ).count()
                future_stats[target_date.strftime('%Y-%m-%d')] = count
                
            return future_stats
        finally:
            session.close()
    
    def get_review_history(self, limit: int = 100) -> List[Dict]:
        """获取复习历史记录"""
        session = self.db.get_session()
        try:
            # 按日期分组获取复习会话
            sessions = session.query(
                func.date(ReviewHistory.review_date).label('date'),
                func.count(ReviewHistory.id).label('word_count'),
                func.sum(case((ReviewHistory.quality >= 3, 1), else_=0)).label('known_count')
            ).group_by(
                func.date(ReviewHistory.review_date)
            ).order_by(
                ReviewHistory.review_date.desc()
            ).limit(limit).all()
            
            history = []
            for date, word_count, known_count in sessions:
                # 获取该会话的单词详情
                words = session.query(ReviewHistory).filter(
                    func.date(ReviewHistory.review_date) == date
                ).all()
                
                word_results = []
                for review in words:
                    word = session.query(Word).filter_by(id=review.word_id).first()
                    if word:
                        word_results.append({
                            'word': word.word,
                            'known': review.quality >= 3
                        })
                
                history.append({
                    'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'words': word_results,
                    'known_count': int(known_count or 0)
                })
            
            return history
        finally:
            session.close()
    
    def clear_all_data(self) -> bool:
        """清空所有数据（包括配置等）"""
        return self.clear_all_words()
