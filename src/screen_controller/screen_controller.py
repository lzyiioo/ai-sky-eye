"""
Screen Controller - 屏幕捕获和键鼠控制
"""

import pyautogui
import mss
import time
import os
from typing import Optional, List, Tuple
from PIL import Image

# 安全设置
pyautogui.FAILSAFE = True  # 鼠标移到角落停止
pyautogui.PAUSE = 0.1  # 操作间隔


def capture_screen(output: str = 'screenshot.png', region: Optional[Tuple] = None) -> str:
    """
    截取屏幕
    
    Args:
        output: 输出文件路径
        region: 截取区域 (left, top, width, height)
        
    Returns:
        str: 输出文件路径
    """
    print(f"📸 截取屏幕...")
    
    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()
    
    screenshot.save(output)
    print(f"✅ 屏幕已保存：{output}")
    
    return output


def capture_screen_base64() -> str:
    """
    截取屏幕并返回 Base64
    
    Returns:
        str: Base64 编码的屏幕截图
    """
    print(f"📸 截取屏幕...")
    
    screenshot = pyautogui.screenshot()
    
    import io
    import base64
    
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    buffer.seek(0)
    
    base64_str = base64.b64encode(buffer.read()).decode('utf-8')
    
    print(f"✅ 屏幕已捕获（Base64，{len(base64_str)} 字符）")
    
    return base64_str


def move_mouse(x: int, y: int, duration: float = 0.5) -> dict:
    """
    移动鼠标
    
    Args:
        x: 目标 X 坐标
        y: 目标 Y 坐标
        duration: 移动时间（秒）
        
    Returns:
        dict: 执行结果
    """
    print(f"🖱️ 移动鼠标到 ({x}, {y})")
    
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return {
            "success": True,
            "action": "move_mouse",
            "position": {"x": x, "y": y}
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def click(x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> dict:
    """
    鼠标点击
    
    Args:
        x: X 坐标（可选，None=当前位置）
        y: Y 坐标（可选，None=当前位置）
        button: 按钮（left/right/middle）
        clicks: 点击次数
        
    Returns:
        dict: 执行结果
    """
    print(f"🖱️ 点击 {clicks} 次 ({button}键)")
    
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
        else:
            pyautogui.click(clicks=clicks, button=button)
        
        return {
            "success": True,
            "action": "click",
            "button": button,
            "clicks": clicks
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def type_text(text: str, interval: float = 0.1) -> dict:
    """
    键盘打字
    
    Args:
        text: 要输入的文本
        interval: 字符间隔（秒）
        
    Returns:
        dict: 执行结果
    """
    print(f"⌨️ 输入文本：{text[:50]}...")
    
    try:
        pyautogui.typewrite(text, interval=interval)
        return {
            "success": True,
            "action": "type_text",
            "length": len(text)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def press_hotkey(*keys) -> dict:
    """
    按快捷键
    
    Args:
        keys: 按键列表（如 'ctrl', 's'）
        
    Returns:
        dict: 执行结果
    """
    print(f"⌨️ 按快捷键：{'+'.join(keys)}")
    
    try:
        pyautogui.hotkey(*keys)
        return {
            "success": True,
            "action": "press_hotkey",
            "keys": list(keys)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def press_key(key: str, presses: int = 1) -> dict:
    """
    按单个键
    
    Args:
        key: 按键名称
        presses: 按几次
        
    Returns:
        dict: 执行结果
    """
    print(f"⌨️ 按键：{key} x{presses}")
    
    try:
        pyautogui.press(key, presses=presses)
        return {
            "success": True,
            "action": "press_key",
            "key": key,
            "presses": presses
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_screen_size() -> dict:
    """
    获取屏幕分辨率
    
    Returns:
        dict: 屏幕尺寸
    """
    width, height = pyautogui.size()
    return {
        "success": True,
        "width": width,
        "height": height
    }


def get_mouse_position() -> dict:
    """
    获取鼠标位置
    
    Returns:
        dict: 鼠标位置
    """
    x, y = pyautogui.position()
    return {
        "success": True,
        "x": x,
        "y": y
    }


def monitor_screen(interval: float = 5.0, output_dir: str = 'screenshots', count: int = 10) -> dict:
    """
    监控屏幕（定时截图）
    
    Args:
        interval: 截图间隔（秒）
        output_dir: 输出目录
        count: 截图次数
        
    Returns:
        dict: 监控结果
    """
    print(f"📸 开始监控屏幕，每{interval}秒截图，共{count}次")
    
    os.makedirs(output_dir, exist_ok=True)
    
    screenshots = []
    
    for i in range(count):
        filename = f"screen_{time.time()}.png"
        filepath = os.path.join(output_dir, filename)
        
        capture_screen(filepath)
        screenshots.append(filepath)
        
        if i < count - 1:
            time.sleep(interval)
    
    return {
        "success": True,
        "action": "monitor_screen",
        "count": len(screenshots),
        "screenshots": screenshots
    }


# OpenClaw 技能入口函数
def screen_capture(output: str = 'screen.png') -> dict:
    """OpenClaw 技能：截取屏幕"""
    return {"success": True, "output": capture_screen(output)}

def mouse_move(x: int, y: int) -> dict:
    """OpenClaw 技能：移动鼠标"""
    return move_mouse(x, y)

def mouse_click(x: int = None, y: int = None) -> dict:
    """OpenClaw 技能：鼠标点击"""
    return click(x, y)

def keyboard_type(text: str) -> dict:
    """OpenClaw 技能：键盘打字"""
    return type_text(text)

def keyboard_hotkey(*keys) -> dict:
    """OpenClaw 技能：按快捷键"""
    return press_hotkey(*keys)
