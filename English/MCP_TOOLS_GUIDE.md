# MCP Tools Detailed Guide

**Model Context Protocol**

---

## 📋 MCP Introduction

MCP is an open standard protocol by Anthropic for secure interaction between AI models and external tools.

### Core Concepts

```
┌─────────────┐      MCP      ┌──────────────┐
│   AI Model   │  ←────────→   │  Local Tool  │
│  (Claude)    │   JSON-RPC    │ (AI Sky Eye) │
└─────────────┘               └──────────────┘
```

### MCP Advantages
- ✅ Standardized interface
- ✅ Security isolation
- ✅ Permission control
- ✅ Bidirectional communication

---

## 🔧 MCP Server Configuration

### 1. Install MCP SDK

```bash
pip install mcp
pip install mcp-server
```

### 2. Create MCP Server

Create `mcp_server.py`:
```python
#!/usr/bin/env python3
"""
AI Sky Eye MCP Server
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

# Import AI Sky Eye
import sys
sys.path.insert(0, '../src')
from screen_controller.smart_controller_v2 import ai_click, ai_type
from screen_controller.enhanced_screenshot import capture_to_base64

# Create MCP Server
app = Server("ai-sky-eye")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="capture_screen",
            description="Capture a screenshot of the current screen",
            input_schema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="ai_click",
            description="Click on a UI element by name (e.g., 'OK', 'Cancel')",
            input_schema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Name of the element to click"}
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
                    "target": {"type": "string", "description": "Name of the input field"},
                    "text": {"type": "string", "description": "Text to type"}
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
                    "name": {"type": "string", "description": "Name of the element to find"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_windows",
            description="List all open windows",
            input_schema={"type": "object", "properties": {}, "required": []}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Call tool"""
    try:
        if name == "capture_screen":
            base64_img = capture_to_base64()
            return [TextContent(type="text", text=f"Screenshot: {base64_img[:100]}...")]
        
        elif name == "ai_click":
            target = arguments.get("target")
            result = ai_click(target)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "ai_type":
            target = arguments.get("target")
            text = arguments.get("text")
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

### 3. Configure MCP Client

**Claude Desktop Config** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ai-sky-eye": {
      "command": "python",
      "args": ["C:/AI-Sky-Eye/mcp_server.py"],
      "env": {"PYTHONPATH": "C:/AI-Sky-Eye/src"}
    }
  }
}
```

---

## 🛠️ Available Tools

### 1. capture_screen
Capture current screen screenshot.

### 2. ai_click
Click UI element by name.

### 3. ai_type
Type text into input field.

### 4. find_element
Find UI element position.

### 5. list_windows
List all open windows.

---

## 📝 Usage Examples

### Example 1: Auto Login
```
User: Help me auto-login with username "admin", password "123456"

AI Actions:
1. capture_screen (check current screen)
2. ai_click {"target": "Username"}
3. ai_type {"target": "Username", "text": "admin"}
4. ai_click {"target": "Password"}
5. ai_type {"target": "Password", "text": "123456"}
6. ai_click {"target": "Login"}
7. capture_screen (verify login)
```

---

## 🔒 Security

- Local process communication
- Permission-based access
- Operation logging
- Sensitive operation confirmation

---

**Let Claude truly "see" and control your desktop!** 🦞
