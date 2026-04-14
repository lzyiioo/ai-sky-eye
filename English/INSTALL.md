# Installation Guide

## 📋 System Requirements

- **OS**: Windows 10 / Windows 11
- **Python**: 3.8 or higher
- **Memory**: 4GB+ recommended
- **Permissions**: Administrator (required for some features)

---

## 🚀 Quick Installation

### Step 1: Install Python

1. Visit https://www.python.org/downloads/
2. Download Python 3.8+ version
3. **Important**: Check "Add Python to PATH" during installation

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create project folder
mkdir AI-Sky-Eye
cd AI-Sky-Eye

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Base dependencies (required)
pip install Pillow numpy

# UI Automation
pip install uiautomation

# Screenshot backends (choose one or more)
pip install dxcam          # Recommended: GPU acceleration
pip install mss            # Alternative: Cross-platform

# OCR recognition (choose one or more)
pip install paddleocr      # Recommended: Chinese recognition
pip install easyocr        # Alternative: Multi-language

# Windows system features
pip install pywin32

# Advanced features
pip install schedule       # Scheduled tasks
pip install win10toast     # System notifications
pip install flask          # Remote API
```

### Step 4: Verify Installation

```bash
python -c "from screen_controller.smart_controller_v2 import ai_click; print('✅ Installation successful!')"
```

---

## 📁 Project Structure

```
AI-Sky-Eye/
├── src/
│   └── screen_controller/     # Core modules
│       ├── safety_config.py
│       ├── enhanced_screenshot.py
│       ├── ui_element_finder.py
│       ├── smart_controller_v2.py
│       ├── ai_enhancements.py
│       ├── enhanced_ocr.py
│       ├── image_compare.py
│       ├── clipboard_manager.py
│       ├── window_manager.py
│       ├── action_recorder.py
│       ├── task_queue.py
│       ├── scheduler.py
│       ├── notifications.py
│       └── remote_api.py
├── examples/                   # Example code
└── docs/                       # Documentation
```

---

## 🔧 FAQ

### Q: uiautomation installation fails?
```bash
# Run CMD as administrator, then:
pip install uiautomation --user
```

### Q: dxcam installation fails?
```bash
# dxcam requires specific dependencies
pip install comtypes
pip install dxcam
```

### Q: PaddleOCR installation is slow?
```bash
# Use domestic mirror (for China users)
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: Missing win32api error?
```bash
pip install pywin32
# Then execute
python Scripts\pywin32_postinstall.py -install
```

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Base dependencies (Pillow, numpy) installed
- [ ] UI automation (uiautomation) installed
- [ ] At least one screenshot backend installed
- [ ] pywin32 installed

---

**Installation complete! Start your automation journey!** 🎉
