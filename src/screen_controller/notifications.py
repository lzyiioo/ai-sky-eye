"""
Notifications - Windows 通知系统
原生 Toast 通知
"""

import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from win10toast import ToastNotifier
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    """通知对象"""
    title: str
    message: str
    icon: Optional[str] = None
    duration: int = 5  # 秒
    threaded: bool = True


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self._toaster: Optional[ToastNotifier] = None
        self._history: list = []
        
        if HAS_TOAST:
            try:
                self._toaster = ToastNotifier()
            except Exception as e:
                logger.warning(f"ToastNotifier init failed: {e}")
    
    def notify(
        self,
        title: str,
        message: str,
        icon: Optional[str] = None,
        duration: int = 5,
        threaded: bool = True
    ) -> bool:
        """
        发送通知
        
        Args:
            title: 标题
            message: 内容
            icon: 图标路径
            duration: 显示时长（秒）
            threaded: 是否异步
            
        Returns:
            是否成功
        """
        try:
            if HAS_TOAST and self._toaster:
                self._toaster.show_toast(
                    title=title,
                    msg=message,
                    icon_path=icon,
                    duration=duration,
                    threaded=threaded
                )
            elif HAS_PLYER:
                notification.notify(
                    title=title,
                    message=message,
                    app_icon=icon,
                    timeout=duration
                )
            else:
                # 回退：打印
                print(f"[通知] {title}: {message}")
                return False
            
            # 记录历史
            self._history.append({
                "title": title,
                "message": message,
                "time": __import__('datetime').datetime.now()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            print(f"[通知] {title}: {message}")
            return False
    
    def notify_success(self, message: str, title: str = "✅ 成功"):
        """成功通知"""
        return self.notify(title, message)
    
    def notify_error(self, message: str, title: str = "❌ 错误"):
        """错误通知"""
        return self.notify(title, message, duration=10)
    
    def notify_warning(self, message: str, title: str = "⚠️ 警告"):
        """警告通知"""
        return self.notify(title, message, duration=7)
    
    def notify_info(self, message: str, title: str = "ℹ️ 信息"):
        """信息通知"""
        return self.notify(title, message)
    
    def get_history(self, limit: int = 10) -> list:
        """获取历史通知"""
        return self._history[-limit:]
    
    def clear_history(self):
        """清除历史"""
        self._history.clear()


# 快捷函数
_manager: Optional[NotificationManager] = None

def get_manager() -> NotificationManager:
    global _manager
    if _manager is None:
        _manager = NotificationManager()
    return _manager

def notify(title: str, message: str, **kwargs) -> bool:
    """发送通知"""
    return get_manager().notify(title, message, **kwargs)

def notify_success(message: str, title: str = "✅ 成功"):
    return get_manager().notify_success(message, title)

def notify_error(message: str, title: str = "❌ 错误"):
    return get_manager().notify_error(message, title)

def notify_warning(message: str, title: str = "⚠️ 警告"):
    return get_manager().notify_warning(message, title)

def notify_info(message: str, title: str = "ℹ️ 信息"):
    return get_manager().notify_info(message, title)
