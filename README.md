# Game Danmaku AI

游戏弹幕AI助手 - 在打游戏时根据游戏画面进行AI识别，生成类似B站弹幕的实时滚动效果。

## 功能特点

- **云端AI识别**: 支持多种大模型API（阿里Qwen、OpenAI、Claude、DeepSeek、小米MiMo等）
- **B站风格弹幕**: 从右向左滚动，可配置颜色、大小、速度、透明度
- **透明覆盖**: 透明窗口，不阻挡游戏操作，支持鼠标穿透
- **系统托盘**: 方便的系统托盘控制（暂停、隐藏、清除弹幕）
- **随机颜色**: 支持随机弹幕颜色，增加视觉效果
- **智能去重**: 基于文本相似度的弹幕去重，避免重复刷屏
- **现代UI**: 深蓝色主题设置界面，支持窗口缩放
- **EXE打包**: 支持打包为独立可执行文件，无需Python环境

## 安装

### 环境要求

- Python 3.10+
- Windows 10/11

### 安装步骤

1. 克隆项目：

```bash
git clone https://github.com/zzy486346/game-danmaku-ai.git
cd game-danmaku-ai
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

### 系统托盘

- **右键点击**: 打开菜单
- **双击**: 打开设置
- **菜单选项**: 暂停、隐藏弹幕、清除弹幕、设置、退出

## 配置

### 云端AI配置

在设置界面的"云端AI"标签页中配置：

1. 勾选"启用云端识别"
2. 选择API提供商
3. 输入API Key
4. 点击"验证配置"检查API是否可用
5. 保存设置

API Key 会保存到本地 `.env` 文件，`config.yaml` 只保存非敏感配置。`.env` 和 `config.yaml` 默认不会上传到 GitHub。

### 支持的API提供商

| 提供商 | Provider ID | 默认模型 | 获取API Key |
|--------|------------|---------|-------------|
| 通义千问 | `qwen` | qwen-vl-max | [DashScope控制台](https://dashscope.console.aliyun.com) |
| DeepSeek | `deepseek` | deepseek-vl2 | [DeepSeek Platform](https://platform.deepseek.com) |
| OpenAI | `openai` | gpt-4o | [OpenAI Platform](https://platform.openai.com) |
| Claude | `claude` | claude-sonnet-4-20250514 | [Anthropic Console](https://console.anthropic.com) |
| 自定义 | `openai_compatible` | - | 任何OpenAI兼容API |

### 弹幕设置

在"弹幕设置"标签页中可以调整：

- **弹幕帧率**: 30/60/120/144 FPS
- **滚动速度**: 1-10（推荐5-8）
- **透明度**: 10%-100%
- **最大弹幕数**: 10-200
- **弹幕颜色**: 自定义颜色或使用随机颜色
- **显示位置**: 顶部/居中/底部

### 配置文件

配置文件: `config.yaml`

首次运行时程序会自动生成默认配置。

```yaml
ai:
  cloud:
    enabled: true
    provider: 'qwen'
    model: 'qwen-vl-max'
    base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    interval: 3

danmaku:
  animation:
    fps: 144
    speed: 5
    opacity: 0.8
    max_count: 50
  style:
    size: 16
    color: '#FFFFFF'
    random_color: false
  display:
    position: 'center'
    height_ratio: 0.3
```

## 项目结构

```
game-danmaku-ai/
├── main.py                  # 程序入口
├── config.yaml              # 配置文件
├── build.spec               # PyInstaller打包配置
├── create_icon.py           # 图标生成脚本
├── icon.ico                 # 应用图标
├── requirements.txt         # 依赖列表
│
├── core/                    # 核心模块
│   ├── ai_engine.py         # AI识别引擎（统一管理云端/本地）
│   ├── screen_capture.py    # 屏幕捕获（mss高性能截图）
│   ├── danmaku_manager.py   # 弹幕管理器（队列/去重/调度）
│   └── game_detector.py     # 游戏检测器
│
├── ai/                      # AI模块
│   ├── cloud_vision.py      # 云端视觉API（多提供商统一接口）
│   ├── ocr_engine.py        # PaddleOCR文字识别
│   ├── object_detector.py   # YOLOv8目标检测
│   └── event_classifier.py  # 游戏事件分类
│
├── danmaku/                 # 弹幕系统
│   ├── animation.py         # 动画引擎（delta-time/轨道管理）
│   ├── renderer.py          # QPainter渲染器（描边/阴影）
│   └── styles.py            # 弹幕样式定义
│
├── ui/                      # 界面
│   ├── overlay_window.py    # 透明覆盖窗口
│   ├── settings_dialog.py   # 设置对话框（深蓝色主题）
│   └── tray_icon.py         # 系统托盘
│
└── utils/                   # 工具
    ├── config_manager.py    # 配置管理（YAML + .env）
    ├── logger.py            # 日志配置
    └── performance.py       # 性能监控
```

## 打包为EXE

```bash
uv run pyinstaller build.spec --clean --noconfirm
```

生成的可执行文件位于 `dist/GameDanmakuAI.exe`（约115MB），可直接双击运行，无需Python环境。

## 工作原理

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  屏幕捕获   │ ──▶ │  云端AI识别 │ ──▶ │ 弹幕生成器  │
│  (60fps)    │     │  (每3秒)    │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ 弹幕渲染器  │
                                        │ (144fps)    │
                                        └─────────────┘
```

1. **屏幕捕获**: 以60fps持续捕获游戏画面
2. **云端AI识别**: 每3秒将画面发送给大模型分析
3. **弹幕生成**: AI返回2-3条有趣的弹幕评论
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
- 检查Python版本（需要3.10+）
- 确认依赖已安装
- 查看终端错误信息

### Q: 验证配置失败？

A:
- 检查API Key是否正确
- 确认API地址（Base URL）是否正确
- 检查网络连接
- 401错误表示API Key无效，404错误表示地址错误，429表示请求过于频繁

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
