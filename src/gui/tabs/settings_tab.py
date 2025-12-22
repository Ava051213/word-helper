#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from .base_tab import BaseTab

class SettingsTab(BaseTab):
    """系统设置标签页"""
    def __init__(self, master, parent_gui, **kwargs):
        super().__init__(master, parent_gui, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        """创建设置标签页内容"""
        # 设置主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 设置内容滚动容器
        settings_scroll = ctk.CTkScrollableFrame(main_container, label_text="系统设置")
        settings_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据管理部分
        data_frame = ctk.CTkFrame(settings_scroll)
        data_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(data_frame, text="数据管理", font=('Arial', 16, 'bold')).pack(pady=10, padx=15, anchor=tk.W)
        
        btn_container = ctk.CTkFrame(data_frame, fg_color="transparent")
        btn_container.pack(fill=tk.X, padx=15, pady=10)
        
        ctk.CTkButton(btn_container, text="备份数据", command=self.backup_data, width=120).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_container, text="恢复数据", command=self.restore_data, width=120).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_container, text="清空所有数据", command=self.clear_data, width=120, fg_color="#e74c3c", hover_color="#c0392b").pack(side=tk.LEFT, padx=10)
        
        # 界面设置部分
        ui_frame = ctk.CTkFrame(settings_scroll)
        ui_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(ui_frame, text="界面设置", font=('Arial', 16, 'bold')).pack(pady=10, padx=15, anchor=tk.W)
        
        theme_container = ctk.CTkFrame(ui_frame, fg_color="transparent")
        theme_container.pack(fill=tk.X, padx=15, pady=10)
        
        ctk.CTkLabel(theme_container, text="外观模式:").pack(side=tk.LEFT, padx=10)
        saved_appearance = self.config_manager.get("appearance_mode", "System")
        self.appearance_mode_var = tk.StringVar(value=saved_appearance)
        ctk.CTkOptionMenu(theme_container, variable=self.appearance_mode_var, 
                          values=["System", "Light", "Dark"], 
                          command=self.change_appearance_mode).pack(side=tk.LEFT, padx=10)
        
        # 关于信息部分
        about_frame = ctk.CTkFrame(settings_scroll)
        about_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(about_frame, text="关于", font=('Arial', 16, 'bold')).pack(pady=10, padx=15, anchor=tk.W)
        
        about_text = """单词记忆助手 V1.0
        
基于艾宾浩斯遗忘曲线理论的智能单词记忆系统
帮助您科学高效地记忆单词

开发者: 计算机专业学生
开发时间: 2025年12月"""
        
        ctk.CTkLabel(about_frame, text=about_text, justify=tk.LEFT).pack(pady=10, padx=20)

    def change_appearance_mode(self, new_appearance_mode: str):
        """更改外观模式"""
        ctk.set_appearance_mode(new_appearance_mode)
        self.config_manager.set("appearance_mode", new_appearance_mode)
        # 更新样式以匹配新模式
        if hasattr(self.parent_gui, 'setup_styles'):
            self.parent_gui.setup_styles()

    def backup_data(self):
        """备份数据"""
        try:
            from tkinter import filedialog
            import shutil
            import os
            
            # 获取数据目录
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
            
            # 选择备份位置
            backup_file = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip")],
                title="备份数据"
            )
            
            if backup_file:
                # 创建压缩包
                shutil.make_archive(backup_file.replace('.zip', ''), 'zip', data_dir)
                messagebox.showinfo("成功", f"数据已成功备份至: {backup_file}")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败: {str(e)}")

    def restore_data(self):
        """恢复数据"""
        try:
            from tkinter import filedialog
            import shutil
            import zipfile
            import os
            
            # 选择备份文件
            backup_file = filedialog.askopenfilename(
                filetypes=[("ZIP files", "*.zip")],
                title="选择备份文件"
            )
            
            if backup_file:
                if messagebox.askyesno("确认恢复", "恢复数据将覆盖当前所有数据，确定继续吗？"):
                    # 获取数据目录
                    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
                    
                    # 解压备份
                    with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                        zip_ref.extractall(data_dir)
                    
                    # 重新加载数据
                    if hasattr(self.parent_gui, 'refresh_word_list'):
                        self.parent_gui.refresh_word_list()
                    
                    messagebox.showinfo("成功", "数据已成功恢复，请重启程序以应用所有更改")
        except Exception as e:
            messagebox.showerror("错误", f"恢复失败: {str(e)}")

    def clear_data(self):
        """清空所有数据"""
        if messagebox.askyesno("警告", "确定要清空所有单词和学习记录吗？此操作不可撤销！"):
            if messagebox.askyesno("二次确认", "您真的确定要删除所有数据吗？"):
                if self.word_manager.clear_all_data():
                    if hasattr(self.parent_gui, 'refresh_word_list'):
                        self.parent_gui.refresh_word_list()
                    messagebox.showinfo("成功", "所有数据已清空")
                else:
                    messagebox.showerror("错误", "数据清空失败")
