#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import datetime
from .base_tab import BaseTab

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

class StatsTab(BaseTab):
    """学习统计标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        self.canvas = None
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
        ctk.CTkButton(control_frame, text="导出数据", command=self.export_chart, width=100, fg_color="#2c3e50").pack(side=tk.LEFT, padx=10, pady=10)
        
        # 时间范围筛选
        filter_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        filter_frame.pack(side=tk.RIGHT, padx=10)
        
        ctk.CTkLabel(filter_frame, text="趋势范围:").pack(side=tk.LEFT, padx=5)
        self.time_range_var = tk.StringVar(value="30")
        time_range_combo = ctk.CTkComboBox(filter_frame, variable=self.time_range_var, 
                                          values=["7", "14", "30", "60", "90"], width=100,
                                          command=self.on_time_range_change)
        time_range_combo.pack(side=tk.LEFT, padx=5)
        
        # 统计内容框架
        self.stats_display_tabview = ctk.CTkTabview(main_container)
        self.stats_display_tabview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        overview_tab = self.stats_display_tabview.add("学习概览")
        trend_tab = self.stats_display_tabview.add("学习趋势")
        forecast_tab = self.stats_display_tabview.add("复习预警")
        heatmap_tab = self.stats_display_tabview.add("记忆热力图")
        
        # 概览统计内容
        self.overview_text = ctk.CTkTextbox(overview_tab, font=('Arial', 13))
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 趋势图表容器
        self.trend_container = ctk.CTkFrame(trend_tab, fg_color="transparent")
        self.trend_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 预警图表容器
        self.forecast_container = ctk.CTkFrame(forecast_tab, fg_color="transparent")
        self.forecast_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 热力图容器
        self.heatmap_container = ctk.CTkFrame(heatmap_tab, fg_color="transparent")
        self.heatmap_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        overview += f"  • 已掌握 (掌握度 >= 4): {mastered_words}\n"
        overview += f"  • 掌握率: {(mastered_words / stats['total_words'] * 100) if stats['total_words'] > 0 else 0:.1f}%\n\n"
        
        # 获取最近学习记录
        recent_activity = self.word_manager.get_recent_activity(days=int(self.time_range_var.get()))
        overview += f"🕒 最近 {self.time_range_var.get()} 天动态:\n"
        overview += f"  • 新增单词: {recent_activity.get('new_words', 0)}\n"
        overview += f"  • 完成复习: {recent_activity.get('review_sessions', 0)} 次\n"
        
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(tk.END, overview)
        
        # 更新图表
        self.update_trend_chart_real(recent_activity)
        self.update_forecast_chart()
        self.update_heatmap()
        
        self.status_bar.configure(text="统计信息已更新")

    def update_trend_chart_real(self, activity_data):
        """使用 Matplotlib 更新趋势图表"""
        # 清除旧图表
        for widget in self.trend_container.winfo_children():
            widget.destroy()

        daily_stats = activity_data.get('daily_stats', {})
        if not daily_stats:
            ctk.CTkLabel(self.trend_container, text="暂无足够的活动数据生成图表").pack(expand=True)
            return

        dates = sorted(daily_stats.keys())
        new_counts = [daily_stats[d].get('new', 0) for d in dates]
        review_counts = [daily_stats[d].get('review', 0) for d in dates]

        # 创建图表
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        if is_dark:
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_edgecolor('white')
        
        x = range(len(dates))
        ax.bar(x, new_counts, label='新增单词', color='#3b8ed0', alpha=0.7)
        ax.plot(x, review_counts, label='复习次数', color='#e74c3c', marker='o', linewidth=2)
        
        ax.set_xticks(x)
        ax.set_xticklabels([d[5:] for d in dates], rotation=45) # 只显示月-日
        ax.legend()
        ax.set_title(f"最近 {self.time_range_var.get()} 天学习趋势")
        
        fig.tight_layout()

        # 嵌入到 Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.trend_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_forecast_chart(self):
        """更新未来复习预警图表"""
        # 清除旧图表
        for widget in self.forecast_container.winfo_children():
            widget.destroy()

        future_stats = self.word_manager.get_future_review_stats(days=7)
        if not future_stats:
            ctk.CTkLabel(self.forecast_container, text="暂无预警数据").pack(expand=True)
            return

        dates = sorted(future_stats.keys())
        counts = [future_stats[d] for d in dates]

        # 创建图表
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        bg_color = '#2b2b2b' if is_dark else 'white'
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        if is_dark:
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_edgecolor('white')
        
        x = range(len(dates))
        # 使用阶梯图显示预警更具代表性，或者简单的柱状图
        bars = ax.bar(x, counts, color='#e67e22', alpha=0.8)
        
        # 在柱状图上方添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', 
                    color='white' if is_dark else 'black')

        ax.set_xticks(x)
        ax.set_xticklabels([d[5:] for d in dates], rotation=45)
        ax.set_title("未来 7 天复习任务量预警")
        ax.set_ylabel("预计复习单词数")
        
        fig.tight_layout()

        # 嵌入到 Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.forecast_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_heatmap(self):
        """更新记忆热力图 (GitHub 风格)"""
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap
        
        # 清除旧图表
        for widget in self.heatmap_container.winfo_children():
            widget.destroy()
            
        # 获取过去 140 天的数据 (20 周)
        weeks = 20
        days_to_show = weeks * 7
        activity = self.word_manager.get_recent_activity(days=days_to_show)
        daily_stats = activity.get('daily_stats', {})
        
        # 准备数据矩阵 (7行 x 20列)
        data = np.zeros((7, weeks))
        today = datetime.date.today()
        # 找到最近的一个周日作为结束
        end_date = today + datetime.timedelta(days=(6 - today.weekday()))
        start_date = end_date - datetime.timedelta(days=days_to_show - 1)
        
        for date_str, stats in daily_stats.items():
            try:
                cur_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                if start_date <= cur_date <= end_date:
                    diff = (cur_date - start_date).days
                    col = diff // 7
                    row = diff % 7
                    if col < weeks:
                        # 强度 = 新增 + 复习
                        intensity = stats.get('new', 0) + stats.get('review', 0)
                        data[row, col] = intensity
            except:
                continue

        # 创建热力图
        fig, ax = plt.subplots(figsize=(10, 3), dpi=100)
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        bg_color = '#2b2b2b' if is_dark else 'white'
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # 自定义颜色映射 (绿色系)
        colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
        if is_dark:
            colors[0] = '#161b22'
        cmap = LinearSegmentedColormap.from_list('github', colors)
        
        im = ax.imshow(data, cmap=cmap, aspect='equal')
        
        # 设置轴
        ax.set_xticks([])
        ax.set_yticks(range(7))
        ax.set_yticklabels(['Mon', '', 'Wed', '', 'Fri', '', 'Sun'], fontsize=8, color='gray' if not is_dark else '#8b949e')
        
        # 移除边框
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.set_title("最近 20 周学习活跃度", color='white' if is_dark else 'black', fontsize=10)
        fig.tight_layout()

        # 嵌入到 Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.heatmap_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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
