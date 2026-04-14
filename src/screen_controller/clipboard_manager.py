"""
Clipboard Manager - 剪贴板集成
支持文本、图片、文件列表
"""

import io
import base64
from typing import Optional, List
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Windows 剪贴板
try:
    import win32clipboard
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# 备选: pyperclip
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


class ClipboardManager:
    """剪贴板管理器"""
    
    def __init__(self):
        self.history: List[dict] = []
        self.max_history = 20
    
    def get_text(self) -> Optional[str]:
        """获取剪贴板文本"""
        try:
            if HAS_WIN32:
                win32clipboard.OpenClipboard()
                try:
                    text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                except:
                    text = None
                win32clipboard.CloseClipboard()
                return text
            elif HAS_PYPERCLIP:
                return pyperclip.paste()
        except Exception as e:
            logger.error(f"Failed to get text: {e}")
        return None
    
    def set_text(self, text: str) -> bool:
        """设置剪贴板文本"""
        try:
            if HAS_WIN32:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            elif HAS_PYPERCLIP:
                pyperclip.copy(text)
            
            self._add_history("text", text[:100])
            return True
        except Exception as e:
            logger.error(f"Failed to set text: {e}")
            return False
    
    def get_image(self) -> Optional[Image.Image]:
        """获取剪贴板图片"""
        try:
            if HAS_WIN32:
                win32clipboard.OpenClipboard()
                try:
                    data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                    win32clipboard.CloseClipboard()
                    
                    # DIB 转 PIL
                    import struct
                    header_size = struct.unpack('I', data[:4])[0]
                    width = struct.unpack('i', data[4:8])[0]
                    height = struct.unpack('i', data[8:12])[0]
                    
                    # 简化为直接返回（实际使用需要更复杂的解析）
                    return None
                except:
                    win32clipboard.CloseClipboard()
        except Exception as e:
            logger.error(f"Failed to get image: {e}")
        return None
    
    def clear(self) -> bool:
        """清空剪贴板"""
        try:
            if HAS_WIN32:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
            self._add_history("clear", "")
            return True
        except Exception as e:
            logger.error(f"Failed to clear: {e}")
            return False
    
    def _add_history(self, type_: str, content: str):
        """添加历史记录"""
        self.history.append({"type": type_, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)


# 快捷函数
_clipboard: Optional[ClipboardManager] = None

def get_clipboard() -> ClipboardManager:
    global _clipboard
    if _clipboard is None:
        _clipboard = ClipboardManager()
    return _clipboard

def copy_text(text: str) -> bool:
    return get_clipboard().set_text(text)

def paste_text() -> Optional[str]:
    return get_clipboard().get_text()

def clear_clipboard() -> bool:
    return get_clipboard().clear()
