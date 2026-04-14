# AI 编程工具安装指南

本指南介绍如何将 AI 天眼通与主流 AI 编程工具集成。

---

## 🤖 支持的 AI 编程工具

| 工具 | 开发商 | 特点 |
|------|--------|------|
| **Claude Code** | Anthropic | 最强的代码理解和生成能力 |
| **Codex CLI** | OpenAI | 基于 GPT-4，代码能力强 |
| **Gemini CLI** | Google | 多模态，上下文窗口大 |
| **Qwen Code** | 阿里云 | 中文优化，代码生成快 |

---

## 1️⃣ Claude Code 安装与配置

### 安装
```bash
# 使用 npm 安装
npm install -g @anthropics/claude-code

# 或使用 pip
pip install claude-code
```

### 配置 AI 天眼通
```bash
# 在 Claude Code 项目中创建技能配置
mkdir -p ~/.claude-code/skills/ai-sky-eye
cp /path/to/AI天眼通升级版/src/SKILL.md ~/.claude-code/skills/ai-sky-eye/
```

### 使用示例
```python
# 在 Claude Code 中直接使用
@ai-sky-eye ai_click("确定")
@ai-sky-eye ai_type("用户名", "admin")
@ai-sky-eye capture_screen()
```

---

## 2️⃣ Codex CLI 安装与配置

### 安装
```bash
# 需要 OpenAI API Key
pip install openai-codex

# 配置 API Key
export OPENAI_API_KEY="your-api-key"
```

### 配置 AI 天眼通
```bash
# 创建 Codex 配置目录
mkdir -p ~/.config/codex/skills
cp -r /path/to/AI天眼通升级版/src/ ~/.config/codex/skills/ai-sky-eye
```

### 使用示例
```python
# 在 Codex CLI 中使用
# 提示词：使用 AI 天眼通自动点击屏幕上的"登录"按钮
```

---

## 3️⃣ Gemini CLI 安装与配置

### 安装
```bash
# 安装 Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# 安装 Gemini 组件
gcloud components install gemini

# 认证
gcloud auth login
```

### 配置 AI 天眼通
```bash
# 设置环境变量
export AI_SKY_EYE_PATH="/path/to/AI天眼通升级版/src"
export PYTHONPATH="$AI_SKY_EYE_PATH:$PYTHONPATH"
```

### 使用示例
```python
# Gemini 可以通过 Python 调用
import sys
sys.path.insert(0, '/path/to/AI天眼通升级版/src')
from screen_controller.smart_controller_v2 import ai_click
```

---

## 4️⃣ Qwen Code 安装与配置

### 安装
```bash
# 安装 Qwen Code
pip install qwen-code

# 或使用 conda
conda install -c conda-forge qwen-code
```

### 配置
```bash
# 配置阿里云 API Key
export DASHSCOPE_API_KEY="your-api-key"

# 初始化 Qwen Code
qwen-code init
```

### 使用示例
```python
# Qwen Code 中文支持最好
# 提示词：请帮我使用AI天眼通写一个自动登录脚本
```

---

## 🔌 MCP (Model Context Protocol) 集成

### MCP 简介
MCP 是 Anthropic 提出的标准协议，让 AI 可以安全地访问本地工具和资源。

### AI 天眼通 MCP 配置

创建 `mcp_config.json`:
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

### MCP 可用工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `capture_screen` | 屏幕截图 | {} |
| `ai_click` | 智能点击 | {"target": "按钮名"} |
| `ai_type` | 智能输入 | {"target": "输入框", "text": "内容"} |
| `find_element` | 查找元素 | {"name": "元素名"} |
| `list_windows` | 列出窗口 | {} |
| `get_clipboard` | 获取剪贴板 | {} |

---

## 🌐 远程模式配置

### 启动远程 API 服务器

```bash
# 方法1：使用提供的启动脚本
cd AI天眼通升级版
python start_remote.py

# 方法2：Python 代码启动
from screen_controller.remote_api import start_remote_api
start_remote_api(host="0.0.0.0", port=8888)
```

### AI 编程工具远程连接

```python
# 在 AI 工具中配置远程地址
REMOTE_API_URL = "http://your-pc-ip:8888"

import requests

# 截图
response = requests.get(f"{REMOTE_API_URL}/screenshot")
screenshot_base64 = response.json()["image"]

# 智能点击
requests.post(f"{REMOTE_API_URL}/ai_click", 
    json={"target": "确定"})
```

---

## 🖥️ 配置服务器（Windows 服务）

### 创建 Windows 服务

```powershell
# 使用 NSSM (Non-Sucking Service Manager)
# 1. 下载 NSSM: https://nssm.cc/download

# 2. 安装服务
nssm install AI-Sky-Eye

# 3. 配置路径
Path: C:\Python311\python.exe
Startup directory: C:\AI天眼通升级版
Arguments: start_remote.py

# 4. 启动服务
nssm start AI-Sky-Eye
```

### 开机自启配置

```python
# 创建启动脚本 run_at_startup.py
import os
import sys

startup_path = os.path.expandvars(
    r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'
)

# 创建快捷方式
with open(os.path.join(startup_path, 'AI-Sky-Eye.bat'), 'w') as f:
    f.write(f'cd /d "{os.getcwd()}"\n')
    f.write('python start_remote.py\n')
```

---

## 📜 许可证/授权证书

### 开源许可

AI 天眼通使用 **MIT License** 开源协议。

```
MIT License

Copyright (c) 2026 小梁子 (Xiao Liangzi)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

### 商业使用

✅ 允许商业使用  
✅ 允许修改和分发  
✅ 允许私有使用  
⚠️ 需保留版权声明  

### 免责条款

本软件按"原样"提供，作者不对任何使用本软件造成的损失负责。

---

## ⚠️ 缺点/限制

### 1. 平台限制
| 限制 | 说明 |
|------|------|
| Windows 专用 | 仅支持 Windows 10/11 |
| 不支持 Linux/Mac | 依赖 Windows API |
| 需要管理员权限 | 部分功能需要提权 |

### 2. 性能限制
| 限制 | 说明 | 解决方案 |
|------|------|----------|
| UI 识别速度 | 首次识别较慢 | 使用缓存 |
| OCR 准确度 | 复杂背景识别率低 | 预处理截图 |
| 截图延迟 | dxcam 可能有1-2帧延迟 | 使用 mss 回退 |

### 3. 功能限制
| 限制 | 说明 |
|------|------|
| 游戏兼容性 | 部分游戏可能无法识别 UI |
| 安全软件 | 可能被杀毒软件误报 |
| DPI 缩放 | 高分屏需要适配 |

### 4. 安全限制
```
⚠️ 危险操作需要确认
- 屏幕边缘点击
- 系统菜单操作
- 快速连续点击
- 删除文件操作
```

### 5. AI 工具兼容性
| 工具 | 兼容性 | 备注 |
|------|--------|------|
| Claude Code | ✅ 完美 | 推荐使用 |
| Codex CLI | ✅ 良好 | 需配置 API |
| Gemini CLI | ⚠️ 一般 | 需额外配置 |
| Qwen Code | ✅ 良好 | 中文优化 |

### 6. 已知问题
1. **uiautomation 初始化慢** - 首次导入需 2-3 秒
2. **PaddleOCR 内存占用大** - 约 500MB+
3. **Flask 远程 API 单线程** - 高并发场景需优化

---

## 💡 最佳实践

### AI 编程工具 + AI 天眼通 工作流

```
1. AI 工具写代码
   ↓
2. 代码调用 AI 天眼通
   ↓
3. 自动执行操作
   ↓
4. 截图反馈给 AI
   ↓
5. AI 判断下一步
```

### 安全建议

1. 开发时使用 `SafetyLevel.NORMAL`
2. 生产环境使用 `SafetyLevel.STRICT`
3. 重要操作前截图确认
4. 定期备份配置文件

---

## 📞 技术支持

- 开发者：小梁子
- GitHub：[Your Repository]
- 问题反馈：[Issues Link]

---

**让 AI 编程工具真正控制你的桌面！** 🦞
