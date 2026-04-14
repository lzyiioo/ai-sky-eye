# AI 天眼通 / AI Sky Eye

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/平台-Windows-blue?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/许可证-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/模块-31个-orange?style=for-the-badge" alt="Modules">
</p>

> **智能 Windows 桌面自动化系统，具备 AI 视觉、智能决策和学习能力**
>
> **Intelligent Windows Desktop Automation System with AI Vision, Decision Making, and Learning Capabilities**

**开发者**: 小梁子 (Xiao Liangzi)

---

## 🌟 什么是 AI 天眼通？

AI 天眼通是一个全面的 Windows 桌面自动化框架，赋予 AI **看**、**想**、**记**、**做** 的能力。

### 四大核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 天眼通 架构图                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   👁️  看 (视觉)              🧠  想 (大脑)                  │
│   ├─ 屏幕截图                ├─ 上下文理解                  │
│   ├─ OCR识别 (7种语言)       ├─ 异常检测                    │
│   ├─ UI元素查找              ├─ 智能决策                    │
│   └─ AI视觉分析              └─ 策略学习                    │
│                                                             │
│   📝  记 (学习)               🖐️  做 (控制)                 │
│   ├─ 操作录制                ├─ 鼠标控制                    │
│   ├─ 模式识别                ├─ 键盘输入                    │
│   ├─ 流程优化                ├─ 窗口管理                    │
│   └─ 自动回放                └─ 浏览器自动化                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ 核心功能

### 1. AI 视觉系统 👁️
| 功能 | 说明 |
|------|------|
| **多引擎OCR** | 支持 PaddleOCR、EasyOCR、Tesseract |
| **7种语言** | 中文、英文、日文、韩文、法文、德文、西班牙文 |
| **UI元素检测** | 自动识别按钮、输入框、文本等元素 |
| **视觉理解** | AI 描述屏幕上的内容 |
| **错误检测** | 识别错误弹窗、警告信息 |

### 2. 智能大脑 🧠
| 功能 | 说明 |
|------|------|
| **上下文感知** | 理解当前屏幕状态（登录、主界面、错误等） |
| **异常检测** | 检测崩溃、超时、网络错误等异常 |
| **智能决策** | 自动选择重试、跳过、等待或调整策略 |
| **自我学习** | 从成功/失败中学习优化 |

### 3. 学习记忆 📝
| 功能 | 说明 |
|------|------|
| **操作录制** | 录制任意用户操作 |
| **流程回放** | 自动回放录制的流程 |
| **模式学习** | 从重复操作中学习模式 |
| **流程优化** | 去除冗余、添加智能等待 |

### 4. AI 代理 🤖
| 功能 | 说明 |
|------|------|
| **自然语言** | "帮我把这个表格复制到Excel" |
| **观察-思考-执行** | 实时观察屏幕 → 决策 → 执行 |
| **语音控制** | 说话就能控制电脑 |
| **自动确认** | 无需手动确认自动执行 |

### 5. 高级控制 🖐️
| 功能 | 说明 |
|------|------|
| **精确鼠标** | 点击、移动、拖拽、滚动 |
| **智能键盘** | 输入文字、快捷键、输入法切换 |
| **窗口管理** | 查找、移动、调整大小、最小化/最大化 |
| **浏览器自动化** | Selenium 集成网页自动化 |
| **剪贴板** | 复制、粘贴、监控剪贴板 |

### 6. 性能与安全 ⚡
| 功能 | 说明 |
|------|------|
| **OCR缓存** | 避免重复初始化引擎 |
| **截图缓存** | 减少重复截图 |
| **安全控制器** | 防止危险操作 |
| **频率限制** | 控制操作频率 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/lzyiioo/ai-sky-eye.git
cd ai-sky-eye

# 安装依赖
pip install -r requirements.txt

# 可选：安装 OCR 引擎
pip install paddleocr easyocr pytesseract

# 可选：安装语音识别
pip install SpeechRecognition pyaudio
```

### 基础用法

```python
from screen_controller import (
    capture_screen, click, type_text,
    SmartBrain, LearningEngine, ai_do
)

# 1. 基础控制
capture_screen()
click(100, 200)
type_text("Hello World")

# 2. AI 视觉
from screen_controller import vision_describe
desc = vision_describe()
print(desc)  # "这是一个登录界面，有用户名和密码输入框..."

# 3. 智能大脑
brain = SmartBrain()
context = brain.analyze_context()
print(context.state)  # ScreenState.LOGIN

decision = brain.decide_action("完成登录")
print(decision.action)  # "fill_credentials"

# 4. 录制回放
engine = LearningEngine()
engine.start_recording("登录流程")
# ... 执行操作 ...
flow = engine.stop_recording()
engine.replay(flow)

# 5. AI 代理
ai_do("帮我把这个表格的数据复制到Excel")
```

---

## 📚 文档

### 模块概览

| 模块 | 用途 | 关键类/函数 |
|------|------|------------|
| `screen_controller` | 基础控制 | `capture_screen()`, `click()`, `type_text()` |
| `enhanced_ocr` | OCR识别 | `EnhancedOCR`, `recognize()` |
| `ui_element_finder` | 查找UI元素 | `find_element()`, `get_finder()` |
| `vision` | AI视觉理解 | `vision_describe()`, `vision_find()` |
| `smart_brain` | 智能决策 | `SmartBrain`, `analyze_context()`, `decide_action()` |
| `learning` | 录制回放 | `LearningEngine`, `record_flow()`, `replay()` |
| `ai_agent` | 自主代理 | `AIAgent`, `ai_do()`, `VoiceAIAgent` |
| `performance` | 性能优化 | `OCREngineCache`, `ScreenshotCache` |
| `browser_controller` | 浏览器自动化 | `BrowserController` |
| `scheduler` | 任务调度 | `Scheduler`, `schedule_task()` |
| `remote_api` | 远程控制 | HTTP API 服务 |

### 高级示例

#### 示例 1：智能登录自动化

```python
from screen_controller import SmartBrain, LearningEngine

# 首先，手动录制登录流程
engine = LearningEngine()
engine.start_recording("微信登录")
input("手动执行登录，完成后按回车...")
flow = engine.stop_recording()

# 优化流程
result = engine.optimize(flow)
print(f"优化完成：去除了 {result.removed_redundancy} 个冗余操作")

# 现在 AI 可以自动登录
engine.replay(flow, adaptive=True)
```

#### 示例 2：AI 数据录入

```python
from screen_controller import AIAgent

agent = AIAgent(auto_confirm=False)

# AI 观察屏幕、理解任务、自动执行
result = agent.run(""
    找到左边表格中的所有客户姓名，
    复制到右边的 Excel 表格中，
    然后保存文件
"")

print(f"任务完成: {result['success']}")
print(f"执行了 {result['steps']} 步")
```

#### 示例 3：语音控制

```python
from screen_controller import VoiceAIAgent

agent = VoiceAIAgent()
print("说 '登录微信' 或 '截个图'")
agent.run_interactive()
```

#### 示例 4：带错误处理的批量自动化

```python
from screen_controller import SmartBrain

brain = SmartBrain()

for task in tasks:
    # 执行前检查异常
    anomaly = brain.detect_anomaly()
    if anomaly:
        print(f"警告: {anomaly.description}")
        decision = brain.decide_action(task)
        if decision.type == DecisionType.ABORT:
            print("因严重错误中止")
            break

    # 智能重试执行
    execute_task(task)
    brain.learn_from_result(context, decision, success=True)
```

---

## 🏗️ 架构

```
ai-sky-eye/
├── src/
│   └── screen_controller/
│       ├── __init__.py              # 主导出
│       ├── screen_controller.py     # 基础控制
│       ├── enhanced_screenshot.py   # 截图增强
│       ├── enhanced_ocr.py          # OCR引擎
│       ├── ui_element_finder.py     # UI检测
│       ├── vision.py                # AI视觉理解
│       ├── smart_brain.py           # 智能决策 ⭐
│       ├── learning.py              # 录制回放 ⭐
│       ├── ai_agent.py              # 自主代理 ⭐
│       ├── ai_enhancements.py       # 智能等待、恢复
│       ├── smart_controller.py      # 智能控制
│       ├── performance.py           # 缓存优化
│       ├── browser_controller.py    # 浏览器自动化
│       ├── scheduler.py             # 任务调度
│       ├── remote_api.py            # HTTP API
│       ├── safe_controller.py       # 安全控制
│       └── ... (共31个模块)
├── examples/                        # 示例脚本
├── docs/                           # 文档
├── requirements.txt                # 依赖
└── README.md                       # 本文件
```

---

## 🎯 使用场景

| 场景 | AI 天眼通如何帮助 |
|------|------------------|
| **日常重复任务** | 录制一次，永久回放 |
| **数据录入** | AI 理解表单，自动填写 |
| **软件测试** | 自动化 UI 测试，视觉验证 |
| **RPA 流程自动化** | 企业工作流自动化 |
| **无障碍辅助** | 语音控制，解放双手 |
| **远程协助** | 手机通过 HTTP API 控制电脑 |

---

## 🔧 配置

### 环境变量

```bash
# OCR 引擎选择
export AI_SKY_EYE_OCR_ENGINE=paddle  # paddle, easy, tesseract

# 安全级别
export AI_SKY_EYE_SAFETY_LEVEL=normal  # strict, normal, relaxed

# 性能
export AI_SKY_EYE_CACHE_ENABLED=true
export AI_SKY_EYE_CACHE_TTL=1.0
```

### 配置文件

```yaml
# ~/.ai_sky_eye/config.yaml
ocr:
  engine: paddle
  language: ch
  use_gpu: false

safety:
  level: normal
  max_ops_per_second: 10

performance:
  cache_enabled: true
  screenshot_cache_ttl: 1.0

learning:
  storage_path: ~/.ai_sky_eye/flows
  auto_optimize: true
```

---

## 🤝 集成

### 与 Claude Code 集成

```json
{
  "mcpServers": {
    "ai-sky-eye": {
      "command": "python",
      "args": ["-m", "screen_controller.mcp_server"]
    }
  }
}
```

### 与 OpenClaw 集成

```python
# 在 OpenClaw 技能中
from screen_controller import capture_screen, click

def skill_capture():
    """为 OpenClaw 截图"""
    return capture_screen()
```

### HTTP API

```bash
# 启动 API 服务
python -m screen_controller.remote_api

# 使用 API
curl http://localhost:8888/screenshot
curl http://localhost:8888/click -X POST -d '{"x":100,"y":200}'
```

---

## 📊 性能

| 操作 | 优化前 | 优化后 |
|------|--------|--------|
| OCR 引擎初始化 | 2-5秒/次 | <0.01秒 (缓存) |
| 截图 | 0.5-2秒 | <0.001秒 (缓存) |
| UI 元素查找 | 1-3秒 | <0.1秒 (缓存) |
| 流程回放 | 实时 | 2倍速 (优化后) |

---

## 🛡️ 安全特性

- ✅ 操作确认（可选）
- ✅ 频率限制
- ✅ 危险操作检测
- ✅ 变更前自动备份
- ✅ 回滚能力

---

## 📝 更新日志

### v2.5 (2026-04-14)
- ✨ 新增智能大脑模块（智能决策）
- ✨ 新增学习模块（录制、回放、优化）
- ✨ 新增 AI 代理模块（自主操作）
- ✨ 新增性能模块（缓存优化）
- ✨ 新增语音控制支持
- 🔧 增强 OCR 多引擎支持
- 🔧 改进错误处理和恢复

### v2.0 (2026-04-09)
- ✨ 模块化架构完全重写
- ✨ 新增浏览器自动化
- ✨ 新增远程 API
- ✨ 新增任务调度

### v1.0 (2026-04-01)
- 🎉 初始版本
- 基础屏幕控制和 OCR

---

## 🤖 与其他工具对比

| 功能 | AI 天眼通 | PyAutoGUI | Sikuli | AutoHotkey |
|---------|-----------|-----------|--------|------------|
| AI 视觉 | ✅ | ❌ | ✅ | ❌ |
| 智能决策 | ✅ | ❌ | ❌ | ❌ |
| 学习/回放 | ✅ | ❌ | ❌ | ❌ |
| 语音控制 | ✅ | ❌ | ❌ | ❌ |
| OCR (7种语言) | ✅ | ❌ | ✅ | ❌ |
| Python API | ✅ | ✅ | ✅ | ❌ |
| 跨平台 | ❌ | ✅ | ✅ | ❌ |

**AI 天眼通** 专注于**智能**和**学习**，在复杂自动化任务中独树一帜。

---

## 👨‍💻 开发者

- **姓名**: 小梁子 (Xiao Liangzi)
- **GitHub**: https://github.com/lzyiioo
- **邮箱**: [your-email@example.com]

---

## 📜 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- PaddleOCR 提供优秀的 OCR 能力
- OpenCV 提供图像处理
- PyAutoGUI 提供灵感
- 所有贡献者和用户！

---

## 💬 支持

- 📧 邮箱: [your-email@example.com]
- 🐛 问题: [GitHub Issues](https://github.com/lzyiioo/ai-sky-eye/issues)
- 💡 讨论: [GitHub Discussions](https://github.com/lzyiioo/ai-sky-eye/discussions)

---

**赋予 AI 看见的眼睛、思考的大脑和行动的双手！** 🤖👁️🧠
