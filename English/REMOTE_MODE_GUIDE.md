# Remote Mode Detailed Guide

**Control Windows PC from phone/other devices**

---

## 📱 Remote Mode Overview

### What is Remote Mode?

Remote mode allows HTTP API control from any device:
- 📱 Phone/Tablet browser
- 💻 Other computers
- 🤖 Automation scripts
- ☁️ Cloud services

### Architecture

```
┌─────────────┐      HTTP       ┌─────────────┐
│   Phone/    │  ←──────────→   │   Windows   │
│   Tablet    │   (Same WiFi)   │   AI Sky    │
└─────────────┘                 └─────────────┘
                                       │
                                       │ API
                                       ↓
                               ┌─────────────┐
                               │   Windows   │
                               │   Desktop   │
                               └─────────────┘
```

---

## 🚀 Quick Start

### Step 1: Start Remote Service

```bash
# Method 1: Use startup script
cd AI-Sky-Eye
python start_remote.py

# Method 2: Python code
from screen_controller.remote_api import start_remote_api
start_remote_api(host="0.0.0.0", port=8888)
```

### Step 2: Get PC IP

```powershell
# Windows Command
ipconfig
# Find IPv4 Address, e.g., 192.168.1.100
```

### Step 3: Access from Phone

```
Phone browser:
http://192.168.1.100:8888/health

If you see {"status": "ok"}, connection successful!
```

---

## 🔌 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/screenshot` | GET | Capture screen |
| `/ai_click` | POST | Smart click by name |
| `/type` | POST | Type text |
| `/find` | POST | Find element |
| `/windows` | GET |