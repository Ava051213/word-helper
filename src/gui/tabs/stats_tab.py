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
# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

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
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 顶部控制栏
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="📊 学习数据分析", font=('Arial', 24, 'bold')).pack(side=tk.LEFT)
        
        # 按钮组
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side=tk.RIGHT)
        
        ctk.CTkButton(btn_frame, text="🔄 刷新数据", command=self.show_statistics, 
                      width=100, height=32, fg_color="#3498db", hover_color="#2980b9").pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="📤 导出报告", command=self.export_chart, 
                      width=100, height=32, fg_color="#2c3e50", hover_color="#1a252f").pack(side=tk.LEFT, padx=5)
        
        # 主内容区域
        self.stats_display_tabview = ctk.CTkTabview(main_container, corner_radius=15)
        self.stats_display_tabview.pack(fill=tk.BOTH, expand=True)
        
        overview_tab = self.stats_display_tabview.add("学习概览")
        trend_tab = self.stats_display_tabview.add("学习趋势")
        forecast_tab = self.stats_display_tabview.add("复习预警")
        heatmap_tab = self.stats_display_tabview.add("记忆热力图")
        
        # 概览页布局
        self.setup_overview_tab(overview_tab)
        
        # 趋势页布局
        self.setup_chart_tab(trend_tab, "trend")
        
        # 预警页布局
        self.setup_chart_tab(forecast_tab, "forecast")
        
        # 热力图页布局
        self.setup_chart_tab(heatmap_tab, "heatmap")

    def setup_overview_tab(self, parent):
        """设置概览页布局"""
        # 使用滚动框架
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 1. 核心指标卡片组
        metrics_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        metrics_frame.pack(fill=tk.X, pady=10)
        metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        card_style = {"corner_radius": 12, "height": 120}
        
        # 总单词
        c1 = ctk.CTkFrame(metrics_frame, **card_style)
        c1.grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkLabel(c1, text="📚 词库总量", font=('Arial', 14)).pack(pady=(20, 5))
        self.total_words_label = ctk.CTkLabel(c1, text="0", font=('Arial', 28, 'bold'))
        self.total_words_label.pack()
        
        # 掌握率
        c2 = ctk.CTkFrame(metrics_frame, **card_style)
        c2.grid(row=0, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(c2, text="🏆 掌握率", font=('Arial', 14)).pack(pady=(20, 5))
        self.mastery_rate_label = ctk.CTkLabel(c2, text="0%", font=('Arial', 28, 'bold'), text_color="#2ecc71")
        self.mastery_rate_label.pack()
        
        # 复习任务
        c3 = ctk.CTkFrame(metrics_frame, **card_style)
        c3.grid(row=0, column=2, padx=10, sticky="ew")
        ctk.CTkLabel(c3, text="⏳ 待复习", font=('Arial', 14)).pack(pady=(20, 5))
        self.pending_review_label = ctk.CTkLabel(c3, text="0", font=('Arial', 28, 'bold'), text_color="#e67e22")
        self.pending_review_label.pack()
        
        # 2. 详细数据表格样式
        details_frame = ctk.CTkFrame(scroll_frame, corner_radius=15)
        details_frame.pack(fill=tk.X, pady=20, padx=10)
        
        ctk.CTkLabel(details_frame, text="学习详情统计", font=('Arial', 16, 'bold')).pack(anchor="w", padx=20, pady=(15, 10))
        
        self.details_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        self.details_container.pack(fill=tk.X, padx=20, pady=(0, 15))

    def setup_chart_tab(self, parent, chart_type):
        """设置图表页布局"""
        # 顶部控制
        ctrl_frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        if chart_type == "trend":
            ctk.CTkLabel(ctrl_frame, text="趋势范围:").pack(side=tk.LEFT, padx=5)
            self.time_range_var = tk.StringVar(value="30")
            time_range_combo = ctk.CTkComboBox(ctrl_frame, variable=self.time_range_var, 
                                              values=["7", "14", "30", "60", "90"], width=100,
                                              command=self.on_time_range_change)
            time_range_combo.pack(side=tk.LEFT, padx=5)
            self.trend_container = ctk.CTkFrame(parent, fg_color="transparent")
            self.trend_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        elif chart_type == "forecast":
            self.forecast_container = ctk.CTkFrame(parent, fg_color="transparent")
            self.forecast_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        elif chart_type == "heatmap":
            self.heatmap_container = ctk.CTkFrame(parent, fg_color="transparent")
            self.heatmap_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_statistics(self):
        """显示统计信息"""
        stats = self.word_manager.get_statistics()
        review_count = len(self.word_manager.get_words_for_review())
        mastered_words = stats.get('mastered_words', 0)
        total_words = stats['total_words']
        mastery_rate = (mastered_words / total_words * 100) if total_words > 0 else 0
        
        # 更新核心指标
        self.total_words_label.configure(text=str(total_words))
        self.mastery_rate_label.configure(text=f"{mastery_rate:.1f}%")
        self.pending_review_label.configure(text=str(review_count))
        
        # 更新详情区域
        for widget in self.details_container.winfo_children():
            widget.destroy()
            
        detail_items = [
            ("已复习单词", f"{stats['reviewed_words']} 个"),
            ("学习中的单词", f"{total_words - mastered_words} 个"),
            ("平均记忆强度", f"{stats.get('avg_mastery', 0):.2f}"),
            ("连续打卡天数", f"{stats.get('streak_days', 0)} 天")
        ]
        
        for i, (label, val) in enumerate(detail_items):
            row = ctk.CTkFrame(self.details_container, fg_color="transparent")
            row.pack(fill=tk.X, pady=5)
            ctk.CTkLabel(row, text=label, font=('Arial', 13)).pack(side=tk.LEFT)
            ctk.CTkLabel(row, text=val, font=('Arial', 13, 'bold')).pack(side=tk.RIGHT)
            if i < len(detail_items) - 1:
                ctk.CTkFrame(self.details_container, height=1, fg_color="gray30").pack(fill=tk.X, pady=2)
        
        # 获取最近学习记录
        recent_activity = self.word_manager.get_recent_activity(days=int(self.time_range_var.get()))
        
        # 更新图表
        self.update_trend_chart_real(recent_activity)
        self.update_forecast_chart()
        self.update_heatmap()
        
        self.status_bar.configure(text="统计信息已刷新")

    def _apply_chart_theme(self, fig, ax):
        """应用统一的图表主题"""
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = '#2b2b2b' if is_dark else '#ffffff'
        text_color = '#ffffff' if is_dark else '#2c3e50'
        grid_color = '#404040' if is_dark else '#ecf0f1'
        
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # 轴标签和刻度
        ax.tick_params(colors=text_color, labelsize=9)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        ax.title.set_weight('bold')
        
        # 网格线
        ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
        
        # 移除顶部和右侧边框
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 边框颜色
        for spine in ax.spines.values():
            spine.set_edgecolor(grid_color)
            
        return text_color, grid_color

    def update_trend_chart_real(self, activity_data):
        """使用 Matplotlib 更新趋势图表"""
        for widget in self.trend_container.winfo_children():
            widget.destroy()

        daily_stats = activity_data.get('daily_stats', {})
        if not daily_stats:
            ctk.CTkLabel(self.trend_container, text="暂无足够的活动数据生成图表").pack(expand=True)
            return

        dates = sorted(daily_stats.keys())
        new_counts = [daily_stats[d].get('new', 0) for d in dates]
        review_counts = [daily_stats[d].get('review', 0) for d in dates]

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        text_color, _ = self._apply_chart_theme(fig, ax)
        
        x = range(len(dates))
        
        # 绘制渐变填充的面积图或柱状图
        ax.bar(x, new_counts, label='新增单词', color='#3498db', alpha=0.6, width=0.6)
        ax.plot(x, review_counts, label='复习次数', color='#e67e22', marker='o', 
                markersize=4, linewidth=2, markerfacecolor='white', markeredgewidth=2)
        
        # 填充复习曲线下方区域
        ax.fill_between(x, review_counts, color='#e67e22', alpha=0.1)
        
        ax.set_xticks(x)
        ax.set_xticklabels([d[5:] for d in dates], rotation=45)
        
        # 优化图例
        legend = ax.legend(frameon=False, loc='upper left', fontsize=9)
        for text in legend.get_texts():
            text.set_color(text_color)
            
        ax.set_title(f"最近 {self.time_range_var.get()} 天学习趋势", pad=20)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.trend_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_forecast_chart(self):
        """更新未来复习预警图表"""
        for widget in self.forecast_container.winfo_children():
            widget.destroy()

        future_stats = self.word_manager.get_future_review_stats(days=7)
        if not future_stats:
            ctk.CTkLabel(self.forecast_container, text="暂无预警数据").pack(expand=True)
            return

        dates = sorted(future_stats.keys())
        counts = [future_stats[d] for d in dates]

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        text_color, _ = self._apply_chart_theme(fig, ax)
        
        x = range(len(dates))
        bars = ax.bar(x, counts, color='#2ecc71', alpha=0.7, width=0.5, edgecolor='#27ae60', linewidth=1)
        
        # 在柱状图上方添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', 
                    color=text_color, fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels([d[5:] for d in dates], rotation=45)
        ax.set_title("未来 7 天复习任务量预警", pad=20)
        ax.set_ylabel("预计复习单词数")
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.forecast_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_heatmap(self):
        """更新记忆热力图 (GitHub 风格)"""
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap
        
        for widget in self.heatmap_container.winfo_children():
            widget.destroy()
            
        weeks = 25  # 增加周数
        days_to_show = weeks * 7
        activity = self.word_manager.get_recent_activity(days=days_to_show)
        daily_stats = activity.get('daily_stats', {})
        
        data = np.zeros((7, weeks))
        today = datetime.date.today()
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
                        intensity = stats.get('new', 0) + stats.get('review', 0)
                        data[row, col] = intensity
            except:
                continue

        fig, ax = plt.subplots(figsize=(10, 3.5), dpi=100)
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = '#2b2b2b' if is_dark else '#ffffff'
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # 优化颜色映射
        if is_dark:
            colors = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
        else:
            colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
        cmap = LinearSegmentedColormap.from_list('github', colors)
        
        # 绘制热力图，增加间隙
        im = ax.imshow(data, cmap=cmap, aspect='equal', interpolation='nearest')
        
        # 绘制网格线来模拟格子之间的间隙
        ax.set_xticks(np.arange(-.5, weeks, 1), minor=True)
        ax.set_yticks(np.arange(-.5, 7, 1), minor=True)
        ax.grid(which='minor', color=bg_color, linestyle='-', linewidth=2)
        ax.tick_params(which='minor', size=0)

        # 设置轴
        ax.set_xticks([])
        ax.set_yticks(range(7))
        ax.set_yticklabels(['周一', '', '周三', '', '周五', '', '周日'], 
                          fontsize=8, color='#8b949e' if is_dark else '#57606a')
        
        # 移除所有边框
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.set_title("最近 25 周学习活跃度", color='white' if is_dark else '#2c3e50', 
                    fontsize=12, pad=15, fontweight='bold')
        fig.tight_layout()

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
