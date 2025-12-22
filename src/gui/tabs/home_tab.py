#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import customtkinter as ctk
from .base_tab import BaseTab

class HomeTab(BaseTab):
    """主页标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        self.create_widgets()
        self.update_reminder()

    def create_widgets(self):
        """创建主页标签页内容"""
        # 欢迎信息
        welcome_frame = ctk.CTkFrame(self)
        welcome_frame.pack(fill=tk.X, padx=20, pady=20)
        
        welcome_title = ctk.CTkLabel(welcome_frame, text="欢迎使用", font=('Arial', 18, 'bold'))
        welcome_title.pack(pady=(15, 5))
        
        welcome_text = """
        欢迎使用单词记忆助手！
        
        本系统基于艾宾浩斯遗忘曲线理论，通过科学的时间间隔安排单词复习，
        帮助您更高效地记忆单词。
        
        使用指南：
        1. 在"添加单词"页面添加您需要记忆的单词
        2. 在"复习单词"页面进行定期复习
        3. 查看"学习统计"了解您的学习进度
        """
        
        welcome_label = ctk.CTkLabel(welcome_frame, text=welcome_text, justify=tk.LEFT)
        welcome_label.pack(pady=(0, 15))
        
        # 快捷操作
        quick_frame = ctk.CTkFrame(self)
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        quick_title = ctk.CTkLabel(quick_frame, text="快捷操作", font=('Arial', 18, 'bold'))
        quick_title.pack(pady=(15, 5))
        
        button_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # 使用更大的按钮
        ctk.CTkButton(button_frame, text="添加单词", 
                      command=lambda: self.parent_gui.tabview.set("添加单词"), 
                      width=140, height=40).pack(side=tk.LEFT, padx=20, pady=15)
        
        ctk.CTkButton(button_frame, text="开始复习", 
                      command=lambda: self.parent_gui.review_tab_comp.quick_review(), 
                      width=140, height=40).pack(side=tk.LEFT, padx=20, pady=15)
        
        ctk.CTkButton(button_frame, text="查看统计", 
                      command=lambda: self.parent_gui.tabview.set("学习统计"), 
                      width=140, height=40).pack(side=tk.LEFT, padx=20, pady=15)
        
        # 今日学习提醒
        reminder_frame = ctk.CTkFrame(self)
        reminder_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        reminder_title = ctk.CTkLabel(reminder_frame, text="今日学习提醒", font=('Arial', 18, 'bold'))
        reminder_title.pack(pady=(15, 5))
        
        self.reminder_text = ctk.CTkTextbox(reminder_frame, font=('Arial', 12))
        self.reminder_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    def update_reminder(self):
        """更新首页提醒"""
        review_count = len(self.word_manager.get_words_for_review())
        stats = self.word_manager.get_statistics()
        total_words = stats['total_words']
        
        reminder_text = f"""
今日学习提醒
=================

📊 数据统计:
  • 总单词数: {total_words}
  • 待复习单词: {review_count}
  
📝 学习建议:
"""
        
        if review_count > 0:
            reminder_text += f"  • 有 {review_count} 个单词需要复习，请及时复习\n"
        else:
            reminder_text += "  • 暂无待复习单词，可以添加新单词\n"
        
        if total_words == 0:
            reminder_text += "  • 还没有添加单词，建议先添加一些单词\n"
        elif total_words < 10:
            reminder_text += "  • 单词量较少，建议添加更多单词\n"
        
        reminder_text += """
💡 使用技巧:
  • 定期复习是记忆的关键
  • 结合例句记忆效果更好
  • 按分类学习有助于建立词汇网络
"""
        
        self.reminder_text.delete(1.0, tk.END)
        self.reminder_text.insert(tk.END, reminder_text)
