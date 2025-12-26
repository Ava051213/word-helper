# 项目目录结构说明

本文档详细说明了 `word_helper` 项目在重构后的目录结构和命名规范。

## 1. 目录结构概览

```
word_helper/
├── data/                   # 数据存储目录
│   ├── words.db            # SQLite 数据库文件 (核心存储)
│   ├── config.json          # 配置文件
│   ├── dictionary_cache.json # 词典API缓存
│   └── *_words.txt         # 预置词库文件 (CET4/6/GRE)
├── docs/                   # 项目文档
│   ├── structure_guide.md   # 本文档
│   ├── development_log.md   # 开发日志
│   └── ...
├── src/                    # 源代码根目录
│   ├── api/                # 外部服务接口层
│   │   ├── dictionary_api.py        # 在线词典API客户端
│   │   ├── buffered_dictionary_api.py # 带缓存的API客户端
│   │   └── translation_api.py       # 翻译服务接口
│   ├── cli/                # 命令行界面层
│   │   └── main.py                  # CLI入口程序
│   ├── core/               # 核心层
│   │   ├── database.py              # 数据库连接与Session管理
│   │   ├── models.py                # SQLAlchemy ORM 模型定义
│   │   ├── word_manager.py          # 外观层 (Facade)，统一调用入口
│   │   ├── scheduler.py             # CLI 调度控制逻辑
│   │   ├── config_manager.py        # 配置管理
│   │   └── constants.py             # 全局常量定义
│   ├── services/           # 业务逻辑服务层 (核心重构)
│   │   ├── base_service.py          # 服务基类 (Session/Logger 管理)
│   │   ├── word_service.py          # 单词 CRUD 服务
│   │   ├── review_service.py        # SM-2 算法及复习状态服务
│   │   ├── stats_service.py         # 数据统计与聚合服务
│   │   ├── dictionary_service.py    # 词典 API 封装服务
│   │   └── tts_service.py           # 语音合成 (TTS) 服务
│   ├── gui/                # 图形用户界面层
│   │   ├── main_window.py           # GUI 主窗口
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
│       ├── common.py                # 日志、通用工具函数
│       └── decorators.py            # 性能监控等装饰器
├── tests/                  # 自动化测试目录
│   └── verify_refactored_services.py # 服务层验证脚本
├── start_cli.bat           # Windows CLI启动脚本
├── start_gui.bat           # Windows GUI启动脚本
└── requirements.txt        # 项目依赖清单
```

## 2. 模块职责说明

### src/services (服务层 - 核心逻辑)

这是重构后的核心层，采用了**服务导向架构**，实现了逻辑解耦：

- **word_service.py**: 处理单词的底层存储逻辑。
- **review_service.py**: 封装 **SM-2 算法**，负责复习计划的计算和未来复习量的预估。
- **stats_service.py**: 负责学习趋势、打卡天数等统计数据的计算。
- **tts_service.py**: 采用多线程方式实现异步语音播放，避免界面卡顿。

### src/core (核心层)

- **database.py & models.py**: 负责数据持久化，采用 SQLite + SQLAlchemy 架构。
- **word_manager.py**: 采用 **Facade (外观) 模式**，作为 GUI/CLI 与底层 Service 的统一接口，保持了向后兼容性。
- **config_manager.py**: 管理用户偏好设置。

### src/gui/tabs (表现层 - 模块化)

- **base_tab.py**: 定义了所有标签页的共有行为和依赖注入。
- **review_tab.py**: 实现了卡片交互及进度管理，支持自动/手动语音朗读。
- **stats_tab.py**: 负责数据可视化，对接 `stats_service` 提供图表数据。

### src/api (接口层)

- **buffered_dictionary_api.py**: 提供带本地缓存的词典查询。
- **translation_api.py**: 处理例句翻译。

## 3. 命名规范

- **目录**: 全小写，使用单数形式（如 `core`, `api`）。
- **Python 文件**: snake_case（如 `word_manager.py`）。
- **类名**: PascalCase（如 `WordManager`）。
- **函数/变量**: snake_case（如 `get_word_info`）。
- **常量**: SCREAMING_SNAKE_CASE（如 `MAX_RETRIES`）。

## 4. 引用规范

所有模块间的引用均采用基于项目根目录的绝对引用。

示例：

```python
from core.word_manager import WordManager
from services.word_service import WordService
from api.dictionary_api import DictionaryAPI
```
