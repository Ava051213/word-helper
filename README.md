# 单词记忆助手 (Word Reminder)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)](#)

基于艾宾浩斯遗忘曲线理论的智能单词记忆系统，帮助您科学高效地记忆单词。

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [安装要求](#安装要求)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
- [项目结构](#项目结构)
- [开发文档](#开发文档)
- [测试](#测试)
- [贡献](#贡献)
- [许可证](#许可证)

## 📖 项目简介

单词记忆助手是一款基于认知心理学中艾宾浩斯遗忘曲线理论开发的学习工具。该系统通过科学的时间间隔安排单词复习，帮助用户更有效地将单词从短期记忆转移到长期记忆。

传统的单词记忆方法往往效率低下，容易遗忘。本系统采用间隔重复算法，根据用户的记忆情况动态调整复习计划，确保在即将遗忘的时候进行复习，从而最大化记忆效果。

## ✨ 功能特性

### 核心功能
- **智能复习调度**: 基于艾宾浩斯遗忘曲线自动安排复习时间
- **双界面支持**: 提供命令行和图形界面两种操作方式
- **数据持久化**: 自动保存学习进度，支持数据备份与恢复
- **统计分析**: 详细的统计数据帮助了解学习进度

### 界面功能
#### 命令行版本
- 添加、查看、搜索、删除单词
- 开始复习模式
- 查看学习统计

#### 图形界面版本
- **首页**: 欢迎信息和快捷操作
- **添加单词**: 直观的表单界面添加新单词
- **查看单词**: 表格形式展示所有单词，支持搜索和筛选
- **复习单词**: 卡片式复习界面，记录复习结果
- **搜索单词**: 多维度搜索功能
- **学习统计**: 图表化的学习进度展示
- **设置**: 数据管理和系统设置

### 数据管理
- **CSV导入/导出**: 支持与其他学习工具数据交换
- **自动备份**: 定期自动备份学习数据
- **恢复机制**: 支持从备份恢复数据

## 🛠 安装要求

### 系统要求
- Windows 7/8/10/11, macOS 10.12+, 或 Linux
- Python 3.6 或更高版本

### Python依赖
```bash
# 标准库依赖（无需额外安装）
tkinter  # GUI界面 (通常随Python一起安装)
json     # 数据存储
datetime # 时间处理
csv      # CSV文件操作
```

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

#### Windows系统
```bash
# 启动图形界面
start_gui.bat

# 启动命令行界面
start_cli.bat
```

#### macOS/Linux系统
```bash
# 启动图形界面
./start_gui.sh

# 启动命令行界面
./start_cli.sh
```

### 方法二：直接运行Python脚本

```bash
# 启动图形界面
python src/gui_main_improved.py

# 启动命令行界面
python src/main.py
```

## 🎮 使用方法

### 添加单词
1. 在"添加单词"页面填写单词信息
2. 点击"添加单词"按钮保存
3. 新单词会自动安排首次复习时间

### 复习单词
1. 进入"复习单词"页面
2. 点击"开始复习"按钮
3. 根据是否认识单词点击相应按钮
4. 系统会根据回答调整下次复习时间

### 查看统计
1. 进入"学习统计"页面
2. 查看总体学习进度和趋势
3. 根据建议调整学习策略

## 📁 项目结构

```
word_helper/
├── src/                    # 源代码目录
│   ├── main.py            # 命令行主程序
│   ├── gui_main.py        # 图形界面主程序
│   ├── gui_main_improved.py # 改进版图形界面
│   ├── word_manager.py    # 单词管理模块
│   ├── scheduler.py       # 调度器模块
│   ├── utils.py           # 工具函数模块
│   └── data_manager.py    # 数据管理模块
├── data/                  # 数据目录
│   ├── words.json         # 单词数据文件
│   └── backups/           # 数据备份目录
├── docs/                  # 文档目录
│   ├── user_manual.md     # 用户手册
│   └── development_log.md # 开发日志
├── tests/                 # 测试目录
│   ├── test_all.py        # 基础测试套件
│   └── test_all_enhanced.py # 增强测试套件
├── start_gui.bat          # Windows图形界面启动脚本
├── start_cli.bat          # Windows命令行启动脚本
├── start_gui.sh           # macOS/Linux图形界面启动脚本
├── start_cli.sh           # macOS/Linux命令行启动脚本
├── requirements.txt       # 依赖文件
└── README.md             # 项目说明文件
```

## 📚 开发文档

### 核心算法

#### 艾宾浩斯遗忘曲线
系统基于德国心理学家赫尔曼·艾宾浩斯的研究成果，采用以下复习间隔：
- 第1次复习：学习后20分钟
- 第2次复习：学习后1小时
- 第3次复习：学习后8-12小时
- 第4次复习：学习后1天
- 第5次复习：学习后2天
- 第6次复习：学习后4天
- 第7次复习：学习后7天
- 第8次复习：学习后15天
- 第9次复习：学习后30天

#### 间隔重复算法
本系统采用简化的间隔重复算法：
- 用户认识单词：间隔时间乘以3
- 用户不认识单词：间隔时间重置为1天

### 模块说明

#### WordManager (单词管理器)
负责单词的增删改查和数据持久化。

#### Scheduler (调度器)
负责根据艾宾浩斯遗忘曲线安排单词复习时间。

#### Utils (工具函数)
提供通用的辅助函数。

#### DataManager (数据管理器)
提供高级数据操作功能，如导入导出、备份恢复等。

## 🧪 测试

### 运行测试

```bash
# 运行基础测试
python tests/test_all.py

# 运行增强测试
python tests/test_all_enhanced.py
```

### 测试覆盖率
- [x] WordManager 功能测试
- [x] Scheduler 调度算法测试
- [x] Utils 工具函数测试
- [x] DataManager 数据管理测试
- [x] GUI 界面基本功能测试

## 🤝 贡献

欢迎任何形式的贡献！

### 开发流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范
- 遵循 PEP 8 Python 编码规范
- 添加相应的单元测试
- 更新相关文档
- 保持代码简洁清晰

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢德国心理学家赫尔曼·艾宾浩斯的遗忘曲线理论
- 感谢所有为开源社区做出贡献的开发者
- 感谢使用本系统的每一位学习者

---

<p align="center">
  <strong>让学习变得更简单，让记忆变得更轻松！</strong>
</p>