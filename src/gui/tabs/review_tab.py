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
        # 1. 顶部状态与控制栏
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # 左侧状态
        status_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_container.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.review_count_label = ctk.CTkLabel(status_container, text="📚 待复习: 0", font=('Arial', 16, 'bold'))
        self.review_count_label.pack(side=tk.LEFT, padx=10)
        
        ctk.CTkButton(status_container, text="🔄 刷新", command=self.update_review_count, width=80, height=32).pack(side=tk.LEFT, padx=5)

        # 右侧模式切换
        mode_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        mode_container.pack(side=tk.RIGHT, padx=10, pady=10)
        
        ctk.CTkLabel(mode_container, text="模式:").pack(side=tk.LEFT, padx=5)
        self.mode_selector = ctk.CTkSegmentedButton(mode_container, values=["标准", "听写", "选择"],
                                                   variable=self.review_mode, command=self.on_mode_change,
                                                   height=32)
        self.mode_selector.pack(side=tk.LEFT, padx=5)
        self.review_mode_map = {"标准": "Standard", "听写": "Dictation", "选择": "Choice"}
        
        # 2. 复习主区域 (卡片)
        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 卡片容器 - 增加阴影感 (模拟)
        self.card_outer = ctk.CTkFrame(self.main_area, corner_radius=15, border_width=2)
        self.card_outer.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        # 单词展示区
        self.word_info_frame = ctk.CTkFrame(self.card_outer, fg_color="transparent")
        self.word_info_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        self.word_label = ctk.CTkLabel(self.word_info_frame, text="准备好了吗？", font=('Arial', 48, 'bold'))
        self.word_label.pack(pady=(40, 10))
        
        self.word_sub_info = ctk.CTkFrame(self.word_info_frame, fg_color="transparent")
        self.word_sub_info.pack(pady=5)
        
        self.phonetic_label = ctk.CTkLabel(self.word_sub_info, text="", font=('Arial', 20), text_color='gray')
        self.phonetic_label.pack(side=tk.LEFT)
        
        self.review_speak_button = ctk.CTkButton(self.word_sub_info, text="🔊", width=40, height=32,
                                                command=lambda: self.word_manager.speak(self.current_review_word))
        self.review_speak_button.pack(side=tk.LEFT, padx=10)
        self.review_speak_button.pack_forget() # 初始隐藏
        
        self.meaning_label = ctk.CTkLabel(self.word_info_frame, text="", font=('Arial', 24))
        self.meaning_label.pack(pady=20)
        
        self.example_label = ctk.CTkLabel(self.word_info_frame, text="", font=('Arial', 18), text_color='gray', wraplength=600)
        self.example_label.pack(pady=10)

        # 3. 底部操作区
        self.bottom_controls = ctk.CTkFrame(self)
        self.bottom_controls.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # 进度条
        progress_container = ctk.CTkFrame(self.bottom_controls, fg_color="transparent")
        progress_container.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        self.progress_label = ctk.CTkLabel(progress_container, text="0 / 0", font=('Arial', 12))
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.review_progress = ctk.CTkProgressBar(progress_container, height=10)
        self.review_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.review_progress.set(0)

        # 交互按钮容器
        self.interaction_frame = ctk.CTkFrame(self.bottom_controls, fg_color="transparent")
        self.interaction_frame.pack(fill=tk.X, padx=20, pady=10)

        # A. 初始状态按钮
        self.start_controls = ctk.CTkFrame(self.interaction_frame, fg_color="transparent")
        self.start_controls.pack(expand=True)
        
        self.start_review_button = ctk.CTkButton(self.start_controls, text="🚀 开始复习", command=self.start_review, 
                                                width=200, height=45, font=('Arial', 16, 'bold'))
        self.start_review_button.pack(side=tk.LEFT, padx=10)
        
        self.quick_review_button = ctk.CTkButton(self.start_controls, text="⚡ 快速复习 (10个)", command=self.quick_review, 
                                                width=200, height=45, fg_color="#f39c12", hover_color="#e67e22")
        self.quick_review_button.pack(side=tk.LEFT, padx=10)

        # B. 标准模式复习按钮 (初始隐藏)
        self.standard_buttons = ctk.CTkFrame(self.interaction_frame, fg_color="transparent")
        
        self.not_know_button = ctk.CTkButton(self.standard_buttons, text="❌ 不认识", 
                                         command=lambda: self.review_feedback(False),
                                         width=160, height=50, fg_color="#e74c3c", hover_color="#c0392b", font=('Arial', 14, 'bold'))
        self.not_know_button.pack(side=tk.LEFT, padx=20)
        
        self.know_button = ctk.CTkButton(self.standard_buttons, text="✅ 认识", 
                                     command=lambda: self.review_feedback(True),
                                     width=160, height=50, fg_color="#2ecc71", hover_color="#27ae60", font=('Arial', 14, 'bold'))
        self.know_button.pack(side=tk.LEFT, padx=20)
        
        self.later_button = ctk.CTkButton(self.standard_buttons, text="🕒 稍后", 
                                      command=lambda: self.review_feedback(None),
                                      width=120, height=50, fg_color="#95a5a6", hover_color="#7f8c8d")
        self.later_button.pack(side=tk.LEFT, padx=20)

        # C. 听写模式界面 (初始隐藏)
        self.dictation_frame = ctk.CTkFrame(self.interaction_frame, fg_color="transparent")
        self.dictation_entry = ctk.CTkEntry(self.dictation_frame, placeholder_text="在此输入单词拼写...", width=350, height=45, font=('Arial', 16))
        self.dictation_entry.pack(side=tk.LEFT, padx=10)
        self.dictation_entry.bind("<Return>", lambda e: self.check_dictation())
        ctk.CTkButton(self.dictation_frame, text="提交 (Enter)", command=self.check_dictation, width=120, height=45).pack(side=tk.LEFT)

        # D. 选择模式界面 (初始隐藏)
        self.choice_frame = ctk.CTkFrame(self.interaction_frame, fg_color="transparent")
        self.choice_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(self.choice_frame, text="", command=lambda idx=i: self.check_choice(idx), 
                                width=280, height=55, fg_color="transparent", border_width=2, font=('Arial', 13))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.choice_buttons.append(btn)

        # E. 复习中控制 (暂停/停止)
        self.running_controls = ctk.CTkFrame(self.bottom_controls, fg_color="transparent")
        # 初始隐藏
        
        self.pause_review_button = ctk.CTkButton(self.running_controls, text="⏸ 暂停", command=self.toggle_pause_review, width=100)
        self.pause_review_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_review_button = ctk.CTkButton(self.running_controls, text="⏹ 停止", command=self.stop_review, 
                                               width=100, fg_color="#e74c3c", hover_color="#c0392b")
        self.stop_review_button.pack(side=tk.LEFT, padx=5)
        
        # 初始加载统计视图中的控制按钮 (这些可以保持在单独的标签页或弹出层)
        self.update_review_count()

    def on_mode_change(self, selected_mode):
        """处理复习模式改变"""
        mode = self.review_mode_map.get(selected_mode, "Standard")
        
        # 隐藏所有模式按钮
        self.standard_buttons.pack_forget()
        self.dictation_frame.pack_forget()
        self.choice_frame.pack_forget()
        
        # 如果正在复习，显示当前模式的控制
        if self.review_words and self.current_review_index < len(self.review_words):
            if mode == "Standard":
                self.standard_buttons.pack(expand=True)
                if self.current_review_word:
                    self.word_label.configure(text=self.current_review_word)
            elif mode == "Dictation":
                self.dictation_frame.pack(expand=True)
                self.word_label.configure(text="***")
            elif mode == "Choice":
                self.choice_frame.pack(expand=True)
                self.word_label.configure(text=self.current_review_word)
                self.update_choices()
        
        self.status_bar.configure(text=f"已切换到 {selected_mode} 模式")

    def update_choices(self):
        """为选择模式更新选项"""
        if not self.current_review_word:
            return
            
        info = self.word_manager.get_word(self.current_review_word)
        correct_meaning = info['meaning']
        
        all_words = self.word_manager.get_all_words()
        other_meanings = [w['meaning'] for w in all_words if w['word'] != self.current_review_word]
        
        if len(other_meanings) < 3:
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

    def start_review(self, words=None):
        """开始复习"""
        self.is_quick_review = words is not None
        self.review_start_time = time.time()
        
        if words:
            self.review_words = words
        else:
            self.review_words = self.word_manager.get_words_for_review()
        
        if not self.review_words:
            if not self.is_quick_review:
                messagebox.showinfo("提示", "暂无需要复习的单词。")
            return
        
        random.shuffle(self.review_words)
        self.review_results = []
        self.current_review_index = 0
        
        # UI 切换
        self.start_controls.pack_forget()
        self.running_controls.pack(side=tk.RIGHT, padx=10)
        self.review_speak_button.pack(side=tk.LEFT, padx=10)
        
        # 根据模式显示对应的交互组件
        self.on_mode_change(self.mode_selector.get())
        
        self.show_next_review_word()
        self.status_bar.configure(text="复习已开始")

    def show_next_review_word(self):
        """显示下一个复习单词"""
        if self.current_review_index >= len(self.review_words):
            self.finish_review()
            return
        
        self.current_review_word = self.review_words[self.current_review_index]
        info = self.word_manager.get_word(self.current_review_word)
        
        # 获取当前模式
        current_mode = self.review_mode_map.get(self.mode_selector.get(), "Standard")
        
        # 重置选择题按钮颜色
        if current_mode == "Choice":
            for btn in self.choice_buttons:
                btn.configure(fg_color="transparent")
        
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
        if self.config_manager.get("auto_play_tts", True):
            self.word_manager.speak(self.current_review_word)
            
        # 补充详细信息
        phonetic_text = ""
        word_info = self.word_manager.dict_service.get_word_info(self.current_review_word)
        if word_info and word_info.get('phonetic'):
            phonetic_text = f"/{word_info['phonetic']}/"
        
        self.phonetic_label.configure(text=phonetic_text)
        self.example_label.configure(text=info.get('example', ''))
        
        # 更新进度
        total = len(self.review_words)
        current = self.current_review_index + 1
        self.review_progress.set(current / total)
        self.progress_label.configure(text=f"{current} / {total}")

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

    def finish_review(self, aborted=False):
        """结束复习"""
        self.review_words = []
        self.current_review_word = None
        
        # UI 重置
        self.word_label.configure(text="准备好了吗？")
        self.phonetic_label.configure(text="")
        self.meaning_label.configure(text="复习已结束" if not aborted else "复习已取消")
        self.example_label.configure(text="")
        self.review_speak_button.pack_forget()
        
        self.standard_buttons.pack_forget()
        self.dictation_frame.pack_forget()
        self.choice_frame.pack_forget()
        self.running_controls.pack_forget()
        self.start_controls.pack(expand=True)
        
        self.review_progress.set(0)
        self.progress_label.configure(text="0 / 0")
        
        if not aborted:
            messagebox.showinfo("复习完成", "太棒了！您已完成本次复习。")
        self.update_review_count()

    def toggle_pause_review(self):
        """暂停/继续复习"""
        self.review_paused = not self.review_paused
        if self.review_paused:
            self.pause_review_button.configure(text="▶ 继续")
            self.main_area.pack_forget() # 隐藏复习内容
        else:
            self.pause_review_button.configure(text="⏸ 暂停")
            self.main_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def stop_review(self):
        """停止复习"""
        if messagebox.askyesno("确认", "确定要停止当前的复习吗？进度将不会被保存。"):
            self.finish_review(aborted=True)

    def show_review_history(self):
        """显示复习历史 (占位)"""
        messagebox.showinfo("提示", "历史记录功能开发中...")

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
        """导出复习记录 (占位)"""
        messagebox.showinfo("提示", "导出功能开发中...")

    def restart_review(self):
        """重新开始复习"""
        if self.review_words:
            self.start_review(self.review_words)

    def quick_review(self):
        """快速复习 (10个)"""
        all_words = self.word_manager.get_all_words()
        if not all_words:
            messagebox.showinfo("提示", "词库为空，请先添加单词。")
            return
        
        count = min(10, len(all_words))
        words = [w['word'] for w in random.sample(all_words, count)]
        self.start_review(words=words)
