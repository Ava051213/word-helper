#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复习服务类
负责 SM-2 算法调度和复习队列管理
"""

import datetime
from typing import List, Dict
from sqlalchemy import or_
from .base_service import BaseService
from core.models import Word, ReviewHistory

class ReviewService(BaseService):
    """复习服务"""
    
    def get_words_for_review(self, limit: int = 100) -> List[Dict]:
        """获取待复习单词列表"""
        session = self.get_session()
        try:
            now = datetime.datetime.now()
            words = session.query(Word).filter(
                or_(
                    Word.next_review <= now,
                    Word.next_review == None
                )
            ).order_by(Word.next_review.asc()).limit(limit).all()
            return [w.to_dict() for w in words]
        finally:
            session.close()

    def update_review_status(self, word_text: str, quality: int) -> bool:
        """更新复习状态"""
        session = self.get_session()
        try:
            word = session.query(Word).filter_by(word=word_text.lower()).first()
            if not word:
                return False
            
            # 1. 记录复习历史
            history = ReviewHistory(word_id=word.id, quality=quality)
            session.add(history)
            
            # 2. 执行 SM-2 算法更新
            self._apply_sm2(word, quality)
            
            session.commit()
            return True
        except Exception as e:
            self.logger.error(f"更新复习状态失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_future_review_stats(self, days: int = 7) -> Dict[str, int]:
        """获取未来几天的复习量预估"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            now = datetime.date.today()
            end_date = now + datetime.timedelta(days=days-1)
            
            results = session.query(
                func.date(Word.next_review).label('date'),
                func.count(Word.id).label('count')
            ).filter(
                Word.next_review >= now,
                Word.next_review <= end_date
            ).group_by('date').all()
            
            # 初始化日期字典
            stats = {}
            for i in range(days):
                d = (now + datetime.timedelta(days=i)).isoformat()
                stats[d] = 0
            
            for date_str, count in results:
                if date_str in stats:
                    stats[date_str] = count
            
            return stats
        finally:
            session.close()

    def _apply_sm2(self, word: Word, quality: int):
        """SM-2 算法核心逻辑"""
        if quality < 3:
            # 记忆不佳，重置进度
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
            
        # 更新容易度因子
        word.easiness_factor = max(1.3, word.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # 设置下一次复习时间
        word.last_review = datetime.datetime.now()
        word.next_review = word.last_review + datetime.timedelta(days=word.interval)
        word.mastery_level = quality
