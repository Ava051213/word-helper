#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移工具
将旧的 words.json 数据迁移到 SQLite 数据库
"""

import os
import json
import sys
import datetime

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database
from core.models import Word

def migrate():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "data", "words.json")
    
    if not os.path.exists(json_path):
        print(f"找不到 JSON 文件: {json_path}")
        return

    print(f"正在从 {json_path} 迁移数据...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("JSON 文件格式错误")
            return

    db = Database()
    session = db.get_session()
    
    count = 0
    for word_text, info in data.items():
        # 检查是否已存在
        existing = session.query(Word).filter_by(word=word_text).first()
        if existing:
            continue
            
        # 处理日期
        added_date = datetime.datetime.now()
        if info.get('added_date'):
            try:
                added_date = datetime.datetime.strptime(info['added_date'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
                
        last_review = None
        if info.get('last_review'):
            try:
                last_review = datetime.datetime.strptime(info['last_review'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        new_word = Word(
            word=word_text,
            phonetic=info.get('phonetic', ''),
            meaning=info.get('meaning', ''),
            example=info.get('example', ''),
            added_date=added_date,
            last_review=last_review,
            review_count=info.get('review_count', 0),
            mastery_level=info.get('mastery_level', 0)
        )
        session.add(new_word)
        count += 1
        
    session.commit()
    print(f"迁移完成！成功迁移 {count} 条数据。")
    session.close()

if __name__ == "__main__":
    migrate()
