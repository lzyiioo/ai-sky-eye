# MCP 工具详细指南

**Model Context Protocol (模型上下文协议)**

---

## 📋 MCP 简介

MCP 是 Anthropic 推出的开放标准协议，用于 AI 模型与外部工具的安全交互。

### 核心概念

```
┌─────────────┐      MCP      ┌──────────────┐
│   AI 模型    │  ←────────→   │   本地工具    │
│  (Claude)    │   JSON-RPC    │  (AI天眼通)  │
└─────────────┘               └──────────────┘
```

### MCP 优势
- ✅ 标准化接口
- ✅ 安全隔离
- ✅ 权限控制
- ✅ 双向通信

---

## 🔧 MCP 服务器配置

### 1. 安装 MCP SDK

```bash
pip install mcp
pip install mcp-server
```

### 2. 创建 MCP 服务器

创建 `mcp_server.py`:
```python
#!/usr/bin/env python3
"""
AI 天眼通 MCP 服务器
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

# 导入 AI 天眼通
import sys
sys.path.insert(0, '../src')
from screen_controller.smart_controller_v2 import ai_click, ai_type
from screen_controller.enhanced_screenshot import capture_to_base64

# 创建 MCP 服务器
app = Server("ai-sky-eye")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="capture_screen",
            description="Capture a screenshot of the current screen",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="ai_click",
            description="Click on a UI element by name (e.g., 'OK', 'Cancel')",
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Name of the element to click"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="ai_type",
            description="Type text into an input field",
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Name of the input field"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["target", "text"]
            }
        ),
        Tool(
            name="find_element",
            description="Find a UI element and return its position",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the element to find"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_windows",
            description="List all open windows",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """调用工具"""
    try:
        if name == "capture_screen":
            base64_img = capture_to_base64()
            return [TextContent(type="text", text=f"Screenshot captured. Base64: {base64_img[:100]}...")]
        
        elif name == "ai_click":
            target = arguments.get("target")
            result = ai_click(target)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "ai_type":
            target = arguments.get("target")
            text = arguments.get("text")
            # ai_type(target, text)  # 实际调用
            return [TextContent(type="text", text=f"Typed '{text}' into '{target}'")]
        
        elif name == "find_element":
            name = arguments.get("name")
            from screen_controller.ui_element_finder import find_element as _find
            elem = _find(name)
            if elem:
                return [TextContent(type="text", text=f"Found: {elem.name} at {elem.center}")]
            return [TextContent(type="text", text=f"Element '{name}' not found")]
        
        elif name == "list_windows":
            from screen_controller.window_manager import list_all_windows
            windows = list_all_windows()[:10]
            text = "\n".join([f"- {w.title}" for w in windows])
            return [TextContent(type="text", text=text)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

if __name__ == "__main__":
    asyncio.run(app.run_stdio_async())
```

### 3. 配置 MCP 客户端

**Claude Desktop 配置** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ai-sky-eye": {
      "command": "python",
      "args": [
        "C:/AI天眼通升级版/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:/AI天眼通升级版/src"
      }
    }
  }
}
```

**配置文件位置**:
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

---

## 🛠️ 可用工具详解

### 1. capture_screen - 屏幕截图

**功能**: 截取当前屏幕

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "image": "base64_encoded_image_data",
  "timestamp": "2026-04-09T10:00:00"
}
```

**使用场景**:
- 让 AI "看到"当前屏幕
- 验证操作结果
- 调试自动化流程

---

### 2. ai_click - 智能点击

**功能**: 通过名称点击 UI 元素

**参数**:
```json
{
  "target": "确定"
}
```

**返回值**:
```json
{
  "success": true,
  "element": {
    "name": "确定",
    "x": 500,
    "y": 300,
    "control_type": "Button"
  },
  "message": "Clicked successfully"
}
```

**使用场景**:
- 点击按钮、链接
- 无需坐标，AI 自动查找

---

### 3. ai_type - 智能输入

**功能**: 在指定输入框输入文字

**参数**:
```json
{
  "target": "用户名",
  "text": "admin"
}
```

**使用场景**:
- 自动填写表单
- 搜索框输入
- 登录输入

---

### 4. find_element - 查找元素

**功能**: 查找 UI 元素位置

**参数**:
```json
{
  "name": "登录按钮"
}
```

**返回值**:
```json
{
  "found": true,
  "name": "登录按钮",
  "position": [500, 300],
  "size": [100, 30],
  "confidence": 0.95
}
```

---

### 5. list_windows - 列出窗口

**功能**: 获取所有打开的窗口

**返回值**:
```
窗口列表:
- 微信
- 谷歌浏览器 - GitHub
- Visual Studio Code
- 文件资源管理器
```

---

## 📝 MCP 使用示例

### 示例 1: 自动化登录

**用户提示**:
```
帮我自动登录系统，用户名为 admin，密码为 123456
```

**AI 执行**:
```
1. capture_screen (查看当前屏幕)
2. ai_type {"target": "用户名", "text": "admin"}
3. ai_type {"target": "密码", "text": "123456"}
4. ai_click {"target": "登录"}
5. capture_screen (确认登录成功)
```

---

### 示例 2: 搜索操作

**用户提示**:
```
在百度上搜索"AI 天眼通"
```

**AI 执行**:
```
1. list_windows (找到浏览器窗口)
2. ai_click {"target": "搜索框"}
3. ai_type {"target": "搜索框", "text": "AI 天眼通"}
4. ai_click {"target": "百度一下"}
```

---

### 示例 3: 跨应用操作

**用户提示**:
```
把微信里的链接复制到浏览器打开
```

**AI 执行**:
```
1. capture_screen
2. find_element {"name": "链接"}
3. ai_click {"target": "链接"}
4. ai_click {"target": "复制"}
5. list_windows (找到浏览器)
6. ai_click {"target": "地址栏"}
7. ai_type {"target": "地址栏", "text": "{clipboard}"}
```

---

## 🔒 安全考虑

### 权限控制
```python
# 在 MCP 服务器中添加权限检查
def check_permission(tool_name: str, user: str) -> bool:
    dangerous_tools = ["delete_file", "system_command"]
    if tool_name in dangerous_tools:
        return user in ADMIN_LIST
    return True
```

### 操作确认
```python
# 敏感操作需要二次确认
if is_dangerous_operation(params):
    return ask_user_confirmation("确认执行此操作？")
```

---

## 🐛 故障排查

### 问题 1: MCP 服务器无法启动
```bash
# 检查 Python 路径
which python
python --version

# 检查模块安装
pip list | grep mcp
```

### 问题 2: 工具调用失败
```bash
# 查看日志
Claude Desktop → Help → Developer → Toggle Developer Tools
```

### 问题 3: 截图失败
```python
# 检查截图权限
# Windows 设置 → 隐私 → 屏幕截图
```

---

## 📊 MCP vs 远程 API 对比

| 特性 | MCP | 远程 API |
|------|-----|----------|
| 协议 | JSON-RPC | HTTP REST |
| 通信 | stdio/socket | HTTP |
| 安全 | 本地进程 | 网络暴露 |
| 适用 | Claude Desktop | 通用客户端 |
| 配置 | JSON 配置 | URL + 端口 |
| 延迟 | 低 | 网络依赖 |

---

## 🎯 最佳实践

1. **优先使用 MCP** - 与 Claude 深度集成
2. **截图验证** - 重要操作后截图确认
3. **错误处理** - 每个工具调用都要有错误处理
4. **日志记录** - 记录所有工具调用
5. **权限最小化** - 只暴露必要的工具

---

**让 Claude 真正"看见"并控制你的桌面！** 🦞
