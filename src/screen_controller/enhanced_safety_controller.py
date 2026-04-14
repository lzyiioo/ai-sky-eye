"""
Enhanced Safety Controller - 增强版安全控制器
支持三种安全级别：strict / normal / off
"""

import pyautogui
import threading
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from collections import deque

from .safety_config import SafetyConfig, SafetyLevel, SafetyRules
from .screen_controller import (
    move_mouse as _original_move_mouse,
    click as _original_click,
    type_text as _original_type_text,
    press_hotkey as _original_press_hotkey,
    press_key as _original_press_key,
    capture_screen as _original_capture_screen,
    capture_screen_base64 as _original_capture_screen_base64,
    get_screen_size as _original_get_screen_size,
    get_mouse_position as _original_get_mouse_position
)


class RateLimiter:
    """频率限制器"""
    
    def __init__(self, max_ops_per_second: int = 10):
        self.max_ops = max_ops_per_second
        self.operations = deque()
        self.lock = threading.Lock()
    
    def allow(self) -> bool:
        """检查是否允许操作"""
        with self.lock:
            now = time.time()
            # 移除1秒前的操作记录
            while self.operations and now - self.operations[0] > 1:
                self.operations.popleft()
            
            # 检查是否超过限制
            if len(self.operations) >= self.max_ops:
                return False
            
            # 记录本次操作
            self.operations.append(now)
            return True
    
    def get_current_rate(self) -> float:
        """获取当前操作频率"""
        with self.lock:
            now = time.time()
            # 清理旧记录
            while self.operations and now - self.operations[0] > 1:
                self.operations.popleft()
            return len(self.operations)


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, enabled: bool = True, log_level: str = "INFO"):
        self.enabled = enabled
        self.log_level = log_level
        self.logs = deque(maxlen=1000)  # 内存中保留最近1000条
        self.log_file = None
    
    def log(self, action: str, params: Dict, success: bool = True, message: str = ""):
        """记录操作日志"""
        if not self.enabled:
            return
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'params': params,
            'success': success,
            'message': message
        }
        
        self.logs.append(entry)
        
        # 控制台输出
        status = "✅" if success else "❌"
        print(f"📝 [{entry['timestamp']}] {status} {action}: {message or params}")
    
    def get_recent_logs(self, count: int = 10) -> list:
        """获取最近的操作日志"""
        return list(self.logs)[-count:]
    
    def export_logs(self, filepath: str):
        """导出日志到文件"""
        import json
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(list(self.logs), f, indent=2, ensure_ascii=False)
            print(f"✅ 日志已导出：{filepath}")
        except Exception as e:
            print(f"❌ 日志导出失败：{e}")


class EnhancedSafeController:
    """
    增强版安全控制器
    
    特性：
    - 三种安全级别：strict / normal / off
    - 实时频率限制
    - 敏感区域保护
    - 完整审计日志
    - 紧急停止机制
    """
    
    def __init__(self, level: str = "normal", config_file: Optional[str] = None):
        """
        初始化安全控制器
        
        Args:
            level: "strict" / "normal" / "off"
            config_file: 配置文件路径（可选）
        """
        # 加载配置
        self.config = SafetyConfig(
            level=SafetyLevel(level.lower()),
            config_file=config_file
        )
        self.rules = self.config.rules
        
        # 初始化组件
        self.rate_limiter = RateLimiter(self.rules.max_ops_per_second)
        self.audit_logger = AuditLogger(
            enabled=self.rules.enable_audit_log,
            log_level=self.rules.log_level
        )
        
        # 安全状态
        self.stopped = False
        self.operation_count = 0
        
        # 设置 PyAutoGUI
        pyautogui.FAILSAFE = self.rules.enable_failsafe
        
        # 启动紧急停止监听
        if self.rules.enable_emergency_stop:
            self._start_emergency_listener()

        print("=" * 60)
        print("[Safety] EnhancedSafeController started")
        print(f"   Safety level: {self.config.level.value.upper()}")
        print("=" * 60)
    
    def _start_emergency_listener(self):
        """启动紧急停止监听"""
        def listen():
            try:
                import keyboard
                while not self.stopped:
                    if keyboard.is_pressed(self.rules.emergency_hotkey):
                        self.emergency_stop()
                        break
                    time.sleep(0.1)
            except ImportError:
                print("⚠️ keyboard 库未安装，F12 紧急停止不可用")
            except Exception as e:
                print(f"⚠️ 紧急停止监听异常：{e}")
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
    
    def _check_rate_limit(self) -> bool:
        """检查频率限制"""
        if not self.rate_limiter.allow():
            current_rate = self.rate_limiter.get_current_rate()
            print(f"⚠️ 操作频率过高（当前：{current_rate}次/秒，限制：{self.rules.max_ops_per_second}次/秒）")
            return False
        return True
    
    def _check_sensitive_area(self, x: int, y: int) -> bool:
        """检查敏感区域"""
        if self.config.is_sensitive_area(x, y):
            print(f"🚫 操作被拒绝：坐标({x}, {y})位于敏感区域内")
            return False
        return True
    
    def _user_confirm(self, action: str, details: str = "") -> bool:
        """请求用户确认"""
        print(f"\n🔒 安全确认 [{action}]")
        print(f"   操作详情：{details}")
        
        # 在 OFF 模式下自动确认
        if self.config.level == SafetyLevel.OFF:
            return True
        
        try:
            response = input("   确认执行？(y/n/cancel): ").strip().lower()
            if response in ['y', 'yes', '是']:
                return True
            elif response in ['cancel', '取消']:
                self.emergency_stop()
                return False
            else:
                print("   ❌ 操作已取消")
                return False
        except:
            # 非交互环境，默认允许
            return True
    
    # ==================== 公共 API ====================
    
    def emergency_stop(self):
        """紧急停止所有操作"""
        self.stopped = True
        self.audit_logger.log("EMERGENCY_STOP", {}, True, "用户触发紧急停止")
        print("\n" + "🛑" * 20)
        print("紧急停止！所有后续操作将被拒绝")
        print("🛑" * 20 + "\n")
    
    def reset(self):
        """重置停止状态"""
        self.stopped = False
        self.operation_count = 0
        self.audit_logger.log("RESET", {}, True, "控制器已重置")
        print("✅ 控制器已重置，可以继续操作")
    
    def set_level(self, level: str):
        """切换安全级别"""
        self.config.set_level(SafetyLevel(level.lower()))
        self.rules = self.config.rules
        # 更新组件
        self.rate_limiter = RateLimiter(self.rules.max_ops_per_second)
        self.audit_logger.enabled = self.rules.enable_audit_log
        pyautogui.FAILSAFE = self.rules.enable_failsafe
    
    def move_mouse(self, x: int, y: int, reason: str = "") -> Dict[str, Any]:
        """安全移动鼠标"""
        if self.stopped:
            return {"success": False, "error": "控制器已停止"}
        
        if not self._check_rate_limit():
            return {"success": False, "error": "操作频率过高"}
        
        if not self._check_sensitive_area(x, y):
            return {"success": False, "error": "敏感区域"}
        
        if self.rules.confirm_before_click:
            if not self._user_confirm("移动鼠标", f"到({x}, {y}) {reason}"):
                return {"success": False, "error": "用户取消"}
        
        try:
            duration = self.rules.mouse_move_duration
            _original_move_mouse(x, y, duration)
            self.operation_count += 1
            self.audit_logger.log("MOVE_MOUSE", {"x": x, "y": y, "reason": reason}, True)
            return {"success": True, "action": "move_mouse", "position": {"x": x, "y": y}}
        except Exception as e:
            self.audit_logger.log("MOVE_MOUSE", {"x": x, "y": y}, False, str(e))
            return {"success": False, "error": str(e)}
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', reason: str = "") -> Dict[str, Any]:
        """安全点击"""
        if self.stopped:
            return {"success": False, "error": "控制器已停止"}
        
        if not self._check_rate_limit():
            return {"success": False, "error": "操作频率过高"}
        
        # 检查敏感区域
        if x is not None and y is not None:
            if not self._check_sensitive_area(x, y):
                return {"success": False, "error": "敏感区域"}
        
        if self.rules.confirm_before_click:
            details = f"坐标({x}, {y})" if x and y else "当前位置"
            if not self._user_confirm("鼠标点击", f"{button}键 @ {details} {reason}"):
                return {"success": False, "error": "用户取消"}
        
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y, f"准备点击")
            
            _original_click(button=button)
            self.operation_count += 1
            self.audit_logger.log("CLICK", {"x": x, "y": y, "button": button, "reason": reason}, True)
            return {"success": True, "action": "click", "button": button}
        except Exception as e:
            self.audit_logger.log("CLICK", {"x": x, "y": y}, False, str(e))
            return {"success": False, "error": str(e)}
    
    def type_text(self, text: str, reason: str = "") -> Dict[str, Any]:
        """安全输入文字"""
        if self.stopped:
            return {"success": False, "error": "控制器已停止"}
        
        if not self._check_rate_limit():
            return {"success": False, "error": "操作频率过高"}
        
        preview = text[:30] + "..." if len(text) > 30 else text
        
        if self.rules.confirm_before_type:
            if not self._user_confirm("输入文字", f'"{preview}" {reason}'):
                return {"success": False, "error": "用户取消"}
        
        try:
            interval = self.rules.type_interval
            _original_type_text(text, interval)
            self.operation_count += 1
            self.audit_logger.log("TYPE_TEXT", {"text": preview, "length": len(text), "reason": reason}, True)
            return {"success": True, "action": "type_text", "length": len(text)}
        except Exception as e:
            self.audit_logger.log("TYPE_TEXT", {"text": preview}, False, str(e))
            return {"success": False, "error": str(e)}
    
    def press_hotkey(self, *keys, reason: str = "") -> Dict[str, Any]:
        """安全按快捷键"""
        if self.stopped:
            return {"success": False, "error": "控制器已停止"}
        
        if not self._check_rate_limit():
            return {"success": False, "error": "操作频率过高"}
        
        hotkey_str = "+".join(keys)
        
        if self.rules.confirm_before_hotkey:
            if not self._user_confirm("快捷键", f"{hotkey_str} {reason}"):
                return {"success": False, "error": "用户取消"}
        
        try:
            _original_press_hotkey(*keys)
            self.operation_count += 1
            self.audit_logger.log("HOTKEY", {"keys": list(keys), "reason": reason}, True)
            return {"success": True, "action": "hotkey", "keys": list(keys)}
        except Exception as e:
            self.audit_logger.log("HOTKEY", {"keys": list(keys)}, False, str(e))
            return {"success": False, "error": str(e)}
    
    def capture_screen(self, region: Optional[Tuple] = None) -> Dict[str, Any]:
        """安全截屏"""
        if self.stopped:
            return {"success": False, "error": "控制器已停止"}
        
        if self.rules.confirm_before_capture:
            details = f"区域{region}" if region else "全屏"
            if not self._user_confirm("屏幕截图", details):
                return {"success": False, "error": "用户取消"}
        
        try:
            result = _original_capture_screen_base64()
            self.audit_logger.log("CAPTURE", {"region": region}, True)
            return {"success": True, "image": result}
        except Exception as e:
            self.audit_logger.log("CAPTURE", {"region": region}, False, str(e))
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "level": self.config.level.value,
            "stopped": self.stopped,
            "operation_count": self.operation_count,
            "current_rate": self.rate_limiter.get_current_rate(),
            "config": self.config.get_status()
        }
    
    def print_status(self):
        """打印状态"""
        status = self.get_status()
        print("=" * 60)
        print("📊 安全控制器状态")
        print("=" * 60)
        print(f"安全级别：{status['level'].upper()}")
        print(f"运行状态：{'🛑 已停止' if status['stopped'] else '✅ 运行中'}")
        print(f"操作次数：{status['operation_count']}")
        print(f"当前频率：{status['current_rate']}次/秒")
        print("=" * 60)


# ==================== 快捷函数 ====================

_controller: Optional[EnhancedSafeController] = None

def get_controller(level: str = "normal") -> EnhancedSafeController:
    """获取全局控制器实例"""
    global _controller
    if _controller is None:
        _controller = EnhancedSafeController(level)
    return _controller

def set_safety_level(level: str):
    """设置安全级别"""
    get_controller().set_level(level)

def safe_move(x: int, y: int, reason: str = ""):
    """快捷：移动鼠标"""
    return get_controller().move_mouse(x, y, reason)

def safe_click(x: int = None, y: int = None, button: str = 'left', reason: str = ""):
    """快捷：点击"""
    return get_controller().click(x, y, button, reason)

def safe_type(text: str, reason: str = ""):
    """快捷：输入文字"""
    return get_controller().type_text(text, reason)

def safe_hotkey(*keys, reason: str = ""):
    """快捷：快捷键"""
    return get_controller().press_hotkey(*keys, reason=reason)

def emergency_stop():
    """快捷：紧急停止"""
    get_controller().emergency_stop()

def reset_controller():
    """快捷：重置"""
    get_controller().reset()


if __name__ == "__main__":
    # 测试
    print("🧪 增强版安全控制器测试\n")
    
    # 测试 NORMAL 模式
    ctrl = EnhancedSafeController("normal")
    
    print("\n[测试 1] 移动鼠标...")
    ctrl.move_mouse(500, 500, "测试")
    
    print("\n[测试 2] 查看状态...")
    ctrl.print_status()
    
    print("\n✅ 测试完成")
    print(f"按 {ctrl.rules.emergency_hotkey.upper()} 紧急停止")
