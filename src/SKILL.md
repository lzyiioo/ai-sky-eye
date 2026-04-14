# AI 天眼通 - Windows 智能桌面自动化系统

**AI Sky Eye - Intelligent Windows Desktop Automation System**

---

## 📋 技能信息

| 属性 | 值 |
|------|-----|
| **名称** | AI 天眼通 / AI Sky Eye |
| **版本** | v2.5 |
| **开发者** | 小梁子 (Xiao Liangzi) |
| **平台** | Windows 10/11 |
| **语言** | Python 3.8+ |
| **授权** | 开源免费 / Open Source & Free |

---

## 🎯 核心能力

### 1. 智能 UI 自动化
- 通过名称自动查找按钮、输入框
- 无需固定坐标，分辨率无关
- 支持菜单选择、窗口切换

### 2. 智能等待系统
- 自动检测页面加载完成
- OCR 识别文字出现/消失
- 画面稳定/变化检测

### 3. 异常处理机制
- 失败自动重试
- 指数退避策略
- 操作回滚支持

### 4. 多语言 OCR
- 支持中文、英文、日文、韩文等7种语言
- PaddleOCR、EasyOCR、Tesseract 多引擎

### 5. 图像对比监控
- 屏幕变化检测
- 差异区域定位
- 持续监控模式

### 6. 远程控制 API
- HTTP 接口远程操作
- 手机浏览器即可控制
- 截图、点击、输入一站式

### 7. 定时任务调度
- 每天定时执行
- 每 X 分钟/小时执行
- 延迟执行支持

---

## 🚀 快速开始

### 安装
```bash
# 1. 安装依赖
pip install Pillow numpy uiautomation pywin32

# 2. 可选：高级功能
pip install schedule win10toast flask

# 3. 使用
from screen_controller.smart_controller_v2 import ai_click
ai_click("确定")
```

### 基础示例
```python
from screen_controller.smart_controller_v2 import ai_click, ai_type
from screen_controller.scheduler import schedule_daily

# 智能点击
ai_click("登录")

# 智能输入
ai_type("用户名", "admin")

# 定时任务
def auto_work():
    ai_click("开始")
    
schedule_daily("09:00", auto_work)
```

---

## 📦 模块清单

### 核心模块 (15个)
1. `safety_config.py` - 安全配置
2. `enhanced_screenshot.py` - 多后端截图
3. `ui_element_finder.py` - UI 元素识别
4. `smart_controller_v2.py` - 智能控制器
5. `ai_enhancements.py` - 智能等待/异常恢复/操作链
6. `enhanced_ocr.py` - OCR 增强
7. `image_compare.py` - 图像对比
8. `clipboard_manager.py` - 剪贴板管理
9. `window_manager.py` - 窗口管理
10. `action_recorder.py` - 录制回放
11. `task_queue.py` - 任务队列
12. `scheduler.py` - 定时任务
13. `notifications.py` - 系统通知
14. `remote_api.py` - 远程 API
15. `safe_controller.py` - 安全控制器

---

## 📚 文档

- 软件介绍: `中文/软件介绍.md`
- 安装说明: `中文/安装说明.md`
- 功能说明: `中文/功能说明.md`
- 开发文档: `中文/开发文档.md`
- 宣传文案: `中文/宣传文案.md`

English:
- Overview: `English/README.md`
- Install: `English/INSTALL.md`
- Features: `English/FEATURES.md`
- Marketing: `English/MARKETING.md`

---

## 🦞 关于

AI 天眼通由 小梁子 开发，旨在让 Windows 桌面自动化更简单、更智能。

AI Sky Eye was developed by Xiao Liangzi to make Windows desktop automation easier and smarter.

**版本**: v2.5  
**模块**: 15个  
**功能**: 22+  
**代码**: 6000+ 行  

---

**让 AI 成为你的桌面助手！**

**Let AI be your desktop assistant!** 🦞
