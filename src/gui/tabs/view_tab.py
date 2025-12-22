#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import json
import os
from .base_tab import BaseTab

class ViewTab(BaseTab):
    """查看单词标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        # 防抖定时器
        self.search_debounce_timer = None
        self._create_widgets()
        self.load_view_search_history()

    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ctk.CTkFrame(self)
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
        detail_window = ctk.CTkToplevel(self.parent_gui.root)
        detail_window.title(f"单词详情 - {word}")
        detail_window.geometry("600x600")
        detail_window.minsize(500, 400)
        
        # 设置窗口居中
        detail_window.transient(self.parent_gui.root)
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
            self.parent_gui.show_loading_indicator(f"正在获取单词 '{word}' 的详细信息...")
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
                self.parent_gui.hide_loading_indicator()
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
        self.parent_gui.show_loading_indicator(f"正在获取单词 '{word}' 的详细信息...")
        
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
            self.parent_gui.hide_loading_indicator()

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
        """视图搜索框内容变化时触发（带防抖）"""
        # 取消之前的定时器
        if self.search_debounce_timer:
            self.after_cancel(self.search_debounce_timer)
        
        # 300ms后执行搜索（防抖）
        from ..core.constants import Constants
        self.search_debounce_timer = self.after(Constants.DEBOUNCE_DELAY, self._perform_search)
    
    def _perform_search(self):
        """执行搜索操作"""
        self.refresh_word_list()
        # 保存搜索历史
        search_term = self.view_search_var.get().strip()
        if search_term:
            self.save_view_search_history(search_term)

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
                if hasattr(self.parent_gui, 'update_review_count'):
                    self.parent_gui.update_review_count()
                if hasattr(self.parent_gui, 'home_tab'):
                    self.parent_gui.home_tab.update_reminder()
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
        edit_window = ctk.CTkToplevel(self.parent_gui.root)
        edit_window.title(f"编辑单词 - {word}")
        edit_window.geometry("600x500")
        edit_window.minsize(500, 400)
        
        # 设置窗口居中
        edit_window.transient(self.parent_gui.root)
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

    def load_view_search_history(self):
        """加载单词管理界面的搜索历史"""
        try:
            # 使用正确的数据文件路径
            data_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            history_file = os.path.join(data_dir, "data", "view_search_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # 只显示最近10条历史记录
                    self.view_search_history_combo.configure(values=history[:10])
        except Exception as e:
            print(f"加载单词管理搜索历史时出错: {e}")

    def save_view_search_history(self, keyword):
        """保存单词管理界面的搜索历史"""
        try:
            # 使用正确的数据文件路径
            data_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            history_file = os.path.join(data_dir, "data", "view_search_history.json")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            
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
            self.view_search_history_combo.configure(values=history[:10])
            
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
            data_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
                self.view_search_history_combo.configure(values=history[:10])
                self.view_search_history_var.set("")
                
                messagebox.showinfo("成功", f"已删除搜索历史: {selected_keyword}")
            else:
                messagebox.showwarning("警告", "未找到该搜索历史记录")
                
        except Exception as e:
            messagebox.showerror("错误", f"删除搜索历史时发生错误:\n{str(e)}")
