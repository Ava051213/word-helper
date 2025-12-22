#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import json
import os
from .base_tab import BaseTab

class SearchTab(BaseTab):
    """搜索单词标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        self.search_results = []
        # 防抖定时器
        self.search_debounce_timer = None
        self._create_widgets()

    def _create_widgets(self):
        """创建搜索单词标签页内容"""
        # 搜索主容器
        main_container = ctk.CTkFrame(self)
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
        self.search_entry.bind('<KeyRelease>', lambda event: self.on_search_key_release())
        
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

    def search_words(self):
        """搜索单词核心逻辑"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword and not self.realtime_search_var.get():
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
            
        # 清空现有结果
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
            
        # 获取所有单词
        all_words = self.word_manager.get_all_words()
        results = []
        
        mode = self.search_mode_var.get()
        scope = self.search_scope_var.get()
        
        for info in all_words:
            word = info['word'].lower()
            meaning = info['meaning'].lower()
            category = info.get('category', '').lower()
            
            match = False
            if mode == "exact":
                if scope == "all":
                    match = keyword == word or keyword == meaning or keyword == category
                elif scope == "word":
                    match = keyword == word
                elif scope == "meaning":
                    match = keyword == meaning
                elif scope == "category":
                    match = keyword == category
            else: # partial
                if scope == "all":
                    match = keyword in word or keyword in meaning or keyword in category
                elif scope == "word":
                    match = keyword in word
                elif scope == "meaning":
                    match = keyword in meaning
                elif scope == "category":
                    match = keyword in category
            
            if match:
                results.append(info)
                
        # 排序
        sort_by = self.sort_var.get()
        results = self._sort_search_results(results, sort_by)
        
        # 显示结果
        for info in results:
            add_date = info.get('added_date', '')[:10] if info.get('added_date') else ''
            self.search_tree.insert("", tk.END, values=(
                info['word'], 
                info['meaning'], 
                info.get('category', ''), 
                add_date, 
                info.get('review_count', 0)
            ))
            
        self.search_results = results
        self._show_search_stats(len(results), keyword)
        
        if not results and not self.realtime_search_var.get():
            self.status_bar.configure(text=f"未找到与 '{keyword}' 匹配的单词")
        else:
            self.status_bar.configure(text=f"找到 {len(results)} 个匹配项")

    def _sort_search_results(self, results, sort_by):
        """对搜索结果进行排序"""
        if sort_by == "word":
            return sorted(results, key=lambda x: x['word'])
        elif sort_by == "date":
            return sorted(results, key=lambda x: x.get('added_date', ''), reverse=True)
        elif sort_by == "category":
            return sorted(results, key=lambda x: x.get('category', ''))
        elif sort_by == "review_count":
            return sorted(results, key=lambda x: x.get('review_count', 0), reverse=True)
        return results

    def _show_search_stats(self, result_count, keyword):
        """显示搜索统计信息"""
        if keyword:
            self.search_stats_label.configure(text=f"找到 {result_count} 个匹配项 (关键词: {keyword})")
        else:
            self.search_stats_label.configure(text=f"找到 {result_count} 个匹配项")

    def clear_search(self):
        """清空搜索框和结果"""
        self.search_entry.delete(0, tk.END)
        self.clear_search_results()
        self.status_bar.configure(text="搜索已重置")

    def on_search_key_release(self):
        """搜索框按键释放事件（带防抖）"""
        # 如果实时搜索未启用，不执行
        if not self.realtime_search_var.get():
            return
        
        # 取消之前的定时器
        if self.search_debounce_timer:
            self.after_cancel(self.search_debounce_timer)
        
        # 300ms后执行搜索（防抖）
        from ..core.constants import Constants
        self.search_debounce_timer = self.after(Constants.DEBOUNCE_DELAY, self.search_words)
        """搜索框按键释放事件"""
        if self.realtime_search_var.get():
            self.search_words()

    def toggle_realtime_search(self):
        """切换实时搜索"""
        if self.realtime_search_var.get():
            self.search_button.configure(state=tk.DISABLED)
            self.search_words()
        else:
            self.search_button.configure(state=tk.NORMAL)

    def on_search_double_click(self, event):
        """搜索结果双击事件"""
        selected = self.search_tree.selection()
        if not selected:
            return
            
        item = selected[0]
        word = self.search_tree.item(item, 'values')[0]
        
        # 切换到查看单词标签页并选中该单词
        if hasattr(self.parent_gui, 'tabview') and hasattr(self.parent_gui, 'view_tab_comp'):
            self.parent_gui.tabview.set("查看单词")
            self.parent_gui.view_tab_comp.view_search_var.set(word)
            self.parent_gui.view_tab_comp.refresh_word_list()

    def export_search_results(self):
        """导出搜索结果"""
        if not self.search_results:
            messagebox.showwarning("警告", "没有可导出的搜索结果")
            return
            
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="导出搜索结果"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        json.dump(self.search_results, f, ensure_ascii=False, indent=4)
                    else:
                        for info in self.search_results:
                            f.write(f"单词: {info['word']}\n释义: {info['meaning']}\n分类: {info.get('category', '')}\n\n")
                
                messagebox.showinfo("成功", f"结果已成功导出至: {file_path}")
                self.status_bar.configure(text=f"导出成功: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def copy_selected_search_results(self):
        """复制选中的搜索结果到剪贴板"""
        selected = self.search_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要复制的项")
            return
            
        copy_text = ""
        for item in selected:
            values = self.search_tree.item(item, 'values')
            copy_text += f"{values[0]}: {values[1]}\n"
            
        self.clipboard_clear()
        self.clipboard_append(copy_text)
        messagebox.showinfo("成功", "选中项已复制到剪贴板")

    def clear_search_results(self):
        """清空搜索结果列表"""
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        self.search_results = []
        self.search_stats_label.configure(text="找到 0 个匹配项")
