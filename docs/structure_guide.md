# 项目目录结构说明

本文档详细说明了 `word_helper` 项目在重构后的目录结构和命名规范。

## 1. 目录结构概览

```
word_helper/
├── data/                   # 数据存储目录
│   ├── words.db            # SQLite 数据库文件 (核心存储)
│   ├── words.json          # 历史 JSON 数据 (备份)
│   ├── dictionary_cache.json # 词典API缓存
│   └── *_words.txt         # 预置词库文件 (CET4/6/GRE)
├── docs/                   # 项目文档
├── src/                    # 源代码根目录
│   ├── api/                # 外部服务接口层
│   │   ├── dictionary_api.py        # 在线词典API客户端
│   │   ├── buffered_dictionary_api.py # 带缓存的API客户端
│   │   └── translation_api.py       # 翻译服务接口
│   ├── cli/                # 命令行界面层
│   │   └── main.py                  # CLI入口程序
│   ├── core/               # 核心业务逻辑层
│   │   ├── database.py              # 数据库连接与Session管理
│   │   ├── models.py                # SQLAlchemy ORM 模型定义
│   │   ├── word_manager.py          # 单词管理逻辑 (核心控制器)
│   │   ├── scheduler.py             # 艾宾浩斯调度算法
│   │   ├── config_manager.py        # 配置管理
│   │   └── constants.py             # 全局常量定义
│   ├── gui/                # 图形用户界面层
│   │   ├── main_window.py           # GUI 主窗口 (标签页容器)
│   │   └── tabs/                    # 模块化标签页组件
│   │       ├── base_tab.py          # 标签页基类
│   │       ├── home_tab.py          # 首页
│   │       ├── add_tab.py           # 添加单词
│   │       ├── view_tab.py          # 查看词库
│   │       ├── review_tab.py        # 复习模块
│   │       ├── search_tab.py        # 搜索模块
│   │       ├── stats_tab.py         # 统计图表
│   │       └── settings_tab.py      # 系统设置
│   └── utils/              # 通用工具层
│       ├── common.py                # 日志、工具函数
│       └── migrate_json_to_db.py    # 数据迁移脚本
├── tests/                  # 单元测试目录
├── start_cli.bat           # Windows CLI启动脚本
├── start_gui.bat           # Windows GUI启动脚本
└── requirements.txt        # 项目依赖清单
```

## 2. 模块职责说明

### src/core (核心层)

- **database.py & models.py**: 负责数据持久化，采用 SQLite + SQLAlchemy 架构。
- **word_manager.py**: 负责单词的业务逻辑处理。
- **scheduler.py**: 实现艾宾浩斯遗忘曲线算法，计算下次复习时间。
- **config_manager.py**: 管理用户偏好设置（如主题、词汇级别）。

### src/gui/tabs (表现层 - 模块化)

- **base_tab.py**: 定义了所有标签页的共有行为和依赖注入。
- **review_tab.py**: 实现了复杂的复习逻辑、卡片交互及进度管理。
- **stats_tab.py**: 负责数据可视化，生成学习趋势和掌握情况报告。
- **add_tab.py**: 集成了表单校验和 API 自动查询。

### src/api (接口层)

- **buffered_dictionary_api.py**: 提供带本地缓存的词典查询，显著减少网络开销。
- **translation_api.py**: 处理例句翻译及多语言转换。

## 3. 命名规范

- **目录**: 全小写，使用单数形式（如 `core`, `api`）。
- **Python 文件**: snake_case（如 `word_manager.py`）。
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
