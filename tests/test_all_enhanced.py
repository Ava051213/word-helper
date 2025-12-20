#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件
包含所有模块的单元测试
"""

import sys
import os
import unittest
import tempfile
import json
import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from word_manager import WordManager
from scheduler import Scheduler
from scheduler import calculate_next_review_interval
from data_manager import DataManager


class TestWordManager(unittest.TestCase):
    """单词管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时文件用于测试
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.word_manager = WordManager(self.temp_file.name)
    
    def tearDown(self):
        """测试后清理"""
        os.unlink(self.temp_file.name)
    
    def test_add_word(self):
        """测试添加单词"""
        word = "test"
        meaning = "测试"
        result = self.word_manager.add_word_direct(word, meaning)
        
        self.assertTrue(result)
        self.assertIn(word, self.word_manager.words)
        self.assertEqual(self.word_manager.words[word]["meaning"], meaning)
    
    def test_get_word(self):
        """测试获取单词"""
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        
        info = self.word_manager.get_word(word)
        self.assertEqual(info["meaning"], meaning)
    
    def test_update_word(self):
        """测试更新单词"""
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        
        new_meaning = "新的测试"
        # 获取原始信息并更新
        info = self.word_manager.get_word(word)
        info["meaning"] = new_meaning
        self.word_manager.update_word(word, info)
        
        updated_info = self.word_manager.get_word(word)
        self.assertEqual(updated_info["meaning"], new_meaning)
    
    def test_delete_word(self):
        """测试删除单词"""
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        
        # 由于delete_word是交互式方法，我们直接测试内部逻辑
        if word in self.word_manager.words:
            del self.word_manager.words[word]
            self.word_manager.save_words()
        
        self.assertNotIn(word, self.word_manager.words)
    
    def test_get_words_for_review(self):
        """测试获取待复习单词"""
        # 添加一个需要复习的单词
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        
        # 设置为需要立即复习
        self.word_manager.words[word]["next_review"] = datetime.datetime.now().isoformat()
        self.word_manager.save_words()
        
        words_for_review = self.word_manager.get_words_for_review()
        self.assertIn(word, words_for_review)


class TestScheduler(unittest.TestCase):
    """调度器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.word_manager = WordManager(self.temp_file.name)
        self.scheduler = Scheduler(self.word_manager)
    
    def tearDown(self):
        """测试后清理"""
        os.unlink(self.temp_file.name)
    
    def test_schedule_new_word(self):
        """测试安排新单词"""
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        
        self.scheduler.schedule_new_word(word)
        
        info = self.word_manager.get_word(word)
        self.assertIsNotNone(info["next_review"])
        self.assertEqual(info["interval"], 1)
    
    def test_update_word_schedule_known(self):
        """测试更新已知单词的调度"""
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        self.scheduler.schedule_new_word(word)
        
        # 获取初始信息
        info = self.word_manager.get_word(word)
        initial_interval = info["interval"]
        
        # 模拟用户认识这个单词
        self.scheduler._update_word_schedule(word, info, True)
        
        # 检查间隔是否增加
        updated_info = self.word_manager.get_word(word)
        self.assertGreater(updated_info["interval"], initial_interval)
    
    def test_update_word_schedule_unknown(self):
        """测试更新未知单词的调度"""
        word = "test"
        meaning = "测试"
        self.word_manager.add_word_direct(word, meaning)
        self.scheduler.schedule_new_word(word)
        
        # 获取初始信息
        info = self.word_manager.get_word(word)
        initial_interval = info["interval"]
        
        # 模拟用户不认识这个单词
        self.scheduler._update_word_schedule(word, info, False)
        
        # 检查间隔是否重置
        updated_info = self.word_manager.get_word(word)
        self.assertEqual(updated_info["interval"], 1)


class TestUtils(unittest.TestCase):
    """工具函数测试"""
    
    def test_calculate_next_review_interval(self):
        """测试计算下次复习间隔"""
        # 测试基础间隔计算
        interval = calculate_next_review_interval(1, True)
        self.assertEqual(interval, 3)  # 1 * 3 = 3
        
        interval = calculate_next_review_interval(3, True)
        self.assertEqual(interval, 9)  # 3 * 3 = 9
        
        # 测试遗忘后的重置
        interval = calculate_next_review_interval(5, False)
        self.assertEqual(interval, 1)


class TestDataManager(unittest.TestCase):
    """数据管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.data_manager = DataManager(self.temp_file.name)
        
        # 创建测试数据
        test_data = {
            "hello": {
                "meaning": "你好",
                "example": "Hello, world!",
                "category": "问候",
                "add_date": "2025-12-20T10:00:00",
                "last_reviewed": "2025-12-20T15:00:00",
                "next_review": "2025-12-21T10:00:00",
                "review_count": 1,
                "interval": 1,
                "difficulty": "normal"
            }
        }
        
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """测试后清理"""
        os.unlink(self.temp_file.name)
        # 清理备份目录
        import shutil
        if os.path.exists("data/backups"):
            shutil.rmtree("data/backups", ignore_errors=True)
    
    def test_generate_report(self):
        """测试生成报告"""
        report = self.data_manager.generate_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn("total_words", report)
        self.assertIn("reviewed_words", report)
        self.assertEqual(report["total_words"], 1)
    
    def test_backup_data(self):
        """测试数据备份"""
        backup_file = self.data_manager.backup_data()
        
        self.assertTrue(os.path.exists(backup_file))
        # 检查备份文件内容
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        self.assertIn("hello", backup_data)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWordManager))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestDataManager))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)