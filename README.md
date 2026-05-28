# Game Danmaku AI

游戏弹幕AI助手 - 在打游戏时根据游戏画面进行AI识别，生成类似B站弹幕的实时滚动效果。

## 功能特点

- **云端AI识别**: 支持多种大模型API（阿里Qwen、OpenAI、Claude、DeepSeek、小米MiMo等）
- **B站风格弹幕**: 从右向左滚动，可配置颜色、大小、速度、透明度
- **透明覆盖**: 透明窗口，不阻挡游戏操作，支持鼠标穿透
- **系统托盘**: 方便的系统托盘控制
- **随机颜色**: 支持随机弹幕颜色，增加视觉效果
- **去重机制**: 自动过滤重复弹幕，避免刷屏

## 安装

### 环境要求

- Python 3.9+
- Windows 10/11

### 安装步骤

1. 克隆或下载项目：

```bash
cd D:\Project\myproject\game-danmaku-ai
```

2. 创建虚拟环境（推荐使用 uv）：

```bash
uv venv
```

3. 激活虚拟环境：

```bash
# PowerShell
.venv\Scripts\activate

# Git Bash
source .venv/Scripts/activate
```

4. 安装依赖：

```bash
uv pip install -r requirements.txt
```

或使用 pip：

```bash
pip install -r requirements.txt
```

5. 配置本地 API Key（不要提交到 GitHub）：

```bash
copy .env.example .env
```

然后编辑 `.env`：

```env
GAME_DANMAKU_AI_API_KEY=your-api-key-here
```

## 使用方法

### 启动程序

```bash
python main.py
```

或使用 uv：

```bash
uv run python main.py
```

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `F9` | 暂停/继续 |
| `F10` | 显示/隐藏弹幕 |
| `F11` | 打开设置 |

### 系统托盘

- **右键点击**: 打开菜单
- **双击**: 打开设置
- **菜单选项**: 暂停、隐藏弹幕、清空弹幕、退出

## 配置

### 云端AI配置

在设置界面（F11）的"云端AI"标签页中配置：

1. 勾选"启用云端识别"
2. 选择API提供商
3. 输入API Key
4. 点击"验证配置"检查本地配置
5. 保存设置

API Key 会保存到本地 `.env` 文件，`config.yaml` 只保存非敏感配置。`.env` 和 `config.yaml` 默认不会上传到 GitHub。

### 支持的API提供商

| 提供商 | 默认模型 | 获取API Key |
|--------|----------|-------------|
| 阿里 Qwen | qwen-vl-max | [DashScope控制台](https://dashscope.console.aliyun.com) |
| OpenAI | gpt-4o | [OpenAI Platform](https://platform.openai.com) |
| Claude | claude-sonnet-4-20250514 | [Anthropic Console](https://console.anthropic.com) |
| DeepSeek | deepseek-vl2 | [DeepSeek Platform](https://platform.deepseek.com) |
| 小米 MiMo | mimo-v2.5-pro | [小米MiMo](https://api.xiaomimimo.com) |

### 弹幕设置

在"弹幕设置"标签页中可以调整：

- **弹幕帧率**: 30/60/120/144 FPS
- **滚动速度**: 1-20（推荐8-12）
- **透明度**: 10%-100%
- **最大弹幕数**: 10-200
- **弹幕颜色**: 自定义颜色或使用随机颜色
- **显示位置**: 顶部/居中/底部

### 配置文件

配置文件: `config.yaml`

仓库提供 `config.example.yaml` 作为示例；首次运行时如果没有 `config.yaml`，程序会自动生成默认配置。

```yaml
ai:
  cloud:
    enabled: true
    provider: 'qwen'
    api_key: ''
    base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    model: 'qwen-vl-max'
    interval: 5

danmaku:
  animation:
    fps: 144
    speed: 8
    opacity: 0.8
    max_count: 50
  style:
    size: 16
    color: '#FFFFFF'
    random_color: true
  display:
    position: 'top'
    height_ratio: 0.3

performance:
  ai_interval: 3
  use_gpu: true
  num_threads: 6
```

## 项目结构

```
game-danmaku-ai/
├── main.py                 # 程序入口
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖列表
├── README.md               # 项目说明
│
├── core/                   # 核心模块
│   ├── screen_capture.py   # 屏幕捕获
│   ├── ai_engine.py        # AI识别引擎
│   ├── danmaku_manager.py  # 弹幕管理器
│   └── game_detector.py    # 游戏检测器
│
├── ui/                     # 用户界面
│   ├── overlay_window.py   # 透明覆盖窗口
│   ├── settings_dialog.py  # 设置对话框
│   └── tray_icon.py        # 系统托盘图标
│
├── ai/                     # AI模型
│   ├── ocr_engine.py       # OCR文字识别
│   ├── object_detector.py  # 目标检测
│   ├── event_classifier.py # 事件分类
│   └── cloud_vision.py     # 云端视觉API
│
├── danmaku/                # 弹幕渲染
│   ├── renderer.py         # 弹幕渲染器
│   ├── animation.py        # 动画系统
│   └── styles.py           # 样式定义
│
└── utils/                  # 工具函数
    ├── logger.py           # 日志工具
    ├── config_manager.py   # 配置管理
    └── performance.py      # 性能监控
```

## 工作原理

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  屏幕捕获   │ ──▶ │  云端AI识别 │ ──▶ │ 弹幕生成器  │
│  (60fps)    │     │  (每5秒)    │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ 弹幕渲染器  │
                                        │ (144fps)    │
                                        └─────────────┘
```

1. **屏幕捕获**: 以60fps持续捕获游戏画面
2. **云端AI识别**: 每5秒将画面发送给大模型分析
3. **弹幕生成**: AI返回有趣的弹幕评论
4. **弹幕渲染**: 在透明窗口上以144fps渲染滚动弹幕

## 常见问题

### Q: 弹幕卡顿怎么办？

A: 尝试以下方法：
- 降低弹幕帧率（设置中选择60 FPS）
- 减少最大弹幕数
- 关闭弹幕描边效果

### Q: AI识别不准确？

A:
- 确保游戏窗口在前台
- 调整识别间隔（3-5秒）
- 使用更强大的模型（如qwen-vl-max）

### Q: 弹幕颜色无法修改？

A:
- 取消勾选"使用随机颜色"
- 然后点击颜色按钮选择颜色

### Q: 程序无法启动？

A:
- 检查Python版本（需要3.9+）
- 确认依赖已安装
- 查看终端错误信息

## 注意事项

- 部分游戏的反作弊系统可能拦截屏幕捕获
- 建议使用窗口化或无边框窗口模式运行游戏
- 云端AI识别会产生API调用费用
- 本工具仅用于娱乐和学习目的

## 许可证

MIT License

## 致谢

- [PySide6](https://wiki.qt.io/Qt_for_Python) - GUI框架
- [mss](https://github.com/BoboTiG/python-mss) - 屏幕捕获
- [OpenAI](https://openai.com) - API兼容
- [DashScope](https://dashscope.aliyun.com) - 阿里云AI服务
