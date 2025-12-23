import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import time
import random
import datetime
import os
from .base_tab import BaseTab

class ReviewTab(BaseTab):
    """复习单词标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        
        # 初始化复习状态
        self.review_words = []
        self.current_review_index = 0
        self.current_review_word = None
        self.review_results = []  # 记录复习结果
        self.is_quick_review = False
        self.review_start_time = None
        self.review_paused = False
        self.review_mode = tk.StringVar(value="Standard") # "Standard", "Dictation", "Choice"
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建复习单词标签页内容"""
        # 复习控制面板
        control_frame = ctk.CTkFrame(self)
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

        # 添加复习模式选择
        mode_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        mode_frame.pack(side=tk.RIGHT, padx=10)
        
        ctk.CTkLabel(mode_frame, text="复习模式:").pack(side=tk.LEFT, padx=5)
        self.mode_selector = ctk.CTkSegmentedButton(mode_frame, values=["Standard", "Dictation", "Choice"],
                                                   variable=self.review_mode, command=self.on_mode_change)
        self.mode_selector.pack(side=tk.LEFT, padx=5)
        # 设置中文显示
        self.mode_selector.configure(values=["标准", "听写", "选择"])
        self.review_mode_map = {"标准": "Standard", "听写": "Dictation", "选择": "Choice"}
        
        # 复习区域 - 使用 CTkTabview
        self.review_tabview = ctk.CTkTabview(self)
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
        
        self.word_display_container = ctk.CTkFrame(word_display_frame, fg_color="transparent")
        self.word_display_container.pack(pady=(40, 10))
        
        self.word_label = ctk.CTkLabel(self.word_display_container, text="", font=('Arial', 32, 'bold'))
        self.word_label.pack(side=tk.LEFT)
        
        self.review_speak_button = ctk.CTkButton(self.word_display_container, text="🔊", width=40, height=40,
                                                command=lambda: self.audio_manager.speak(self.current_review_word))
        self.review_speak_button.pack(side=tk.LEFT, padx=10)
        
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
        self.button_frame = ctk.CTkFrame(card_content_frame, fg_color="transparent")
        self.button_frame.pack(pady=20, fill=tk.X, padx=50)
        
        # 1. 标准模式按钮
        self.standard_buttons = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.standard_buttons.pack(expand=True)
        
        self.not_know_button = ctk.CTkButton(self.standard_buttons, text="不认识 (✗)", 
                                         command=lambda: self.review_feedback(False),
                                         state=tk.DISABLED, width=150, height=45, fg_color="#e74c3c", hover_color="#c0392b")
        self.not_know_button.pack(side=tk.LEFT, padx=20)
        
        self.know_button = ctk.CTkButton(self.standard_buttons, text="认识 (✓)", 
                                     command=lambda: self.review_feedback(True),
                                     state=tk.DISABLED, width=150, height=45, fg_color="#2ecc71", hover_color="#27ae60")
        self.know_button.pack(side=tk.LEFT, padx=20)
        
        self.later_button = ctk.CTkButton(self.standard_buttons, text="稍后复习", 
                                      command=lambda: self.review_feedback(None),
                                      state=tk.DISABLED, width=150, height=45, fg_color="#f39c12", hover_color="#d35400")
        self.later_button.pack(side=tk.LEFT, padx=20)
        
        # 2. 听写模式界面
        self.dictation_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        # 初始隐藏
        
        self.dictation_entry = ctk.CTkEntry(self.dictation_frame, placeholder_text="输入单词拼写...", width=300, height=40)
        self.dictation_entry.pack(side=tk.LEFT, padx=10)
        self.dictation_entry.bind("<Return>", lambda e: self.check_dictation())
        
        self.dictation_submit = ctk.CTkButton(self.dictation_frame, text="检查", command=self.check_dictation, width=100, height=40)
        self.dictation_submit.pack(side=tk.LEFT, padx=10)
        
        # 3. 选择模式界面
        self.choice_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        # 初始隐藏
        
        self.choice_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(self.choice_frame, text="", command=lambda idx=i: self.check_choice(idx), 
                                width=250, height=50, fg_color="transparent", border_width=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.choice_buttons.append(btn)

        # 在统计视图中添加控制按钮
        stats_control_frame = ctk.CTkFrame(self.stats_frame)
        stats_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkButton(stats_control_frame, text="导出复习记录", command=self.export_review_record, width=120).pack(side=tk.LEFT, padx=10, pady=10)
        ctk.CTkButton(stats_control_frame, text="重新开始", command=self.restart_review, width=120).pack(side=tk.LEFT, padx=10, pady=10)
        ctk.CTkButton(stats_control_frame, text="查看历史记录", command=self.show_review_history, width=120).pack(side=tk.LEFT, padx=10, pady=10)
        
        ctk.CTkLabel(stats_control_frame, text="复习完成后可导出记录或重新开始", font=('Arial', 12)).pack(side=tk.LEFT, padx=20)
        
        self.stats_text = ctk.CTkTextbox(self.stats_frame, font=('Arial', 12))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 更新待复习单词数量
        self.update_review_count()

    def on_mode_change(self, selected_mode):
        """处理复习模式改变"""
        mode = self.review_mode_map.get(selected_mode, "Standard")
        
        # 隐藏所有模式按钮
        self.standard_buttons.pack_forget()
        self.dictation_frame.pack_forget()
        self.choice_frame.pack_forget()
        
        # 显示选中的模式按钮
        if mode == "Standard":
            self.standard_buttons.pack(expand=True)
            if self.current_review_word:
                self.word_label.configure(text=self.current_review_word)
                self.meaning_label.configure(text=self.word_manager.get_word(self.current_review_word)['meaning'])
        elif mode == "Dictation":
            self.dictation_frame.pack(expand=True)
            self.dictation_entry.delete(0, tk.END)
            self.dictation_entry.focus_set()
            if self.current_review_word:
                # 听写模式下，如果还没开始或已完成，显示提示
                if self.word_label.cget("text") not in ["复习已结束", "复习已暂停", "复习已完成"]:
                    self.word_label.configure(text="***")
                    self.meaning_label.configure(text=self.word_manager.get_word(self.current_review_word)['meaning'])
        elif mode == "Choice":
            self.choice_frame.pack(expand=True)
            if self.current_review_word:
                self.word_label.configure(text=self.current_review_word)
                self.update_choices()

    def update_choices(self):
        """为选择模式生成并显示选项"""
        if not self.current_review_word:
            return
            
        correct_meaning = self.word_manager.get_word(self.current_review_word)['meaning']
        
        # 获取干扰项 (从所有单词中随机选)
        all_words = self.word_manager.get_all_words()
        other_meanings = [w['meaning'] for w in all_words if w['word'] != self.current_review_word]
        
        if len(other_meanings) < 3:
            # 如果单词太少，用占位符
            other_meanings += ["(占位选项1)", "(占位选项2)", "(占位选项3)"]
            
        distractors = random.sample(other_meanings, 3)
        self.current_choices = distractors + [correct_meaning]
        random.shuffle(self.current_choices)
        
        for i, btn in enumerate(self.choice_buttons):
            btn.configure(text=self.current_choices[i], fg_color="transparent", border_color="#3b8ed0")

    def check_dictation(self):
        """检查听写拼写"""
        if not self.current_review_word:
            return
            
        user_input = self.dictation_entry.get().strip().lower()
        is_correct = user_input == self.current_review_word.lower()
        
        if is_correct:
            self.status_bar.configure(text=f"拼写正确: {self.current_review_word}", text_color="#2ecc71")
            self.review_feedback(True)
            self.dictation_entry.delete(0, tk.END)
        else:
            self.status_bar.configure(text=f"拼写错误，正确是: {self.current_review_word}", text_color="#e74c3c")
            # 摇晃效果 (模拟)
            self.dictation_entry.configure(border_color="#e74c3c")
            self.parent_gui.root.after(1000, lambda: self.dictation_entry.configure(border_color="#3b8ed0"))
            self.review_feedback(False)

    def check_choice(self, idx):
        """检查选择题答案"""
        if not self.current_review_word:
            return
            
        selected_meaning = self.current_choices[idx]
        correct_meaning = self.word_manager.get_word(self.current_review_word)['meaning']
        is_correct = selected_meaning == correct_meaning
        
        # 反馈颜色
        btn = self.choice_buttons[idx]
        if is_correct:
            btn.configure(fg_color="#2ecc71")
            self.status_bar.configure(text="回答正确！", text_color="#2ecc71")
        else:
            btn.configure(fg_color="#e74c3c")
            self.status_bar.configure(text=f"回答错误，正确释义是: {correct_meaning}", text_color="#e74c3c")
            
        # 延迟进入下一个
        self.parent_gui.root.after(500, lambda: self.review_feedback(is_correct))

    def update_review_count(self):
        """更新待复习单词数量显示"""
        review_count = len(self.word_manager.get_words_for_review())
        self.review_count_label.configure(text=f"待复习单词: {review_count}")

    def start_review(self):
        """开始复习（标准复习，更新复习数据）"""
        self.is_quick_review = False
        self.review_start_time = time.time()
        self.review_words = self.word_manager.get_words_for_review()
        
        if not self.review_words:
            messagebox.showinfo("提示", "暂无需要复习的单词。\n\n建议：\n1. 添加更多单词到词库中\n2. 等待已学单词到达复习时间")
            return
        
        random.shuffle(self.review_words)
        new_words = [word for word in self.review_words if self.word_manager.get_word(word).get('review_count', 0) == 0]
        
        self.review_results = []
        self.current_review_index = 0
        
        if new_words:
            welcome_msg = f"开始复习！\n\n本次复习包含 {len(self.review_words)} 个单词：\n- 新单词: {len(new_words)} 个\n- 待复习单词: {len(self.review_words) - len(new_words)} 个"
            messagebox.showinfo("复习开始", welcome_msg)
        
        self.show_next_review_word()
        
        # 启用按钮
        self.know_button.configure(state=tk.NORMAL)
        self.not_know_button.configure(state=tk.NORMAL)
        self.later_button.configure(state=tk.NORMAL)
        self.start_review_button.configure(state=tk.DISABLED)
        self.pause_review_button.configure(state=tk.NORMAL)
        self.stop_review_button.configure(state=tk.NORMAL)
        
        # 切换到卡片视图
        self.review_tabview.set("学习卡片")

    def show_next_review_word(self):
        """显示下一个复习单词"""
        if self.current_review_index >= len(self.review_words):
            self.finish_review()
            return
        
        self.current_review_word = self.review_words[self.current_review_index]
        info = self.word_manager.get_word(self.current_review_word)
        
        # 获取当前模式
        current_mode = self.review_mode_map.get(self.mode_selector.get(), "Standard")
        
        # 根据模式显示内容
        if current_mode == "Dictation":
            self.word_label.configure(text="***")
            self.meaning_label.configure(text=info['meaning'])
            self.dictation_entry.delete(0, tk.END)
            self.dictation_entry.focus_set()
        elif current_mode == "Choice":
            self.word_label.configure(text=self.current_review_word)
            self.meaning_label.configure(text="请选择正确的释义")
            self.update_choices()
        else:
            self.word_label.configure(text=self.current_review_word)
            self.meaning_label.configure(text=info['meaning'])
            
        # 自动朗读逻辑
        if self.config_manager.get("auto_play_tts", False):
            self.audio_manager.speak(self.current_review_word)
            
        phonetic_text = ""
        meaning_text = info['meaning']
        
        if self.buffered_dictionary_api:
            word_info = self.buffered_dictionary_api.get_word_info(self.current_review_word)
            if word_info:
                if word_info.get('phonetic'):
                    phonetic_text = f"/{word_info['phonetic']}/"
                if word_info.get('chinese_meanings'):
                    meaning_text = word_info['chinese_meanings'][0]['definition']
                elif word_info.get('meanings'):
                    meaning_text = word_info['meanings'][0]['definition']
                
                if not info.get('example') and word_info.get('examples'):
                    self.example_label.configure(text=word_info['examples'][0])
        
        self.phonetic_label.configure(text=phonetic_text)
        self.meaning_label.configure(text=meaning_text)
        
        if not self.example_label.cget("text"):
            self.example_label.configure(text=info.get('example', ''))
        
        # 更新进度条
        progress = (self.current_review_index) / len(self.review_words)
        self.review_progress.set(progress)
        
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
            
            self.review_results.append({
                'word': self.current_review_word,
                'known': is_known,
                'old_interval': old_interval
            })
            
            if is_known is not None:
                if not self.is_quick_review:
                    quality = 4 if is_known else 1
                    self.word_manager.update_review_status(self.current_review_word, quality)
            else:
                if self.current_review_word in self.review_words:
                    self.review_words.remove(self.current_review_word)
                    self.review_words.append(self.current_review_word)
                self.show_next_review_word()
                return
        
        self.current_review_index += 1
        self.show_next_review_word()

    def finish_review(self):
        """完成复习"""
        self.word_label.configure(text="复习已完成")
        self.phonetic_label.configure(text="")
        self.meaning_label.configure(text="请查看复习统计信息")
        self.example_label.configure(text="")
        self.progress_label.configure(text="")
        self.review_progress.set(1.0)
        
        try:
            self.know_button.configure(state=tk.DISABLED)
            self.not_know_button.configure(state=tk.DISABLED)
            self.later_button.configure(state=tk.DISABLED)
            self.start_review_button.configure(state=tk.NORMAL)
            self.pause_review_button.configure(state=tk.DISABLED)
            self.stop_review_button.configure(state=tk.DISABLED)
        except Exception as e:
            print(f"按钮状态设置错误: {e}")
        
        self.show_review_stats()
        
        try:
            self.review_tabview.set("复习统计")
        except:
            pass
        
        if not self.is_quick_review:
            self.update_review_count()
            if hasattr(self.parent_gui, 'update_reminder'):
                self.parent_gui.update_reminder()
            if hasattr(self.parent_gui, 'refresh_word_list'):
                self.parent_gui.refresh_word_list()
            if hasattr(self.parent_gui, 'show_statistics'):
                self.parent_gui.show_statistics()
            self.status_bar.configure(text="复习已完成，界面已更新")
        else:
            self.status_bar.configure(text="快捷复习已完成（练习模式）")
        
        if self.review_results:
            known_count = sum(1 for result in self.review_results if result['known'])
            total_count = len(self.review_results)
            accuracy = (known_count / total_count) * 100 if total_count > 0 else 0
            
            if self.is_quick_review:
                completion_message = f"快捷复习完成！\n\n📊 本次练习统计:\n  • 练习单词数: {total_count}\n  • 掌握单词数: {known_count}\n  • 正确率: {accuracy:.1f}%\n\n💡 提示: 快捷复习是练习模式，不会影响正式的复习计划。"
            else:
                completion_message = f"复习完成！\n\n📊 本次复习统计:\n  • 复习单词数: {total_count}\n  • 掌握单词数: {known_count}\n  • 正确率: {accuracy:.1f}%\n\n💡 提示: 定期复习是记忆的关键，建议按照复习计划持续学习。"
            
            messagebox.showinfo("复习完成", completion_message)
        else:
            messagebox.showinfo("复习完成", "复习已完成，但未复习任何单词。")
        
        self.is_quick_review = False

    def toggle_pause_review(self):
        """暂停/继续复习"""
        if self.review_paused:
            self.review_paused = False
            self.pause_review_button.configure(text="暂停复习")
            self.know_button.configure(state=tk.NORMAL)
            self.not_know_button.configure(state=tk.NORMAL)
            self.later_button.configure(state=tk.NORMAL)
            self.status_bar.configure(text="复习已继续")
            if self.current_review_word:
                self.show_next_review_word()
        else:
            self.review_paused = True
            self.pause_review_button.configure(text="继续复习")
            self.know_button.configure(state=tk.DISABLED)
            self.not_know_button.configure(state=tk.DISABLED)
            self.later_button.configure(state=tk.DISABLED)
            self.status_bar.configure(text="复习已暂停")
            if self.current_review_word:
                self.word_label.configure(text="复习已暂停")
                self.meaning_label.configure(text="点击'继续复习'按钮继续学习")
                self.example_label.configure(text="")
                self.phonetic_label.configure(text="")

    def stop_review(self):
        """结束当前复习会话"""
        confirm = messagebox.askyesno("确认结束", "确定要结束当前复习会话吗？\n\n已完成的复习将保留，未完成的单词将不会更新复习数据。")
        if not confirm:
            return
        
        self.review_results = []
        self.current_review_index = 0
        self.current_review_word = None
        
        self.word_label.configure(text="复习已结束")
        self.phonetic_label.configure(text="")
        self.meaning_label.configure(text="点击'开始复习'按钮重新开始")
        self.example_label.configure(text="")
        self.progress_label.configure(text="")
        self.review_progress.set(0)
        
        self.know_button.configure(state=tk.DISABLED)
        self.not_know_button.configure(state=tk.DISABLED)
        self.later_button.configure(state=tk.DISABLED)
        self.start_review_button.configure(state=tk.NORMAL)
        self.pause_review_button.configure(state=tk.DISABLED)
        self.stop_review_button.configure(state=tk.DISABLED)
        
        self.status_bar.configure(text="复习已结束")
        messagebox.showinfo("复习已结束", "当前复习会话已结束。\n\n您可以：\n1. 点击'开始复习'重新开始复习\n2. 查看复习统计了解已完成的进度")

    def show_review_history(self):
        """显示复习历史记录"""
        try:
            history = self.word_manager.get_review_history()
            if not history:
                messagebox.showinfo("复习历史", "暂无复习历史记录。")
                return
            
            history_window = ctk.CTkToplevel(self)
            history_window.title("复习历史记录")
            history_window.geometry("900x700")
            history_window.minsize(700, 500)
            
            history_window.transient(self.parent_gui.root)
            history_window.grab_set()
            
            main_container = ctk.CTkFrame(history_window)
            main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(main_container, text="复习历史记录", font=('Arial', 20, 'bold')).pack(pady=(0, 20))
            
            history_tabview = ctk.CTkTabview(main_container)
            history_tabview.pack(fill=tk.BOTH, expand=True)
            
            overview_tab = history_tabview.add("概览")
            detail_tab = history_tabview.add("详细记录")
            
            overview_text = ctk.CTkTextbox(overview_tab, font=('Arial', 13))
            overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            detail_text = ctk.CTkTextbox(detail_tab, font=('Arial', 12))
            detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            total_sessions = len(history)
            total_words = sum(len(session.get('words', [])) for session in history)
            total_known = sum(session.get('known_count', 0) for session in history)
            
            overview_content = f"""复习历史概览\n================\n\n总复习次数: {total_sessions}\n总复习单词数: {total_words}\n掌握单词数: {total_known}\n平均正确率: {(total_known / total_words * 100) if total_words > 0 else 0:.1f}%\n\n最近复习记录:\n"""
            
            recent_sessions = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            for i, session in enumerate(recent_sessions):
                timestamp = session.get('timestamp', '未知时间')
                word_count = len(session.get('words', []))
                known_count = session.get('known_count', 0)
                accuracy = (known_count / word_count * 100) if word_count > 0 else 0
                overview_content += f"\n{i+1}. {timestamp[:16]}: {word_count}个单词, 正确率{accuracy:.1f}%"
            
            overview_text.insert(tk.END, overview_content)
            overview_text.configure(state="disabled")
            
            detail_content = "详细复习记录\n================\n\n"
            for i, session in enumerate(sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)):
                timestamp = session.get('timestamp', '未知时间')
                words = session.get('words', [])
                known_count = session.get('known_count', 0)
                detail_content += f"复习会话 #{i+1} - {timestamp}\n单词数: {len(words)}, 掌握: {known_count}, 正确率: {(known_count/len(words)*100) if words else 0:.1f}%\n"
                for j, word_result in enumerate(words):
                    word = word_result.get('word', '未知单词')
                    known = word_result.get('known')
                    status = "✓ 掌握" if known is True else "✗ 未掌握" if known is False else "⧖ 稍后复习"
                    detail_content += f"  {j+1}. {status} {word}\n"
                detail_content += "\n" + "-" * 50 + "\n\n"
            
            detail_text.insert(tk.END, detail_content)
            detail_text.configure(state="disabled")
            
            button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def export_history():
                try:
                    filename = f"复习历史_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(overview_content + "\n\n" + detail_content)
                    messagebox.showinfo("导出成功", f"复习历史已导出到:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("导出失败", f"导出复习历史时发生错误:\n{str(e)}")
            
            ctk.CTkButton(button_frame, text="导出历史记录", command=export_history, width=150).pack(side=tk.RIGHT, padx=10)
            ctk.CTkButton(button_frame, text="关闭", command=history_window.destroy, width=100, fg_color="gray").pack(side=tk.RIGHT, padx=10)
        except Exception as e:
            messagebox.showerror("错误", f"显示复习历史时发生错误: {e}")

    def show_review_stats(self):
        """显示复习统计"""
        if not self.review_results:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "暂无复习记录。")
            return
        
        known_count = sum(1 for result in self.review_results if result['known'])
        unknown_count = sum(1 for result in self.review_results if result['known'] is False)
        later_count = sum(1 for result in self.review_results if result['known'] is None)
        total_count = len(self.review_results)
        accuracy = (known_count / total_count) * 100 if total_count > 0 else 0
        
        difficulty_analysis = self._analyze_word_difficulty()
        time_analysis = self._analyze_review_time()
        progress_analysis = self._analyze_learning_progress()
        
        stats_text = f"""\n📊 复习统计报告\n=================\n\n📈 基本统计\n复习单词数: {total_count}\n掌握单词数: {known_count}\n未掌握单词数: {unknown_count}\n稍后复习单词数: {later_count}\n正确率: {accuracy:.1f}%\n\n🎯 难度分析\n{difficulty_analysis}\n\n⏱️ 时间分析\n{time_analysis}\n\n📈 学习进度\n{progress_analysis}\n\n📋 详细记录:\n"""
        
        for i, result in enumerate(self.review_results, 1):
            status = "✓ 掌握" if result['known'] is True else "✗ 未掌握" if result['known'] is False else "⧖ 稍后复习"
            word = result['word']
            word_info = self.word_manager.get_word(word)
            meaning = word_info['meaning']
            review_count = word_info.get('review_count', 0)
            stats_text += f"{i:2d}. {status} {word} - {meaning} (复习次数: {review_count}, 间隔: {result['old_interval']}天)\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)

    def _analyze_word_difficulty(self):
        difficulty_stats = {"简单": 0, "中等": 0, "困难": 0}
        for result in self.review_results:
            word = result['word']
            word_info = self.word_manager.get_word(word)
            review_count = word_info.get('review_count', 0)
            interval = word_info.get('interval', 1)
            if review_count <= 1 and interval <= 1: difficulty_stats["困难"] += 1
            elif review_count <= 3 and interval <= 3: difficulty_stats["中等"] += 1
            else: difficulty_stats["简单"] += 1
        
        total = len(self.review_results)
        return "\n".join([f"{d}: {c}个 ({(c/total*100) if total else 0:.1f}%)" for d, c in difficulty_stats.items()])

    def _analyze_review_time(self):
        if not self.review_start_time: return "时间数据不可用"
        total_time = time.time() - self.review_start_time
        avg_time = total_time / len(self.review_results) if self.review_results else 0
        return f"总复习时间: {total_time/60:.1f}分钟\n平均每个单词: {avg_time:.1f}秒"

    def _analyze_learning_progress(self):
        mastered = [r['word'] for r in self.review_results if r['known']]
        struggling = [r['word'] for r in self.review_results if not r['known'] and self.word_manager.get_word(r['word']).get('review_count', 0) > 2]
        progress = f"掌握单词: {len(mastered)}个\n需要重点复习: {len(struggling)}个\n"
        if len(struggling) > len(mastered): progress += "建议: 需要加强复习困难单词"
        elif len(mastered) >= len(self.review_results) * 0.8: progress += "建议: 学习进度良好，继续保持"
        else: progress += "建议: 稳步推进，注意复习频率"
        return progress

    def export_review_record(self):
        if not self.review_results:
            messagebox.showwarning("警告", "暂无复习记录可导出。")
            return
        export_text = f"单词复习记录\n===============\n\n复习时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n复习单词数: {len(self.review_results)}\n\n"
        for result in self.review_results:
            status = "✓ 掌握" if result['known'] is True else "✗ 未掌握" if result['known'] is False else "⧖ 稍后复习"
            word = result['word']
            meaning = self.word_manager.get_word(word)['meaning']
            export_text += f"{status} {word} - {meaning}\n"
        try:
            filename = f"复习记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(export_text)
            messagebox.showinfo("成功", f"复习记录已导出到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出复习记录时发生错误:\n{str(e)}")

    def restart_review(self):
        self.review_results = []
        self.current_review_index = 0
        self.current_review_word = None
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "准备开始新的复习会话...")
        self.start_review_button.configure(state=tk.NORMAL)
        self.review_tabview.set("学习卡片")
        messagebox.showinfo("提示", "已准备好重新开始复习。点击'开始复习'按钮开始新的复习会话。")

    def quick_review(self):
        """快捷复习 - 随机复习所有已存在的单词（不更新复习数据）"""
        self.is_quick_review = True
        self.review_start_time = time.time()
        all_words_info = self.word_manager.get_all_words()
        all_words = [w['word'] for w in all_words_info]
        
        if not all_words:
            messagebox.showinfo("提示", "词库中暂无单词。\n\n建议：\n1. 添加更多单词到词库中\n2. 使用随机生成功能添加单词")
            return
        
        random.shuffle(all_words)
        self.review_words = all_words[:20]
        
        new_words = [word for word in self.review_words if self.word_manager.get_word(word).get('review_count', 0) == 0]
        self.review_results = []
        self.current_review_index = 0
        
        welcome_msg = f"开始快捷复习！\n\n本次将随机复习 {len(self.review_words)} 个单词：\n"
        if new_words: welcome_msg += f"- 新单词: {len(new_words)} 个\n"
        welcome_msg += f"- 已复习单词: {len(self.review_words) - len(new_words)} 个\n\n💡 提示: 快捷复习是单纯的练习，不会更新复习日期和间隔。"
        messagebox.showinfo("快捷复习开始", welcome_msg)
        
        self.show_next_review_word()
        self.know_button.configure(state=tk.NORMAL)
        self.not_know_button.configure(state=tk.NORMAL)
        self.later_button.configure(state=tk.NORMAL)
        self.start_review_button.configure(state=tk.DISABLED)
        self.pause_review_button.configure(state=tk.NORMAL)
        self.stop_review_button.configure(state=tk.NORMAL)
        
        self.review_tabview.set("学习卡片")
        self.status_bar.configure(text=f"快捷复习已开始，将随机复习 {len(self.review_words)} 个单词（练习模式）")
