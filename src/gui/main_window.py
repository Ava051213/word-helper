#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词记忆助手 GUI 版本 (改进版)
基于 tkinter 的图形用户界面，提供更好的用户体验
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sys
import os
import logging
import time
import threading

logger = logging.getLogger(__name__)

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.word_manager import WordManager
from core.scheduler import Scheduler
from core.config_manager import ConfigManager
from api.buffered_dictionary_api import BufferedDictionaryAPI
from utils.common import init_logging
from gui.tabs import HomeTab, AddTab, ViewTab, ReviewTab, SearchTab, StatsTab, SettingsTab


class WordReminderGUI:
    """单词记忆助手图形界面"""
    
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 设置 CustomTkinter 主题
        appearance_mode = self.config_manager.get("appearance_mode", "System")
        ctk.set_appearance_mode(appearance_mode)
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
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定键盘快捷键
        self.root.bind('<Control-f>', lambda event: self.focus_search_entry())
        
        # 检查词典API状态
        self.check_dictionary_api_status()
        
        # 初始化加载指示器
        self.loading_window = None
        
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
        
        # 如果统计页面已初始化，刷新统计页面以适应新主题
        if hasattr(self, 'stats_tab_comp'):
            self.stats_tab_comp.show_statistics()

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
        # 创建状态栏
        self.status_bar_frame = ctk.CTkFrame(self.root, height=30)
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ctk.CTkLabel(self.status_bar_frame, text="就绪", anchor=tk.W, padx=10)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X)

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
        
        # 绑定标签页切换事件以添加过渡效果
        self.tabview.configure(command=self.on_tab_change)
        
        # 初始化标签页组件
        self.home_tab_comp = HomeTab(self.home_tab, self)
        self.add_tab_comp = AddTab(self.add_tab, self)
        self.view_tab_comp = ViewTab(self.view_tab, self)
        self.review_tab_comp = ReviewTab(self.review_tab, self)
        self.search_tab_comp = SearchTab(self.search_tab, self)
        self.stats_tab_comp = StatsTab(self.stats_tab, self)
        self.settings_tab_comp = SettingsTab(self.settings_tab, self)
    
    def on_tab_change(self):
        """处理标签页切换"""
        current_tab = self.tabview.get()
        
        # 刷新对应标签页的数据
        if current_tab == "学习统计" and hasattr(self, 'stats_tab_comp'):
            self.stats_tab_comp.show_statistics()
        elif current_tab == "首页" and hasattr(self, 'home_tab_comp'):
            self.home_tab_comp.update_reminder()
        elif current_tab == "复习单词" and hasattr(self, 'review_tab_comp'):
            self.review_tab_comp.update_review_count()
        elif current_tab == "查看单词" and hasattr(self, 'view_tab_comp'):
            self.view_tab_comp.refresh_word_list()

    def refresh_word_list(self):
        """刷新单词列表 (委托给 ViewTab)"""
        if hasattr(self, 'view_tab_comp'):
            self.view_tab_comp.refresh_word_list()
    
    def update_review_count(self):
        """更新待复习数量 (委托给 ReviewTab)"""
        if hasattr(self, 'review_tab_comp'):
            self.review_tab_comp.update_review_count()
            
    def update_reminder(self):
        """更新首页提醒 (委托给 HomeTab)"""
        if hasattr(self, 'home_tab_comp'):
            self.home_tab_comp.update_reminder()

    def focus_search_entry(self):
        """聚焦到搜索输入框 (委托给 SearchTab)"""
        self.tabview.set("搜索单词")
        if hasattr(self, 'search_tab_comp'):
            self.search_tab_comp.search_entry.focus_set()

    def on_closing(self):
        """处理窗口关闭"""
        if messagebox.askokcancel("退出", "确定要退出单词记忆助手吗？"):
            self.root.destroy()


def main():
    """主函数"""
    root = ctk.CTk()
    app = WordReminderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
