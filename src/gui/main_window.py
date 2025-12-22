#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词记忆助手 GUI 版本 (改进版)
基于 tkinter 的图形用户界面，提供更好的用户体验
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
import sys
import os
import json
import datetime
import threading
import time
import random
import logging

logger = logging.getLogger(__name__)

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.word_manager import WordManager
from core.scheduler import Scheduler
from api.buffered_dictionary_api import BufferedDictionaryAPI
from utils.common import init_logging


class WordReminderGUI:
    """单词记忆助手图形界面"""
    
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        
        # 设置 CustomTkinter 主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.root.title("单词记忆助手 - V1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 初始化日志
        init_logging()
        
        # 设置样式
        self.setup_styles()
        
        # 初始化数据管理器
        self.word_manager = WordManager()
        self.scheduler = Scheduler(self.word_manager)
        
        # 移除自动测试功能，让用户通过按钮手动操作
        
        # 初始化缓冲字典API
        self.buffered_dictionary_api = BufferedDictionaryAPI()
        self.word_manager.dictionary_api = self.buffered_dictionary_api
        
        # 性能优化相关变量
        self.last_refresh_time = 0
        self.refresh_cooldown = 1.0  # 刷新冷却时间（秒）
        self.async_operations = []
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.refresh_word_list()
        
        # 设置表单验证
        self.setup_form_validation()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定键盘快捷键
        self.root.bind('<Control-f>', lambda event: self.focus_search_entry())
        self.root.bind('<F3>', lambda event: self.search_next())
        
        # 检查词典API状态
        self.check_dictionary_api_status()
        
        # 初始化加载指示器
        self.loading_window = None
        
        # 表单验证状态
        self.form_validation_states = {}
        self.validation_errors = {}
        
        # 启动后台预加载
        self.start_background_preloading()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 获取当前主题模式
        mode = ctk.get_appearance_mode()
        is_dark = mode == "Dark"
        
        # 配置 Treeview 样式以匹配 CustomTkinter
        bg_color = "#2b2b2b" if is_dark else "#ffffff"
        fg_color = "#ffffff" if is_dark else "#000000"
        selected_color = "#1f538d" if is_dark else "#3b8ed0"
        header_bg = "#333333" if is_dark else "#eeeeee"
        
        style.theme_use('clam')
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=fg_color, 
                        fieldbackground=bg_color,
                        rowheight=30,
                        font=('Arial', 11))
        
        style.map("Treeview", 
                  background=[('selected', selected_color)],
                  foreground=[('selected', 'white')])
        
        style.configure("Treeview.Heading", 
                        background=header_bg, 
                        foreground=fg_color, 
                        relief="flat",
                        font=('Arial', 11, 'bold'))
        
        style.map("Treeview.Heading", 
                  background=[('active', selected_color)])

    def check_dictionary_api_status(self):
        """检查词典API状态"""
        # 在状态栏显示API状态
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            status_text = "词典API: 可用"
        else:
            status_text = "词典API: 不可用"
        
        # 更新状态栏
        self.status_bar.configure(text=status_text)
    
    def show_loading_indicator(self, message="正在处理..."):
        """显示加载指示器"""
        if self.loading_window is None or not self.loading_window.winfo_exists():
            self.loading_window = ctk.CTkToplevel(self.root)
            self.loading_window.title("请稍候")
            self.loading_window.geometry("300x150")
            self.loading_window.resizable(False, False)
            
            # 设置窗口居中
            self.loading_window.transient(self.root)
            self.loading_window.grab_set()
            
            # 容器
            container = ctk.CTkFrame(self.loading_window)
            container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 添加消息和进度条
            label = ctk.CTkLabel(container, text=message, font=('Arial', 14))
            label.pack(pady=(10, 15))
            
            self.loading_progress = ctk.CTkProgressBar(container, mode='indeterminate')
            self.loading_progress.pack(padx=20, pady=10, fill=tk.X)
            self.loading_progress.start()
            
            # 更新界面
            self.loading_window.update_idletasks()
        
        # 更新状态栏
        self.status_bar.configure(text=message)
    
    def hide_loading_indicator(self):
        """隐藏加载指示器"""
        if self.loading_window and self.loading_window.winfo_exists():
            if hasattr(self, 'loading_progress'):
                self.loading_progress.stop()
            self.loading_window.destroy()
            self.loading_window = None
        
        # 恢复状态栏信息
        self.check_dictionary_api_status()
    
    def start_background_preloading(self):
        """启动后台预加载"""
        # 获取当前词库中的单词列表用于预加载
        all_words = self.word_manager.get_all_words()
        if all_words:
            words_to_preload = [w['word'] for w in all_words[:50]]  # 预加载前50个单词
            self.buffered_dictionary_api.start_preloading(words_to_preload)
    
    def refresh_word_list_optimized(self):
        """优化后的刷新单词列表方法，避免频繁刷新"""
        current_time = time.time()
        if current_time - self.last_refresh_time < self.refresh_cooldown:
            # 还在冷却时间内，不进行刷新
            return
        
        self.last_refresh_time = current_time
        self.refresh_word_list()
    
    def async_operation(self, func, *args, **kwargs):
        """异步执行操作"""
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"异步操作执行失败: {e}")
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        self.async_operations.append(thread)
    
    def check_async_operations(self):
        """检查异步操作状态"""
        # 清理已完成的操作
        self.async_operations = [op for op in self.async_operations if op.is_alive()]
        return len(self.async_operations)
    
    def get_performance_stats(self):
        """获取性能统计信息"""
        if hasattr(self, 'buffered_dictionary_api'):
            cache_stats = self.buffered_dictionary_api.get_cache_stats()
            async_ops = self.check_async_operations()
            
            stats = {
                'cache_hit_rate': f"{cache_stats['cache_hit_rate']:.1f}%",
                'cache_size': cache_stats['cache_size'],
                'total_requests': cache_stats['total_requests'],
                'async_operations': async_ops,
                'word_count': self.word_manager.get_statistics().get('total_words', 0)
            }
            return stats
        return {}
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建顶部标题
        self.title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(self.title_frame, text="单词记忆助手", font=('Arial', 24, 'bold'))
        self.title_label.pack(side=tk.LEFT)
        
        self.version_label = ctk.CTkLabel(self.title_frame, text="V1.0", font=('Arial', 12))
        self.version_label.pack(side=tk.RIGHT)
        
        # 创建标签页 - 使用 CTkTabview
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 添加各个标签页
        self.home_tab = self.tabview.add("首页")
        self.add_tab = self.tabview.add("添加单词")
        self.view_tab = self.tabview.add("查看单词")
        self.review_tab = self.tabview.add("复习单词")
        self.search_tab = self.tabview.add("搜索单词")
        self.stats_tab = self.tabview.add("学习统计")
        self.settings_tab = self.tabview.add("系统设置")
        
        # 为了兼容旧代码，将 frame 引用指向 tab 对象
        self.home_frame = self.home_tab
        self.add_frame = self.add_tab
        self.view_frame = self.view_tab
        self.review_frame = self.review_tab
        self.search_frame = self.tabview.tab("搜索单词") # 修正：search_tab 已经是对象了
        self.stats_frame = self.tabview.tab("学习统计")
        self.settings_frame = self.tabview.tab("系统设置")
        
        # 调用各个标签页的创建函数
        self.create_home_tab_content()
        self.create_add_tab_content()
        self.create_view_tab_content()
        self.create_review_tab_content()
        self.create_search_tab_content()
        self.create_stats_tab_content()
        self.create_settings_tab_content()
        
        # 创建状态栏
        self.status_bar_frame = ctk.CTkFrame(self.root, height=30)
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ctk.CTkLabel(self.status_bar_frame, text="就绪", anchor=tk.W, padx=10)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X)
    
    def create_home_tab_content(self):
        """创建主页标签页内容"""
        # 欢迎信息
        welcome_frame = ctk.CTkFrame(self.home_frame)
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
        quick_frame = ctk.CTkFrame(self.home_frame)
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        quick_title = ctk.CTkLabel(quick_frame, text="快捷操作", font=('Arial', 18, 'bold'))
        quick_title.pack(pady=(15, 5))
        
        button_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # 使用更大的按钮
        ctk.CTkButton(button_frame, text="添加单词", 
                      command=lambda: self.tabview.set("添加单词"), 
                      width=140, height=40).pack(side=tk.LEFT, padx=20, pady=15)
        
        ctk.CTkButton(button_frame, text="开始复习", 
                      command=self.quick_review, 
                      width=140, height=40).pack(side=tk.LEFT, padx=20, pady=15)
        
        ctk.CTkButton(button_frame, text="查看统计", 
                      command=lambda: self.tabview.set("学习统计"), 
                      width=140, height=40).pack(side=tk.LEFT, padx=20, pady=15)
        
        # 今日学习提醒
        reminder_frame = ctk.CTkFrame(self.home_frame)
        reminder_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        reminder_title = ctk.CTkLabel(reminder_frame, text="今日学习提醒", font=('Arial', 18, 'bold'))
        reminder_title.pack(pady=(15, 5))
        
        self.reminder_text = ctk.CTkTextbox(reminder_frame, font=('Arial', 12))
        self.reminder_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.update_reminder()
    
    def create_add_tab_content(self):
        """创建添加单词标签页内容"""
        # 创建主容器
        main_container = ctk.CTkFrame(self.add_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(main_container, text="添加新单词", font=('Arial', 20, 'bold'))
        title_label.pack(pady=(20, 10))
        
        # 表单框架
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # 使用 grid 布局
        form_frame.grid_columnconfigure(1, weight=1)
        
        # 单词输入
        ctk.CTkLabel(form_frame, text="单词:", font=('Arial', 14)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=15)
        self.word_entry = ctk.CTkEntry(form_frame, placeholder_text="输入英文单词...", height=35)
        self.word_entry.grid(row=0, column=1, padx=10, pady=15, sticky=tk.EW)
        
        # 释义输入
        ctk.CTkLabel(form_frame, text="释义:", font=('Arial', 14)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=15)
        self.meaning_entry = ctk.CTkEntry(form_frame, placeholder_text="输入单词释义...", height=35)
        self.meaning_entry.grid(row=1, column=1, padx=10, pady=15, sticky=tk.EW)
        
        # 例句输入
        ctk.CTkLabel(form_frame, text="例句:", font=('Arial', 14)).grid(row=2, column=0, sticky=tk.W, padx=10, pady=15)
        self.example_entry = ctk.CTkEntry(form_frame, placeholder_text="输入例句 (可选)...", height=35)
        self.example_entry.grid(row=2, column=1, padx=10, pady=15, sticky=tk.EW)
        
        # 分类输入
        ctk.CTkLabel(form_frame, text="分类:", font=('Arial', 14)).grid(row=3, column=0, sticky=tk.W, padx=10, pady=15)
        self.category_entry = ctk.CTkEntry(form_frame, placeholder_text="输入分类 (可选)...", height=35)
        self.category_entry.grid(row=3, column=1, padx=10, pady=15, sticky=tk.EW)
        
        # 词汇级别
        ctk.CTkLabel(form_frame, text="词汇级别:", font=('Arial', 14)).grid(row=4, column=0, sticky=tk.W, padx=10, pady=15)
        self.vocab_level_var = tk.StringVar(value="cet6")
        self.vocab_combobox = ctk.CTkComboBox(form_frame, variable=self.vocab_level_var, 
                                             values=["cet4", "cet6", "gre"], height=35)
        self.vocab_combobox.grid(row=4, column=1, padx=10, pady=15, sticky=tk.W)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=30)
        
        self.add_button = ctk.CTkButton(button_frame, text="添加单词", command=self.add_word, 
                                       width=150, height=45, font=('Arial', 14, 'bold'))
        self.add_button.pack(side=tk.LEFT, padx=15)
        
        ctk.CTkButton(button_frame, text="清空", command=self.clear_form, 
                      width=100, height=45, fg_color="gray").pack(side=tk.LEFT, padx=15)
        
        ctk.CTkButton(button_frame, text="随机生成单词", command=self.generate_random_words, 
                      width=150, height=45, fg_color="#2c3e50").pack(side=tk.LEFT, padx=15)
    
    def create_view_tab_content(self):
        """创建查看单词标签页内容"""
        # 主容器
        main_container = ctk.CTkFrame(self.view_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 控制面板
        control_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        control_panel.pack(fill=tk.X, padx=10, pady=10)
        
        # 左侧按钮
        button_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        button_frame.pack(side=tk.LEFT)
        
        ctk.CTkButton(button_frame, text="刷新", command=self.refresh_word_list, width=80).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="删除选中", command=self.delete_selected_word, width=100, fg_color="#e74c3c", hover_color="#c0392b").pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="详情查看", command=self.show_selected_word_detail, width=100).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="获取详细信息", command=self.fetch_detailed_info, width=120).pack(side=tk.LEFT, padx=5)
        
        # 右侧搜索
        search_panel = ctk.CTkFrame(control_panel, fg_color="transparent")
        search_panel.pack(side=tk.RIGHT)
        
        ctk.CTkLabel(search_panel, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.view_search_var = tk.StringVar()
        self.view_search_var.trace('w', self.on_view_search_change)
        self.view_search_entry = ctk.CTkEntry(search_panel, textvariable=self.view_search_var, width=150)
        self.view_search_entry.pack(side=tk.LEFT, padx=5)
        
        # 搜索历史 (使用 CTkComboBox)
        self.view_search_history_var = tk.StringVar()
        self.view_search_history_combo = ctk.CTkComboBox(search_panel, variable=self.view_search_history_var, 
                                                        values=[], width=120, command=self.on_view_search_history_selected)
        self.view_search_history_combo.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(search_panel, text="删除历史", command=self.delete_view_search_history, width=70, fg_color="gray").pack(side=tk.LEFT, padx=2)
        
        # 加载搜索历史
        self.load_view_search_history()
        
        # 表格容器 (使用 CTkFrame 来包裹 Treeview)
        tree_container = ctk.CTkFrame(main_container)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格 (继续使用 ttk.Treeview)
        columns = ("单词", "释义", "分类", "添加日期", "复习次数", "下次复习")
        self.word_tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        
        # 定义列标题和宽度
        column_widths = [150, 250, 120, 120, 80, 120]
        column_headers = ["单词", "释义", "分类", "添加日期", "复习次数", "下次复习"]
        for i, (col, header) in enumerate(zip(columns, column_headers)):
            self.word_tree.heading(col, text=header)
            self.word_tree.column(col, width=column_widths[i], anchor=tk.CENTER)
        
        # 滚动条 (CustomTkinter 的滚动条不能直接用于 Treeview，所以用标准的)
        tree_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.word_tree.yview)
        self.word_tree.configure(yscrollcommand=tree_scroll_y.set)
        
        # 布局
        self.word_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.word_tree.bind("<Double-1>", self.on_word_double_click)
        self.word_tree.bind("<Button-3>", self.show_context_menu)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.word_tree, tearoff=0)
        self.context_menu.add_command(label="查看详情", command=self.show_selected_word_detail)
        self.context_menu.add_command(label="获取详细信息", command=self.fetch_detailed_info)
        self.context_menu.add_command(label="编辑单词", command=self.edit_selected_word)
        self.context_menu.add_command(label="删除单词", command=self.delete_selected_word)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选择被点击的项
        item = self.word_tree.identify_row(event.y)
        if item:
            self.word_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def show_selected_word_detail(self):
        """显示选中单词的详细信息"""
        selected = self.word_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个单词！")
            return
        
        item = selected[0]
        word = self.word_tree.item(item, 'values')[0]
        info = self.word_manager.get_word(word)
        
        # 创建详情窗口
        detail_window = ctk.CTkToplevel(self.root)
        detail_window.title(f"单词详情 - {word}")
        detail_window.geometry("600x600")
        detail_window.minsize(500, 400)
        
        # 设置窗口居中
        detail_window.transient(self.root)
        detail_window.grab_set()
        
        # 创建标签页
        detail_tabview = ctk.CTkTabview(detail_window)
        detail_tabview.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 基本信息标签页
        basic_tab = detail_tabview.add("基本信息")
        basic_scroll = ctk.CTkScrollableFrame(basic_tab, fg_color="transparent")
        basic_scroll.pack(fill=tk.BOTH, expand=True)
        
        def add_info_row(parent, label, value):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill=tk.X, pady=5)
            ctk.CTkLabel(row, text=f"{label}:", font=('Arial', 12, 'bold'), width=100, anchor=tk.W).pack(side=tk.LEFT)
            ctk.CTkLabel(row, text=str(value), font=('Arial', 12), wraplength=350, justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

        add_info_row(basic_scroll, "单词", word)
        add_info_row(basic_scroll, "释义", info['meaning'])
        
        if info.get('example'):
            add_info_row(basic_scroll, "例句", info['example'])
        
        if info.get('category'):
            add_info_row(basic_scroll, "分类", info['category'])
        
        if info.get('add_date'):
            add_info_row(basic_scroll, "添加日期", info['add_date'][:10])
        
        add_info_row(basic_scroll, "复习次数", info.get('review_count', 0))
        
        if info.get('last_reviewed'):
            add_info_row(basic_scroll, "上次复习", info['last_reviewed'][:10])
        
        if info.get('next_review'):
            add_info_row(basic_scroll, "下次复习", info['next_review'][:10])
        
        # 详细信息标签页（从词典API获取）
        detail_tab = detail_tabview.add("详细信息")
        detail_scroll = ctk.CTkScrollableFrame(detail_tab, fg_color="transparent")
        detail_scroll.pack(fill=tk.BOTH, expand=True)
        
        # 尝试从词典API获取更详细的信息
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            self.show_loading_indicator(f"正在获取单词 '{word}' 的详细信息...")
            try:
                word_info = self.word_manager.dictionary_api.get_word_info(word)
                if word_info:
                    # 显示音标
                    if word_info.get('phonetic'):
                        ctk.CTkLabel(detail_scroll, text="音标:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        ctk.CTkLabel(detail_scroll, text=word_info['phonetic'], font=('Arial', 12)).pack(anchor=tk.W, padx=20)
                    
                    # 显示英文释义
                    if word_info.get('meanings'):
                        ctk.CTkLabel(detail_scroll, text="英文释义:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        for i, meaning_info in enumerate(word_info['meanings']):
                            part_of_speech = meaning_info.get('part_of_speech', '')
                            definition = meaning_info.get('definition', '')
                            meaning_text = f"{i+1}. {part_of_speech}: {definition}" if part_of_speech else f"{i+1}. {definition}"
                            ctk.CTkLabel(detail_scroll, text=meaning_text, font=('Arial', 11), wraplength=450, justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=2)
                    
                    # 显示中文释义
                    if word_info.get('chinese_meanings'):
                        ctk.CTkLabel(detail_scroll, text="中文释义:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        for i, meaning_info in enumerate(word_info['chinese_meanings']):
                            part_of_speech = meaning_info.get('part_of_speech', '')
                            definition = meaning_info.get('definition', '')
                            meaning_text = f"{i+1}. {part_of_speech}: {definition}" if part_of_speech else f"{i+1}. {definition}"
                            ctk.CTkLabel(detail_scroll, text=meaning_text, font=('Arial', 11), wraplength=450, justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=2)
                    
                    # 显示例句
                    if word_info.get('examples'):
                        ctk.CTkLabel(detail_scroll, text="例句:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        for i, example in enumerate(word_info['examples']):
                            ctk.CTkLabel(detail_scroll, text=f"{i+1}. {example}", font=('Arial', 11), wraplength=450, justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=2)
                else:
                    ctk.CTkLabel(detail_scroll, text="未找到该单词的详细信息", font=('Arial', 12)).pack(pady=20)
            except Exception as e:
                ctk.CTkLabel(detail_scroll, text=f"获取详细信息时发生错误: {str(e)}", font=('Arial', 12)).pack(pady=20)
            finally:
                self.hide_loading_indicator()
        else:
            ctk.CTkLabel(detail_scroll, text="词典API不可用，无法获取详细信息", font=('Arial', 12)).pack(pady=20)
        
        # 添加关闭按钮
        button_frame = ctk.CTkFrame(detail_window, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ctk.CTkButton(button_frame, text="关闭", command=detail_window.destroy, width=100).pack(side=tk.RIGHT, padx=5)
    
    def fetch_detailed_info(self):
        """获取选中单词的详细信息"""
        selected = self.word_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个单词！")
            return
        
        item = selected[0]
        word = self.word_tree.item(item, 'values')[0]
        
        # 检查词典API是否可用
        if not hasattr(self.word_manager, 'dictionary_api') or not self.word_manager.dictionary_api:
            messagebox.showwarning("警告", "词典API不可用，无法获取详细信息！")
            return
        
        # 显示加载指示器
        self.show_loading_indicator(f"正在获取单词 '{word}' 的详细信息...")
        
        try:
            # 从词典API获取详细信息
            word_info = self.word_manager.dictionary_api.get_word_info(word)
            if not word_info:
                messagebox.showwarning("警告", f"未找到单词 '{word}' 的详细信息！")
                return
            
            # 获取当前单词信息
            current_info = self.word_manager.get_word(word)
            if current_info:
                meaning = current_info['meaning']
                example = current_info.get('example', '')
                phonetic = current_info.get('phonetic', '')

                # 更新释义（如果获取到了中文释义则使用中文释义）
                if word_info.get('chinese_meanings'):
                    meaning = word_info['chinese_meanings'][0]['definition']
                elif word_info.get('meanings'):
                    meaning = word_info['meanings'][0]['definition']
                
                # 如果当前没有例句但获取到了例句，则添加例句
                if not example and word_info.get('examples'):
                    example = word_info['examples'][0]
                
                # 获取音标
                if word_info.get('phonetic'):
                    phonetic = word_info['phonetic']
                
                # 保存更新
                if self.word_manager.update_word(word, meaning=meaning, example=example, phonetic=phonetic):
                    # 刷新单词列表
                    self.refresh_word_list()
                    messagebox.showinfo("成功", f"单词 '{word}' 的信息已更新！")
                else:
                    messagebox.showerror("错误", f"更新单词 '{word}' 失败！")
            else:
                messagebox.showwarning("警告", f"单词 '{word}' 不在词库中！")
        except Exception as e:
            messagebox.showerror("错误", f"获取单词详细信息时发生错误:\n{str(e)}")
        finally:
            # 隐藏加载指示器
            self.hide_loading_indicator()
    
    def create_review_tab_content(self):
        """创建复习单词标签页内容"""
        # 复习控制面板
        control_frame = ctk.CTkFrame(self.review_tab)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 按钮容器
        button_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_container.pack(fill=tk.X, padx=10, pady=10)
        
        # 使用更大的按钮
        self.start_review_button = ctk.CTkButton(button_container, text="开始复习", command=self.start_review, width=120)
        self.start_review_button.pack(side=tk.LEFT, padx=10)
        
        # 添加快捷复习按钮
        self.quick_review_button = ctk.CTkButton(button_container, text="快速复习", command=self.quick_review, width=120)
        self.quick_review_button.pack(side=tk.LEFT, padx=10)
        
        # 添加暂停/继续按钮
        self.pause_review_button = ctk.CTkButton(button_container, text="暂停复习", command=self.toggle_pause_review, 
                                                width=120, state=tk.DISABLED)
        self.pause_review_button.pack(side=tk.LEFT, padx=10)
        
        # 添加结束复习按钮
        self.stop_review_button = ctk.CTkButton(button_container, text="结束复习", command=self.stop_review, 
                                               width=120, state=tk.DISABLED, fg_color="#e74c3c", hover_color="#c0392b")
        self.stop_review_button.pack(side=tk.LEFT, padx=10)
        
        # 信息容器
        info_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        info_container.pack(fill=tk.X, padx=10, pady=10)
        
        self.review_count_label = ctk.CTkLabel(info_container, text="待复习单词: 0", font=('Arial', 14, 'bold'))
        self.review_count_label.pack(side=tk.LEFT, padx=10)
        
        # 添加刷新按钮
        ctk.CTkButton(info_container, text="刷新", command=self.update_review_count, width=80).pack(side=tk.LEFT, padx=10)
        
        # 复习区域 - 使用 CTkTabview 代替 Notebook
        self.review_tabview = ctk.CTkTabview(self.review_tab)
        self.review_tabview.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 添加标签页
        self.card_frame = self.review_tabview.add("学习卡片")
        self.stats_frame = self.review_tabview.add("复习统计")
        
        # 卡片内容
        card_content_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        card_content_frame.pack(expand=True, fill=tk.BOTH)
        
        # 单词显示区域
        word_display_frame = ctk.CTkFrame(card_content_frame)
        word_display_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        self.word_label = ctk.CTkLabel(word_display_frame, text="", font=('Arial', 32, 'bold'))
        self.word_label.pack(pady=(40, 10))
        
        self.phonetic_label = ctk.CTkLabel(word_display_frame, text="", font=('Arial', 18), text_color='gray')
        self.phonetic_label.pack(pady=5)
        
        self.meaning_label = ctk.CTkLabel(word_display_frame, text="", font=('Arial', 20))
        self.meaning_label.pack(pady=20)
        
        self.example_label = ctk.CTkLabel(word_display_frame, text="", font=('Arial', 16), text_color='gray')
        self.example_label.pack(pady=10)
        
        # 进度显示
        progress_frame = ctk.CTkFrame(card_content_frame, fg_color="transparent")
        progress_frame.pack(pady=10, fill=tk.X, padx=40)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="")
        self.progress_label.pack(side=tk.LEFT)
        
        # 添加进度条
        self.review_progress = ctk.CTkProgressBar(progress_frame)
        self.review_progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        self.review_progress.set(0)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(card_content_frame, fg_color="transparent")
        button_frame.pack(pady=20, fill=tk.X, padx=50)
        
        # 按钮居中容器
        button_sub_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_sub_frame.pack(expand=True)
        
        # 按钮布局
        self.not_know_button = ctk.CTkButton(button_sub_frame, text="不认识 (✗)", 
                                         command=lambda: self.review_feedback(False),
                                         state=tk.DISABLED, width=150, height=45, fg_color="#e74c3c", hover_color="#c0392b")
        self.not_know_button.pack(side=tk.LEFT, padx=20)
        
        self.know_button = ctk.CTkButton(button_sub_frame, text="认识 (✓)", 
                                     command=lambda: self.review_feedback(True),
                                     state=tk.DISABLED, width=150, height=45, fg_color="#2ecc71", hover_color="#27ae60")
        self.know_button.pack(side=tk.LEFT, padx=20)
        
        # 添加"稍后复习"按钮
        self.later_button = ctk.CTkButton(button_sub_frame, text="稍后复习", 
                                      command=lambda: self.review_feedback(None),
                                      state=tk.DISABLED, width=150, height=45, fg_color="#f39c12", hover_color="#d35400")
        self.later_button.pack(side=tk.LEFT, padx=20)
        
        # 在统计视图中添加控制按钮
        stats_control_frame = ctk.CTkFrame(self.stats_frame)
        stats_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkButton(stats_control_frame, text="导出复习记录", command=self.export_review_record, width=120).pack(side=tk.LEFT, padx=10, pady=10)
        ctk.CTkButton(stats_control_frame, text="重新开始", command=self.restart_review, width=120).pack(side=tk.LEFT, padx=10, pady=10)
        ctk.CTkButton(stats_control_frame, text="查看历史记录", command=self.show_review_history, width=120).pack(side=tk.LEFT, padx=10, pady=10)
        
        ctk.CTkLabel(stats_control_frame, text="复习完成后可导出记录或重新开始", font=('Arial', 12)).pack(side=tk.LEFT, padx=20)
        
        self.stats_text = ctk.CTkTextbox(self.stats_frame, font=('Arial', 12))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 初始化复习状态
        self.review_words = []
        self.current_review_index = 0
        self.current_review_word = None
        self.review_results = []  # 记录复习结果
        
        # 更新待复习单词数量
        self.update_review_count()
    
    def create_search_tab_content(self):
        """创建搜索单词标签页内容"""
        # 搜索主容器
        main_container = ctk.CTkFrame(self.search_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 搜索框区域
        search_area = ctk.CTkFrame(main_container)
        search_area.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(search_area, text="搜索单词", font=('Arial', 20, 'bold')).pack(pady=10)
        
        # 第一行：搜索输入和基本操作
        search_input_frame = ctk.CTkFrame(search_area, fg_color="transparent")
        search_input_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ctk.CTkLabel(search_input_frame, text="关键词:", font=('Arial', 14)).pack(side=tk.LEFT, padx=10)
        self.search_entry = ctk.CTkEntry(search_input_frame, placeholder_text="输入要搜索的单词或释义...", height=35)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.search_entry.bind('<Return>', lambda event: self.search_words())
        
        # 搜索和清空按钮
        self.search_button = ctk.CTkButton(search_input_frame, text="搜索", command=self.search_words, width=100, height=35)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(search_input_frame, text="清空", command=self.clear_search, width=80, height=35, fg_color="gray").pack(side=tk.LEFT, padx=5)
        
        # 第二行：搜索选项
        options_frame = ctk.CTkFrame(search_area, fg_color="transparent")
        options_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # 搜索模式
        ctk.CTkLabel(options_frame, text="匹配模式:", font=('Arial', 12)).pack(side=tk.LEFT, padx=10)
        self.search_mode_var = tk.StringVar(value="partial")
        ctk.CTkRadioButton(options_frame, text="模糊匹配", variable=self.search_mode_var, value="partial").pack(side=tk.LEFT, padx=10)
        ctk.CTkRadioButton(options_frame, text="精确匹配", variable=self.search_mode_var, value="exact").pack(side=tk.LEFT, padx=10)
        
        # 搜索范围
        ctk.CTkLabel(options_frame, text="搜索范围:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(30, 10))
        self.search_scope_var = tk.StringVar(value="all")
        ctk.CTkRadioButton(options_frame, text="全部", variable=self.search_scope_var, value="all").pack(side=tk.LEFT, padx=10)
        ctk.CTkRadioButton(options_frame, text="单词", variable=self.search_scope_var, value="word").pack(side=tk.LEFT, padx=10)
        ctk.CTkRadioButton(options_frame, text="释义", variable=self.search_scope_var, value="meaning").pack(side=tk.LEFT, padx=10)
        ctk.CTkRadioButton(options_frame, text="分类", variable=self.search_scope_var, value="category").pack(side=tk.LEFT, padx=10)
        
        # 排序选项
        ctk.CTkLabel(options_frame, text="排序:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(30, 10))
        self.sort_var = tk.StringVar(value="word")
        sort_options = [("单词", "word"), ("添加日期", "date"), ("分类", "category"), ("复习次数", "review_count")]
        for text, value in sort_options:
            ctk.CTkRadioButton(options_frame, text=text, variable=self.sort_var, value=value).pack(side=tk.LEFT, padx=5)
            
        # 实时搜索选项
        self.realtime_search_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="实时搜索", variable=self.realtime_search_var, 
                       command=self.toggle_realtime_search).pack(side=tk.LEFT, padx=20)
        
        # 结果区域
        result_container = ctk.CTkFrame(main_container)
        result_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 结果操作栏
        result_actions = ctk.CTkFrame(result_container, fg_color="transparent")
        result_actions.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(result_actions, text="搜索结果", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        ctk.CTkButton(result_actions, text="导出搜索结果", command=self.export_search_results, width=100).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(result_actions, text="复制选中项", command=self.copy_selected_search_results, width=100).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(result_actions, text="清空结果", command=self.clear_search_results, width=80, fg_color="gray").pack(side=tk.RIGHT, padx=5)
        
        self.search_stats_label = ctk.CTkLabel(result_actions, text="找到 0 个匹配项", text_color="#2ecc71")
        self.search_stats_label.pack(side=tk.RIGHT, padx=20)
        
        # 表格容器 (使用 CTkFrame 来包裹 Treeview)
        tree_container = ctk.CTkFrame(result_container)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建搜索结果表格
        columns = ("单词", "释义", "分类", "添加日期", "复习次数")
        self.search_tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        
        # 定义列
        col_widths = [150, 250, 100, 120, 80]
        for i, col in enumerate(columns):
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=col_widths[i], anchor=tk.CENTER)
            
        # 滚动条
        search_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.search_tree.yview)
        search_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.search_tree.xview)
        self.search_tree.configure(yscrollcommand=search_scroll_y.set, xscrollcommand=search_scroll_x.set)
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        search_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定双击事件
        self.search_tree.bind("<Double-1>", self.on_search_double_click)
        
        # 初始化搜索结果列表
        self.search_results = []
    
    def create_stats_tab_content(self):
        """创建统计信息标签页内容"""
        # 统计主容器
        main_container = ctk.CTkFrame(self.stats_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 统计控制面板
        control_frame = ctk.CTkFrame(main_container)
        control_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 按钮
        ctk.CTkButton(control_frame, text="刷新统计", command=self.show_statistics, width=100).pack(side=tk.LEFT, padx=10, pady=10)
        ctk.CTkButton(control_frame, text="导出图表", command=self.export_chart, width=100, fg_color="#2c3e50").pack(side=tk.LEFT, padx=10, pady=10)
        
        # 时间范围筛选
        filter_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        filter_frame.pack(side=tk.RIGHT, padx=10)
        
        ctk.CTkLabel(filter_frame, text="时间范围:").pack(side=tk.LEFT, padx=5)
        self.time_range_var = tk.StringVar(value="30")
        time_range_combo = ctk.CTkComboBox(filter_frame, variable=self.time_range_var, 
                                          values=["7", "14", "30", "60", "90"], width=100,
                                          command=self.on_time_range_change)
        time_range_combo.pack(side=tk.LEFT, padx=5)
        
        # 统计内容框架 - 使用 CTkTabview 来组织不同的统计视图
        stats_display_tabview = ctk.CTkTabview(main_container)
        stats_display_tabview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        overview_tab = stats_display_tabview.add("学习概览")
        trend_tab = stats_display_tabview.add("学习趋势")
        
        # 概览统计内容
        self.overview_text = ctk.CTkTextbox(overview_tab, font=('Arial', 13))
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 趋势统计内容
        self.chart_text = ctk.CTkTextbox(trend_tab, font=('Arial', 13))
        self.chart_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 为图表文本组件绑定鼠标点击事件
        self.chart_text.bind("<Button-1>", self.on_chart_click)
        
        # 初始化显示统计信息
        self.show_statistics()
    
    def create_settings_tab_content(self):
        """创建设置标签页内容"""
        # 设置主容器
        main_container = ctk.CTkFrame(self.settings_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 设置内容滚动容器
        settings_scroll = ctk.CTkScrollableFrame(main_container, label_text="系统设置")
        settings_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据管理部分
        data_frame = ctk.CTkFrame(settings_scroll)
        data_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(data_frame, text="数据管理", font=('Arial', 16, 'bold')).pack(pady=10, padx=15, anchor=tk.W)
        
        btn_container = ctk.CTkFrame(data_frame, fg_color="transparent")
        btn_container.pack(fill=tk.X, padx=15, pady=10)
        
        ctk.CTkButton(btn_container, text="备份数据", command=self.backup_data, width=120).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_container, text="恢复数据", command=self.restore_data, width=120).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_container, text="清空所有数据", command=self.clear_data, width=120, fg_color="#e74c3c", hover_color="#c0392b").pack(side=tk.LEFT, padx=10)
        
        # 界面设置部分
        ui_frame = ctk.CTkFrame(settings_scroll)
        ui_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(ui_frame, text="界面设置", font=('Arial', 16, 'bold')).pack(pady=10, padx=15, anchor=tk.W)
        
        theme_container = ctk.CTkFrame(ui_frame, fg_color="transparent")
        theme_container.pack(fill=tk.X, padx=15, pady=10)
        
        ctk.CTkLabel(theme_container, text="外观模式:").pack(side=tk.LEFT, padx=10)
        self.appearance_mode_var = tk.StringVar(value="System")
        ctk.CTkOptionMenu(theme_container, variable=self.appearance_mode_var, 
                          values=["System", "Light", "Dark"], 
                          command=self.change_appearance_mode).pack(side=tk.LEFT, padx=10)
        
        # 关于信息部分
        about_frame = ctk.CTkFrame(settings_scroll)
        about_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(about_frame, text="关于", font=('Arial', 16, 'bold')).pack(pady=10, padx=15, anchor=tk.W)
        
        about_text = """单词记忆助手 V1.0
        
基于艾宾浩斯遗忘曲线理论的智能单词记忆系统
帮助您科学高效地记忆单词

开发者: 计算机专业学生
开发时间: 2025年12月"""
        
        ctk.CTkLabel(about_frame, text=about_text, justify=tk.LEFT).pack(pady=10, padx=20)
    
    def change_appearance_mode(self, new_appearance_mode: str):
        """更改外观模式"""
        ctk.set_appearance_mode(new_appearance_mode)
    
    def add_word(self):
        """添加单词"""
        # 首先验证所有字段
        if not self.validate_all_fields():
            error_messages = []
            for field, message in self.validation_errors.items():
                error_messages.append(f"{field.capitalize()}: {message}")
            
            if error_messages:
                messagebox.showerror("输入错误", "请修正以下错误：\n" + "\n".join(error_messages))
            return
        
        word = self.word_entry.get().strip().lower()
        
        # 检查单词是否已存在（显示确认对话框）
        existing_word = self.word_manager.get_word(word)
        if existing_word:
            if not messagebox.askyesno("确认", f"单词 '{word}' 已存在，是否更新？"):
                return
        
        # 尝试从词典API获取单词信息
        meaning = ""
        example = ""
        phonetic = ""
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            # 显示加载指示器
            self.show_loading_indicator(f"正在获取单词 '{word}' 的信息...")
            
            try:
                word_info = self.word_manager.dictionary_api.get_word_info(word)
                if word_info:
                    # 显示获取到的信息供用户确认
                    info_text = f"找到单词信息:\n单词: {word_info['word']}"
                    if word_info['phonetic']:
                        info_text += f"\n音标: {word_info['phonetic']}"
                        phonetic = word_info['phonetic']
                    
                    # 优先显示中文释义
                    if word_info['chinese_meanings']:
                        info_text += "\n中文释义:"
                        for i, meaning_info in enumerate(word_info['chinese_meanings'][:3]):  # 只显示前3个中文释义
                            info_text += f"\n  {i+1}. {meaning_info['part_of_speech']}: {meaning_info['definition']}"
                        # 优先使用第一个中文释义作为默认释义
                        meaning = word_info['chinese_meanings'][0]['definition']
                    
                    # 如果没有中文释义，显示英文释义
                    elif word_info['meanings']:
                        info_text += "\n英文释义:"
                        for i, meaning_info in enumerate(word_info['meanings'][:3]):  # 只显示前3个释义
                            info_text += f"\n  {i+1}. {meaning_info['part_of_speech']}: {meaning_info['definition']}"
                        # 使用第一个释义作为默认释义
                        meaning = word_info['meanings'][0]['definition']
                    
                    if word_info['examples']:
                        info_text += "\n例句:"
                        for i, ex in enumerate(word_info['examples'][:2]):  # 只显示前2个例句
                            info_text += f"\n  {i+1}. {ex}"
                        # 使用第一个例句作为默认例句
                        example = word_info['examples'][0]
                    
                    # 显示获取到的信息
                    messagebox.showinfo("词典信息", info_text)
                else:
                    # 如果没有获取到信息，显示提示
                    messagebox.showinfo("词典信息", f"未找到单词 '{word}' 的定义")
            except Exception as e:
                # 网络请求或其他错误
                messagebox.showerror("错误", f"获取单词信息时发生错误:\n{str(e)}")
            finally:
                # 隐藏加载指示器
                self.hide_loading_indicator()
        
        # 获取用户输入的释义（如果有自动获取的释义，则预填充）
        if meaning:
            self.meaning_entry.delete(0, tk.END)
            self.meaning_entry.insert(0, meaning)
        
        # 获取用户输入的例句（如果有自动获取的例句，则预填充）
        if example:
            self.example_entry.delete(0, tk.END)
            self.example_entry.insert(0, example)
        
        # 如果没有自动获取到释义，要求用户必须输入
        meaning_input = self.meaning_entry.get().strip()
        if not meaning_input:
            messagebox.showwarning("输入错误", "释义不能为空！")
            self.add_button.configure(state=tk.NORMAL, text="添加单词")
            return
        
        example_input = self.example_entry.get().strip()
        category_input = self.category_entry.get().strip()
        
        # 添加或更新单词
        success = False
        if existing_word:
            success = self.word_manager.update_word(word, meaning=meaning_input, example=example_input, category=category_input, phonetic=phonetic)
            action = "更新"
        else:
            success = self.word_manager.add_word_direct(word, meaning_input, example_input, phonetic)
            # 如果有分类信息，由于 add_word_direct 不支持分类，我们需要额外更新一下
            if success and category_input:
                self.word_manager.update_word(word, category=category_input)
            action = "添加"
        
        if success:
            self.refresh_word_list()
            self.update_review_count()
            self.show_success_feedback(f"单词 '{word}' {action}成功！")
            self.clear_form()
            self.update_reminder()
        else:
            self.show_error_feedback(f"单词 '{word}' {action}失败！")
            self.add_button.configure(state=tk.NORMAL, text="添加单词")
    
    def setup_form_validation(self):
        """设置表单验证"""
        # 绑定实时验证事件
        self.word_entry.bind('<KeyRelease>', lambda e: self.validate_word_field())
        self.meaning_entry.bind('<KeyRelease>', lambda e: self.validate_meaning_field())
        self.example_entry.bind('<KeyRelease>', lambda e: self.validate_example_field())
        self.category_entry.bind('<KeyRelease>', lambda e: self.validate_category_field())
        
        # 绑定焦点事件
        self.word_entry.bind('<FocusOut>', lambda e: self.validate_word_field())
        self.meaning_entry.bind('<FocusOut>', lambda e: self.validate_meaning_field())
        self.example_entry.bind('<FocusOut>', lambda e: self.validate_example_field())
        self.category_entry.bind('<FocusOut>', lambda e: self.validate_category_field())
        
        # 初始化验证状态
        self.form_validation_states = {
            'word': 'neutral',
            'meaning': 'neutral',
            'example': 'neutral',
            'category': 'neutral'
        }
        self.validation_errors = {}
    
    def validate_word_field(self):
        """验证单词字段"""
        word = self.word_entry.get().strip()
        
        if not word:
            self.set_field_validation_state('word', 'error', "单词不能为空")
            return False
        
        if not word.isalpha():
            self.set_field_validation_state('word', 'error', "单词只能包含字母")
            return False
        
        if len(word) < 2:
            self.set_field_validation_state('word', 'warning', "单词太短，建议至少2个字符")
            return True  # 警告但不阻止提交
        
        if self.word_manager.get_word(word):
            self.set_field_validation_state('word', 'warning', "单词已存在，将更新现有记录")
            return True  # 警告但不阻止提交
        
        self.set_field_validation_state('word', 'success', "单词格式正确")
        return True
    
    def validate_meaning_field(self):
        """验证释义字段"""
        meaning = self.meaning_entry.get().strip()
        
        if not meaning:
            self.set_field_validation_state('meaning', 'error', "释义不能为空")
            return False
        
        if len(meaning) < 2:
            self.set_field_validation_state('meaning', 'warning', "释义太短，建议详细描述")
            return True  # 警告但不阻止提交
        
        if len(meaning) > 200:
            self.set_field_validation_state('meaning', 'warning', "释义过长，建议简洁明了")
            return True  # 警告但不阻止提交
        
        self.set_field_validation_state('meaning', 'success', "释义格式正确")
        return True
    
    def validate_example_field(self):
        """验证例句字段"""
        example = self.example_entry.get().strip()
        
        if example and len(example) < 5:
            self.set_field_validation_state('example', 'warning', "例句太短，建议提供完整句子")
            return True  # 警告但不阻止提交
        
        if example and len(example) > 500:
            self.set_field_validation_state('example', 'warning', "例句过长，建议简洁明了")
            return True  # 警告但不阻止提交
        
        if example:
            self.set_field_validation_state('example', 'success', "例句格式正确")
        else:
            self.set_field_validation_state('example', 'neutral', "例句可选")
        
        return True
    
    def validate_category_field(self):
        """验证分类字段"""
        category = self.category_entry.get().strip()
        
        if category and len(category) > 50:
            self.set_field_validation_state('category', 'warning', "分类名称过长，建议简洁")
            return True  # 警告但不阻止提交
        
        if category:
            self.set_field_validation_state('category', 'success', "分类格式正确")
        else:
            self.set_field_validation_state('category', 'neutral', "分类可选")
        
        return True
    
    def set_field_validation_state(self, field_name, state, message=None):
        """设置字段验证状态"""
        entry_widgets = {
            'word': self.word_entry,
            'meaning': self.meaning_entry,
            'example': self.example_entry,
            'category': self.category_entry
        }
        
        widget = entry_widgets.get(field_name)
        if not widget:
            return
        
        # 应用新样式 (CustomTkinter 使用 border_color)
        if state == 'error':
            widget.configure(border_color="#e74c3c")
            self.validation_errors[field_name] = message
        elif state == 'success':
            widget.configure(border_color="#2ecc71")
            if field_name in self.validation_errors:
                del self.validation_errors[field_name]
        elif state == 'warning':
            widget.configure(border_color="#f39c12")
            if field_name in self.validation_errors:
                del self.validation_errors[field_name]
        else:  # neutral
            widget.configure(border_color=ctk.ThemeManager.theme["CTkEntry"]["border_color"])
            if field_name in self.validation_errors:
                del self.validation_errors[field_name]
        
        self.form_validation_states[field_name] = state
        
        # 更新状态栏显示验证信息
        if message and state in ['error', 'warning']:
            self.status_bar.configure(text=f"{field_name.capitalize()}: {message}")
        elif state == 'success':
            self.status_bar.configure(text=f"{field_name.capitalize()}: 验证通过")
    
    def validate_all_fields(self):
        """验证所有字段"""
        validations = [
            self.validate_word_field(),
            self.validate_meaning_field(),
            self.validate_example_field(),
            self.validate_category_field()
        ]
        
        # 检查是否有错误
        has_errors = any(state == 'error' for state in self.form_validation_states.values())
        
        # 更新添加按钮状态
        if has_errors:
            self.add_button.configure(state="disabled")
        else:
            self.add_button.configure(state="normal")
        
        return not has_errors
    
    def show_success_feedback(self, message):
        """显示成功反馈"""
        # 在状态栏显示成功信息
        self.status_bar.configure(text=message, text_color='#2ecc71')
        
        # 短暂改变状态栏颜色
        def reset_status_bar():
            mode = ctk.get_appearance_mode()
            self.status_bar.configure(text_color="#ffffff" if mode == "Dark" else "#000000")
        
        # 3秒后恢复状态栏颜色
        self.root.after(3000, reset_status_bar)
        
        # 显示成功消息框
        messagebox.showinfo("成功", message)
    
    def show_error_feedback(self, message, field_name=None):
        """显示错误反馈"""
        # 在状态栏显示错误信息
        self.status_bar.configure(text=message, text_color='#e74c3c')
        
        # 短暂改变状态栏颜色
        def reset_status_bar():
            mode = ctk.get_appearance_mode()
            self.status_bar.configure(text_color="#ffffff" if mode == "Dark" else "#000000")
        
        # 3秒后恢复状态栏颜色
        self.root.after(3000, reset_status_bar)
        
        # 如果指定了字段，聚焦到该字段
        if field_name:
            entry_widgets = {
                'word': self.word_entry,
                'meaning': self.meaning_entry,
                'example': self.example_entry,
                'category': self.category_entry
            }
            widget = entry_widgets.get(field_name)
            if widget:
                widget.focus_set()
        
        # 显示错误消息框
        messagebox.showerror("错误", message)
    
    def show_warning_feedback(self, message):
        """显示警告反馈"""
        # 在状态栏显示警告信息
        self.status_bar.configure(text=message, text_color='#f39c12')
        
        # 短暂改变状态栏颜色
        def reset_status_bar():
            mode = ctk.get_appearance_mode()
            self.status_bar.configure(text_color="#ffffff" if mode == "Dark" else "#000000")
        
        # 3秒后恢复状态栏颜色
        self.root.after(3000, reset_status_bar)
        
        # 显示警告消息框
        messagebox.showwarning("警告", message)
    
    def clear_form(self):
        """清空表单"""
        self.word_entry.delete(0, tk.END)
        self.meaning_entry.delete(0, tk.END)
        self.example_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        
        # 重置验证状态
        for field in ['word', 'meaning', 'example', 'category']:
            self.set_field_validation_state(field, 'neutral')
        
        self.status_bar.configure(text="表单已清空")
        self.add_button.configure(state=tk.NORMAL)
    
    def refresh_word_list(self):
        """刷新单词列表"""
        # 清空现有数据
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 获取所有数据
        all_words = self.word_manager.get_all_words()
        
        # 添加新数据
        search_term = self.view_search_var.get().lower()
        for info in all_words:
            word = info['word']
            # 如果有搜索条件，过滤数据
            if search_term and search_term not in word.lower() and search_term not in info['meaning'].lower():
                continue
                
            add_date = info.get('added_date', '')[:10] if info.get('added_date') else ''
            review_count = info.get('review_count', 0)
            next_review = info.get('next_review', '')[:10] if info.get('next_review') else ''
            self.word_tree.insert("", tk.END, values=(word, info['meaning'], info.get('category', ''), add_date, review_count, next_review))
    
    def on_view_search_change(self, *args):
        """视图搜索框内容变化时触发"""
        self.refresh_word_list()
    
    def delete_selected_word(self):
        """删除选中的单词"""
        selected = self.word_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的单词！")
            return
        
        # 获取选中的单词
        item = selected[0]
        word = self.word_tree.item(item, 'values')[0]
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除单词 '{word}' 吗？"):
            if self.word_manager.delete_word(word):
                self.refresh_word_list()
                messagebox.showinfo("成功", f"单词 '{word}' 删除成功！")
            else:
                messagebox.showerror("错误", f"单词 '{word}' 删除失败！")
    
    def edit_selected_word(self):
        """编辑选中的单词"""
        selected = self.word_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的单词！")
            return
        
        # 获取选中的单词
        item = selected[0]
        word = self.word_tree.item(item, 'values')[0]
        info = self.word_manager.get_word(word)
        
        # 创建编辑窗口
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title(f"编辑单词 - {word}")
        edit_window.geometry("600x500")
        edit_window.minsize(500, 400)
        
        # 设置窗口居中
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # 主容器
        main_container = ctk.CTkFrame(edit_window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        ctk.CTkLabel(main_container, text="编辑单词信息", font=('Arial', 20, 'bold')).pack(pady=(10, 20))
        
        # 表单容器
        form_scroll = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        form_scroll.pack(fill=tk.BOTH, expand=True, padx=10)
        
        def add_edit_row(parent, label, variable, is_readonly=False):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill=tk.X, pady=10)
            ctk.CTkLabel(row, text=f"{label}:", font=('Arial', 13), width=80, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
            
            if is_readonly:
                entry = ctk.CTkEntry(row, textvariable=variable, font=('Arial', 12), state='readonly', height=35)
            else:
                entry = ctk.CTkEntry(row, textvariable=variable, font=('Arial', 12), height=35)
            
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return entry

        # 单词（只读）
        word_var = tk.StringVar(value=word)
        add_edit_row(form_scroll, "单词", word_var, is_readonly=True)
        
        # 释义
        meaning_var = tk.StringVar(value=info['meaning'])
        add_edit_row(form_scroll, "释义", meaning_var)
        
        # 例句
        example_var = tk.StringVar(value=info.get('example', ''))
        add_edit_row(form_scroll, "例句", example_var)
        
        # 分类
        category_var = tk.StringVar(value=info.get('category', ''))
        add_edit_row(form_scroll, "分类", category_var)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def save_changes():
            """保存修改"""
            # 更新单词信息
            meaning = meaning_var.get().strip()
            example = example_var.get().strip()
            category = category_var.get().strip()
            
            if not meaning:
                messagebox.showwarning("警告", "释义不能为空！")
                return
            
            if self.word_manager.update_word(word, meaning=meaning, example=example, category=category):
                # 刷新单词列表
                self.refresh_word_list()
                
                # 关闭编辑窗口
                edit_window.destroy()
                
                messagebox.showinfo("成功", f"单词 '{word}' 修改成功！")
            else:
                messagebox.showerror("错误", f"单词 '{word}' 修改失败！")
        
        ctk.CTkButton(button_frame, text="保存修改", command=save_changes, width=120, height=40).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(button_frame, text="取消", command=edit_window.destroy, width=100, height=40, fg_color="gray").pack(side=tk.LEFT, padx=15)
    
    def on_word_double_click(self, event):
        """单词列表双击事件"""
        selected = self.word_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        word = self.word_tree.item(item, 'values')[0]
        info = self.word_manager.get_word(word)
        
        # 显示单词详情
        detail_text = f"单词: {word}\n释义: {info['meaning']}\n"
        if info.get('example'):
            detail_text += f"例句: {info['example']}\n"
        if info.get('category'):
            detail_text += f"分类: {info['category']}\n"
        if info.get('add_date'):
            detail_text += f"添加日期: {info['add_date'][:10]}\n"
        detail_text += f"复习次数: {info.get('review_count', 0)}"
        
        messagebox.showinfo("单词详情", detail_text)
    
    def update_review_count(self):
        """更新待复习单词数量显示"""
        review_count = len(self.word_manager.get_words_for_review())
        self.review_count_label.configure(text=f"待复习单词: {review_count}")
    
    def start_review(self):
        """开始复习（标准复习，更新复习数据）"""
        # 设置复习类型为标准复习（更新复习数据）
        self.is_quick_review = False
        
        # 记录复习开始时间
        self.review_start_time = time.time()
        
        self.review_words = self.word_manager.get_words_for_review()
        
        if not self.review_words:
            messagebox.showinfo("提示", "暂无需要复习的单词。\n\n建议：\n1. 添加更多单词到词库中\n2. 等待已学单词到达复习时间")
            return
        
        # 随机打乱复习单词顺序
        random.shuffle(self.review_words)
        
        # 检查是否有新单词（未复习过的单词）
        new_words = [word for word in self.review_words if self.word_manager.get_word(word).get('review_count', 0) == 0]
        
        self.review_results = []  # 清空之前的复习结果
        self.current_review_index = 0
        
        # 显示欢迎信息
        if new_words:
            welcome_msg = f"开始复习！\n\n本次复习包含 {len(self.review_words)} 个单词：\n- 新单词: {len(new_words)} 个\n- 待复习单词: {len(self.review_words) - len(new_words)} 个"
            messagebox.showinfo("复习开始", welcome_msg)
        
        self.show_next_review_word()
        
        # 启用按钮
        self.know_button.configure(state=tk.NORMAL)
        self.not_know_button.configure(state=tk.NORMAL)
        self.later_button.configure(state=tk.NORMAL)
        self.start_review_button.configure(state=tk.DISABLED)
        
        # 启用暂停和停止按钮
        self.pause_review_button.configure(state=tk.NORMAL)
        self.stop_review_button.configure(state=tk.NORMAL)
        
        # 切换到卡片视图
        self.review_notebook.select(self.card_frame)
    
    def show_next_review_word(self):
        """显示下一个复习单词"""
        if self.current_review_index >= len(self.review_words):
            self.finish_review()
            return
        
        self.current_review_word = self.review_words[self.current_review_index]
        info = self.word_manager.get_word(self.current_review_word)
        
        # 显示单词信息
        self.word_label.configure(text=self.current_review_word)
        
        # 尝试从词典API获取音标信息
        phonetic_text = ""
        meaning_text = info['meaning']
        
        # 从词典API获取更详细的信息
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            word_info = self.word_manager.dictionary_api.get_word_info(self.current_review_word)
            if word_info:
                # 显示音标
                if word_info.get('phonetic'):
                    phonetic_text = f"/{word_info['phonetic']}/"
                
                # 显示更详细的释义
                if word_info.get('chinese_meanings'):
                    # 优先显示中文释义
                    meaning_text = word_info['chinese_meanings'][0]['definition'] if word_info['chinese_meanings'] else meaning_text
                elif word_info.get('meanings'):
                    # 如果没有中文释义，显示英文释义
                    meaning_text = word_info['meanings'][0]['definition']
                
                # 显示例句（如果没有用户自定义例句）
                if not info.get('example') and word_info.get('examples'):
                    example_text = word_info['examples'][0] if word_info['examples'] else ""
                    self.example_label.configure(text=example_text)
        
        # 更新显示
        self.phonetic_label.configure(text=phonetic_text)
        self.meaning_label.configure(text=meaning_text)
        
        # 如果没有从词典API获取到例句，则显示用户自定义的例句
        if not self.example_label.cget("text"):
            self.example_label.configure(text=info.get('example', ''))
        
        self.progress_label.configure(text=f"进度: {self.current_review_index + 1}/{len(self.review_words)}")
        
        # 添加复习提示
        review_count = info.get('review_count', 0)
        if review_count == 0:
            self.progress_label.configure(text=f"进度: {self.current_review_index + 1}/{len(self.review_words)} (新单词)")
        else:
            interval = info.get('interval', 1)
            self.progress_label.configure(text=f"进度: {self.current_review_index + 1}/{len(self.review_words)} (第{review_count}次复习, 间隔{interval}天)")
    
    def review_feedback(self, is_known):
        """处理复习反馈"""
        if self.current_review_word:
            info = self.word_manager.get_word(self.current_review_word)
            old_interval = info.get('interval', 1)
            
            # 记录复习结果
            self.review_results.append({
                'word': self.current_review_word,
                'known': is_known,
                'old_interval': old_interval
            })
            
            # 如果是"稍后复习"，则不更新调度，只记录结果
            if is_known is not None:
                # 检查复习类型：快捷复习不更新复习数据
                if not getattr(self, 'is_quick_review', False):
                    # 标准复习：更新单词调度 (使用 SM-2 质量映射)
                    # True (认识) -> 4 (良好)
                    # False (不认识) -> 1 (重来)
                    quality = 4 if is_known else 1
                    self.word_manager.update_review_status(self.current_review_word, quality)
                else:
                    # 快捷复习：不更新任何复习数据，只记录结果
                    pass
            else:
                # 对于"稍后复习"，我们将这个词移到队列末尾
                # 先移除当前单词
                if self.current_review_word in self.review_words:
                    self.review_words.remove(self.current_review_word)
                    # 然后添加到末尾
                    self.review_words.append(self.current_review_word)
                # 对于"稍后复习"，我们不需要增加索引，因为当前单词已经被移到末尾
                # 直接显示下一个单词即可
                self.show_next_review_word()
                return
        
        # 移动到下一个单词
        self.current_review_index += 1
        self.show_next_review_word()
    
    def finish_review(self):
        """完成复习"""
        # 清空当前显示的单词信息
        self.word_label.configure(text="复习已完成")
        self.phonetic_label.configure(text="")
        self.meaning_label.configure(text="请查看复习统计信息")
        self.example_label.configure(text="")
        self.progress_label.configure(text="")
        
        # 确保按钮状态正确设置
        try:
            # 禁用复习操作按钮
            self.know_button.configure(state=tk.DISABLED)
            self.not_know_button.configure(state=tk.DISABLED)
            self.later_button.configure(state=tk.DISABLED)
            
            # 确保开始复习按钮被重新启用
            self.start_review_button.configure(state=tk.NORMAL)
            
            # 禁用暂停和结束按钮
            self.pause_review_button.configure(state=tk.DISABLED)
            self.stop_review_button.configure(state=tk.DISABLED)
        except Exception as e:
            # 如果按钮状态设置失败，记录错误但继续执行
            print(f"按钮状态设置错误: {e}")
            # 尝试在UI线程中重新设置按钮状态
            self.after(100, lambda: self.start_review_button.configure(state=tk.NORMAL))
            self.after(100, lambda: self.pause_review_button.configure(state=tk.DISABLED))
            self.after(100, lambda: self.stop_review_button.configure(state=tk.DISABLED))
        
        # 显示复习统计
        self.show_review_stats()
        
        # 切换到统计视图（确保控件存在）
        try:
            self.review_notebook.select(self.stats_frame)
        except:
            # 如果切换失败，切换到卡片视图
            self.review_notebook.select(self.card_frame)
        
        # 检查复习类型
        is_quick_review = getattr(self, 'is_quick_review', False)
        
        if not is_quick_review:
            # 标准复习：更新所有相关数据
            self.update_review_count()
            self.update_reminder()
            self.refresh_word_list()
            self.show_statistics()
            self.status_bar.configure(text="复习已完成，界面已更新")
        else:
            # 快捷复习：只更新界面显示，不更新复习数据
            self.status_bar.configure(text="快捷复习已完成（练习模式）")
        
        # 显示详细的完成信息
        if self.review_results:
            known_count = sum(1 for result in self.review_results if result['known'])
            total_count = len(self.review_results)
            accuracy = (known_count / total_count) * 100 if total_count > 0 else 0
            
            if is_quick_review:
                completion_message = f"快捷复习完成！\n\n"
                completion_message += f"📊 本次练习统计:\n"
                completion_message += f"  • 练习单词数: {total_count}\n"
                completion_message += f"  • 掌握单词数: {known_count}\n"
                completion_message += f"  • 正确率: {accuracy:.1f}%\n\n"
                completion_message += f"💡 提示: 快捷复习是练习模式，不会影响正式的复习计划。"
            else:
                completion_message = f"复习完成！\n\n"
                completion_message += f"📊 本次复习统计:\n"
                completion_message += f"  • 复习单词数: {total_count}\n"
                completion_message += f"  • 掌握单词数: {known_count}\n"
                completion_message += f"  • 正确率: {accuracy:.1f}%\n\n"
                completion_message += f"💡 提示: 定期复习是记忆的关键，建议按照复习计划持续学习。"
            
            messagebox.showinfo("复习完成", completion_message)
        else:
            messagebox.showinfo("复习完成", "复习已完成，但未复习任何单词。")
        
        # 重置复习类型标志
        self.is_quick_review = False
    
    def toggle_pause_review(self):
        """暂停/继续复习"""
        if not hasattr(self, 'review_paused'):
            self.review_paused = False
        
        if self.review_paused:
            # 继续复习
            self.review_paused = False
            self.pause_review_button.configure(text="暂停复习")
            
            # 启用复习按钮
            self.know_button.configure(state=tk.NORMAL)
            self.not_know_button.configure(state=tk.NORMAL)
            self.later_button.configure(state=tk.NORMAL)
            
            # 更新状态栏
            self.status_bar.configure(text="复习已继续")
            
            # 显示当前单词
            if self.current_review_word:
                self.show_next_review_word()
        else:
            # 暂停复习
            self.review_paused = True
            self.pause_review_button.configure(text="继续复习")
            
            # 禁用复习按钮
            self.know_button.configure(state=tk.DISABLED)
            self.not_know_button.configure(state=tk.DISABLED)
            self.later_button.configure(state=tk.DISABLED)
            
            # 更新状态栏
            self.status_bar.configure(text="复习已暂停")
            
            # 显示暂停信息
            if self.current_review_word:
                self.word_label.configure(text="复习已暂停")
                self.meaning_label.configure(text="点击'继续复习'按钮继续学习")
                self.example_label.configure(text="")
                self.phonetic_label.configure(text="")
    
    def stop_review(self):
        """结束当前复习会话"""
        # 确认结束
        confirm = messagebox.askyesno("确认结束", "确定要结束当前复习会话吗？\n\n已完成的复习将保留，未完成的单词将不会更新复习数据。")
        if not confirm:
            return
        
        # 重置复习状态
        self.review_results = []
        self.current_review_index = 0
        self.current_review_word = None
        
        # 清空当前显示的单词信息
        self.word_label.configure(text="复习已结束")
        self.phonetic_label.configure(text="")
        self.meaning_label.configure(text="点击'开始复习'按钮重新开始")
        self.example_label.configure(text="")
        self.progress_label.configure(text="")
        
        # 禁用复习操作按钮
        self.know_button.configure(state=tk.DISABLED)
        self.not_know_button.configure(state=tk.DISABLED)
        self.later_button.configure(state=tk.DISABLED)
        
        # 启用开始复习按钮
        self.start_review_button.configure(state=tk.NORMAL)
        
        # 禁用暂停和结束按钮
        self.pause_review_button.configure(state=tk.DISABLED)
        self.stop_review_button.configure(state=tk.DISABLED)
        
        # 更新状态栏
        self.status_bar.configure(text="复习已结束")
        
        # 显示结束信息
        messagebox.showinfo("复习已结束", "当前复习会话已结束。\n\n您可以：\n1. 点击'开始复习'重新开始复习\n2. 查看复习统计了解已完成的进度")
    
    def show_review_history(self):
        """显示复习历史记录"""
        try:
            # 获取复习历史记录
            history = self.word_manager.get_review_history()
            
            if not history:
                messagebox.showinfo("复习历史", "暂无复习历史记录。")
                return
            
            # 创建历史记录窗口
            history_window = ctk.CTkToplevel(self.root)
            history_window.title("复习历史记录")
            history_window.geometry("900x700")
            history_window.minsize(700, 500)
            
            # 设置窗口居中
            history_window.transient(self.root)
            history_window.grab_set()
            
            # 创建主容器
            main_container = ctk.CTkFrame(history_window)
            main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 标题
            ctk.CTkLabel(main_container, text="复习历史记录", font=('Arial', 20, 'bold')).pack(pady=(0, 20))
            
            # 创建标签页 - 使用 CTkTabview
            history_tabview = ctk.CTkTabview(main_container)
            history_tabview.pack(fill=tk.BOTH, expand=True)
            
            overview_tab = history_tabview.add("概览")
            detail_tab = history_tabview.add("详细记录")
            
            # 概览内容 - 使用 CTkTextbox
            overview_text = ctk.CTkTextbox(overview_tab, font=('Arial', 13))
            overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 详细记录内容 - 使用 CTkTextbox
            detail_text = ctk.CTkTextbox(detail_tab, font=('Arial', 12))
            detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 生成概览统计
            total_sessions = len(history)
            total_words = sum(len(session.get('words', [])) for session in history)
            total_known = sum(session.get('known_count', 0) for session in history)
            total_unknown = sum(session.get('unknown_count', 0) for session in history)
            total_later = sum(session.get('later_count', 0) for session in history)
            
            overview_content = f"""复习历史概览
================

总复习次数: {total_sessions}
总复习单词数: {total_words}

掌握单词数: {total_known}
未掌握单词数: {total_unknown}
稍后复习单词数: {total_later}

平均正确率: {(total_known / total_words * 100) if total_words > 0 else 0:.1f}%

最近复习记录:
"""
            
            # 显示最近5次复习记录
            recent_sessions = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            for i, session in enumerate(recent_sessions):
                timestamp = session.get('timestamp', '未知时间')
                word_count = len(session.get('words', []))
                known_count = session.get('known_count', 0)
                accuracy = (known_count / word_count * 100) if word_count > 0 else 0
                
                overview_content += f"\n{i+1}. {timestamp[:16]}: {word_count}个单词, 正确率{accuracy:.1f}%"
            
            overview_text.insert(tk.END, overview_content)
            overview_text.configure(state="disabled")
            
            # 生成详细记录
            detail_content = "详细复习记录\n================\n\n"
            
            for i, session in enumerate(sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)):
                timestamp = session.get('timestamp', '未知时间')
                words = session.get('words', [])
                known_count = session.get('known_count', 0)
                unknown_count = session.get('unknown_count', 0)
                later_count = session.get('later_count', 0)
                accuracy = (known_count / len(words) * 100) if len(words) > 0 else 0
                
                detail_content += f"复习会话 #{i+1} - {timestamp}\n"
                detail_content += f"单词数: {len(words)}, 掌握: {known_count}, 未掌握: {unknown_count}, 稍后: {later_count}, 正确率: {accuracy:.1f}%\n"
                
                for j, word_result in enumerate(words):
                    word = word_result.get('word', '未知单词')
                    known = word_result.get('known')
                    
                    if known is True:
                        status = "✓ 掌握"
                    elif known is False:
                        status = "✗ 未掌握"
                    else:
                        status = "⧖ 稍后复习"
                    
                    detail_content += f"  {j+1}. {status} {word}\n"
                
                detail_content += "\n" + "-" * 50 + "\n\n"
            
            detail_text.insert(tk.END, detail_content)
            detail_text.configure(state="disabled")
            
            # 底部按钮
            button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def export_history():
                """导出历史记录"""
                try:
                    filename = f"复习历史_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    filepath = os.path.join(os.path.dirname(__file__), "..", filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(overview_content + "\n\n" + detail_content)
                    
                    messagebox.showinfo("导出成功", f"复习历史已导出到:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("导出失败", f"导出复习历史时发生错误:\n{str(e)}")
            
            ctk.CTkButton(button_frame, text="导出历史记录", command=export_history, width=150).pack(side=tk.RIGHT, padx=10)
            ctk.CTkButton(button_frame, text="关闭", command=history_window.destroy, width=100, fg_color="gray").pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示复习历史时发生错误:\n{str(e)}")
    
    def show_review_stats(self):
        """显示复习统计"""
        if not self.review_results:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "暂无复习记录。")
            return
        
        # 基本统计数据
        known_count = sum(1 for result in self.review_results if result['known'])
        unknown_count = sum(1 for result in self.review_results if result['known'] is False)
        later_count = sum(1 for result in self.review_results if result['known'] is None)
        total_count = len(self.review_results)
        accuracy = (known_count / total_count) * 100 if total_count > 0 else 0
        
        # 难度分析
        difficulty_analysis = self._analyze_word_difficulty()
        
        # 时间分析
        time_analysis = self._analyze_review_time()
        
        # 进度分析
        progress_analysis = self._analyze_learning_progress()
        
        # 构建详细的统计报告
        stats_text = f"""
📊 复习统计报告
=================

📈 基本统计
复习单词数: {total_count}
掌握单词数: {known_count}
未掌握单词数: {unknown_count}
稍后复习单词数: {later_count}
正确率: {accuracy:.1f}%

🎯 难度分析
{difficulty_analysis}

⏱️ 时间分析
{time_analysis}

📈 学习进度
{progress_analysis}

📋 详细记录:
"""
        
        # 收集需要查询详细信息的单词
        words_to_query = [result['word'] for result in self.review_results[:10]]  # 限制查询数量以提高性能
        
        # 批量获取单词的详细信息
        word_details = {}
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            for word in words_to_query:
                word_info = self.word_manager.dictionary_api.get_word_info(word)
                if word_info:
                    # 优先使用中文释义
                    if word_info['chinese_meanings']:
                        word_details[word] = word_info['chinese_meanings'][0]['definition']
                    elif word_info['meanings']:
                        word_details[word] = word_info['meanings'][0]['definition']
                    else:
                        word_details[word] = self.word_manager.get_word(word)['meaning']
                else:
                    word_details[word] = self.word_manager.get_word(word)['meaning']
        
        # 显示详细记录
        for i, result in enumerate(self.review_results, 1):
            if result['known'] is True:
                status = "✓ 掌握"
            elif result['known'] is False:
                status = "✗ 未掌握"
            else:
                status = "⧖ 稍后复习"
                
            word = result['word']
            # 显示单词及其释义
            meaning = word_details.get(word, self.word_manager.get_word(word)['meaning']) if word in word_details else self.word_manager.get_word(word)['meaning']
            word_info = self.word_manager.get_word(word)
            review_count = word_info.get('review_count', 0)
            stats_text += f"{i:2d}. {status} {word} - {meaning} (复习次数: {review_count}, 间隔: {result['old_interval']}天)\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def _analyze_word_difficulty(self):
        """分析单词难度"""
        if not self.review_results:
            return "暂无数据"
        
        # 根据复习次数和间隔分析难度
        difficulty_stats = {
            "简单": 0,
            "中等": 0,
            "困难": 0
        }
        
        for result in self.review_results:
            word = result['word']
            word_info = self.word_manager.get_word(word)
            review_count = word_info.get('review_count', 0)
            interval = word_info.get('interval', 1)
            
            # 根据复习次数和间隔判断难度
            if review_count <= 1 and interval <= 1:
                difficulty_stats["困难"] += 1
            elif review_count <= 3 and interval <= 3:
                difficulty_stats["中等"] += 1
            else:
                difficulty_stats["简单"] += 1
        
        total = len(self.review_results)
        analysis_text = ""
        for difficulty, count in difficulty_stats.items():
            percentage = (count / total) * 100 if total > 0 else 0
            analysis_text += f"{difficulty}: {count}个 ({percentage:.1f}%)\n"
        
        return analysis_text
    
    def _analyze_review_time(self):
        """分析复习时间"""
        if not hasattr(self, 'review_start_time') or not self.review_start_time:
            return "时间数据不可用"
        
        try:
            end_time = time.time()
            total_time = end_time - self.review_start_time
            avg_time_per_word = total_time / len(self.review_results) if self.review_results else 0
            
            return f"总复习时间: {total_time/60:.1f}分钟\n平均每个单词: {avg_time_per_word:.1f}秒"
        except:
            return "时间数据不可用"
    
    def _analyze_learning_progress(self):
        """分析学习进度"""
        if not self.review_results:
            return "暂无数据"
        
        # 分析掌握进度
        mastered_words = []
        struggling_words = []
        
        for result in self.review_results:
            word = result['word']
            word_info = self.word_manager.get_word(word)
            review_count = word_info.get('review_count', 0)
            
            if result['known']:
                mastered_words.append(word)
            elif not result['known'] and review_count > 2:
                struggling_words.append(word)
        
        progress_text = f"掌握单词: {len(mastered_words)}个\n"
        progress_text += f"需要重点复习: {len(struggling_words)}个\n"
        
        # 建议
        if len(struggling_words) > len(mastered_words):
            progress_text += "建议: 需要加强复习困难单词"
        elif len(mastered_words) >= len(self.review_results) * 0.8:
            progress_text += "建议: 学习进度良好，继续保持"
        else:
            progress_text += "建议: 稳步推进，注意复习频率"
        
        return progress_text
    
    def export_review_record(self):
        """导出复习记录"""
        if not self.review_results:
            messagebox.showwarning("警告", "暂无复习记录可导出。")
            return
        
        # 创建导出内容
        export_text = "单词复习记录\n===============\n\n"
        export_text += f"复习时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"复习单词数: {len(self.review_results)}\n\n"
        
        # 添加详细记录
        for result in self.review_results:
            if result['known'] is True:
                status = "✓ 掌握"
            elif result['known'] is False:
                status = "✗ 未掌握"
            else:
                status = "⧖ 稍后复习"
                
            word = result['word']
            info = self.word_manager.get_word(word)
            meaning = info['meaning']
            export_text += f"{status} {word} - {meaning}\n"
        
        # 保存到文件
        try:
            filename = f"复习记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(os.path.dirname(__file__), "..", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(export_text)
            
            messagebox.showinfo("成功", f"复习记录已导出到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出复习记录时发生错误:\n{str(e)}")
    
    def restart_review(self):
        """重新开始复习"""
        # 重置复习状态
        self.review_results = []
        self.current_review_index = 0
        self.current_review_word = None
        
        # 清空统计文本
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "准备开始新的复习会话...")
        
        # 启用开始复习按钮
        self.start_review_button.configure(state=tk.NORMAL)
        
        # 切换到卡片视图
        self.review_notebook.select(self.card_frame)
        
        messagebox.showinfo("提示", "已准备好重新开始复习。点击'开始复习'按钮开始新的复习会话。")
    
    def search_words(self):
        """搜索单词"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            messagebox.showwarning("输入错误", "请输入搜索关键词！")
            return
        
        # 清空现有数据
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # 获取搜索选项
        search_mode = self.search_mode_var.get()
        search_scope = self.search_scope_var.get()
        sort_by = self.sort_var.get()
        
        # 搜索匹配的单词
        all_words = self.word_manager.get_all_words()
        matched_words = []
        for info in all_words:
            word = info['word']
            # 根据搜索范围进行匹配
            if search_scope == "all":
                # 搜索所有字段
                search_fields = [word, info['meaning'], info.get('example', ''), info.get('category', '')]
                match_found = any(self._matches_keyword(field, keyword, search_mode) for field in search_fields if field)
            elif search_scope == "word":
                match_found = self._matches_keyword(word, keyword, search_mode)
            elif search_scope == "meaning":
                match_found = self._matches_keyword(info['meaning'], keyword, search_mode)
            elif search_scope == "category":
                match_found = self._matches_keyword(info.get('category', ''), keyword, search_mode)
            else:
                match_found = False
            
            if match_found:
                matched_words.append((word, info))
        
        # 对结果进行排序
        matched_words = self._sort_search_results(matched_words, sort_by)
        
        # 保存搜索结果
        self.search_results = matched_words
        
        # 显示搜索结果
        for word, info in matched_words:
            add_date = info.get('added_date', '')[:10] if info.get('added_date') else ''
            review_count = info.get('review_count', 0)
            self.search_tree.insert("", tk.END, values=(word, info['meaning'], info.get('category', ''), add_date, review_count))
        
        # 显示搜索结果统计
        self._show_search_stats(len(matched_words), keyword)
        
        # 已移除搜索历史功能
        pass
    
    def _matches_keyword(self, text, keyword, mode):
        """检查文本是否匹配关键词"""
        if not text:
            return False
            
        if mode == "exact":
            return text.lower() == keyword
        else:  # partial mode
            return keyword in text.lower()
    
    def _sort_search_results(self, results, sort_by):
        """对搜索结果进行排序"""
        if sort_by == "word":
            return sorted(results, key=lambda x: x[0])
        elif sort_by == "date":
            return sorted(results, key=lambda x: x[1].get('add_date', ''), reverse=True)
        elif sort_by == "category":
            return sorted(results, key=lambda x: x[1].get('category', ''))
        elif sort_by == "review_count":
            return sorted(results, key=lambda x: x[1].get('review_count', 0), reverse=True)
        else:
            return results
    
    def _show_search_stats(self, result_count, keyword):
        """显示搜索结果统计"""
        if result_count == 0:
            messagebox.showinfo("搜索结果", f"未找到包含 '{keyword}' 的单词")
            self.search_stats_label.configure(text="找到 0 个匹配项", text_color="#e74c3c")
        else:
            self.status_bar.configure(text=f"找到 {result_count} 个匹配的单词", text_color="#2ecc71")
            self.search_stats_label.configure(text=f"找到 {result_count} 个匹配项", text_color="#2ecc71")
            # 3秒后恢复状态栏
            self.root.after(3000, lambda: self.status_bar.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]))
    
    def clear_search(self):
        """清空搜索"""
        self.search_entry.delete(0, tk.END)
        # 清空搜索结果
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        # 重置状态栏
        self.status_bar.configure(text="", text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
    
    def on_search_key_release(self):
        """搜索框按键释放事件 - 实时搜索"""
        if self.realtime_search_var.get():
            # 延迟执行搜索，避免频繁搜索
            if hasattr(self, '_search_timer'):
                self.root.after_cancel(self._search_timer)
            self._search_timer = self.root.after(500, self.search_words)  # 500ms延迟
    
    def toggle_realtime_search(self):
        """切换实时搜索模式"""
        if self.realtime_search_var.get():
            self.status_bar.configure(text="实时搜索已启用", text_color="#3498db")
        else:
            self.status_bar.configure(text="实时搜索已禁用", text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
    

    

    

    

    

    

    

        
        print("=== 自动测试完成 ===")
    
    def load_view_search_history(self):
        """加载单词管理界面的搜索历史"""
        try:
            # 使用正确的数据文件路径
            data_dir = os.path.dirname(os.path.dirname(__file__))
            history_file = os.path.join(data_dir, "data", "view_search_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # 只显示最近10条历史记录
                    self.view_search_history_combo['values'] = history[:10]
        except Exception as e:
            print(f"加载单词管理搜索历史时出错: {e}")
    
    def save_view_search_history(self, keyword):
        """保存单词管理界面的搜索历史"""
        try:
            # 使用正确的数据文件路径
            data_dir = os.path.dirname(os.path.dirname(__file__))
            history_file = os.path.join(data_dir, "data", "view_search_history.json")
            
            # 加载现有历史记录
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 移除重复的关键词，并将新关键词添加到开头
            if keyword in history:
                history.remove(keyword)
            history.insert(0, keyword)
            
            # 只保留最近20条记录
            history = history[:20]
            
            # 保存历史记录
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            # 更新下拉框
            self.view_search_history_combo['values'] = history[:10]
            
        except Exception as e:
            print(f"保存单词管理搜索历史时出错: {e}")
    
    def on_view_search_history_selected(self, event):
        """单词管理搜索历史选择事件"""
        selected_keyword = self.view_search_history_var.get()
        if selected_keyword:
            self.view_search_var.set(selected_keyword)
            self.refresh_word_list()
    
    def delete_view_search_history(self):
        """删除单词管理界面的选中的搜索历史"""
        selected_keyword = self.view_search_history_var.get()
        if not selected_keyword:
            messagebox.showwarning("警告", "请先选择一个搜索历史记录进行删除")
            return
        
        # 确认删除
        confirm = messagebox.askyesno("确认删除", f"确定要删除搜索历史 '{selected_keyword}' 吗？")
        if not confirm:
            return
        
        try:
            # 使用正确的数据文件路径
            data_dir = os.path.dirname(os.path.dirname(__file__))
            history_file = os.path.join(data_dir, "data", "view_search_history.json")
            
            # 加载现有历史记录
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 删除选中的关键词
            if selected_keyword in history:
                history.remove(selected_keyword)
                
                # 保存更新后的历史记录
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                
                # 更新下拉框
                self.view_search_history_combo['values'] = history[:10]
                self.view_search_history_var.set("")
                
                messagebox.showinfo("成功", f"已删除搜索历史: {selected_keyword}")
            else:
                messagebox.showwarning("警告", "未找到该搜索历史记录")
                
        except Exception as e:
            messagebox.showerror("错误", f"删除搜索历史时发生错误:\n{str(e)}")
    
    def clear_view_search_history(self):
        """清空单词管理界面的所有搜索历史"""
        # 确认清空
        confirm = messagebox.askyesno("确认清空", "确定要清空所有搜索历史记录吗？\n此操作不可恢复！")
        if not confirm:
            return
        
        try:
            # 使用正确的数据文件路径
            data_dir = os.path.dirname(os.path.dirname(__file__))
            history_file = os.path.join(data_dir, "data", "view_search_history.json")
            
            # 清空历史记录文件
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
            # 更新下拉框
            self.view_search_history_combo['values'] = []
            self.view_search_history_var.set("")
            
            messagebox.showinfo("成功", "已清空所有搜索历史记录")
            
        except Exception as e:
            messagebox.showerror("错误", f"清空搜索历史时发生错误:\n{str(e)}")
    
    def on_search_double_click(self, event):
        """搜索结果双击事件"""
        selected = self.search_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        word = self.search_tree.item(item, 'values')[0]
        info = self.word_manager.get_word(word)
        
        # 显示单词详情
        detail_text = f"单词: {word}\n释义: {info['meaning']}\n"
        if info.get('example'):
            detail_text += f"例句: {info['example']}\n"
        if info.get('category'):
            detail_text += f"分类: {info['category']}\n"
        if info.get('add_date'):
            detail_text += f"添加日期: {info['add_date'][:10]}\n"
        detail_text += f"复习次数: {info.get('review_count', 0)}"
        
        messagebox.showinfo("单词详情", detail_text)
    
    def export_search_results(self):
        """导出搜索结果到文件"""
        if not hasattr(self, 'search_results') or not self.search_results:
            messagebox.showwarning("警告", "暂无搜索结果可导出！")
            return
        
        # 获取搜索关键词
        keyword = self.search_entry.get().strip()
        
        # 创建导出内容
        export_text = f"单词搜索结果\n{'='*30}\n\n"
        export_text += f"搜索关键词: {keyword}\n"
        export_text += f"搜索时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"匹配单词数: {len(self.search_results)}\n\n"
        export_text += f"{'单词':<20}{'释义':<30}{'分类':<15}{'添加日期':<12}{'复习次数'}\n"
        export_text += f"{'-'*85}\n"
        
        for word, info in self.search_results:
            meaning = info['meaning']
            category = info.get('category', '')
            add_date = info.get('add_date', '')[:10] if info.get('add_date') else ''
            review_count = info.get('review_count', 0)
            
            # 截断过长的文本
            if len(meaning) > 25:
                meaning = meaning[:25] + "..."
            
            export_text += f"{word:<20}{meaning:<30}{category:<15}{add_date:<12}{review_count}\n"
        
        # 保存到文件
        try:
            filename = f"搜索结果_{keyword}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(os.path.dirname(__file__), "..", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(export_text)
            
            messagebox.showinfo("导出成功", f"搜索结果已导出到:\n{filepath}")
            self.status_bar.configure(text=f"搜索结果已导出到 {filename}", text_color="#2ecc71")
        except Exception as e:
            messagebox.showerror("导出失败", f"导出搜索结果时发生错误:\n{str(e)}")
            self.status_bar.configure(text="导出失败", text_color="#e74c3c")
    
    def copy_selected_search_results(self):
        """复制选中的搜索结果到剪贴板"""
        selected_items = self.search_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要复制的单词！")
            return
        
        # 获取选中的单词信息
        copied_text = ""
        for item in selected_items:
            values = self.search_tree.item(item, 'values')
            word = values[0]
            meaning = values[1]
            category = values[2]
            
            copied_text += f"{word} - {meaning}"
            if category:
                copied_text += f" ({category})"
            copied_text += "\n"
        
        # 复制到剪贴板
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(copied_text.strip())
            
            count = len(selected_items)
            messagebox.showinfo("复制成功", f"已复制 {count} 个单词到剪贴板！")
            self.status_bar.configure(text=f"已复制 {count} 个单词到剪贴板", text_color="#2ecc71")
        except Exception as e:
            messagebox.showerror("复制失败", f"复制到剪贴板时发生错误:\n{str(e)}")
            self.status_bar.configure(text="复制失败", text_color="#e74c3c")
    
    def clear_search_results(self):
        """清空搜索结果"""
        # 清空搜索结果树
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # 清空搜索结果列表
        if hasattr(self, 'search_results'):
            self.search_results = []
        
        # 更新状态
        self.search_stats_label.configure(text="找到 0 个匹配项", text_color="#e74c3c")
        self.status_bar.configure(text="搜索结果已清空", text_color="#3498db")
        
        # 3秒后恢复状态栏
        self.root.after(3000, lambda: self.status_bar.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]))
    
    def show_statistics(self):
        """显示统计信息"""
        stats = self.word_manager.get_statistics()
        total_words = stats['total_words']
        reviewed_words = stats['reviewed_words']
        
        # 获取所有单词以计算总复习次数和本周复习情况
        all_words = self.word_manager.get_all_words()
        total_reviews = sum(info.get('review_count', 0) for info in all_words)
        
        # 计算最近7天的复习情况
        week_reviews = 0
        now = datetime.datetime.now()
        for info in all_words:
            last_reviewed = info.get('last_review') # 注意：SQLite 中字段名是 last_review
            if last_reviewed:
                if isinstance(last_reviewed, str):
                    last_reviewed_time = datetime.datetime.fromisoformat(last_reviewed)
                else:
                    last_reviewed_time = last_reviewed
                if (now - last_reviewed_time).days <= 7:
                    week_reviews += 1
        
        overview_text = f"""
学习统计概览
=================

总单词数: {total_words}
已复习单词数: {reviewed_words}
未复习单词数: {total_words - reviewed_words}

总体复习次数: {total_reviews}
本周复习单词数: {week_reviews}

"""
        
        if total_words > 0:
            review_rate = stats['review_rate']
            overview_text += f"复习率: {review_rate:.1f}%\n"
        
        if total_reviews > 0:
            avg_reviews_per_word = total_reviews / total_words if total_words > 0 else 0
            overview_text += f"平均每个单词复习次数: {avg_reviews_per_word:.1f}\n"
        
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(tk.END, overview_text)
        
        # 显示图表信息（改进版趋势图）
        self._generate_learning_trend_chart()
    
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
    
    def _setup_chart_text_tags(self):
        """设置图表文本的标签样式（简洁实用版）"""
        # 配置必要类型的标签样式
        self.chart_text._textbox.tag_configure("title", foreground="black", font=('Arial', 14, 'bold'))
        self.chart_text._textbox.tag_configure("header", foreground="black", font=('Arial', 11, 'bold'))
        self.chart_text._textbox.tag_configure("new_word", foreground="red")
        self.chart_text._textbox.tag_configure("review_word", foreground="orange")
        self.chart_text._textbox.tag_configure("mastered_word", foreground="purple")
        self.chart_text._textbox.tag_configure("positive", foreground="green")
        self.chart_text._textbox.tag_configure("negative", foreground="red")
        self.chart_text._textbox.tag_configure("neutral", foreground="blue")
        self.chart_text._textbox.tag_configure("metric_value", foreground="black")
        self.chart_text._textbox.tag_configure("date_header", foreground="gray")
        self.chart_text._textbox.tag_configure("separator", foreground="gray")
        self.chart_text._textbox.tag_configure("legend_label", foreground="black")

    def _insert_colored_text(self, text, tag=None):
        """插入带颜色的文本"""
        if tag:
            self.chart_text._textbox.insert(tk.END, text, tag)
        else:
            self.chart_text._textbox.insert(tk.END, text)

    def on_chart_click(self, event):
        """处理图表点击事件"""
        try:
            # 获取点击位置的索引
            index = self.chart_text._textbox.index(f"@{event.x},{event.y}")
            
            # 获取当前行的所有文本
            line_start = f"{index.split('.')[0]}.0"
            line_end = f"{index.split('.')[0]}.end"
            line_text = self.chart_text._textbox.get(line_start, line_end)
            
            # 根据点击的文本内容显示不同的详细信息
            if "学习趋势分析报告" in line_text:
                detail_info = "这是学习趋势分析报告的主标题。\n\n该报告展示了您的单词学习进度和趋势，帮助您了解自己的学习情况。"
            elif "关键学习指标" in line_text:
                detail_info = "关键学习指标部分展示了您的整体学习情况：\n\n" \
                             "• 总单词数：您添加到系统中的所有单词数量\n" \
                             "• 已复习单词：至少复习过一次的单词数量\n" \
                             "• 已掌握单词：复习次数达到3次及以上的单词数量\n" \
                             "• 复习率：已复习单词占总单词数的百分比\n" \
                             "• 掌握率：已掌握单词占总单词数的百分比"
            elif "最近14天学习趋势" in line_text:
                detail_info = "最近14天学习趋势图表展示了您最近两周的学习活动：\n\n" \
                             "• 新增单词趋势（➕）：每天添加的新单词数量\n" \
                             "• 复习单词趋势（📚）：每天复习的单词数量\n" \
                             "• 掌握单词趋势（🎯）：每天达到掌握标准的单词数量\n\n" \
                             "通过这个图表，您可以清楚地看到自己学习的活跃度和进步情况。"
            elif "学习效率分析" in line_text:
                detail_info = "学习效率分析部分评估您的学习效果：\n\n" \
                             "• 新增→复习转化率：新添加的单词转化为复习的比例\n" \
                             "• 复习→掌握转化率：复习过的单词转化为掌握的比例\n\n" \
                             "这些指标可以帮助您了解学习过程中的薄弱环节。"
            elif "个性化学习建议" in line_text:
                detail_info = "个性化学习建议基于您的学习数据提供：\n\n" \
                             "• 复习率建议：根据您的复习频率给出的建议\n" \
                             "• 掌握率建议：根据您的掌握情况给出的建议\n" \
                             "• 学习趋势建议：基于近期学习积极性的变化给出的建议\n\n" \
                             "遵循这些建议可以帮助您优化学习策略。"
            elif "学习目标建议" in line_text:
                detail_info = "学习目标建议根据您的当前水平制定：\n\n" \
                             "• 长期目标：基于您的词汇量设定的阶段性目标\n" \
                             "• 短期目标：针对您当前需要改进的方面设定的具体目标\n\n" \
                             "设定合理的目标有助于保持学习动力和方向。"
            elif "📈" in line_text and "新增单词趋势" not in line_text:
                detail_info = "📈 上升趋势图标表示该指标表现良好，超过了预期目标。"
            elif "📉" in line_text:
                detail_info = "📉 下降趋势图标表示该指标表现不佳，低于预期目标，需要关注和改进。"
            elif "➡️" in line_text:
                detail_info = "➡️ 稳定趋势图标表示该指标表现平稳，维持在正常水平。"
            elif "📊" in line_text:
                detail_info = "这是图表或数据展示区域的标识符。"
            elif "🎯" in line_text:
                detail_info = "🎯 目标达成图标表示某项学习目标已经实现。"
            elif "📚" in line_text:
                detail_info = "📚 学习活动图标表示与学习相关的活动。"
            elif "➕" in line_text:
                detail_info = "➕ 新增图标表示新添加的内容或活动。"
            elif "💡" in line_text:
                detail_info = "💡 建议图标表示这是一个有用的建议或提示。"
            elif "总单词数" in line_text or "已复习单词" in line_text or "已掌握单词" in line_text:
                detail_info = "这是您的核心学习指标之一。\n\n" \
                             "通过跟踪这些数字，您可以了解自己的学习进度和成就。"
            elif "复习率" in line_text or "掌握率" in line_text:
                detail_info = "这是衡量学习效果的重要指标。\n\n" \
                             "较高的复习率和掌握率表明您的学习方法有效，记忆效果良好。"
            elif any(symbol in line_text for symbol in ["■■", "●●", "★★"]):
                detail_info = "这是图表的可视化表示部分。\n\n" \
                             "不同的符号代表不同类型的学习活动：\n" \
                             "• ■■：新增单词\n" \
                             "• ●●：复习单词\n" \
                             "• ★★：掌握单词"
            else:
                detail_info = f"您点击了图表的这一行:\n\n{line_text}\n\n" \
                             "这是学习趋势图表的一部分，展示了您的学习进度和趋势。"
            
            # 显示详细信息
            messagebox.showinfo("图表详情", detail_info)
        except Exception as e:
            # 如果出现错误，显示通用信息
            messagebox.showinfo("图表详情", "点击了图表区域")

    def _generate_learning_trend_chart(self):
        """生成学习趋势图表（简洁实用版）"""
        # 清空现有内容
        self.chart_text.delete(1.0, tk.END)
        
        # 设置标签样式
        self._setup_chart_text_tags()
        
        # 获取所有单词数据
        all_words = self.word_manager.get_all_words()
        if not all_words:
            self._insert_colored_text("暂无数据可显示趋势图。", "title")
            return
        
        # 获取时间范围设置
        try:
            days_range = int(self.time_range_var.get())
        except (ValueError, AttributeError):
            days_range = 30  # 默认30天
        
        # 计算指定天数的数据
        now = datetime.datetime.now()
        daily_new_words = {}  # 每日新增单词数
        daily_reviewed_words = {}  # 每日复习单词数
        daily_mastered_words = {}  # 每日掌握单词数（掌握等级>=4）
        
        # 初始化指定天数的数据
        for i in range(days_range):
            date_key = (now - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            daily_new_words[date_key] = 0
            daily_reviewed_words[date_key] = 0
            daily_mastered_words[date_key] = 0
        
        # 统计每日数据
        for info in all_words:
            # 统计新增单词
            add_date = info.get('added_date') # 注意：SQLite 中字段名是 added_date
            if add_date:
                try:
                    if isinstance(add_date, str):
                        add_date_obj = datetime.datetime.fromisoformat(add_date)
                    else:
                        add_date_obj = add_date
                    add_date_key = add_date_obj.strftime('%Y-%m-%d')
                    if add_date_key in daily_new_words:
                        daily_new_words[add_date_key] += 1
                except (ValueError, TypeError):
                    pass
            
            # 统计复习单词
            last_reviewed = info.get('last_review') # 注意：SQLite 中字段名是 last_review
            if last_reviewed:
                try:
                    if isinstance(last_reviewed, str):
                        review_date_obj = datetime.datetime.fromisoformat(last_reviewed)
                    else:
                        review_date_obj = last_reviewed
                    review_date_key = review_date_obj.strftime('%Y-%m-%d')
                    if review_date_key in daily_reviewed_words:
                        daily_reviewed_words[review_date_key] += 1
                        
                        # 统计掌握单词（掌握等级>=4）
                        if info.get('mastery_level', 0) >= 4:
                            daily_mastered_words[review_date_key] += 1
                except (ValueError, TypeError):
                    pass
        
        # 插入标题
        self._insert_colored_text("学习趋势图表\n", "title")
        self._insert_colored_text("=" * 20 + "\n", "separator")
        
        # 添加关键指标
        stats = self.word_manager.get_statistics()
        total_words = stats['total_words']
        reviewed_words = stats['reviewed_words']
        mastered_words = stats['mastered_words']
        review_rate = stats['review_rate']
        mastery_rate = (mastered_words / total_words * 100) if total_words > 0 else 0
        
        # 关键指标展示
        self._insert_colored_text(f"总单词数: {total_words}\n", "metric_value")
        self._insert_colored_text(f"已复习单词: {reviewed_words}\n", "metric_value")
        self._insert_colored_text(f"已掌握单词: {mastered_words}\n", "metric_value")
        self._insert_colored_text(f"复习率: {review_rate:.1f}%\n", "metric_value")
        self._insert_colored_text(f"掌握率: {mastery_rate:.1f}%\n\n", "metric_value")
        
        # 进度条 (5段)
        self._insert_colored_text("学习进度:\n", "header")
        review_rate_tag = "positive" if review_rate >= 70 else "negative" if review_rate < 30 else "neutral"
        self._insert_colored_text(f"复习 [{'█' * int(review_rate/20)}{'░' * (5-int(review_rate/20))}] {review_rate:.1f}%\n", review_rate_tag)
        
        mastery_rate_tag = "positive" if mastery_rate >= 50 else "negative" if mastery_rate < 20 else "neutral"
        self._insert_colored_text(f"掌握 [{'█' * int(mastery_rate/20)}{'░' * (5-int(mastery_rate/20))}] {mastery_rate:.1f}%\n\n", mastery_rate_tag)
        
        # 时间趋势图（显示最近几天）
        display_days = min(days_range, 7)  # 最多显示7天
        self._insert_colored_text(f"最近{display_days}天学习情况:\n", "header")
        
        # 显示每日数据
        for i in range(display_days-1, -1, -1):
            date_key = (now - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            date_display = (now - datetime.timedelta(days=i)).strftime('%m-%d')
            new_count = daily_new_words.get(date_key, 0)
            review_count = daily_reviewed_words.get(date_key, 0)
            mastered_count = daily_mastered_words.get(date_key, 0)
            
            self._insert_colored_text(f"{date_display}:", "date_header")
            self._insert_colored_text(f" +{new_count}", "new_word")
            self._insert_colored_text(f" 📚{review_count}", "review_word")
            self._insert_colored_text(f" 🎯{mastered_count}\n", "mastered_word")
        
        self._insert_colored_text("\n图例: +新增单词 📚复习单词 🎯掌握单词\n", "legend_label")
    
    def quick_review(self):
        """快捷复习 - 随机复习所有已存在的单词（不更新复习数据）"""
        self.notebook.select(self.review_frame)
        
        # 设置复习类型为快捷复习（不更新复习数据）
        self.is_quick_review = True
        
        # 记录复习开始时间
        self.review_start_time = time.time()
        
        # 获取所有单词
        all_words_info = self.word_manager.get_all_words()
        all_words = [w['word'] for w in all_words_info]
        
        if not all_words:
            messagebox.showinfo("提示", "词库中暂无单词。\n\n建议：\n1. 添加更多单词到词库中\n2. 使用随机生成功能添加单词")
            return
        
        # 随机选择单词进行复习（最多选择20个单词）
        import random
        random.shuffle(all_words)
        self.review_words = all_words[:20]  # 最多复习20个单词
        
        # 检查是否有新单词（未复习过的单词）
        new_words = []
        for word in self.review_words:
            word_info = self.word_manager.get_word(word)
            if word_info and word_info.get('review_count', 0) == 0:
                new_words.append(word)
        
        self.review_results = []  # 清空之前的复习结果
        self.current_review_index = 0
        
        # 显示欢迎信息
        welcome_msg = f"开始快捷复习！\n\n本次将随机复习 {len(self.review_words)} 个单词：\n"
        if new_words:
            welcome_msg += f"- 新单词: {len(new_words)} 个\n"
        welcome_msg += f"- 已复习单词: {len(self.review_words) - len(new_words)} 个\n\n"
        welcome_msg += f"💡 提示: 快捷复习是单纯的练习，不会更新复习日期和间隔。"
        
        messagebox.showinfo("快捷复习开始", welcome_msg)
        
        self.show_next_review_word()
        
        # 启用按钮
        self.know_button.configure(state=tk.NORMAL)
        self.not_know_button.configure(state=tk.NORMAL)
        self.later_button.configure(state=tk.NORMAL)
        self.start_review_button.configure(state=tk.DISABLED)
        
        # 启用暂停和结束按钮
        self.pause_review_button.configure(state=tk.NORMAL)
        self.stop_review_button.configure(state=tk.NORMAL)
        
        # 切换到卡片视图
        self.review_notebook.select(self.card_frame)
        
        # 更新状态栏
        self.status_bar.configure(text=f"快捷复习已开始，将随机复习 {len(self.review_words)} 个单词（练习模式）")
    
    def focus_search_entry(self):
        """聚焦到搜索输入框"""
        self.notebook.select(self.search_frame)
        self.search_entry.focus_set()
        self.status_bar.configure(text="已聚焦到搜索框，可以开始输入关键词")
    
    def search_next(self):
        """搜索下一个匹配项"""
        if hasattr(self, 'search_results') and self.search_results:
            # 如果有搜索结果，可以在这里实现搜索下一个功能
            self.status_bar.configure(text="搜索下一个功能已激活")
        else:
            self.status_bar.configure(text="请先执行搜索操作")
    
    def backup_data(self):
        """备份数据"""
        try:
            import shutil
            os.makedirs("data/backups", exist_ok=True)
            backup_path = f"data/backups/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            db_file = "data/words.db"
            if os.path.exists(db_file):
                shutil.copy(db_file, backup_path)
                messagebox.showinfo("成功", f"数据备份成功！\n备份文件: {backup_path}")
            else:
                messagebox.showerror("错误", "数据库文件不存在，无法备份")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败: {str(e)}")
    
    def restore_data(self):
        """恢复数据"""
        messagebox.showinfo("提示", "请手动将备份的 .db 文件替换为 data/words.db 来恢复数据")
    
    def clear_data(self):
        """清空数据"""
        if messagebox.askyesno("确认", "确定要清空所有单词数据吗？此操作不可恢复！"):
            if self.word_manager.clear_all_words():
                self.refresh_word_list()
                self.update_review_count()
                self.update_reminder()
                self.show_statistics()
                messagebox.showinfo("成功", "所有数据已清空！")
            else:
                messagebox.showerror("错误", "清空数据失败！")
    
    def export_chart(self):
        """导出图表数据"""
        try:
            # 导入必要的模块
            from tkinter import filedialog
            import csv
            
            # 获取保存文件路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="导出图表数据"
            )
            
            if not file_path:
                return  # 用户取消了保存操作
            
            # 获取时间范围设置
            try:
                days_range = int(self.time_range_var.get())
            except (ValueError, AttributeError):
                days_range = 30  # 默认30天
            
            # 计算指定天数的数据
            now = datetime.datetime.now()
            daily_new_words = {}  # 每日新增单词数
            daily_reviewed_words = {}  # 每日复习单词数
            daily_mastered_words = {}  # 每日掌握单词数（复习次数>=3）
            
            # 初始化指定天数的数据
            for i in range(days_range):
                date_key = (now - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                daily_new_words[date_key] = 0
                daily_reviewed_words[date_key] = 0
                daily_mastered_words[date_key] = 0
            
            # 统计每日数据
            all_words = self.word_manager.get_all_words()
            for info in all_words:
                # 统计新增单词
                add_date = info.get('added_date')
                if add_date:
                    try:
                        if isinstance(add_date, str):
                            add_date_obj = datetime.datetime.fromisoformat(add_date)
                        else:
                            add_date_obj = add_date
                        add_date_key = add_date_obj.strftime('%Y-%m-%d')
                        if add_date_key in daily_new_words:
                            daily_new_words[add_date_key] += 1
                    except (ValueError, TypeError):
                        pass
                
                # 统计复习单词
                last_reviewed = info.get('last_review')
                if last_reviewed:
                    try:
                        if isinstance(last_reviewed, str):
                            review_date_obj = datetime.datetime.fromisoformat(last_reviewed)
                        else:
                            review_date_obj = last_reviewed
                        review_date_key = review_date_obj.strftime('%Y-%m-%d')
                        if review_date_key in daily_reviewed_words:
                            daily_reviewed_words[review_date_key] += 1
                            
                            # 统计掌握单词（掌握等级>=4）
                            if info.get('mastery_level', 0) >= 4:
                                daily_mastered_words[review_date_key] += 1
                    except (ValueError, TypeError):
                        pass
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入表头
                writer.writerow(['日期', '新增单词数', '复习单词数', '掌握单词数'])
                
                # 按日期排序并写入数据
                sorted_dates = sorted(daily_new_words.keys())
                for date in sorted_dates:
                    writer.writerow([
                        date,
                        daily_new_words.get(date, 0),
                        daily_reviewed_words.get(date, 0),
                        daily_mastered_words.get(date, 0)
                    ])
            
            messagebox.showinfo("导出成功", f"图表数据已成功导出到:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出图表数据时发生错误:\n{str(e)}")
    
    def on_time_range_change(self, event=None):
        """处理时间范围变化事件"""
        # 当时间范围改变时，重新生成学习趋势图表
        self.show_statistics()
    
    def generate_random_words(self):
        """生成随机单词并直接插入到现有输入字段中"""
        # 检查词典API是否可用
        if not hasattr(self.word_manager, 'dictionary_api') or not self.word_manager.dictionary_api:
            messagebox.showerror("错误", "词典API不可用，无法生成随机单词！")
            return
            
        # 显示加载指示器
        self.show_loading_indicator("正在从词典获取随机单词...")
        
        # 异步执行获取操作
        def async_generate():
            try:
                # 获取1个随机单词（因为我们直接插入到输入框中）
                # 检查词汇级别变量是否已初始化
                if not hasattr(self, 'vocab_level_var'):
                    vocab_level = "cet6"  # 默认使用CET6
                else:
                    vocab_level = self.vocab_level_var.get()
                
                # 使用缓冲字典API
                random_words_info = self.buffered_dictionary_api.get_random_words_info(1, vocabulary_level=vocab_level)
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self._update_ui_with_random_words(random_words_info))
                
            except Exception as e:
                # 在主线程中显示错误
                self.root.after(0, lambda: self._show_random_words_error(str(e)))
        
        # 启动异步操作
        threading.Thread(target=async_generate, daemon=True).start()
    
    def _update_ui_with_random_words(self, random_words_info):
        """在主线程中更新UI显示随机单词"""
        # 关闭加载指示器
        if self.loading_window and self.loading_window.winfo_exists():
            self.loading_window.destroy()
            self.loading_window = None
        
        if not random_words_info:
            messagebox.showerror("错误", "未能获取到随机单词，请检查网络连接或稍后重试。")
            return
        
        # 获取第一个单词
        word_info = random_words_info[0]
        word = word_info['word']
        
        # 将单词插入到现有的单词输入字段中
        self.word_entry.delete(0, tk.END)  # 清空当前内容
        self.word_entry.insert(0, word)    # 插入新单词
        
        # 如果有释义信息，也插入到释义字段中
        meanings = word_info.get('meanings', [])
        chinese_meanings = word_info.get('chinese_meanings', [])
        
        # 优先使用中文释义，如果没有则使用英文释义
        if chinese_meanings:
            # 提取前3个中文释义并组合
            meaning_texts = []
            for meaning in chinese_meanings[:3]:
                part_of_speech = meaning.get('part_of_speech', '')
                definition = meaning.get('definition', '')
                if part_of_speech:
                    meaning_texts.append(f"{part_of_speech} {definition}")
                else:
                    meaning_texts.append(definition)
            combined_meaning = "; ".join(meaning_texts)
            self.meaning_entry.delete(0, tk.END)
            self.meaning_entry.insert(0, combined_meaning)
        elif meanings:
            # 提取前3个英文释义并组合
            meaning_texts = []
            for meaning in meanings[:3]:
                part_of_speech = meaning.get('part_of_speech', '')
                definition = meaning.get('definition', '')
                if part_of_speech:
                    meaning_texts.append(f"{part_of_speech} {definition}")
                else:
                    meaning_texts.append(definition)
            combined_meaning = "; ".join(meaning_texts)
            self.meaning_entry.delete(0, tk.END)
            self.meaning_entry.insert(0, combined_meaning)
        
        # 显示成功消息 - 使用状态栏显示替代弹窗
        self.status_bar.configure(text=f"已将随机单词 '{word}' 插入到输入字段中", text_color="#2ecc71")
        # 3秒后恢复状态栏
        self.root.after(3000, lambda: self.status_bar.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]))
    
    def _show_random_words_error(self, error_msg):
        """显示随机单词生成错误"""
        # 关闭加载指示器
        if self.loading_window and self.loading_window.winfo_exists():
            self.loading_window.destroy()
            self.loading_window = None
            
        # 错误消息也使用状态栏显示
        self.status_bar.configure(text=f"生成随机单词时发生错误: {error_msg}", text_color="#e74c3c")
        # 3秒后恢复状态栏
        self.root.after(3000, lambda: self.status_bar.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]))
    
    def _regenerate_words(self, text_widget):
        """重新生成随机单词"""
        # 检查词典API是否可用
        if not hasattr(self.word_manager, 'dictionary_api') or not self.word_manager.dictionary_api:
            text_widget.configure(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, "错误: 词典API不可用，无法生成随机单词！", "error")
            text_widget.tag_config("error", foreground="red")
            text_widget.configure(state=tk.DISABLED)
            return
            
        # 显示加载指示器
        self.show_loading_indicator("正在从词典获取随机单词...")
        
        # 异步执行获取操作
        def async_regenerate():
            try:
                # 获取用户选择的单词数量
                word_count = self.word_count_var.get()
                if word_count < 1:
                    word_count = 1
                elif word_count > 50:
                    word_count = 50
                
                # 检查词汇级别变量是否已初始化
                if not hasattr(self, 'vocab_level_var'):
                    vocab_level = "cet6"  # 默认使用CET6
                else:
                    vocab_level = self.vocab_level_var.get()
                
                # 使用缓冲字典API
                random_words_info = self.buffered_dictionary_api.get_random_words_info(word_count, vocabulary_level=vocab_level)
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self._update_text_widget_with_words(text_widget, random_words_info))
                
            except Exception as e:
                # 在主线程中显示错误
                self.root.after(0, lambda: self._show_text_widget_error(text_widget, str(e)))
        
        # 启动异步操作
        threading.Thread(target=async_regenerate, daemon=True).start()
    
    def _update_text_widget_with_words(self, text_widget, random_words_info):
        """在主线程中更新文本框显示随机单词"""
        try:
            # 关闭加载指示器
            if self.loading_window and self.loading_window.winfo_exists():
                self.loading_window.destroy()
                self.loading_window = None
                
            # 启用文本框编辑
            text_widget.configure(state=tk.NORMAL)
            
            # 清空内容
            text_widget.delete(1.0, tk.END)
            
            if not random_words_info:
                text_widget.insert(tk.END, "错误: 未能获取到随机单词，请检查网络连接或稍后重试。", "error")
                text_widget.tag_config("error", foreground="red")
                text_widget.configure(state=tk.DISABLED)
                return
                
            # 格式化显示单词详细信息
            text_widget.insert(tk.END, "随机单词:\n", "title")
            text_widget.insert(tk.END, "=" * 70 + "\n\n", "separator")
            
            # 显示所有单词的详细信息
            for i, word_info in enumerate(random_words_info):
                word = word_info['word']
                phonetic = word_info.get('phonetic', '')
                meanings = word_info.get('meanings', [])
                examples = word_info.get('examples', [])
                chinese_meanings = word_info.get('chinese_meanings', [])
                
                # 单词标题
                word_title = f"单词: {word}"
                if phonetic:
                    word_title += f"  [{phonetic}]"
                text_widget.insert(tk.END, word_title + "\n", "word_title")
                
                # 中文释义（优先显示）
                if chinese_meanings:
                    text_widget.insert(tk.END, "中文释义:\n", "subtitle")
                    for j, meaning in enumerate(chinese_meanings[:5]):  # 显示前5个释义
                        part_of_speech = meaning.get('part_of_speech', '')
                        definition = meaning.get('definition', '')
                        meaning_text = f"  {part_of_speech}: {definition}" if part_of_speech else f"  {definition}"
                        text_widget.insert(tk.END, meaning_text + "\n", "chinese_meaning")
                # 英文释义
                elif meanings:
                    text_widget.insert(tk.END, "英文释义:\n", "subtitle")
                    for j, meaning in enumerate(meanings[:5]):  # 显示前5个释义
                        part_of_speech = meaning.get('part_of_speech', '')
                        definition = meaning.get('definition', '')
                        meaning_text = f"  {part_of_speech}: {definition}" if part_of_speech else f"  {definition}"
                        text_widget.insert(tk.END, meaning_text + "\n", "english_meaning")
                
                # 例句
                if examples:
                    text_widget.insert(tk.END, "例句:\n", "subtitle")
                    for j, example in enumerate(examples[:3]):  # 显示前3个例句
                        text_widget.insert(tk.END, f"  • {example}\n", "example")
                
                # 在单词之间添加分隔线（除了最后一个单词）
                if i < len(random_words_info) - 1:
                    text_widget.insert(tk.END, "\n" + "-" * 70 + "\n\n", "separator")
            
            text_widget.insert(tk.END, "=" * 70 + "\n", "separator")
            text_widget.insert(tk.END, f"总共获取了 {len(random_words_info)} 个随机单词的详细信息\n", "info")
            
            # 设置文本样式
            text_widget.tag_config("title", font=('Arial', 12, 'bold'), foreground="blue")
            text_widget.tag_config("word_title", font=('Arial', 11, 'bold'), foreground="darkblue")
            text_widget.tag_config("subtitle", font=('Arial', 10, 'bold'), foreground="darkgreen")
            text_widget.tag_config("chinese_meaning", foreground="black")
            text_widget.tag_config("english_meaning", foreground="black")
            text_widget.tag_config("example", foreground="gray", font=('Arial', 10, 'italic'))
            text_widget.tag_config("separator", foreground="gray")
            text_widget.tag_config("info", font=('Arial', 10, 'italic'), foreground="green")
            
            # 设置文本框为只读
            text_widget.configure(state=tk.DISABLED)
            
        except Exception as e:
            # 关闭加载指示器
            if self.loading_window and self.loading_window.winfo_exists():
                self.loading_window.destroy()
                self.loading_window = None
                
            text_widget.configure(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"重新生成随机单词时发生错误:\n{str(e)}", "error")
            text_widget.tag_config("error", foreground="red")
            text_widget.configure(state=tk.DISABLED)
    
    def on_closing(self):
        """关闭程序时的处理"""
        if messagebox.askokcancel("退出", "确定要退出单词记忆助手吗？"):
            self.root.destroy()


def main():
    """主函数"""
    root = ctk.CTk()
    app = WordReminderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
