#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音服务类
负责单词和例句的文本转语音 (TTS)
"""

import threading
import pyttsx3
import logging

class TTSService:
    """TTS 服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._engine = None
        self._lock = threading.Lock()
        self._init_engine()

    def _init_engine(self):
        """初始化 TTS 引擎"""
        try:
            # 在单独的线程中初始化，避免阻塞主线程
            self._engine = pyttsx3.init()
            # 设置语速
            self._engine.setProperty('rate', 150)
            # 设置音量
            self._engine.setProperty('volume', 1.0)
            
            # 尝试查找英文声音
            voices = self._engine.getProperty('voices')
            for voice in voices:
                if 'EN-US' in voice.id.upper() or 'ENGLISH' in voice.name.upper():
                    self._engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            self.logger.error(f"无法初始化 TTS 引擎: {e}")
            self._engine = None

    def speak(self, text: str):
        """播放语音"""
        if not self._engine:
            self._init_engine()
        
        if not self._engine:
            return

        def _run():
            with self._lock:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    self.logger.error(f"TTS 播放失败: {e}")

        # 在新线程中运行，避免阻塞 GUI
        threading.Thread(target=_run, daemon=True).start()

    def stop(self):
        """停止所有正在播放的语音"""
        if self._engine:
            try:
                self._engine.stop()
            except:
                pass
