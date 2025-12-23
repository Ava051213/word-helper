#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyttsx3
import threading
import logging

logger = logging.getLogger(__name__)

class AudioManager:
    """音频管理器，处理语音播放逻辑"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioManager, cls).__new__(cls)
                cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        """初始化 TTS 引擎"""
        try:
            self.engine = pyttsx3.init()
            # 设置语速
            self.engine.setProperty('rate', 150)
            # 设置音量
            self.engine.setProperty('volume', 0.9)
            
            # 获取并设置英文声音
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'EN-US' in voice.id.upper() or 'ENGLISH' in voice.name.upper():
                    self.engine.setProperty('voice', voice.id)
                    break
                    
            self.is_ready = True
            logger.info("TTS 引擎初始化成功")
        except Exception as e:
            logger.error(f"TTS 引擎初始化失败: {e}")
            self.is_ready = False

    def speak(self, text):
        """异步播放语音"""
        if not hasattr(self, 'is_ready') or not self.is_ready:
            logger.warning("TTS 引擎未就绪，无法播放语音")
            return

        def _speak_task():
            try:
                # pyttsx3 在多线程中需要重新初始化或者使用特定的同步机制
                # 最简单的方法是在线程内创建临时引擎，或者加锁使用全局引擎
                with self._lock:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                logger.error(f"语音播放失败: {e}")

        thread = threading.Thread(target=_speak_task, daemon=True)
        thread.start()

# 全局单例
audio_manager = AudioManager()
