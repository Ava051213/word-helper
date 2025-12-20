#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词记忆助手 GUI 版本
基于 tkinter 的图形用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from word_manager import WordManager
from scheduler import Scheduler


class WordReminderGUI:
    """单词记忆助手图形界面"""
    
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("单词记忆助手")
        self.root.geometry("800x600")
        
        # 初始化数据管理器
        self.word_manager = WordManager("data/words.json")
        self.scheduler = Scheduler(self.word_manager)
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.refresh_word_list()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_add_tab()
        self.create_view_tab()
        self.create_review_tab()
        self.create_search_tab()
        self.create_stats_tab()
    
    def create_add_tab(self):
        """创建添加单词标签页"""
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="添加单词")
        
        # 单词输入
        ttk.Label(self.add_frame, text="单词:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.word_entry = ttk.Entry(self.add_frame, width=30)
        self.word_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 释义输入
        ttk.Label(self.add_frame, text="释义:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.meaning_entry = ttk.Entry(self.add_frame, width=30)
        self.meaning_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 例句输入
        ttk.Label(self.add_frame, text="例句:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.example_entry = ttk.Entry(self.add_frame, width=50)
        self.example_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 分类输入
        ttk.Label(self.add_frame, text="分类:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_entry = ttk.Entry(self.add_frame, width=30)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 添加按钮
        self.add_button = ttk.Button(self.add_frame, text="添加单词", command=self.add_word)
        self.add_button.grid(row=4, column=1, pady=10)
    
    def create_view_tab(self):
        """创建查看单词标签页"""
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="查看单词")
        
        # 创建表格
        columns = ("单词", "释义", "分类", "添加日期")
        self.word_tree = ttk.Treeview(self.view_frame, columns=columns, show="headings", height=20)
        
        # 定义列标题
        for col in columns:
            self.word_tree.heading(col, text=col)
            self.word_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.view_frame, orient=tk.VERTICAL, command=self.word_tree.yview)
        self.word_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.word_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新按钮
        self.refresh_button = ttk.Button(self.view_frame, text="刷新", command=self.refresh_word_list)
        self.refresh_button.pack(pady=5)
    
    def create_review_tab(self):
        """创建复习单词标签页"""
        self.review_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.review_frame, text="复习单词")
        
        # 复习区域
        self.review_area = scrolledtext.ScrolledText(self.review_frame, wrap=tk.WORD, width=70, height=20)
        self.review_area.pack(padx=10, pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(self.review_frame)
        button_frame.pack(pady=5)
        
        self.start_review_button = ttk.Button(button_frame, text="开始复习", command=self.start_review)
        self.start_review_button.pack(side=tk.LEFT, padx=5)
        
        self.know_button = ttk.Button(button_frame, text="认识", state=tk.DISABLED, command=lambda: self.review_feedback(True))
        self.know_button.pack(side=tk.LEFT, padx=5)
        
        self.not_know_button = ttk.Button(button_frame, text="不认识", state=tk.DISABLED, command=lambda: self.review_feedback(False))
        self.not_know_button.pack(side=tk.LEFT, padx=5)
        
        # 初始化复习状态
        self.review_words = []
        self.current_review_index = 0
        self.current_review_word = None
    
    def create_search_tab(self):
        """创建搜索单词标签页"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="搜索单词")
        
        # 搜索框
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(pady=10)
        
        ttk.Label(search_frame, text="搜索关键词:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_button = ttk.Button(search_frame, text="搜索", command=self.search_words)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # 搜索结果
        columns = ("单词", "释义", "分类")
        self.search_tree = ttk.Treeview(self.search_frame, columns=columns, show="headings", height=20)
        
        # 定义列标题
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_stats_tab(self):
        """创建统计信息标签页"""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="学习统计")
        
        # 统计信息显示区域
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD, width=70, height=25)
        self.stats_text.pack(padx=10, pady=10)
        
        # 刷新按钮
        self.stats_refresh_button = ttk.Button(self.stats_frame, text="刷新统计", command=self.show_statistics)
        self.stats_refresh_button.pack(pady=5)
        
        # 初始化显示统计信息
        self.show_statistics()
    
    def add_word(self):
        """添加单词"""
        word = self.word_entry.get().strip().lower()
        meaning = self.meaning_entry.get().strip()
        
        if not word or not meaning:
            messagebox.showwarning("输入错误", "单词和释义不能为空！")
            return
        
        if word in self.word_manager.words:
            messagebox.showwarning("重复单词", f"单词 '{word}' 已存在！")
            return
        
        example = self.example_entry.get().strip()
        category = self.category_entry.get().strip()
        
        # 添加单词
        import datetime
        self.word_manager.words[word] = {
            "meaning": meaning,
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
        
        messagebox.showinfo("成功", f"单词 '{word}' 添加成功！")
        
        # 刷新单词列表
        self.refresh_word_list()
    
    def refresh_word_list(self):
        """刷新单词列表"""
        # 清空现有数据
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 添加新数据
        for word, info in self.word_manager.words.items():
            add_date = info.get('add_date', '')[:10] if info.get('add_date') else ''
            self.word_tree.insert("", tk.END, values=(word, info['meaning'], info['category'], add_date))
    
    def start_review(self):
        """开始复习"""
        self.review_words = self.word_manager.get_words_for_review()
        
        if not self.review_words:
            self.review_area.delete(1.0, tk.END)
            self.review_area.insert(tk.END, "暂无需要复习的单词。\n")
            return
        
        self.current_review_index = 0
        self.show_next_review_word()
        
        # 启用按钮
        self.know_button.config(state=tk.NORMAL)
        self.not_know_button.config(state=tk.NORMAL)
        self.start_review_button.config(state=tk.DISABLED)
    
    def show_next_review_word(self):
        """显示下一个复习单词"""
        if self.current_review_index >= len(self.review_words):
            self.finish_review()
            return
        
        self.current_review_word = self.review_words[self.current_review_index]
        info = self.word_manager.get_word(self.current_review_word)
        
        # 显示单词信息
        self.review_area.delete(1.0, tk.END)
        self.review_area.insert(tk.END, f"单词: {self.current_review_word}\n")
        self.review_area.insert(tk.END, f"释义: {info['meaning']}\n")
        if info.get('example'):
            self.review_area.insert(tk.END, f"例句: {info['example']}\n")
        self.review_area.insert(tk.END, f"\n进度: {self.current_review_index + 1}/{len(self.review_words)}\n")
        self.review_area.insert(tk.END, "请问你是否认识这个单词？\n")
    
    def review_feedback(self, is_known):
        """处理复习反馈"""
        if self.current_review_word:
            info = self.word_manager.get_word(self.current_review_word)
            self.scheduler._update_word_schedule(self.current_review_word, info, is_known)
        
        # 移动到下一个单词
        self.current_review_index += 1
        self.show_next_review_word()
    
    def finish_review(self):
        """完成复习"""
        self.review_area.delete(1.0, tk.END)
        self.review_area.insert(tk.END, f"复习完成！共复习了 {len(self.review_words)} 个单词。\n")
        
        # 禁用按钮
        self.know_button.config(state=tk.DISABLED)
        self.not_know_button.config(state=tk.DISABLED)
        self.start_review_button.config(state=tk.NORMAL)
    
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
                self.search_tree.insert("", tk.END, values=(word, info['meaning'], info['category']))
    
    def show_statistics(self):
        """显示统计信息"""
        total_words = len(self.word_manager.words)
        reviewed_words = sum(1 for info in self.word_manager.words.values() if info['review_count'] > 0)
        
        stats_text = f"""
单词记忆助手 - 学习统计

总单词数: {total_words}
已复习单词数: {reviewed_words}
未复习单词数: {total_words - reviewed_words}

"""
        
        if total_words > 0:
            review_rate = (reviewed_words / total_words) * 100
            stats_text += f"复习率: {review_rate:.1f}%\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = WordReminderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()