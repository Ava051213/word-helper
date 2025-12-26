#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计服务类
负责学习数据的聚合和报表计算
"""

import datetime
from typing import Dict
from sqlalchemy import func
from .base_service import BaseService
from core.models import Word, ReviewHistory

class StatsService(BaseService):
    """统计服务"""
    
    def get_overview_stats(self) -> Dict:
        """获取概览统计数据"""
        session = self.get_session()
        try:
            total = session.query(Word).count()
            reviewed = session.query(Word).filter(Word.review_count > 0).count()
            mastered = session.query(Word).filter(Word.mastery_level >= 4).count()
            
            # 计算平均记忆强度
            avg_mastery = session.query(func.avg(Word.mastery_level)).scalar() or 0
            
            # 计算连续打卡天数 (简化版逻辑)
            streak_days = self._calculate_streak(session)
            
            return {
                "total_words": total,
                "reviewed_words": reviewed,
                "mastered_words": mastered,
                "review_rate": (reviewed / total * 100) if total > 0 else 0,
                "avg_mastery": float(avg_mastery),
                "streak_days": streak_days
            }
        finally:
            session.close()

    def _calculate_streak(self, session) -> int:
        """计算连续打卡天数"""
        # 获取所有有复习记录的日期
        dates = session.query(func.date(ReviewHistory.review_date)).distinct().order_by(func.date(ReviewHistory.review_date).desc()).all()
        if not dates:
            return 0
        
        streak = 0
        today = datetime.date.today()
        current_check = today
        
        # 将结果转换为 date 对象列表
        review_dates = [datetime.datetime.strptime(d[0], '%Y-%m-%d').date() if isinstance(d[0], str) else d[0] for d in dates]
        
        # 如果今天没打卡，从昨天开始算，或者直接返回0（取决于定义）
        # 这里定义为：如果今天打卡了，算上今天；如果今天没打卡但昨天打卡了，连续天数保留；否则断开
        if today not in review_dates:
            current_check = today - datetime.timedelta(days=1)
            if current_check not in review_dates:
                return 0
        
        for date in review_dates:
            if date == current_check:
                streak += 1
                current_check -= datetime.timedelta(days=1)
            elif date < current_check:
                break
        return streak

    def get_recent_activity(self, days: int = 30) -> Dict:
        """获取最近活动统计"""
        session = self.get_session()
        try:
            start_date = datetime.date.today() - datetime.timedelta(days=days-1)
            
            # 1. 查询每日新增
            new_words = session.query(
                func.date(Word.added_date).label('date'),
                func.count(Word.id).label('count')
            ).filter(Word.added_date >= start_date).group_by('date').all()
            
            # 2. 查询每日复习
            reviews = session.query(
                func.date(ReviewHistory.review_date).label('date'),
                func.count(ReviewHistory.id).label('count')
            ).filter(ReviewHistory.review_date >= start_date).group_by('date').all()
            
            # 合并结果
            daily_stats = {}
            # 初始化日期范围
            for i in range(days):
                d = (start_date + datetime.timedelta(days=i)).isoformat()
                daily_stats[d] = {'new': 0, 'review': 0}
            
            for date_str, count in new_words:
                if date_str in daily_stats:
                    daily_stats[date_str]['new'] = count
            
            for date_str, count in reviews:
                if date_str in daily_stats:
                    daily_stats[date_str]['review'] = count
                    
            return {'daily_stats': daily_stats}
        finally:
            session.close()
