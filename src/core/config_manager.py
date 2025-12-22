#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
处理用户偏好设置的持久化
"""
import json
import os

class ConfigManager:
    def __init__(self, config_file="data/config.json"):
        # 确保路径是绝对路径，相对于项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = os.path.join(base_dir, config_file)
        
        # 默认配置
        self.defaults = {
            "appearance_mode": "System",
            "default_vocabulary_level": "cet4",
            "auto_play_tts": False,
            "last_used_at": None,
            "daily_review_goal": 20,
            "reminder_enabled": True,
            "reminder_time": "09:00",
            "auto_backup": True,
            "backup_interval_days": 7
        }
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认值，确保新添加的配置项也有默认值
                    return {**self.defaults, **config}
            except Exception as e:
                print(f"加载配置失败: {e}")
                return self.defaults.copy()
        return self.defaults.copy()

    def save_config(self):
        """保存配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default if default is not None else self.defaults.get(key))

    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        return self.save_config()
