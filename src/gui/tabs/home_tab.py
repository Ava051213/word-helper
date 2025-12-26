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
        self.update_statistics()

    def create_widgets(self):
        """创建主页标签页内容"""
        # 主容器
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. 顶部状态栏 - 仪表盘卡片
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # 定义卡片样式
        card_settings = {"height": 100, "corner_radius": 10}
        
        # 卡片1: 总单词数
        self.total_card = ctk.CTkFrame(stats_frame, **card_settings)
        self.total_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        ctk.CTkLabel(self.total_card, text="📚 总单词数", font=('Arial', 14)).pack(pady=(15, 0))
        self.total_val = ctk.CTkLabel(self.total_card, text="0", font=('Arial', 24, 'bold'))
        self.total_val.pack(pady=(5, 15))
        
        # 卡片2: 待复习
        self.review_card = ctk.CTkFrame(stats_frame, **card_settings)
        self.review_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ctk.CTkLabel(self.review_card, text="⏳ 待复习", font=('Arial', 14)).pack(pady=(15, 0))
        self.review_val = ctk.CTkLabel(self.review_card, text="0", font=('Arial', 24, 'bold'), text_color="#e74c3c")
        self.review_val.pack(pady=(5, 15))
        
        # 卡片3: 已掌握
        self.mastered_card = ctk.CTkFrame(stats_frame, **card_settings)
        self.mastered_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        ctk.CTkLabel(self.mastered_card, text="✅ 已掌握", font=('Arial', 14)).pack(pady=(15, 0))
        self.mastered_val = ctk.CTkLabel(self.mastered_card, text="0", font=('Arial', 24, 'bold'), text_color="#2ecc71")
        self.mastered_val.pack(pady=(5, 15))

        # 2. 中间区域: 快捷操作与建议
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=3) # 左侧建议占更多空间
        content_frame.grid_columnconfigure(1, weight=1) # 右侧按钮

        # 左侧: 学习建议 (使用更美观的容器)
        suggestion_container = ctk.CTkFrame(content_frame)
        suggestion_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(suggestion_container, text="💡 学习建议", font=('Arial', 18, 'bold')).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.suggestion_text = ctk.CTkTextbox(suggestion_container, font=('Arial', 13), fg_color="transparent", border_width=0)
        self.suggestion_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.suggestion_text.configure(state="disabled") # 初始禁用，由 update_statistics 写入

        # 右侧: 快捷操作
        actions_container = ctk.CTkFrame(content_frame)
        actions_container.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(actions_container, text="⚡ 快捷入口", font=('Arial', 18, 'bold')).pack(pady=(15, 10))
        
        btn_style = {"width": 160, "height": 45, "font": ('Arial', 14)}
        
        ctk.CTkButton(actions_container, text="➕ 添加单词", 
                      command=lambda: self.parent_gui.tabview.set("添加单词"), 
                      **btn_style).pack(pady=10)
        
        self.start_review_btn = ctk.CTkButton(actions_container, text="🎯 开始复习", 
                      command=lambda: self.parent_gui.review_tab_comp.quick_review(), 
                      fg_color="#3498db", hover_color="#2980b9",
                      **btn_style)
        self.start_review_btn.pack(pady=10)
        
        ctk.CTkButton(actions_container, text="📊 查看统计", 
                      command=lambda: self.parent_gui.tabview.set("学习统计"), 
                      fg_color="#9b59b6", hover_color="#8e44ad",
                      **btn_style).pack(pady=10)
        
        ctk.CTkButton(actions_container, text="⚙️ 系统设置", 
                      command=lambda: self.parent_gui.tabview.set("设置"), 
                      fg_color="gray", hover_color="#555555",
                      **btn_style).pack(pady=10)

    def update_statistics(self):
        """更新首页数据和统计"""
        review_count = len(self.word_manager.get_words_for_review())
        stats = self.word_manager.get_statistics()
        total_words = stats['total_words']
        mastered_words = stats.get('mastered_words', 0)
        
        # 更新卡片数值
        self.total_val.configure(text=str(total_words))
        self.review_val.configure(text=str(review_count))
        self.mastered_val.configure(text=str(mastered_words))
        
        # 构建建议文本
        suggestion = "根据您的学习情况，我们有以下建议：\n\n"
        
        if review_count > 0:
            suggestion += f"📌 您有 {review_count} 个单词已经到达复习节点，建议立即开始复习，以巩固记忆。\n\n"
            self.start_review_btn.configure(state="normal")
        else:
            suggestion += "✅ 太棒了！您已经完成了所有待复习任务。现在是添加新单词的好时机。\n\n"
            # self.start_review_btn.configure(state="disabled") # 也可以不禁用，支持随时复习
        
        if total_words == 0:
            suggestion += "🆕 您还没有添加过单词。请点击右侧的 '添加单词' 按钮开始您的学习之旅吧！\n\n"
        elif total_words < 20:
            suggestion += "📈 词库量还在起步阶段，多添加一些生词可以更有效地利用复习系统。\n\n"
            
        suggestion += "💡 技巧：\n"
        suggestion += "• 每天坚持复习 10-20 分钟比偶尔长时间学习更有效。\n"
        suggestion += "• 在复习时尝试大声朗读，利用多种感官加强记忆。\n"
        suggestion += "• 统计页面可以帮您了解未来的复习压力，提前做好规划。"
        
        self.suggestion_text.configure(state="normal")
        self.suggestion_text.delete(1.0, tk.END)
        self.suggestion_text.insert(tk.END, suggestion)
        self.suggestion_text.configure(state="disabled")
