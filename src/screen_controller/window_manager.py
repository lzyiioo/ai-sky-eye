"""
Window Manager - 窗口管理
列出、切换、控制窗口
"""

import logging
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import time

try:
    import win32gui
    import win32con
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """窗口信息"""
    hwnd: int
    title: str
    class_name: str
    rect: Tuple[int, int, int, int]  # left, top, right, bottom
    is_visible: bool
    is_minimized: bool
    pid: int


class WindowManager:
    """窗口管理器"""
    
    def list_windows(self, visible_only: bool = True) -> List[WindowInfo]:
        """列出所有窗口"""
        if not HAS_WIN32:
            return []
        
        windows = []
        
        def callback(hwnd, _):
            if visible_only and not win32gui.IsWindowVisible(hwnd):
                return True
            
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True
            
            try:
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                is_minimized = win32gui.IsIconic(hwnd)
                
                # 获取进程ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                windows.append(WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    class_name=class_name,
                    rect=rect,
                    is_visible=win32gui.IsWindowVisible(hwnd),
                    is_minimized=is_minimized,
                    pid=pid
                ))
            except:
                pass
            
            return True
        
        win32gui.EnumWindows(callback, None)
        return windows
    
    def find_window(self, title: str) -> Optional[WindowInfo]:
        """通过标题查找窗口"""
        for window in self.list_windows():
            if title.lower() in window.title.lower():
                return window
        return None
    
    def focus_window(self, hwnd: int) -> bool:
        """激活窗口"""
        try:
            if HAS_WIN32:
                # 恢复最小化
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # 置顶
                win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            logger.error(f"Failed to focus window: {e}")
            return False
    
    def minimize_window(self, hwnd: int) -> bool:
        """最小化窗口"""
        try:
            if HAS_WIN32:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"Failed to minimize: {e}")
            return False
    
    def maximize_window(self, hwnd: int) -> bool:
        """最大化窗口"""
        try:
            if HAS_WIN32:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            logger.error(f"Failed to maximize: {e}")
            return False
    
    def move_window(self, hwnd: int, x: int, y: int, width: int, height: int) -> bool:
        """移动和调整窗口大小"""
        try:
            if HAS_WIN32:
                win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return True
        except Exception as e:
            logger.error(f"Failed to move window: {e}")
            return False
    
    def close_window(self, hwnd: int) -> bool:
        """关闭窗口"""
        try:
            if HAS_WIN32:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            return False
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """获取当前活动窗口"""
        try:
            if HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows = self.list_windows()
                    for w in windows:
                        if w.hwnd == hwnd:
                            return w
        except:
            pass
        return None


# 快捷函数
_manager: Optional[WindowManager] = None

def get_manager() -> WindowManager:
    global _manager
    if _manager is None:
        _manager = WindowManager()
    return _manager

def list_all_windows(visible_only: bool = True) -> List[WindowInfo]:
    return get_manager().list_windows(visible_only)

def switch_to_window(title: str) -> bool:
    window = get_manager().find_window(title)
    if window:
        return get_manager().focus_window(window.hwnd)
    return False

def get_current_window() -> Optional[WindowInfo]:
    return get_manager().get_active_window()
