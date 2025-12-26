#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证重构后的后端服务层
"""

import sys
import os
import unittest
import tempfile
import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.word_manager import WordManager

class TestRefactoredServices(unittest.TestCase):
    """验证服务层重构后的功能"""
    
    def setUp(self):
        """测试前准备"""
        # 使用内存数据库进行测试
        self.manager = WordManager(":memory:")
        self.manager.add_word_direct("apple", "苹果", "An apple a day keeps the doctor away.", "ˈæpl")
        self.manager.add_word_direct("banana", "香蕉", "He likes eating bananas.", "bəˈnɑːnə")

    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'manager'):
            self.manager.db.close()

    def test_word_service(self):
        """测试 WordService 功能"""
        # 测试获取单词
        word = self.manager.get_word("apple")
        self.assertIsNotNone(word)
        self.assertEqual(word['meaning'], "苹果")
        
        # 测试获取所有单词
        all_words = self.manager.get_all_words()
        self.assertEqual(len(all_words), 2)
        
        # 测试更新单词
        self.manager.update_word("apple", meaning="大苹果")
        word = self.manager.get_word("apple")
        self.assertEqual(word['meaning'], "大苹果")
        
        # 测试删除单词
        self.manager.delete_word("banana")
        all_words = self.manager.get_all_words()
        self.assertEqual(len(all_words), 1)

    def test_review_service(self):
        """测试 ReviewService 功能"""
        # 获取待复习列表 (初始都应该在列表里)
        review_list = self.manager.get_words_for_review()
        self.assertIn("apple", review_list)
        
        # 更新复习状态
        self.manager.update_review_status("apple", 5) # 非常容易
        
        # 验证下次复习时间已更新 (apple 应该不在立即复习列表中了)
        review_list = self.manager.get_words_for_review()
        self.assertNotIn("apple", review_list)
        
        # 验证未来统计
        future_stats = self.manager.get_future_review_stats(7)
        self.assertIsNotNone(future_stats)
        self.assertTrue(any(count > 0 for count in future_stats.values()))

    def test_stats_service(self):
        """测试 StatsService 功能"""
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total_words'], 2)
        
        activity = self.manager.get_recent_activity(7)
        self.assertIsNotNone(activity)
        self.assertIn('daily_stats', activity)
        # 验证包含今天的数据
        today = datetime.date.today().isoformat()
        self.assertIn(today, activity['daily_stats'])
        self.assertEqual(activity['daily_stats'][today]['new'], 2)

    def test_tts_service(self):
        """测试 TTSService (非阻塞调用)"""
        try:
            self.manager.speak("Hello test")
            # 只要不报错就行，因为 TTS 是异步的且依赖环境
        except Exception as e:
            self.fail(f"TTS Service failed: {e}")

    def test_clear_all(self):
        """测试清空功能"""
        self.manager.clear_all_words()
        all_words = self.manager.get_all_words()
        self.assertEqual(len(all_words), 0)

if __name__ == '__main__':
    unittest.main()
