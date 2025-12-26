# 个人开发项目规划书：智能单词记忆助手 (Word Helper DIY)

如果你想从零手搓一个类似的单词记忆助手，这份规划书将指导你从底层架构到表现层逐步实现。本项目采用 **Python + SQLite + CustomTkinter** 的技术栈，核心逻辑遵循 **服务导向架构 (SOA)**。

---

## 1. 项目愿景
开发一个轻量级、离线优先的单词记忆工具，通过科学的 **SM-2 间隔复习算法** 帮助用户高效背词，并提供语音朗读、数据可视化和自动化词典查询功能。

## 2. 技术栈选择
- **核心语言**: Python 3.10+
- **数据持久化**: SQLite (数据库) + SQLAlchemy (ORM 框架)
- **图形界面**: CustomTkinter (现代化的 tkinter 封装)
- **语音合成**: pyttsx3 (离线 TTS)
- **网络请求**: requests (用于对接词典 API)
- **数据分析**: 无需复杂库，原生 SQL 聚合即可

---

## 3. 核心架构设计 (三层架构)

### 第一层：数据层 (Data Layer)
- **SQLite**: 存储单词、例句、复习历史、配置信息。
- **ORM (SQLAlchemy)**: 将数据库表映射为 Python 对象，避免手写 SQL，提高开发效率。

### 第二层：服务层 (Service Layer - 业务核心)
将逻辑拆分为独立的 Service 类：
- **WordService**: 单词的增删改查。
- **ReviewService**: 核心算法层。实现 SM-2 算法，计算 `Interval` (间隔) 和 `Easiness Factor` (易用因子)。
- **StatsService**: 聚合学习数据，计算连续打卡天数和学习进度。
- **TTSService**: 封装异步语音播放逻辑。

### 第三层：表现层 (Presentation Layer)
- **CLI**: 适合快速测试和极客使用。
- **GUI**: 模块化设计。主窗口作为容器，每个功能（复习、搜索、统计）作为一个独立的 Tab (Frame)。

---

## 4. 开发阶段规划 (五步走)

### 第一阶段：基础设施 (核心中的核心)
1. **环境搭建**: 初始化虚拟环境，安装依赖。
2. **模型定义**: 使用 SQLAlchemy 定义 `Word` 和 `ReviewHistory` 模型。
3. **数据库初始化**: 编写 `database.py` 处理连接池和表创建。

### 第二阶段：业务逻辑服务化
1. **实现 WordService**: 先能把单词存进去，取出来。
2. **实现 SM-2 算法**: 这是项目的灵魂。你需要研究 SM-2 的数学公式：
   - 第一次复习：1天后
   - 第二次复习：6天后
   - 后续：$I(n) = I(n-1) * EF$
3. **单元测试**: 编写脚本验证 Service 层逻辑是否正确。

### 第三阶段：外部能力集成
1. **词典 API**: 找一个免费的 API (如 Free Dictionary API) 或爬虫，实现输入单词自动填充释义。
2. **TTS 集成**: 封装 `pyttsx3`，确保调用 `speak()` 时不会卡住主界面（使用 `threading`）。

### 第四阶段：GUI 界面开发
1. **主框架**: 使用 `customtkinter` 创建侧边栏或顶部导航。
2. **复习模块**: 重点设计“翻牌卡片”交互，先展示单词，点击后展示释义。
3. **统计模块**: 使用简单的 Canvas 或第三方库展示学习曲线。

### 第五阶段：优化与打包
1. **性能优化**: 增加 API 查询缓存，避免重复请求。
2. **打包发布**: 使用 `PyInstaller` 将项目打包为 `.exe` 或 `.app`。

---

## 5. 关键代码模式建议 (进阶)

### 1. 外观模式 (Facade)
创建一个 `WordManager` 类作为所有服务的统一入口。
```python
class WordManager:
    def __init__(self):
        self.words = WordService()
        self.review = ReviewService()
        self.tts = TTSService()
    
    def add_new_word(self, text, meaning):
        # 统一处理逻辑
        pass
```

### 2. 异步处理
在 GUI 中执行网络请求或语音播放时，务必开启新线程，防止界面“假死”：
```python
def on_speak_click(self):
    threading.Thread(target=self.tts.speak, args=(self.current_word,), daemon=True).start()
```

---

## 6. 个人手搓建议
1. **从 CLI 开始**: 不要一上来就写 GUI。先在终端里实现单词的添加和复习，逻辑通了再套壳。
2. **重视数据迁移**: 哪怕只是手搓，也要考虑以后如果修改了数据库字段，数据怎么保留。
3. **保持简单**: 第一版不要贪多，能实现“背词-记录-提醒”这一个闭环就是巨大的成功。

---
**现在你可以参考当前项目的 `src/services` 目录，那里面就是这份规划书的最佳实践！**
