# AI Programming Tools Installation Guide

This guide covers integrating AI Sky Eye with popular AI coding tools.

---

## 🤖 Supported AI Programming Tools

| Tool | Developer | Features |
|------|-----------|----------|
| **Claude Code** | Anthropic | Best code understanding & generation |
| **Codex CLI** | OpenAI | GPT-4 based, strong coding ability |
| **Gemini CLI** | Google | Multimodal, large context window |
| **Qwen Code** | Alibaba Cloud | Optimized for Chinese, fast generation |

---

## 1️⃣ Claude Code Installation & Configuration

### Installation
```bash
# Install via npm
npm install -g @anthropics/claude-code

# Or via pip
pip install claude-code
```

### Configure AI Sky Eye
```bash
# Create skill config in Claude Code project
mkdir -p ~/.claude-code/skills/ai-sky-eye
cp /path/to/AI-Sky-Eye/src/SKILL.md ~/.claude-code/skills/ai-sky-eye/
```

### Usage Example
```python
# Use directly in Claude Code
@ai-sky-eye ai_click("OK")
@ai-sky-eye ai_type("Username", "admin")
@ai-sky-eye capture_screen()
```

---

## 2️⃣ Codex CLI Installation & Configuration

### Installation
```bash
# Requires OpenAI API Key
pip install openai-codex

# Configure API Key
export OPENAI_API_KEY="your-api-key"
```

### Configure AI Sky Eye
```bash
# Create Codex config directory
mkdir -p ~/.config/codex/skills
cp -r /path/to/AI-Sky-Eye/src/ ~/.config/codex/skills/ai-sky-eye
```

### Usage Example
```python
# Use in Codex CLI
# Prompt: Use AI Sky Eye to automatically click the "Login" button on screen
```

---

## 3️⃣ Gemini CLI Installation & Configuration

### Installation
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Install Gemini component
gcloud components install gemini

# Authenticate
gcloud auth login
```

### Configure AI Sky Eye
```bash
# Set environment variables
export AI_SKY_EYE_PATH="/path/to/AI-Sky-Eye/src"
export PYTHONPATH="$AI_SKY_EYE_PATH:$PYTHONPATH"
```

### Usage Example
```python
# Gemini can call via Python
import sys
sys.path.insert(0, '/path/to/AI-Sky-Eye/src')
from screen_controller.smart_controller_v2 import ai_click
```

---

## 4️⃣ Qwen Code Installation & Configuration

### Installation
```bash
# Install Qwen Code
pip install qwen-code

# Or use conda
conda install -c conda-forge qwen-code
```

### Configuration
```bash
# Configure Alibaba Cloud API Key
export DASHSCOPE_API_KEY="your-api-key"

# Initialize Qwen Code
qwen-code init
```

### Usage Example
```python
# Qwen Code has best Chinese support
# Prompt: Please help me write an auto-login script using AI Sky Eye
```

---

## 🔌 MCP (Model Context Protocol) Integration

### MCP Introduction
MCP is a standard protocol by Anthropic that allows AI to safely access local tools and resources.

### AI Sky Eye MCP Configuration

Create `mcp_config.json`:
```json
{
  "mcpServers": {
    "ai-sky-eye": {
      "command": "python",
      "args": [
        "-m",
        "screen_controller.mcp_server"
      ],
      "env": {
        "AI_SKY_EYE_MODE": "safe"
      }
    }
  }
}
```

### Available MCP Tools

| Tool Name | Function | Parameters |
|-----------|----------|------------|
| `capture_screen` | Capture screenshot | {} |
| `ai_click` | Smart click | {"target": "button_name"} |
| `ai_type` | Smart type | {"target": "input_field", "text": "content"} |
| `find_element` | Find element | {"name": "element_name"} |
| `list_windows` | List windows | {} |
| `get_clipboard` | Get clipboard | {} |

---

## 🌐 Remote Mode Configuration

### Start Remote API Server

```bash
# Method 1: Use provided startup script
cd AI-Sky-Eye
python start_remote.py

# Method 2: Start via Python code
from screen_controller.remote_api import start_remote_api
start_remote_api(host="0.0.0.0", port=8888)
```

### AI Tools Remote Connection

```python
# Configure remote address in AI tools
REMOTE_API_URL = "http://your-pc-ip:8888"

import requests

# Screenshot
response = requests.get(f"{REMOTE_API_URL}/screenshot")
screenshot_base64 = response.json()["image"]

# Smart click
requests.post(f"{REMOTE_API_URL}/ai_click", 
    json={"target": "OK"})
```

---

## 🖥️ Server Configuration (Windows Service)

### Create Windows Service

```powershell
# Use NSSM (Non-Sucking Service Manager)
# 1. Download NSSM: https://nssm.cc/download

# 2. Install service
nssm install AI-Sky-Eye

# 3. Configure paths
Path: C:\Python311\python.exe
Startup directory: C:\AI-Sky-Eye
Arguments: start_remote.py

# 4. Start service
nssm start AI-Sky-Eye
```

### Auto-start Configuration

```python
# Create startup script run_at_startup.py
import os
import sys

startup_path = os.path.expandvars(
    r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'
)

# Create shortcut
with open(os.path.join(startup_path, 'AI-Sky-Eye.bat'), 'w') as f:
    f.write(f'cd /d "{os.getcwd()}"\n')
    f.write('python start_remote.py\n')
```

---

## 📜 License / Authorization

### Open Source License

AI Sky Eye uses **MIT License**.

```
MIT License

Copyright (c) 2026 小梁子 (Xiao Liangzi)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

### Commercial Use

✅ Commercial use allowed  
✅ Modification and distribution allowed  
✅ Private use allowed  
⚠️ Must retain copyright notice  

### Disclaimer

This software is provided "as is". The author is not liable for any damages from using this software.

---

## ⚠️ Limitations / Restrictions

### 1. Platform Limitations
| Limitation | Description |
|------------|-------------|
| Windows Only | Only supports Windows 10/11 |
| No Linux/Mac | Depends on Windows API |
| Requires Admin | Some features need elevation |

### 2. Performance Limitations
| Limitation | Description | Solution |
|------------|-------------|----------|
| UI Recognition Speed | Slow first recognition | Use caching |
| OCR Accuracy | Low on complex backgrounds | Preprocess screenshot |
| Screenshot Delay | dxcam may have 1-2 frame delay | Fallback to mss |

### 3. Feature Limitations
| Limitation | Description |
|------------|-------------|
| Game Compatibility | Some games may not recognize UI |
| Security Software | May be flagged by antivirus |
| DPI Scaling | High-DPI screens need adaptation |

### 4. Security Restrictions
```
⚠️ Dangerous operations require confirmation:
- Screen edge clicks
- System menu operations
- Rapid consecutive clicks
- File deletion operations
```

### 5. AI Tool Compatibility
| Tool | Compatibility | Notes |
|------|---------------|-------|
| Claude Code | ✅ Perfect | Recommended |
| Codex CLI | ✅ Good | API config needed |
| Gemini CLI | ⚠️ Fair | Extra config needed |
| Qwen Code | ✅ Good | Chinese optimized |

### 6. Known Issues
1. **uiautomation slow init** - First import takes 2-3 seconds
2. **PaddleOCR high memory** - Uses ~500MB+
3. **Flask API single-threaded** - Needs optimization for high concurrency

---

## 💡 Best Practices

### AI Tools + AI Sky Eye Workflow

```
1. AI tool writes code
   ↓
2. Code calls AI Sky Eye
   ↓
3. Auto-execute operations
   ↓
4. Screenshot feedback to AI
   ↓
5. AI decides next step
```

### Security Recommendations

1. Use `SafetyLevel.NORMAL` for development
2. Use `SafetyLevel.STRICT` for production
3. Screenshot before important operations
4. Regularly backup config files

---

## 📞 Technical Support

- Developer: 小梁子 (Xiao Liangzi)
- GitHub: [Your Repository]
- Issue Feedback: [Issues Link]

---

**Let AI programming tools truly control your desktop!** 🦞
