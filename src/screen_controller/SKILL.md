---
name: screen-controller
version: 1.0.0
description: 屏幕捕获和键鼠控制 - 让 AI 可以"看到"和"操作"电脑
tags: ["screen", "screenshot", "keyboard", "mouse", "automation", "pyautogui"]
author: OpenClaw Team
---

# Screen Controller - 屏幕控制技能

让 AI 智能体可以：
- ✅ 截取屏幕（看到屏幕内容）
- ✅ 控制鼠标（移动、点击）
- ✅ 控制键盘（打字、快捷键）
- ✅ 实时监控屏幕

## 安装依赖

```bash
pip install pyautogui mss pillow
```

## 使用方法

```python
from skills.screen_controller import capture_screen, move_mouse, click, type_text

# 截取屏幕
capture_screen(output='screen.png')

# 移动鼠标
move_mouse(x=100, y=100)

# 点击
click()

# 打字
type_text('Hello BOSS!')

# 快捷键
press_hotkey('ctrl', 's')
```

## 安全说明

⚠️ **此技能可以完全控制你的电脑！**

- 请在安全环境下使用
- 不要运行不受信任的命令
- 建议先在虚拟机测试
