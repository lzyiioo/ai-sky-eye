# AI Sky Eye / AI 天眼通

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Modules-31-orange?style=for-the-badge" alt="Modules">
</p>

> **Intelligent Windows Desktop Automation System with AI Vision, Decision Making, and Learning Capabilities**
>
> **智能 Windows 桌面自动化系统，具备 AI 视觉、智能决策和学习能力**

**Developer**: 小梁子 (Xiao Liangzi)

---

## 🌟 What is AI Sky Eye?

AI Sky Eye is a comprehensive Windows desktop automation framework that gives AI the ability to **see**, **think**, **remember**, and **act** on your computer.

### The Four Core Capabilities

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Sky Eye Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   👁️  SEE (Vision)          🧠  THINK (Brain)              │
│   ├─ Screen Capture         ├─ Context Understanding        │
│   ├─ OCR (7 Languages)      ├─ Anomaly Detection           │
│   ├─ UI Element Finding     ├─ Smart Decision Making       │
│   └─ AI Visual Analysis     └─ Strategy Learning           │
│                                                             │
│   📝  REMEMBER (Learning)    🖐️  ACT (Control)             │
│   ├─ Action Recording       ├─ Mouse Control               │
│   ├─ Pattern Recognition    ├─ Keyboard Input              │
│   ├─ Flow Optimization      ├─ Window Management           │
│   └─ Auto Replay            └─ Browser Automation          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. AI Vision System 👁️
| Feature | Description |
|---------|-------------|
| **Multi-Engine OCR** | PaddleOCR, EasyOCR, Tesseract support |
| **7 Languages** | Chinese, English, Japanese, Korean, French, German, Spanish |
| **UI Element Detection** | Automatically find buttons, inputs, text |
| **Visual Understanding** | AI describes what it sees on screen |
| **Error Detection** | Recognize error dialogs, warnings |

### 2. Intelligent Brain 🧠
| Feature | Description |
|---------|-------------|
| **Context Awareness** | Understand current screen state (login, main, error, etc.) |
| **Anomaly Detection** | Detect crashes, timeouts, network errors |
| **Smart Decisions** | Auto-retry, skip, wait, or adapt strategy |
| **Self-Learning** | Learn from success/failure patterns |

### 3. Learning & Memory 📝
| Feature | Description |
|---------|-------------|
| **Action Recording** | Record any user operation |
| **Flow Replay** | Automatically replay recorded flows |
| **Pattern Learning** | Learn from repeated operations |
| **Flow Optimization** | Remove redundancy, add smart waits |

### 4. AI Agent 🤖
| Feature | Description |
|---------|-------------|
| **Natural Language** | "Help me copy this table to Excel" |
| **Observe-Think-Act** | Real-time screen observation → decision → execution |
| **Voice Control** | Speak commands to control your computer |
| **Auto-Confirmation** | Execute without manual confirmation |

### 5. Advanced Controls 🖐️
| Feature | Description |
|---------|-------------|
| **Precise Mouse** | Click, move, drag, scroll |
| **Smart Keyboard** | Type text, hotkeys, input method switching |
| **Window Management** | Find, move, resize, minimize/maximize |
| **Browser Automation** | Selenium integration for web automation |
| **Clipboard** | Copy, paste, monitor clipboard |

### 6. Performance & Safety ⚡
| Feature | Description |
|---------|-------------|
| **OCR Caching** | Avoid repeated engine initialization |
| **Screenshot Caching** | Reduce redundant captures |
| **Safety Controller** | Prevent dangerous operations |
| **Rate Limiting** | Control operation frequency |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/lzyiioo/ai-sky-eye.git
cd ai-sky-eye

# Install dependencies
pip install -r requirements.txt

# Optional: Install OCR engines
pip install paddleocr easyocr pytesseract

# Optional: Install voice recognition
pip install SpeechRecognition pyaudio
```

### Basic Usage

```python
from screen_controller import (
    capture_screen, click, type_text,
    SmartBrain, LearningEngine, ai_do
)

# 1. Basic Control
capture_screen()
click(100, 200)
type_text("Hello World")

# 2. AI Vision
from screen_controller import vision_describe
desc = vision_describe()
print(desc)  # "This is a login page with username and password fields..."

# 3. Smart Brain
brain = SmartBrain()
context = brain.analyze_context()
print(context.state)  # ScreenState.LOGIN

decision = brain.decide_action("Complete login")
print(decision.action)  # "fill_credentials"

# 4. Record & Replay
engine = LearningEngine()
engine.start_recording("Login Flow")
# ... perform actions ...
flow = engine.stop_recording()
engine.replay(flow)

# 5. AI Agent
ai_do("Help me copy this table to Excel")
```

---

## 📚 Documentation

### Module Overview

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `screen_controller` | Basic control | `capture_screen()`, `click()`, `type_text()` |
| `enhanced_ocr` | OCR recognition | `EnhancedOCR`, `recognize()` |
| `ui_element_finder` | Find UI elements | `find_element()`, `get_finder()` |
| `vision` | AI visual understanding | `vision_describe()`, `vision_find()` |
| `smart_brain` | Intelligent decisions | `SmartBrain`, `analyze_context()`, `decide_action()` |
| `learning` | Record & replay | `LearningEngine`, `record_flow()`, `replay()` |
| `ai_agent` | Autonomous agent | `AIAgent`, `ai_do()`, `VoiceAIAgent` |
| `performance` | Optimization | `OCREngineCache`, `ScreenshotCache` |
| `browser_controller` | Web automation | `BrowserController` |
| `scheduler` | Task scheduling | `Scheduler`, `schedule_task()` |
| `remote_api` | Remote control | HTTP API server |

### Advanced Examples

#### Example 1: Smart Login Automation

```python
from screen_controller import SmartBrain, LearningEngine

# First, manually record the login process
engine = LearningEngine()
engine.start_recording("WeChat Login")
input("Perform login manually, then press Enter...")
flow = engine.stop_recording()

# Optimize the flow
result = engine.optimize(flow)
print(f"Optimized: removed {result.removed_redundancy} redundant actions")

# Now AI can automatically login
engine.replay(flow, adaptive=True)
```

#### Example 2: AI-Powered Data Entry

```python
from screen_controller import AIAgent

agent = AIAgent(auto_confirm=False)

# AI observes screen, understands task, and executes
result = agent.run(""
    Find all customer names in the left table,
    copy them to the Excel sheet on the right,
    and save the file
"")

print(f"Task completed: {result['success']}")
print(f"Steps executed: {result['steps']}")
```

#### Example 3: Voice Control

```python
from screen_controller import VoiceAIAgent

agent = VoiceAIAgent()
print("Say 'login to WeChat' or 'take a screenshot'")
agent.run_interactive()
```

#### Example 4: Batch Automation with Error Handling

```python
from screen_controller import SmartBrain

brain = SmartBrain()

for task in tasks:
    # Check for anomalies before executing
    anomaly = brain.detect_anomaly()
    if anomaly:
        print(f"Warning: {anomaly.description}")
        decision = brain.decide_action(task)
        if decision.type == DecisionType.ABORT:
            print("Aborting due to critical error")
            break

    # Execute with smart retry
    execute_task(task)
    brain.learn_from_result(context, decision, success=True)
```

---

## 🏗️ Architecture

```
ai-sky-eye/
├── src/
│   └── screen_controller/
│       ├── __init__.py              # Main exports
│       ├── screen_controller.py     # Basic controls
│       ├── enhanced_screenshot.py   # Screenshot enhancements
│       ├── enhanced_ocr.py          # OCR engines
│       ├── ui_element_finder.py     # UI detection
│       ├── vision.py                # AI visual understanding
│       ├── smart_brain.py           # Decision making ⭐
│       ├── learning.py              # Record & replay ⭐
│       ├── ai_agent.py              # Autonomous agent ⭐
│       ├── ai_enhancements.py       # Smart waiting, recovery
│       ├── smart_controller.py      # Intelligent control
│       ├── performance.py           # Caching & optimization
│       ├── browser_controller.py    # Web automation
│       ├── scheduler.py             # Task scheduling
│       ├── remote_api.py            # HTTP API
│       ├── safe_controller.py       # Safety controls
│       └── ... (31 modules total)
├── examples/                        # Example scripts
├── docs/                           # Documentation
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

---

## 🎯 Use Cases

| Scenario | How AI Sky Eye Helps |
|----------|---------------------|
| **Daily Repetitive Tasks** | Record once, replay forever |
| **Data Entry** | AI understands forms, fills automatically |
| **Software Testing** | Automated UI testing with visual validation |
| **RPA (Robotic Process Automation)** | Enterprise workflow automation |
| **Accessibility** | Voice control for hands-free operation |
| **Remote Assistance** | Control PC from phone via HTTP API |

---

## 🔧 Configuration

### Environment Variables

```bash
# OCR Engine Selection
export AI_SKY_EYE_OCR_ENGINE=paddle  # paddle, easy, tesseract

# Safety Level
export AI_SKY_EYE_SAFETY_LEVEL=normal  # strict, normal, relaxed

# Performance
export AI_SKY_EYE_CACHE_ENABLED=true
export AI_SKY_EYE_CACHE_TTL=1.0
```

### Config File

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

## 🤝 Integration

### With Claude Code

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

### With OpenClaw

```python
# In your OpenClaw skill
from screen_controller import capture_screen, click

def skill_capture():
    """Capture screen for OpenClaw"""
    return capture_screen()
```

### HTTP API

```bash
# Start API server
python -m screen_controller.remote_api

# Use the API
curl http://localhost:8888/screenshot
curl http://localhost:8888/click -X POST -d '{"x":100,"y":200}'
```

---

## 📊 Performance

| Operation | Before Optimization | After Optimization |
|-----------|-------------------|-------------------|
| OCR Engine Init | 2-5s every time | <0.01s (cached) |
| Screenshot | 0.5-2s | <0.001s (cached) |
| UI Element Find | 1-3s | <0.1s (cached) |
| Flow Replay | Real-time | 2x faster (optimized) |

---

## 🛡️ Safety Features

- ✅ Operation confirmation (optional)
- ✅ Rate limiting
- ✅ Dangerous operation detection
- ✅ Automatic backup before changes
- ✅ Rollback capability

---

## 📝 Changelog

### v2.5 (2026-04-14)
- ✨ Added Smart Brain module (intelligent decision making)
- ✨ Added Learning module (record, replay, optimize)
- ✨ Added AI Agent module (autonomous operation)
- ✨ Added Performance module (caching & optimization)
- ✨ Added Voice control support
- 🔧 Enhanced OCR with multi-engine support
- 🔧 Improved error handling and recovery

### v2.0 (2026-04-09)
- ✨ Complete rewrite with modular architecture
- ✨ Added browser automation
- ✨ Added remote API
- ✨ Added task scheduling

### v1.0 (2026-04-01)
- 🎉 Initial release
- Basic screen control and OCR

---

## 🤖 Comparison with Other Tools

| Feature | AI Sky Eye | PyAutoGUI | Sikuli | AutoHotkey |
|---------|-----------|-----------|--------|------------|
| AI Vision | ✅ | ❌ | ✅ | ❌ |
| Smart Decisions | ✅ | ❌ | ❌ | ❌ |
| Learning/Replay | ✅ | ❌ | ❌ | ❌ |
| Voice Control | ✅ | ❌ | ❌ | ❌ |
| OCR (7 Languages) | ✅ | ❌ | ✅ | ❌ |
| Python API | ✅ | ✅ | ✅ | ❌ |
| Cross-Platform | ❌ | ✅ | ✅ | ❌ |

**AI Sky Eye** focuses on **intelligence** and **learning**, making it unique for complex automation tasks.

---

## 👨‍💻 Developer

- **Name**: 小梁子 (Xiao Liangzi)
- **GitHub**: https://github.com/lzyiioo
- **Email**: [your-email@example.com]

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- PaddleOCR for excellent OCR capabilities
- OpenCV for image processing
- PyAutoGUI for inspiration
- All contributors and users!

---

## 💬 Support

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/lzyiioo/ai-sky-eye/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/lzyiioo/ai-sky-eye/discussions)

---

**Give AI the eyes to see, the brain to think, and the hands to act!** 🤖👁️🧠
