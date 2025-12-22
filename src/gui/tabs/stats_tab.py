#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import datetime
from .base_tab import BaseTab

class StatsTab(BaseTab):
    """学习统计标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        self._create_widgets()
        self.show_statistics()

    def _create_widgets(self):
        """创建统计信息标签页内容"""
        # 统计主容器
        main_container = ctk.CTkFrame(self)
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

    def show_statistics(self):
        """显示统计信息"""
        stats = self.word_manager.get_statistics()
        
        # 构建概览文本
        overview = f"""学习数据概览\n================\n\n"""
        overview += f"📊 词库统计:\n"
        overview += f"  • 总单词数: {stats['total_words']}\n"
        overview += f"  • 已复习单词: {stats['reviewed_words']}\n"
        overview += f"  • 待复习单词: {len(self.word_manager.get_words_for_review())}\n\n"
        
        overview += f"📈 掌握情况:\n"
        mastered_words = stats.get('mastered_words', 0)
        overview += f"  • 已掌握 (复习次数 > 5): {mastered_words}\n"
        overview += f"  • 掌握率: {(mastered_words / stats['total_words'] * 100) if stats['total_words'] > 0 else 0:.1f}%\n\n"
        
        # 获取最近学习记录
        recent_activity = self.word_manager.get_recent_activity(days=int(self.time_range_var.get()))
        overview += f"🕒 最近 {self.time_range_var.get()} 天动态:\n"
        overview += f"  • 新增单词: {recent_activity.get('new_words', 0)}\n"
        overview += f"  • 完成复习: {recent_activity.get('review_sessions', 0)} 次\n"
        
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(tk.END, overview)
        
        # 构建趋势图表（文本模拟）
        self.update_trend_chart(recent_activity)
        
        self.status_bar.configure(text="统计信息已更新")

    def update_trend_chart(self, activity_data):
        """更新趋势图表（文本模拟）"""
        chart = f"""学习趋势图 (最近 {self.time_range_var.get()} 天)\n==========================\n\n"""
        
        daily_stats = activity_data.get('daily_stats', {})
        if not daily_stats:
            chart += "\n暂无足够的活动数据生成图表。"
        else:
            # 找到最大值用于缩放
            max_val = max([max(day.get('new', 0), day.get('review', 0)) for day in daily_stats.values()] + [1])
            
            for date in sorted(daily_stats.keys(), reverse=True):
                day_data = daily_stats[date]
                new_count = day_data.get('new', 0)
                rev_count = day_data.get('review', 0)
                
                # 绘制简易条形图
                new_bar = "■" * int(new_count / max_val * 20)
                rev_bar = "▤" * int(rev_count / max_val * 20)
                
                chart += f"{date}: \n"
                chart += f"  新增: {new_bar} ({new_count})\n"
                chart += f"  复习: {rev_bar} ({rev_count})\n\n"
        
        self.chart_text.delete(1.0, tk.END)
        self.chart_text.insert(tk.END, chart)

    def export_chart(self):
        """导出统计数据"""
        try:
            stats = self.word_manager.get_statistics()
            recent_activity = self.word_manager.get_recent_activity(days=int(self.time_range_var.get()))
            
            import json
            from tkinter import filedialog
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="导出统计数据"
            )
            
            if file_path:
                export_data = {
                    "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "overall_stats": stats,
                    "recent_activity": recent_activity
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=4)
                
                messagebox.showinfo("成功", f"统计数据已导出至: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def on_time_range_change(self, value):
        """时间范围改变事件"""
        self.show_statistics()

    def on_chart_click(self, event):
        """图表点击事件"""
        pass
