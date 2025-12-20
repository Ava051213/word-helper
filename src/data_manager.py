#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
提供高级数据操作功能
"""

import json
import csv
import datetime
import os
from typing import Dict, List


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_file: str = "data/words.json"):
        """初始化数据管理器"""
        self.data_file = data_file
        self.backup_dir = "data/backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def export_to_csv(self, csv_file: str = "data/words_export.csv") -> bool:
        """导出数据到CSV文件"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                words = json.load(f)
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['单词', '释义', '例句', '分类', '添加日期', '最后复习', '下次复习', '复习次数', '间隔天数'])
                
                # 写入数据
                for word, info in words.items():
                    writer.writerow([
                        word,
                        info.get('meaning', ''),
                        info.get('example', ''),
                        info.get('category', ''),
                        info.get('add_date', '')[:10] if info.get('add_date') else '',
                        info.get('last_reviewed', '')[:10] if info.get('last_reviewed') else '',
                        info.get('next_review', '')[:10] if info.get('next_review') else '',
                        info.get('review_count', 0),
                        info.get('interval', 1)
                    ])
            
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def import_from_csv(self, csv_file: str) -> int:
        """从CSV文件导入数据"""
        try:
            # 先备份现有数据
            self.backup_data()
            
            imported_count = 0
            words = {}
            
            # 如果存在现有数据，先加载
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    words = json.load(f)
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过表头
                
                for row in reader:
                    if len(row) >= 9:
                        word = row[0].strip().lower()
                        if word and word not in words:
                            words[word] = {
                                "meaning": row[1].strip(),
                                "example": row[2].strip(),
                                "category": row[3].strip(),
                                "add_date": row[4].strip() if row[4].strip() else datetime.datetime.now().isoformat(),
                                "last_reviewed": row[5].strip() if row[5].strip() else None,
                                "next_review": row[6].strip() if row[6].strip() else None,
                                "review_count": int(row[7]) if row[7].strip().isdigit() else 0,
                                "interval": int(row[8]) if row[8].strip().isdigit() else 1,
                                "difficulty": "normal"
                            }
                            imported_count += 1
            
            # 保存数据
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(words, f, ensure_ascii=False, indent=2)
            
            return imported_count
        except Exception as e:
            print(f"导入CSV失败: {e}")
            return 0
    
    def backup_data(self) -> str:
        """备份数据"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f"words_backup_{timestamp}.json")
            
            if os.path.exists(self.data_file):
                import shutil
                shutil.copy(self.data_file, backup_file)
                return backup_file
            return ""
        except Exception as e:
            print(f"备份数据失败: {e}")
            return ""
    
    def get_backup_files(self) -> List[str]:
        """获取备份文件列表"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith("words_backup_") and file.endswith(".json"):
                    backups.append(os.path.join(self.backup_dir, file))
            return sorted(backups, reverse=True)
        except Exception as e:
            print(f"获取备份文件列表失败: {e}")
            return []
    
    def restore_backup(self, backup_file: str) -> bool:
        """恢复备份"""
        try:
            if os.path.exists(backup_file):
                import shutil
                shutil.copy(backup_file, self.data_file)
                return True
            return False
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """生成学习报告"""
        try:
            if not os.path.exists(self.data_file):
                return {}
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                words = json.load(f)
            
            total_words = len(words)
            reviewed_words = sum(1 for info in words.values() if info.get('review_count', 0) > 0)
            total_reviews = sum(info.get('review_count', 0) for info in words.values())
            
            # 计算分类统计
            categories = {}
            for info in words.values():
                category = info.get('category', '未分类')
                categories[category] = categories.get(category, 0) + 1
            
            # 计算复习时间分布
            intervals = {}
            for info in words.values():
                interval = info.get('interval', 1)
                intervals[interval] = intervals.get(interval, 0) + 1
            
            report = {
                "total_words": total_words,
                "reviewed_words": reviewed_words,
                "unreviewed_words": total_words - reviewed_words,
                "review_rate": (reviewed_words / total_words * 100) if total_words > 0 else 0,
                "total_reviews": total_reviews,
                "avg_reviews_per_word": (total_reviews / total_words) if total_words > 0 else 0,
                "categories": categories,
                "intervals": intervals
            }
            
            return report
        except Exception as e:
            print(f"生成报告失败: {e}")
            return {}


# 测试代码
if __name__ == "__main__":
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
        },
        "world": {
            "meaning": "世界",
            "example": "Hello, world!",
            "category": "名词",
            "add_date": "2025-12-20T10:05:00",
            "last_reviewed": None,
            "next_review": None,
            "review_count": 0,
            "interval": 1,
            "difficulty": "normal"
        }
    }
    
    # 保存测试数据
    os.makedirs("data", exist_ok=True)
    with open("data/words.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    # 测试数据管理功能
    manager = DataManager()
    
    # 测试导出CSV
    if manager.export_to_csv():
        print("CSV导出成功")
    
    # 测试生成报告
    report = manager.generate_report()
    print("学习报告:", report)
    
    # 测试备份
    backup_file = manager.backup_data()
    if backup_file:
        print(f"数据备份成功: {backup_file}")