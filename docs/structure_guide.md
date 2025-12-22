# 项目目录结构说明

本文档详细说明了 `word_helper` 项目在重构后的目录结构和命名规范。

## 1. 目录结构概览

```
word_helper/
├── data/                   # 数据存储目录
│   ├── words.json          # 用户单词数据
│   ├── dictionary_cache.json # 词典API缓存
│   └── backups/            # 自动备份目录
├── docs/                   # 项目文档
├── src/                    # 源代码根目录
│   ├── api/                # 外部服务接口层
│   │   ├── dictionary_api.py        # 在线词典API客户端
│   │   ├── buffered_dictionary_api.py # 带缓存的API客户端
│   │   └── translation_api.py       # 翻译服务接口
│   ├── cli/                # 命令行界面层
│   │   └── main.py                  # CLI入口程序
│   ├── core/               # 核心业务逻辑层
│   │   ├── word_manager.py          # 单词管理逻辑
│   │   ├── scheduler.py             # 艾宾浩斯调度算法
│   │   └── data_manager.py          # 数据持久化与导入导出
│   ├── gui/                # 图形用户界面层
│   │   └── main_window.py           # GUI主窗口及逻辑
│   └── utils/              # 通用工具层
│       └── common.py                # 日志、配置等通用工具
├── tests/                  # 单元测试目录
│   └── test_all_enhanced.py # 综合测试套件
├── start_cli.bat           # Windows CLI启动脚本
├── start_gui.bat           # Windows GUI启动脚本
├── start_cli.sh            # Linux/macOS CLI启动脚本
└── start_gui.sh            # Linux/macOS GUI启动脚本
```

## 2. 模块职责说明

### src/core (核心层)
- **word_manager.py**: 负责单词的增删改查业务逻辑，是系统的核心控制器。
- **scheduler.py**: 实现艾宾浩斯遗忘曲线算法，计算复习间隔。
- **data_manager.py**: 处理数据的存储、备份、CSV导入导出。

### src/api (接口层)
- **dictionary_api.py**: 封装对 Free Dictionary API 的 HTTP 请求。
- **buffered_dictionary_api.py**: 在 API 之上增加内存和文件缓存，减少网络请求。
- **translation_api.py**: 封装翻译服务。

### src/gui (表现层 - GUI)
- **main_window.py**: 基于 Tkinter 的图形界面实现，包含所有窗口组件和交互逻辑。

### src/cli (表现层 - CLI)
- **main.py**: 基于命令行的交互界面，提供菜单和文本交互。

### src/utils (工具层)
- **common.py**: 包含日志初始化、通用辅助函数等。

## 3. 命名规范

- **目录**: 全小写，使用单数形式（如 `core`, `api`）。
- **Python文件**: snake_case（如 `word_manager.py`）。
- **类名**: PascalCase（如 `WordManager`）。
- **函数/变量**: snake_case（如 `get_word_info`）。
- **常量**: SCREAMING_SNAKE_CASE（如 `MAX_RETRIES`）。

## 4. 引用规范

所有模块间的引用均采用相对引用或基于 `src` 的绝对引用，确保在不同环境下都能正确解析路径。

示例：
```python
from core.word_manager import WordManager
from api.dictionary_api import DictionaryAPI
from utils.common import init_logging
```
