# AI Sky Eye - Examples

This directory contains comprehensive examples demonstrating all features of AI Sky Eye.

## Quick Start

```bash
# Run any example
python 01_basic_control.py
python 02_ocr_vision.py
python 03_smart_brain.py
```

## Examples Overview

### 01_basic_control.py - Basic Screen Control
Learn the fundamentals of screen automation:
- Screenshot capture (full screen, base64)
- Mouse control (move, click, position)
- Keyboard input (type text, hotkeys)
- Screen monitoring

**Key Functions:**
- `capture_screen()` - Capture screenshot
- `click(x, y)` - Mouse click
- `type_text(text)` - Type text
- `press_hotkey('ctrl', 'c')` - Hotkey combinations

---

### 02_ocr_vision.py - OCR and AI Vision
Text recognition and visual understanding:
- OCR text recognition (7 languages)
- AI vision description
- UI element finding
- Error detection
- Screen state analysis

**Key Functions:**
- `vision_describe()` - AI describes screen
- `vision_find('button')` - Find UI elements
- `vision_errors()` - Detect error dialogs
- `vision_state()` - Analyze screen state

---

### 03_smart_brain.py - Intelligent Decision Making
Smart decision making and context awareness:
- Screen context analysis
- Anomaly detection
- Intelligent decisions
- Learning from results

**Key Classes:**
- `SmartBrain` - Main decision engine
- `Context` - Screen context
- `Anomaly` - Detected anomalies
- `Decision` - Decision results

---

### 04_learning_recording.py - Learning & Recording
Record, replay, and optimize workflows:
- Action recording
- Flow replay (adaptive/confirm modes)
- Flow optimization
- Pattern learning

**Key Classes:**
- `LearningEngine` - Recording engine
- `ActionRecord` - Single action record
- `FlowPattern` - Complete workflow

---

### 05_ai_agent.py - AI Agent
Autonomous AI agent capabilities:
- Simple task execution
- Complex multi-step workflows
- Voice control
- Custom agent behavior

**Key Classes:**
- `AIAgent` - Main agent class
- `VoiceAIAgent` - Voice-controlled agent
- `Action` - Agent actions
- `Observation` - Screen observations

---

### 06_performance.py - Performance Optimization
Caching and performance features:
- OCR engine caching
- Screenshot caching
- Element caching
- Performance monitoring

**Key Classes:**
- `OCREngineCache` - OCR caching
- `ScreenshotCache` - Screenshot caching
- `PerformanceMonitor` - Performance tracking

---

## Running Examples

### Prerequisites

```bash
# Install dependencies
pip install -r ../requirements.txt

# Optional: Install OCR engines
pip install paddleocr easyocr pytesseract

# Optional: Install voice recognition
pip install SpeechRecognition pyaudio
```

### Safety Notice

⚠️ **Important:** Mouse and keyboard actions in examples are commented out for safety. Uncomment them to test actual control.

```python
# Example (commented for safety):
# click(500, 500)

# Uncomment to execute:
click(500, 500)
```

### Example Output

Each example produces detailed output showing:
- What operations are performed
- Expected results
- Performance metrics
- Usage tips

---

## Advanced Usage

### Combining Examples

```python
from examples import basic_control, smart_brain

# Use basic control
screenshot = basic_control.capture_screen()

# Use smart brain
context = smart_brain.analyze_screen()
```

### Creating Your Own

Use these examples as templates:

```python
"""
My Custom Automation Script
"""
import sys
sys.path.insert(0, '../src')

from screen_controller import AIAgent, capture_screen

def my_workflow():
    agent = AIAgent()
    result = agent.run("My custom task")
    return result

if __name__ == "__main__":
    my_workflow()
```

---

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the correct directory
cd AI天眼通升级版/examples

# Or use absolute path
python C:/path/to/examples/01_basic_control.py
```

### OCR Not Available

```bash
# Install at least one OCR engine
pip install paddleocr  # Recommended
# OR
pip install easyocr
# OR
pip install pytesseract
```

### Permission Errors (Windows)

Run as Administrator for full control capabilities.

---

## Next Steps

1. **Read the Code** - Each example is well-commented
2. **Modify and Experiment** - Change parameters and see results
3. **Combine Features** - Mix different capabilities
4. **Build Your Own** - Use examples as templates

---

## Support

- 📖 Documentation: See `../docs/`
- 🐛 Issues: https://github.com/lzyiioo/ai-sky-eye/issues
- 💡 Discussions: https://github.com/lzyiioo/ai-sky-eye/discussions
