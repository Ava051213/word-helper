#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import threading
from .base_tab import BaseTab

class AddTab(BaseTab):
    """添加单词标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        
        self.form_validation_states = {
            'word': 'neutral',
            'meaning': 'neutral',
            'example': 'neutral',
            'category': 'neutral'
        }
        self.validation_errors = {}
        
        self._create_widgets()
        self.setup_form_validation()

    def _create_widgets(self):
        """创建界面组件"""
        # 创建主容器
        main_container = ctk.CTkFrame(self)
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
        saved_level = self.config_manager.get("default_vocabulary_level", "cet6")
        self.vocab_level_var = tk.StringVar(value=saved_level)
        self.vocab_combobox = ctk.CTkComboBox(form_frame, variable=self.vocab_level_var, 
                                             values=["cet4", "cet6", "gre"], height=35,
                                             command=self._on_vocab_level_change)
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

    def _on_vocab_level_change(self, new_level: str):
        """处理词汇级别变化"""
        self.config_manager.set("default_vocabulary_level", new_level)
        self.status_bar.configure(text=f"默认词汇级别已更新为: {new_level.upper()}")

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
            # 恢复默认边框颜色
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
            self.parent_gui.show_loading_indicator(f"正在获取单词 '{word}' 的信息...")
            
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
                self.parent_gui.hide_loading_indicator()
        
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
            if hasattr(self.parent_gui, 'refresh_word_list'):
                self.parent_gui.refresh_word_list()
            if hasattr(self.parent_gui, 'update_review_count'):
                self.parent_gui.update_review_count()
            self.show_success_feedback(f"单词 '{word}' {action}成功！")
            self.clear_form()
            if hasattr(self.parent_gui, 'home_tab'):
                self.parent_gui.home_tab.update_reminder()
        else:
            self.show_error_feedback(f"单词 '{word}' {action}失败！")
            self.add_button.configure(state=tk.NORMAL, text="添加单词")

    def show_success_feedback(self, message):
        """显示成功反馈"""
        # 在状态栏显示成功信息
        self.status_bar.configure(text=message, text_color='#2ecc71')
        
        # 短暂改变状态栏颜色
        def reset_status_bar():
            mode = ctk.get_appearance_mode()
            self.status_bar.configure(text_color="#ffffff" if mode == "Dark" else "#000000")
        
        # 3秒后恢复状态栏颜色
        self.parent_gui.root.after(3000, reset_status_bar)
        
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
        self.parent_gui.root.after(3000, reset_status_bar)
        
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
        self.parent_gui.root.after(3000, reset_status_bar)
        
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

    def generate_random_words(self):
        """生成随机单词并直接插入到现有输入字段中"""
        # 检查词典API是否可用
        if not hasattr(self.word_manager, 'dictionary_api') or not self.word_manager.dictionary_api:
            messagebox.showerror("错误", "词典API不可用，无法生成随机单词！")
            return
            
        # 显示加载指示器
        self.parent_gui.show_loading_indicator("正在从词典获取随机单词...")
        
        # 异步执行获取操作
        def async_generate():
            try:
                # 获取1个随机单词
                vocab_level = self.vocab_level_var.get()
                
                # 使用缓冲字典API
                random_words_info = self.buffered_dictionary_api.get_random_words_info(1, vocabulary_level=vocab_level)
                
                # 在主线程中更新UI
                self.parent_gui.root.after(0, lambda: self._update_ui_with_random_words(random_words_info))
                
            except Exception as e:
                # 在主线程中显示错误
                self.parent_gui.root.after(0, lambda: self._show_random_words_error(str(e)))
        
        # 启动异步操作
        threading.Thread(target=async_generate, daemon=True).start()

    def _update_ui_with_random_words(self, random_words_info):
        """在主线程中更新UI显示随机单词"""
        # 关闭加载指示器
        self.parent_gui.hide_loading_indicator()
        
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
        self.parent_gui.root.after(3000, lambda: self.status_bar.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]))

    def _show_random_words_error(self, error_msg):
        """显示随机单词生成错误"""
        # 关闭加载指示器
        self.parent_gui.hide_loading_indicator()
            
        # 错误消息也使用状态栏显示
        self.status_bar.configure(text=f"生成随机单词时发生错误: {error_msg}", text_color="#e74c3c")
        # 3秒后恢复状态栏
        self.parent_gui.root.after(3000, lambda: self.status_bar.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]))
