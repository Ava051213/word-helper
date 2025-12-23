#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk

from src.utils.audio_manager import audio_manager

class BaseTab(ctk.CTkFrame):
    """标签页基类"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, **kwargs)
        self.parent_gui = parent_gui
        self.word_manager = parent_gui.word_manager
        self.config_manager = parent_gui.config_manager
        self.status_bar = parent_gui.status_bar
        self.buffered_dictionary_api = getattr(parent_gui, 'buffered_dictionary_api', None)
        self.audio_manager = audio_manager
        
        # 确保标签页填满父容器
        self.pack(fill="both", expand=True)
