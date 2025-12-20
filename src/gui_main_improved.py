#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词记忆助手 GUI 版本 (改进版)
基于 tkinter 的图形用户界面，提供更好的用户体验
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import json
import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from word_manager import WordManager
from scheduler import Scheduler


class WordReminderGUI:
    """单词记忆助手图形界面"""
    
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("单词记忆助手 - V1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 设置样式
        self.setup_styles()
        
        # 初始化数据管理器
        self.word_manager = WordManager("data/words.json")
        self.scheduler = Scheduler(self.word_manager)
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.refresh_word_list()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 检查词典API状态
        self.check_dictionary_api_status()
        
        # 初始化加载指示器
        self.loading_window = None
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置标签页样式
        style.configure('TNotebook.Tab', padding=[10, 5])
        
        # 配置按钮样式
        style.configure('Accent.TButton', foreground='white', background='#4a6fa5')
        style.map('Accent.TButton', background=[('active', '#3a5a80')])
    
    def check_dictionary_api_status(self):
        """检查词典API状态"""
        # 在状态栏显示API状态
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            status_text = "词典API: 可用"
        else:
            status_text = "词典API: 不可用"
        
        # 更新状态栏
        self.status_bar.config(text=status_text)
    
    def show_loading_indicator(self, message="正在处理..."):
        """显示加载指示器"""
        if self.loading_window is None or not self.loading_window.winfo_exists():
            self.loading_window = tk.Toplevel(self.root)
            self.loading_window.title("请稍候")
            self.loading_window.geometry("250x100")
            self.loading_window.resizable(False, False)
            
            # 设置窗口居中
            self.loading_window.transient(self.root)
            self.loading_window.grab_set()
            
            # 添加消息和进度条
            label = ttk.Label(self.loading_window, text=message)
            label.pack(pady=10)
            
            progress = ttk.Progressbar(self.loading_window, mode='indeterminate')
            progress.pack(padx=20, pady=10, fill=tk.X)
            progress.start(10)
            
            # 更新界面
            self.loading_window.update_idletasks()
        
        # 更新状态栏
        self.status_bar.config(text=message)
    
    def hide_loading_indicator(self):
        """隐藏加载指示器"""
        if self.loading_window and self.loading_window.winfo_exists():
            self.loading_window.destroy()
            self.loading_window = None
        
        # 恢复状态栏信息
        self.check_dictionary_api_status()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建顶部标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        title_label = ttk.Label(title_frame, text="单词记忆助手", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(title_frame, text="V1.0", font=('Arial', 10))
        version_label.pack(side=tk.RIGHT)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建各个标签页
        self.create_home_tab()
        self.create_add_tab()
        self.create_view_tab()
        self.create_review_tab()
        self.create_search_tab()
        self.create_stats_tab()
        self.create_settings_tab()
        
        # 创建状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_home_tab(self):
        """创建主页标签页"""
        self.home_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.home_frame, text="首页")
        
        # 欢迎信息
        welcome_frame = ttk.LabelFrame(self.home_frame, text="欢迎使用", padding=10)
        welcome_frame.pack(fill=tk.X, padx=10, pady=10)
        
        welcome_text = """
        欢迎使用单词记忆助手！
        
        本系统基于艾宾浩斯遗忘曲线理论，通过科学的时间间隔安排单词复习，
        帮助您更高效地记忆单词。
        
        使用指南：
        1. 在"添加单词"页面添加您需要记忆的单词
        2. 在"复习单词"页面进行定期复习
        3. 查看"学习统计"了解您的学习进度
        """
        
        welcome_label = ttk.Label(welcome_frame, text=welcome_text, justify=tk.LEFT)
        welcome_label.pack()
        
        # 快捷操作
        quick_frame = ttk.LabelFrame(self.home_frame, text="快捷操作", padding=10)
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        button_frame = ttk.Frame(quick_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="添加单词", command=lambda: self.notebook.select(self.add_frame)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="开始复习", command=self.quick_review).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看统计", command=lambda: self.notebook.select(self.stats_frame)).pack(side=tk.LEFT, padx=5)
        
        # 今日学习提醒
        reminder_frame = ttk.LabelFrame(self.home_frame, text="今日学习提醒", padding=10)
        reminder_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.reminder_text = scrolledtext.ScrolledText(reminder_frame, wrap=tk.WORD, height=10)
        self.reminder_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_reminder()
    
    def create_add_tab(self):
        """创建添加单词标签页"""
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="添加单词")
        
        # 创建表单框架
        form_frame = ttk.LabelFrame(self.add_frame, text="添加新单词", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 单词输入
        ttk.Label(form_frame, text="单词:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        self.word_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.word_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 释义输入
        ttk.Label(form_frame, text="释义:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.meaning_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.meaning_entry.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 例句输入
        ttk.Label(form_frame, text="例句:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=10)
        self.example_entry = ttk.Entry(form_frame, width=60, font=('Arial', 12))
        self.example_entry.grid(row=2, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 分类输入
        ttk.Label(form_frame, text="分类:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=10)
        self.category_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.category_entry.grid(row=3, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=1, pady=20, sticky=tk.W)
        
        self.add_button = ttk.Button(button_frame, text="添加单词", command=self.add_word)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # 添加随机生成单词按钮
        ttk.Button(button_frame, text="随机生成单词", command=self.generate_random_words).pack(side=tk.LEFT, padx=5)
    
    def create_view_tab(self):
        """创建查看单词标签页"""
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="查看单词")
        
        # 控制面板
        control_frame = ttk.Frame(self.view_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="刷新", command=self.refresh_word_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="删除选中", command=self.delete_selected_word).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="详情查看", command=self.show_selected_word_detail).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="获取详细信息", command=self.fetch_detailed_info).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        ttk.Label(control_frame, text="搜索:").pack(side=tk.RIGHT, padx=5)
        self.view_search_var = tk.StringVar()
        self.view_search_var.trace('w', self.on_view_search_change)
        self.view_search_entry = ttk.Entry(control_frame, textvariable=self.view_search_var, width=20)
        self.view_search_entry.pack(side=tk.RIGHT, padx=5)
        
        # 创建表格
        columns = ("单词", "释义", "分类", "添加日期", "复习次数", "下次复习")
        self.word_tree = ttk.Treeview(self.view_frame, columns=columns, show="headings", height=25)
        
        # 定义列标题和宽度
        column_widths = [150, 200, 120, 120, 80, 120]
        column_headers = ["单词", "释义", "分类", "添加日期", "复习次数", "下次复习"]
        for i, (col, header) in enumerate(zip(columns, column_headers)):
            self.word_tree.heading(col, text=header)
            self.word_tree.column(col, width=column_widths[i], anchor=tk.CENTER)
        
        # 添加滚动条
        tree_scroll_y = ttk.Scrollbar(self.view_frame, orient=tk.VERTICAL, command=self.word_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.view_frame, orient=tk.HORIZONTAL, command=self.word_tree.xview)
        self.word_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # 布局
        self.word_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # 绑定双击事件和右键菜单
        self.word_tree.bind("<Double-1>", self.on_word_double_click)
        self.word_tree.bind("<Button-3>", self.show_context_menu)
        
        # 创建右键菜单
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
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"单词详情 - {word}")
        detail_window.geometry("600x500")
        detail_window.minsize(500, 400)
        
        # 设置窗口居中
        detail_window.transient(self.root)
        detail_window.grab_set()
        
        # 创建笔记本控件用于标签页
        detail_notebook = ttk.Notebook(detail_window)
        detail_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 基本信息标签页
        basic_frame = ttk.Frame(detail_notebook)
        detail_notebook.add(basic_frame, text="基本信息")
        
        # 创建基本信息内容
        basic_canvas = tk.Canvas(basic_frame)
        basic_scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=basic_canvas.yview)
        basic_scrollable_frame = ttk.Frame(basic_canvas)
        
        basic_scrollable_frame.bind(
            "<Configure>",
            lambda e: basic_canvas.configure(scrollregion=basic_canvas.bbox("all"))
        )
        
        basic_canvas.create_window((0, 0), window=basic_scrollable_frame, anchor="nw")
        basic_canvas.configure(yscrollcommand=basic_scrollbar.set)
        
        # 显示基本信息
        ttk.Label(basic_scrollable_frame, text="单词:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(basic_scrollable_frame, text=word, font=('Arial', 12)).pack(anchor=tk.W, padx=20)
        
        ttk.Label(basic_scrollable_frame, text="释义:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(basic_scrollable_frame, text=info['meaning'], font=('Arial', 12), wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, padx=20)
        
        if info.get('example'):
            ttk.Label(basic_scrollable_frame, text="例句:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
            ttk.Label(basic_scrollable_frame, text=info['example'], font=('Arial', 12), wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, padx=20)
        
        if info.get('category'):
            ttk.Label(basic_scrollable_frame, text="分类:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
            ttk.Label(basic_scrollable_frame, text=info['category'], font=('Arial', 12)).pack(anchor=tk.W, padx=20)
        
        if info.get('add_date'):
            ttk.Label(basic_scrollable_frame, text="添加日期:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
            ttk.Label(basic_scrollable_frame, text=info['add_date'][:10], font=('Arial', 12)).pack(anchor=tk.W, padx=20)
        
        ttk.Label(basic_scrollable_frame, text="复习次数:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(basic_scrollable_frame, text=str(info.get('review_count', 0)), font=('Arial', 12)).pack(anchor=tk.W, padx=20)
        
        if info.get('last_reviewed'):
            ttk.Label(basic_scrollable_frame, text="上次复习:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
            ttk.Label(basic_scrollable_frame, text=info['last_reviewed'][:10], font=('Arial', 12)).pack(anchor=tk.W, padx=20)
        
        if info.get('next_review'):
            ttk.Label(basic_scrollable_frame, text="下次复习:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
            ttk.Label(basic_scrollable_frame, text=info['next_review'][:10], font=('Arial', 12)).pack(anchor=tk.W, padx=20)
        
        # 布局滚动区域
        basic_canvas.pack(side="left", fill="both", expand=True)
        basic_scrollbar.pack(side="right", fill="y")
        
        # 详细信息标签页（从词典API获取）
        detail_frame = ttk.Frame(detail_notebook)
        detail_notebook.add(detail_frame, text="详细信息")
        
        # 创建详细信息内容
        detail_canvas = tk.Canvas(detail_frame)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=detail_canvas.yview)
        detail_scrollable_frame = ttk.Frame(detail_canvas)
        
        detail_scrollable_frame.bind(
            "<Configure>",
            lambda e: detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))
        )
        
        detail_canvas.create_window((0, 0), window=detail_scrollable_frame, anchor="nw")
        detail_canvas.configure(yscrollcommand=detail_scrollbar.set)
        
        # 尝试从词典API获取更详细的信息
        if hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            self.show_loading_indicator(f"正在获取单词 '{word}' 的详细信息...")
            try:
                word_info = self.word_manager.dictionary_api.get_word_info(word)
                if word_info:
                    # 显示音标
                    if word_info.get('phonetic'):
                        ttk.Label(detail_scrollable_frame, text="音标:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        ttk.Label(detail_scrollable_frame, text=word_info['phonetic'], font=('Arial', 12)).pack(anchor=tk.W, padx=20)
                    
                    # 显示英文释义
                    if word_info.get('meanings'):
                        ttk.Label(detail_scrollable_frame, text="英文释义:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        for i, meaning_info in enumerate(word_info['meanings']):
                            part_of_speech = meaning_info.get('part_of_speech', '')
                            definition = meaning_info.get('definition', '')
                            meaning_text = f"{i+1}. {part_of_speech}: {definition}" if part_of_speech else f"{i+1}. {definition}"
                            ttk.Label(detail_scrollable_frame, text=meaning_text, font=('Arial', 11), wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=2)
                    
                    # 显示中文释义
                    if word_info.get('chinese_meanings'):
                        ttk.Label(detail_scrollable_frame, text="中文释义:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        for i, meaning_info in enumerate(word_info['chinese_meanings']):
                            part_of_speech = meaning_info.get('part_of_speech', '')
                            definition = meaning_info.get('definition', '')
                            meaning_text = f"{i+1}. {part_of_speech}: {definition}" if part_of_speech else f"{i+1}. {definition}"
                            ttk.Label(detail_scrollable_frame, text=meaning_text, font=('Arial', 11), wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=2)
                    
                    # 显示例句
                    if word_info.get('examples'):
                        ttk.Label(detail_scrollable_frame, text="例句:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10, 2))
                        for i, example in enumerate(word_info['examples']):
                            ttk.Label(detail_scrollable_frame, text=f"{i+1}. {example}", font=('Arial', 11), wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=2)
                else:
                    ttk.Label(detail_scrollable_frame, text="未找到该单词的详细信息", font=('Arial', 12)).pack(pady=20)
            except Exception as e:
                ttk.Label(detail_scrollable_frame, text=f"获取详细信息时发生错误: {str(e)}", font=('Arial', 12)).pack(pady=20)
            finally:
                self.hide_loading_indicator()
        else:
            ttk.Label(detail_scrollable_frame, text="词典API不可用，无法获取详细信息", font=('Arial', 12)).pack(pady=20)
        
        # 布局滚动区域
        detail_canvas.pack(side="left", fill="both", expand=True)
        detail_scrollbar.pack(side="right", fill="y")
        
        # 添加关闭按钮
        button_frame = ttk.Frame(detail_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="关闭", command=detail_window.destroy).pack(side=tk.RIGHT, padx=5)
    
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
            
            # 更新单词信息
            if word in self.word_manager.words:
                # 更新释义（如果获取到了中文释义则使用中文释义）
                if word_info.get('chinese_meanings'):
                    self.word_manager.words[word]['meaning'] = word_info['chinese_meanings'][0]['definition']
                elif word_info.get('meanings'):
                    self.word_manager.words[word]['meaning'] = word_info['meanings'][0]['definition']
                
                # 如果当前没有例句但获取到了例句，则添加例句
                if not self.word_manager.words[word].get('example') and word_info.get('examples'):
                    self.word_manager.words[word]['example'] = word_info['examples'][0]
                
                # 保存更新
                self.word_manager.save_words()
                
                # 刷新单词列表
                self.refresh_word_list()
                
                messagebox.showinfo("成功", f"单词 '{word}' 的信息已更新！")
            else:
                messagebox.showwarning("警告", f"单词 '{word}' 不在词库中！")
        except Exception as e:
            messagebox.showerror("错误", f"获取单词详细信息时发生错误:\n{str(e)}")
        finally:
            # 隐藏加载指示器
            self.hide_loading_indicator()
    
    def create_review_tab(self):
        """创建复习单词标签页"""
        self.review_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.review_frame, text="复习单词")
        
        # 复习控制面板
        control_frame = ttk.Frame(self.review_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_review_button = ttk.Button(control_frame, text="开始复习", command=self.start_review)
        self.start_review_button.pack(side=tk.LEFT, padx=5)
        
        self.review_count_label = ttk.Label(control_frame, text="待复习单词: 0")
        self.review_count_label.pack(side=tk.RIGHT, padx=5)
        
        # 复习区域
        self.review_notebook = ttk.Notebook(self.review_frame)
        self.review_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 学习卡片视图
        self.card_frame = ttk.Frame(self.review_notebook)
        self.review_notebook.add(self.card_frame, text="学习卡片")
        
        # 卡片内容
        card_content_frame = ttk.Frame(self.card_frame)
        card_content_frame.pack(expand=True)
        
        self.word_label = ttk.Label(card_content_frame, text="", font=('Arial', 24, 'bold'))
        self.word_label.pack(pady=(50, 10))
        
        self.meaning_label = ttk.Label(card_content_frame, text="", font=('Arial', 16))
        self.meaning_label.pack(pady=10)
        
        self.example_label = ttk.Label(card_content_frame, text="", font=('Arial', 12), foreground='gray')
        self.example_label.pack(pady=10)
        
        # 进度显示
        self.progress_label = ttk.Label(card_content_frame, text="")
        self.progress_label.pack(pady=20)
        
        # 按钮框架
        button_frame = ttk.Frame(card_content_frame)
        button_frame.pack(pady=20)
        
        self.know_button = ttk.Button(button_frame, text="认识 (✓)", 
                                     command=lambda: self.review_feedback(True),
                                     state=tk.DISABLED, width=15)
        self.know_button.pack(side=tk.LEFT, padx=10)
        
        self.not_know_button = ttk.Button(button_frame, text="不认识 (✗)", 
                                         command=lambda: self.review_feedback(False),
                                         state=tk.DISABLED, width=15)
        self.not_know_button.pack(side=tk.LEFT, padx=10)
        
        # 复习统计视图
        self.stats_frame = ttk.Frame(self.review_notebook)
        self.review_notebook.add(self.stats_frame, text="复习统计")
        
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 初始化复习状态
        self.review_words = []
        self.current_review_index = 0
        self.current_review_word = None
        self.review_results = []  # 记录复习结果
        
        # 更新待复习单词数量
        self.update_review_count()
    
    def create_search_tab(self):
        """创建搜索单词标签页"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="搜索单词")
        
        # 搜索框
        search_frame = ttk.LabelFrame(self.search_frame, text="搜索", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda event: self.search_words())
        
        self.search_button = ttk.Button(search_frame, text="搜索", command=self.search_words)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="清空", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # 搜索结果
        result_frame = ttk.LabelFrame(self.search_frame, text="搜索结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("单词", "释义", "分类", "添加日期")
        self.search_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=20)
        
        # 定义列标题和宽度
        column_widths = [180, 250, 120, 180]
        for i, col in enumerate(columns):
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=column_widths[i], anchor=tk.CENTER)
        
        # 添加滚动条
        tree_scroll_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        tree_scroll_x = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.search_tree.xview)
        self.search_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # 布局
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定双击事件
        self.search_tree.bind("<Double-1>", self.on_search_double_click)
    
    def create_stats_tab(self):
        """创建统计信息标签页"""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="学习统计")
        
        # 统计控制面板
        control_frame = ttk.Frame(self.stats_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="刷新", command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        
        # 添加导出按钮
        ttk.Button(control_frame, text="导出图表", command=self.export_chart).pack(side=tk.LEFT, padx=5)
        
        # 添加时间范围筛选控件
        ttk.Label(control_frame, text="时间范围:").pack(side=tk.LEFT, padx=(20, 5))
        self.time_range_var = tk.StringVar(value="30")
        time_range_combo = ttk.Combobox(control_frame, textvariable=self.time_range_var, 
                                       values=["7", "14", "30", "60", "90"], width=10, state="readonly")
        time_range_combo.pack(side=tk.LEFT, padx=5)
        time_range_combo.bind("<<ComboboxSelected>>", self.on_time_range_change)
        
        # 统计内容框架
        content_frame = ttk.Frame(self.stats_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：概览统计
        overview_frame = ttk.LabelFrame(content_frame, text="学习概览", padding=15)
        overview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.overview_text = scrolledtext.ScrolledText(overview_frame, wrap=tk.WORD, font=('Arial', 11))
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：图表展示（简化版文本展示）
        chart_frame = ttk.LabelFrame(content_frame, text="学习趋势", padding=15)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.chart_text = scrolledtext.ScrolledText(chart_frame, wrap=tk.WORD, font=('Arial', 11))
        self.chart_text.pack(fill=tk.BOTH, expand=True)
        
        # 为图表文本组件绑定鼠标点击事件
        self.chart_text.bind("<Button-1>", self.on_chart_click)
        
        # 初始化显示统计信息
        self.show_statistics()
    
    def create_settings_tab(self):
        """创建设置标签页"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="设置")
        
        # 设置内容
        settings_container = ttk.LabelFrame(self.settings_frame, text="系统设置", padding=20)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 数据管理
        data_frame = ttk.LabelFrame(settings_container, text="数据管理", padding=10)
        data_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(data_frame, text="备份数据", command=self.backup_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_frame, text="恢复数据", command=self.restore_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_frame, text="清空数据", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # 关于信息
        about_frame = ttk.LabelFrame(settings_container, text="关于", padding=10)
        about_frame.pack(fill=tk.X, pady=10)
        
        about_text = """
        单词记忆助手 V1.0
        
        基于艾宾浩斯遗忘曲线理论的智能单词记忆系统
        帮助您科学高效地记忆单词
        
        开发者: 计算机专业学生
        开发时间: 2025年12月
        """
        
        about_label = ttk.Label(about_frame, text=about_text, justify=tk.LEFT)
        about_label.pack()
    
    def add_word(self):
        """添加单词"""
        word = self.word_entry.get().strip().lower()
        
        if not word:
            messagebox.showwarning("输入错误", "单词不能为空！")
            return
        
        if word in self.word_manager.words:
            messagebox.showwarning("重复单词", f"单词 '{word}' 已存在！")
            return
        
        # 尝试从词典API获取单词信息
        meaning = ""
        example = ""
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
                    
                    # 显示英文释义
                    if word_info['meanings']:
                        info_text += "\n英文释义:"
                        for i, meaning_info in enumerate(word_info['meanings'][:3]):  # 只显示前3个释义
                            info_text += f"\n  {i+1}. {meaning_info['part_of_speech']}: {meaning_info['definition']}"
                        # 使用第一个释义作为默认释义
                        meaning = word_info['meanings'][0]['definition']
                    
                    # 显示中文释义（如果有的话）
                    if word_info['chinese_meanings']:
                        info_text += "\n中文释义:"
                        for i, meaning_info in enumerate(word_info['chinese_meanings'][:3]):  # 只显示前3个中文释义
                            info_text += f"\n  {i+1}. {meaning_info['part_of_speech']}: {meaning_info['definition']}"
                        # 如果没有英文释义或优先使用中文释义，使用第一个中文释义作为默认释义
                        if not meaning:  # 如果还没有英文释义
                            meaning = word_info['chinese_meanings'][0]['definition']
                    
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
            self.add_button.config(state=tk.NORMAL, text="添加单词")
            return
        
        example = self.example_entry.get().strip()
        category = self.category_entry.get().strip()
        
        # 添加单词
        self.word_manager.words[word] = {
            "meaning": meaning_input,
            "example": example,
            "category": category,
            "add_date": datetime.datetime.now().isoformat(),
            "last_reviewed": None,
            "next_review": None,
            "review_count": 0,
            "interval": 1,
            "difficulty": "normal"
        }
        
        self.word_manager.save_words()
        
        # 清空输入框
        self.word_entry.delete(0, tk.END)
        self.meaning_entry.delete(0, tk.END)
        self.example_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        
        # 恢复按钮状态
        self.add_button.config(state=tk.NORMAL, text="添加单词")
        
        messagebox.showinfo("成功", f"单词 '{word}' 添加成功！")
        
        # 刷新单词列表
        self.refresh_word_list()
        
        # 更新提醒
        self.update_reminder()
    
    def clear_form(self):
        """清空表单"""
        self.word_entry.delete(0, tk.END)
        self.meaning_entry.delete(0, tk.END)
        self.example_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
    
    def refresh_word_list(self):
        """刷新单词列表"""
        # 清空现有数据
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 添加新数据
        search_term = self.view_search_var.get().lower()
        for word, info in self.word_manager.words.items():
            # 如果有搜索条件，过滤数据
            if search_term and search_term not in word.lower() and search_term not in info['meaning'].lower():
                continue
                
            add_date = info.get('add_date', '')[:10] if info.get('add_date') else ''
            review_count = info.get('review_count', 0)
            next_review = info.get('next_review', '')[:10] if info.get('next_review') else ''
            self.word_tree.insert("", tk.END, values=(word, info['meaning'], info['category'], add_date, review_count, next_review))
    
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
            del self.word_manager.words[word]
            self.word_manager.save_words()
            self.refresh_word_list()
            messagebox.showinfo("成功", f"单词 '{word}' 删除成功！")
    
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
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑单词 - {word}")
        edit_window.geometry("500x400")
        edit_window.minsize(400, 300)
        
        # 设置窗口居中
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # 创建表单框架
        form_frame = ttk.LabelFrame(edit_window, text="编辑单词信息", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 单词（只读）
        ttk.Label(form_frame, text="单词:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        word_var = tk.StringVar(value=word)
        word_entry = ttk.Entry(form_frame, textvariable=word_var, width=40, font=('Arial', 12), state='readonly')
        word_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 释义
        ttk.Label(form_frame, text="释义:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        meaning_var = tk.StringVar(value=info['meaning'])
        meaning_entry = ttk.Entry(form_frame, textvariable=meaning_var, width=40, font=('Arial', 12))
        meaning_entry.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 例句
        ttk.Label(form_frame, text="例句:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=10)
        example_var = tk.StringVar(value=info.get('example', ''))
        example_entry = ttk.Entry(form_frame, textvariable=example_var, width=60, font=('Arial', 12))
        example_entry.grid(row=2, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 分类
        ttk.Label(form_frame, text="分类:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=10)
        category_var = tk.StringVar(value=info.get('category', ''))
        category_entry = ttk.Entry(form_frame, textvariable=category_var, width=40, font=('Arial', 12))
        category_entry.grid(row=3, column=1, padx=5, pady=10, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=1, pady=20, sticky=tk.W)
        
        def save_changes():
            """保存修改"""
            # 更新单词信息
            self.word_manager.words[word]['meaning'] = meaning_var.get().strip()
            self.word_manager.words[word]['example'] = example_var.get().strip()
            self.word_manager.words[word]['category'] = category_var.get().strip()
            
            # 保存到文件
            self.word_manager.save_words()
            
            # 刷新单词列表
            self.refresh_word_list()
            
            # 关闭编辑窗口
            edit_window.destroy()
            
            messagebox.showinfo("成功", f"单词 '{word}' 修改成功！")
        
        ttk.Button(button_frame, text="保存", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
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
        self.review_count_label.config(text=f"待复习单词: {review_count}")
    
    def start_review(self):
        """开始复习"""
        self.review_words = self.word_manager.get_words_for_review()
        
        if not self.review_words:
            messagebox.showinfo("提示", "暂无需要复习的单词。")
            return
        
        self.review_results = []  # 清空之前的复习结果
        self.current_review_index = 0
        self.show_next_review_word()
        
        # 启用按钮
        self.know_button.config(state=tk.NORMAL)
        self.not_know_button.config(state=tk.NORMAL)
        self.start_review_button.config(state=tk.DISABLED)
        
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
        self.word_label.config(text=self.current_review_word)
        
        # 显示释义（如果是从词典API添加的单词，尝试显示更详细的释义）
        meaning_text = info['meaning']
        # 如果当前释义较短，尝试从词典API获取更多信息
        if len(meaning_text) < 20 and hasattr(self.word_manager, 'dictionary_api') and self.word_manager.dictionary_api:
            word_info = self.word_manager.dictionary_api.get_word_info(self.current_review_word)
            if word_info and word_info['chinese_meanings']:
                # 优先显示中文释义
                meaning_text = word_info['chinese_meanings'][0]['definition'] if word_info['chinese_meanings'] else meaning_text
            elif word_info and word_info['meanings']:
                # 如果没有中文释义，显示英文释义
                meaning_text = word_info['meanings'][0]['definition']
        
        self.meaning_label.config(text=meaning_text)
        self.example_label.config(text=info.get('example', ''))
        self.progress_label.config(text=f"进度: {self.current_review_index + 1}/{len(self.review_words)}")
    
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
            
            # 更新单词调度
            self.scheduler._update_word_schedule(self.current_review_word, info, is_known)
        
        # 移动到下一个单词
        self.current_review_index += 1
        self.show_next_review_word()
    
    def finish_review(self):
        """完成复习"""
        # 禁用按钮
        self.know_button.config(state=tk.DISABLED)
        self.not_know_button.config(state=tk.DISABLED)
        self.start_review_button.config(state=tk.NORMAL)
        
        # 显示复习统计
        self.show_review_stats()
        
        # 切换到统计视图
        self.review_notebook.select(self.stats_frame)
        
        # 更新待复习数量
        self.update_review_count()
        
        # 更新提醒
        self.update_reminder()
        
        messagebox.showinfo("复习完成", f"复习完成！共复习了 {len(self.review_words)} 个单词。")
    
    def show_review_stats(self):
        """显示复习统计"""
        if not self.review_results:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "暂无复习记录。")
            return
        
        known_count = sum(1 for result in self.review_results if result['known'])
        total_count = len(self.review_results)
        accuracy = (known_count / total_count) * 100 if total_count > 0 else 0
        
        stats_text = f"""
复习统计报告
=================

复习单词数: {total_count}
掌握单词数: {known_count}
未掌握单词数: {total_count - known_count}
正确率: {accuracy:.1f}%

详细记录:
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
        
        for result in self.review_results:
            status = "✓" if result['known'] else "✗"
            word = result['word']
            # 显示单词及其释义
            meaning = word_details.get(word, self.word_manager.get_word(word)['meaning']) if word in word_details else self.word_manager.get_word(word)['meaning']
            stats_text += f"{status} {word} - {meaning} (间隔: {result['old_interval']}天)\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def search_words(self):
        """搜索单词"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            messagebox.showwarning("输入错误", "请输入搜索关键词！")
            return
        
        # 清空现有数据
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # 搜索匹配的单词
        for word, info in self.word_manager.words.items():
            if (keyword in word or 
                keyword in info['meaning'] or 
                keyword in info.get('example', '') or
                keyword in info.get('category', '')):
                add_date = info.get('add_date', '')[:10] if info.get('add_date') else ''
                self.search_tree.insert("", tk.END, values=(word, info['meaning'], info['category'], add_date))
    
    def clear_search(self):
        """清空搜索"""
        self.search_entry.delete(0, tk.END)
        # 清空搜索结果
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
    
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
    
    def show_statistics(self):
        """显示统计信息"""
        total_words = len(self.word_manager.words)
        reviewed_words = sum(1 for info in self.word_manager.words.values() if info['review_count'] > 0)
        total_reviews = sum(info['review_count'] for info in self.word_manager.words.values())
        
        # 计算最近7天的复习情况
        week_reviews = 0
        now = datetime.datetime.now()
        for info in self.word_manager.words.values():
            last_reviewed = info.get('last_reviewed')
            if last_reviewed:
                last_reviewed_time = datetime.datetime.fromisoformat(last_reviewed)
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
            review_rate = (reviewed_words / total_words) * 100
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
        total_words = len(self.word_manager.words)
        
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
        self.chart_text.tag_configure("title", foreground="black", font=('Arial', 14, 'bold'))
        self.chart_text.tag_configure("header", foreground="black", font=('Arial', 11, 'bold'))
        self.chart_text.tag_configure("new_word", foreground="red")
        self.chart_text.tag_configure("review_word", foreground="orange")
        self.chart_text.tag_configure("mastered_word", foreground="purple")
        self.chart_text.tag_configure("positive", foreground="green")
        self.chart_text.tag_configure("negative", foreground="red")
        self.chart_text.tag_configure("neutral", foreground="blue")
        self.chart_text.tag_configure("metric_value", foreground="black")
        self.chart_text.tag_configure("date_header", foreground="gray")
        self.chart_text.tag_configure("separator", foreground="gray")
        self.chart_text.tag_configure("legend_label", foreground="black")

    def _insert_colored_text(self, text, tag=None):
        """插入带颜色的文本"""
        if tag:
            self.chart_text.insert(tk.END, text, tag)
        else:
            self.chart_text.insert(tk.END, text)

    def on_chart_click(self, event):
        """处理图表点击事件"""
        try:
            # 获取点击位置的索引
            index = self.chart_text.index(f"@{event.x},{event.y}")
            
            # 获取当前行的所有文本
            line_start = f"{index.split('.')[0]}.0"
            line_end = f"{index.split('.')[0]}.end"
            line_text = self.chart_text.get(line_start, line_end)
            
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
        
        # 获取统计数据
        words = self.word_manager.words
        if not words:
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
        daily_mastered_words = {}  # 每日掌握单词数（复习次数>=3）
        
        # 初始化指定天数的数据
        for i in range(days_range):
            date_key = (now - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            daily_new_words[date_key] = 0
            daily_reviewed_words[date_key] = 0
            daily_mastered_words[date_key] = 0
        
        # 统计每日数据
        for word, info in words.items():
            # 统计新增单词
            add_date = info.get('add_date')
            if add_date:
                try:
                    add_date_obj = datetime.datetime.fromisoformat(add_date)
                    add_date_key = add_date_obj.strftime('%Y-%m-%d')
                    if add_date_key in daily_new_words:
                        daily_new_words[add_date_key] += 1
                except ValueError:
                    pass  # 忽略无效日期格式
            
            # 统计复习单词
            last_reviewed = info.get('last_reviewed')
            if last_reviewed:
                try:
                    review_date_obj = datetime.datetime.fromisoformat(last_reviewed)
                    review_date_key = review_date_obj.strftime('%Y-%m-%d')
                    if review_date_key in daily_reviewed_words:
                        daily_reviewed_words[review_date_key] += 1
                        
                        # 统计掌握单词（复习次数>=3）
                        if info.get('review_count', 0) >= 3:
                            daily_mastered_words[review_date_key] += 1
                except ValueError:
                    pass  # 忽略无效日期格式
        
        # 插入标题
        self._insert_colored_text("学习趋势图表\n", "title")
        self._insert_colored_text("=" * 20 + "\n", "separator")
        
        # 添加关键指标
        total_words = len(words)
        reviewed_words = sum(1 for info in words.values() if info['review_count'] > 0)
        mastered_words = sum(1 for info in words.values() if info['review_count'] >= 3)
        review_rate = (reviewed_words / total_words * 100) if total_words > 0 else 0
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
        """快捷复习"""
        self.notebook.select(self.review_frame)
        self.start_review()
    
    def backup_data(self):
        """备份数据"""
        try:
            import shutil
            backup_path = f"data/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy("data/words.json", backup_path)
            messagebox.showinfo("成功", f"数据备份成功！\n备份文件: {backup_path}")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败: {str(e)}")
    
    def restore_data(self):
        """恢复数据"""
        messagebox.showinfo("提示", "请手动替换 data/words.json 文件来恢复数据")
    
    def clear_data(self):
        """清空数据"""
        if messagebox.askyesno("确认", "确定要清空所有单词数据吗？此操作不可恢复！"):
            self.word_manager.words = {}
            self.word_manager.save_words()
            self.refresh_word_list()
            self.update_review_count()
            self.update_reminder()
            self.show_statistics()
            messagebox.showinfo("成功", "所有数据已清空！")
    
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
            words = self.word_manager.words
            for word, info in words.items():
                # 统计新增单词
                add_date = info.get('add_date')
                if add_date:
                    try:
                        add_date_obj = datetime.datetime.fromisoformat(add_date)
                        add_date_key = add_date_obj.strftime('%Y-%m-%d')
                        if add_date_key in daily_new_words:
                            daily_new_words[add_date_key] += 1
                    except ValueError:
                        pass  # 忽略无效日期格式
                
                # 统计复习单词
                last_reviewed = info.get('last_reviewed')
                if last_reviewed:
                    try:
                        review_date_obj = datetime.datetime.fromisoformat(last_reviewed)
                        review_date_key = review_date_obj.strftime('%Y-%m-%d')
                        if review_date_key in daily_reviewed_words:
                            daily_reviewed_words[review_date_key] += 1
                            
                            # 统计掌握单词（复习次数>=3）
                            if info.get('review_count', 0) >= 3:
                                daily_mastered_words[review_date_key] += 1
                    except ValueError:
                        pass  # 忽略无效日期格式
            
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
        """生成随机单词并显示在新窗口中"""
        # 检查词典API是否可用
        if not hasattr(self.word_manager, 'dictionary_api') or not self.word_manager.dictionary_api:
            messagebox.showerror("错误", "词典API不可用，无法生成随机单词！")
            return
            
        # 创建新窗口
        random_window = tk.Toplevel(self.root)
        random_window.title("随机生成单词")
        random_window.geometry("800x600")
        random_window.minsize(600, 500)
        
        # 居中显示
        random_window.transient(self.root)
        random_window.grab_set()
        
        # 标题
        title_label = ttk.Label(random_window, text="随机生成单词", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # 说明文本
        info_label = ttk.Label(random_window, text="以下是从词典中随机获取的单词及其详细信息：")
        info_label.pack(pady=5)
        
        # 创建文本框显示随机单词
        text_frame = ttk.Frame(random_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 添加滚动条
        text_scroll_y = ttk.Scrollbar(text_frame)
        text_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框
        random_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=text_scroll_y.set, font=('Arial', 11))
        random_text.pack(fill=tk.BOTH, expand=True)
        text_scroll_y.config(command=random_text.yview)
        
        # 显示加载指示器
        self.show_loading_indicator("正在从词典获取随机单词...")
        
        # 生成随机单词
        try:
            # 使用词典API获取随机单词信息
            random_words_info = self.word_manager.dictionary_api.get_random_words_info(30)  # 获取30个随机单词的详细信息
            
            # 关闭加载指示器
            if self.loading_window and self.loading_window.winfo_exists():
                self.loading_window.destroy()
                self.loading_window = None
            
            if not random_words_info:
                random_text.insert(tk.END, "未能获取到随机单词，请检查网络连接或稍后重试。\n", "error")
                random_text.tag_config("error", foreground="red")
                random_text.config(state=tk.DISABLED)
                return
            
            # 格式化显示单词详细信息
            random_text.insert(tk.END, "随机单词列表:\n", "title")
            random_text.insert(tk.END, "=" * 70 + "\n\n", "separator")
            
            # 显示每个单词的详细信息
            for i, word_info in enumerate(random_words_info):
                word = word_info['word']
                phonetic = word_info.get('phonetic', '')
                meanings = word_info.get('meanings', [])
                examples = word_info.get('examples', [])
                chinese_meanings = word_info.get('chinese_meanings', [])
                
                # 单词标题
                word_title = f"{i+1:2d}. {word}"
                if phonetic:
                    word_title += f"  [{phonetic}]"
                random_text.insert(tk.END, word_title + "\n", "word_title")
                
                # 中文释义（优先显示）
                if chinese_meanings:
                    random_text.insert(tk.END, "    中文释义:\n", "subtitle")
                    for j, meaning in enumerate(chinese_meanings[:3]):  # 只显示前3个释义
                        part_of_speech = meaning.get('part_of_speech', '')
                        definition = meaning.get('definition', '')
                        meaning_text = f"      {part_of_speech}: {definition}" if part_of_speech else f"      {definition}"
                        random_text.insert(tk.END, meaning_text + "\n", "chinese_meaning")
                # 英文释义
                elif meanings:
                    random_text.insert(tk.END, "    英文释义:\n", "subtitle")
                    for j, meaning in enumerate(meanings[:3]):  # 只显示前3个释义
                        part_of_speech = meaning.get('part_of_speech', '')
                        definition = meaning.get('definition', '')
                        meaning_text = f"      {part_of_speech}: {definition}" if part_of_speech else f"      {definition}"
                        random_text.insert(tk.END, meaning_text + "\n", "english_meaning")
                
                # 例句
                if examples:
                    random_text.insert(tk.END, "    例句:\n", "subtitle")
                    for j, example in enumerate(examples[:2]):  # 只显示前2个例句
                        random_text.insert(tk.END, f"      • {example}\n", "example")
                
                random_text.insert(tk.END, "\n")
            
            random_text.insert(tk.END, "=" * 70 + "\n", "separator")
            random_text.insert(tk.END, f"总共获取了 {len(random_words_info)} 个随机单词的详细信息\n", "info")
            
            # 设置文本样式
            random_text.tag_config("title", font=('Arial', 12, 'bold'), foreground="blue")
            random_text.tag_config("word_title", font=('Arial', 11, 'bold'), foreground="darkblue")
            random_text.tag_config("subtitle", font=('Arial', 10, 'bold'), foreground="darkgreen")
            random_text.tag_config("chinese_meaning", foreground="black")
            random_text.tag_config("english_meaning", foreground="black")
            random_text.tag_config("example", foreground="gray", font=('Arial', 10, 'italic'))
            random_text.tag_config("separator", foreground="gray")
            random_text.tag_config("info", font=('Arial', 10, 'italic'), foreground="green")
            
            # 设置文本框为只读
            random_text.config(state=tk.DISABLED)
            
        except Exception as e:
            # 关闭加载指示器
            if self.loading_window and self.loading_window.winfo_exists():
                self.loading_window.destroy()
                self.loading_window = None
                
            random_text.config(state=tk.NORMAL)
            random_text.insert(tk.END, f"生成随机单词时发生错误:\n{str(e)}", "error")
            random_text.tag_config("error", foreground="red")
            random_text.config(state=tk.DISABLED)
        
        # 按钮框架
        button_frame = ttk.Frame(random_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 重新生成按钮
        ttk.Button(button_frame, text="重新生成", command=lambda: self._regenerate_words(random_text)).pack(side=tk.LEFT, padx=5)
        
        # 关闭按钮
        ttk.Button(button_frame, text="关闭", command=random_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _regenerate_words(self, text_widget):
        """重新生成随机单词"""
        # 检查词典API是否可用
        if not hasattr(self.word_manager, 'dictionary_api') or not self.word_manager.dictionary_api:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, "错误: 词典API不可用，无法生成随机单词！", "error")
            text_widget.tag_config("error", foreground="red")
            text_widget.config(state=tk.DISABLED)
            return
            
        # 显示加载指示器
        self.show_loading_indicator("正在从词典获取随机单词...")
        
        try:
            # 启用文本框编辑
            text_widget.config(state=tk.NORMAL)
            
            # 清空内容
            text_widget.delete(1.0, tk.END)
            
            # 使用词典API获取随机单词信息
            random_words_info = self.word_manager.dictionary_api.get_random_words_info(30)  # 获取30个随机单词的详细信息
            
            # 关闭加载指示器
            if self.loading_window and self.loading_window.winfo_exists():
                self.loading_window.destroy()
                self.loading_window = None
            
            if not random_words_info:
                text_widget.insert(tk.END, "未能获取到随机单词，请检查网络连接或稍后重试。\n", "error")
                text_widget.tag_config("error", foreground="red")
                text_widget.config(state=tk.DISABLED)
                return
            
            # 格式化显示单词详细信息
            text_widget.insert(tk.END, "随机单词列表:\n", "title")
            text_widget.insert(tk.END, "=" * 70 + "\n\n", "separator")
            
            # 显示每个单词的详细信息
            for i, word_info in enumerate(random_words_info):
                word = word_info['word']
                phonetic = word_info.get('phonetic', '')
                meanings = word_info.get('meanings', [])
                examples = word_info.get('examples', [])
                chinese_meanings = word_info.get('chinese_meanings', [])
                
                # 单词标题
                word_title = f"{i+1:2d}. {word}"
                if phonetic:
                    word_title += f"  [{phonetic}]"
                text_widget.insert(tk.END, word_title + "\n", "word_title")
                
                # 中文释义（优先显示）
                if chinese_meanings:
                    text_widget.insert(tk.END, "    中文释义:\n", "subtitle")
                    for j, meaning in enumerate(chinese_meanings[:3]):  # 只显示前3个释义
                        part_of_speech = meaning.get('part_of_speech', '')
                        definition = meaning.get('definition', '')
                        meaning_text = f"      {part_of_speech}: {definition}" if part_of_speech else f"      {definition}"
                        text_widget.insert(tk.END, meaning_text + "\n", "chinese_meaning")
                # 英文释义
                elif meanings:
                    text_widget.insert(tk.END, "    英文释义:\n", "subtitle")
                    for j, meaning in enumerate(meanings[:3]):  # 只显示前3个释义
                        part_of_speech = meaning.get('part_of_speech', '')
                        definition = meaning.get('definition', '')
                        meaning_text = f"      {part_of_speech}: {definition}" if part_of_speech else f"      {definition}"
                        text_widget.insert(tk.END, meaning_text + "\n", "english_meaning")
                
                # 例句
                if examples:
                    text_widget.insert(tk.END, "    例句:\n", "subtitle")
                    for j, example in enumerate(examples[:2]):  # 只显示前2个例句
                        text_widget.insert(tk.END, f"      • {example}\n", "example")
                
                text_widget.insert(tk.END, "\n")
            
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
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            # 关闭加载指示器
            if self.loading_window and self.loading_window.winfo_exists():
                self.loading_window.destroy()
                self.loading_window = None
                
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"重新生成随机单词时发生错误:\n{str(e)}", "error")
            text_widget.tag_config("error", foreground="red")
            text_widget.config(state=tk.DISABLED)
    
    def on_closing(self):
        """关闭程序时的处理"""
        if messagebox.askokcancel("退出", "确定要退出单词记忆助手吗？"):
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = WordReminderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()