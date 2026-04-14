"""
Safe Controller - 安全的屏幕控制包装器
在原有功能基础上增加安全保护、日志记录、紧急停止等功能
"""

import pyautogui
import threading
import time
from datetime import datetime
import os
from typing import Optional, Tuple

# 导入原版功能
from .screen_controller import (
    move_mouse, click, type_text, press_hotkey, press_key,
    capture_screen, capture_screen_base64, get_screen_size,
    get_mouse_position, monitor_screen
)

# 导入输入法检测
try:
    from .input_method import (
        InputMethodDetector, InputMethodSwitcher,
        is_english_mode, ensure_english, ensure_chinese,
        print_ime_status
    )
    IME_SUPPORT = True
except Exception as e:
    IME_SUPPORT = False
    print(f"⚠️ 输入法检测模块加载失败：{e}")

# ==================== 安全设置 ====================

# 基础安全
pyautogui.FAILSAFE = True  # 鼠标移到角落停止
pyautogui.PAUSE = 0.3      # 操作间隔（比原版稍慢，更安全）


class SafeController:
    """
    安全控制器 - 为所有键鼠操作增加安全保护
    
    安全特性：
    - F12 紧急停止
    - 鼠标移到角落停止
    - 操作日志记录
    - 操作前状态检查
    - 关键操作确认
    """
    
    def __init__(self, log_enabled: bool = True, log_file: str = 'control_log.txt',
                 auto_ime_switch: bool = True, confirm_before_type: bool = False):
        """
        初始化安全控制器
        
        Args:
            log_enabled: 是否启用日志
            log_file: 日志文件路径
            auto_ime_switch: 打字时自动切换输入法（True=自动切换）
            confirm_before_type: 打字前是否需要确认（True=每次打字前询问）
        """
        self.stop_flag = False
        self.is_running = False
        self.log_enabled = log_enabled
        self.log_file = log_file
        
        # 输入法设置
        self.auto_ime_switch = auto_ime_switch
        self.ime_detector = InputMethodDetector() if IME_SUPPORT else None
        self.ime_switcher = InputMethodSwitcher() if IME_SUPPORT else None
        
        # 确认设置
        self.confirm_before_type = confirm_before_type
        
        # 速度档位
        self.speed_mode = 'normal'  # slow/normal/fast
        self.speed_settings = {
            'slow': {'move_duration': 1.0, 'type_interval': 0.15},
            'normal': {'move_duration': 0.5, 'type_interval': 0.1},
            'fast': {'move_duration': 0.2, 'type_interval': 0.05}
        }
        
        # 启动热键监听
        self._start_stop_listener()
        
        # 创建日志文件
        if self.log_enabled:
            self._log("系统", "安全控制器已启动")
        
        print("=" * 60)
        print("🛡️  SafeController 安全控制器已启动")
        print("=" * 60)
        print(f"🛑 紧急停止：按 F12 或 鼠标移到屏幕角落")
        print(f"📝 日志文件：{os.path.abspath(log_file)}")
        print(f"⚡ 速度模式：{self.speed_mode}")
        if IME_SUPPORT:
            print(f"🈶 输入法检测：{'已启用' if auto_ime_switch else '已禁用'}")
        else:
            print(f"⚠️ 输入法检测：不支持（仅 Windows）")
        print(f"🔒 打字前确认：{'已启用' if confirm_before_type else '已禁用'}")
        print("=" * 60)
    
    def _start_stop_listener(self):
        """后台监听停止热键"""
        def listen():
            try:
                import keyboard
                while not self.stop_flag:
                    if keyboard.is_pressed('f12'):
                        self.emergency_stop()
                        break
                    time.sleep(0.1)
            except ImportError:
                print("⚠️ 警告：keyboard 库未安装，F12 热键停止不可用")
                print("   请运行：pip install keyboard")
            except Exception as e:
                print(f"⚠️ 热键监听异常：{e}")
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
    
    def _log(self, action: str, details: str):
        """记录操作日志"""
        if not self.log_enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {action}: {details}\n"
        
        # 打印到控制台
        print(f"📝 {log_entry.strip()}")
        
        # 写入文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ 日志写入失败：{e}")
    
    def _check_stopped(self) -> bool:
        """检查是否已停止"""
        if self.stop_flag:
            print("⚠️ 控制器已停止，操作被取消")
            return True
        return False
    
    def _check_bounds(self, x: int, y: int) -> bool:
        """检查坐标是否在屏幕范围内"""
        screen_w, screen_h = pyautogui.size()
        if not (0 <= x <= screen_w and 0 <= y <= screen_h):
            print(f"⚠️ 警告：坐标 ({x},{y}) 超出屏幕范围 ({screen_w}x{screen_h})!")
            return False
        return True
    
    # ==================== 紧急控制 ====================
    
    def emergency_stop(self):
        """紧急停止所有操作"""
        self.stop_flag = True
        self.is_running = False
        
        print("\n" + "=" * 60)
        print("🛑🛑🛑 紧急停止！所有操作已中断！🛑🛑🛑")
        print("=" * 60)
        
        self._log("🛑 紧急停止", "用户触发")
    
    def reset_stop(self):
        """重置停止标志，可以继续操作"""
        self.stop_flag = False
        self.is_running = True
        print("✅ 已重置，可以继续操作")
        self._log("重置", "控制器已重置")
    
    def set_speed(self, mode: str = 'normal'):
        """
        设置速度模式
        
        Args:
            mode: slow/normal/fast
        """
        if mode not in self.speed_settings:
            print(f"⚠️ 无效的速度模式：{mode}，使用默认值 normal")
            mode = 'normal'
        
        self.speed_mode = mode
        settings = self.speed_settings[mode]
        print(f"⚡ 速度模式已设置为：{mode}")
        print(f"   - 鼠标移动：{settings['move_duration']}秒")
        print(f"   - 打字间隔：{settings['type_interval']}秒")
        self._log("速度设置", f"模式={mode}")
    
    # ==================== 鼠标控制（安全包装） ====================
    
    def move_mouse(self, x: int, y: int, reason: str = ""):
        """
        移动鼠标（安全版本）
        
        Args:
            x: 目标 X 坐标
            y: 目标 Y 坐标
            reason: 操作原因（用于日志）
        """
        if self._check_stopped():
            return
        
        # 边界检查
        if not self._check_bounds(x, y):
            self._log("❌ 移动鼠标失败", f"坐标越界 ({x},{y}) - {reason}")
            return
        
        duration = self.speed_settings[self.speed_mode]['move_duration']
        
        self._log("🖱️ 移动鼠标", f"({x},{y}) 耗时{duration}秒 - {reason}")
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            self._log("❌ 移动鼠标异常", str(e))
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1, reason: str = ""):
        """
        鼠标点击（安全版本）
        
        Args:
            x: X 坐标（可选，None=当前位置）
            y: Y 坐标（可选，None=当前位置）
            button: 按钮（left/right/middle）
            clicks: 点击次数
            reason: 操作原因
        """
        if self._check_stopped():
            return
        
        # 如果指定了坐标，先移动
        if x is not None and y is not None:
            if not self._check_bounds(x, y):
                self._log("❌ 点击失败", f"坐标越界 ({x},{y}) - {reason}")
                return
            self.move_mouse(x, y, reason=f"准备点击 ({reason})")
        
        self._log("🖱️ 点击", f"{button}键 x{clicks} @ 当前位置 - {reason}")
        
        try:
            pyautogui.click(clicks=clicks, button=button)
        except Exception as e:
            self._log("❌ 点击异常", str(e))
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None, reason: str = ""):
        """双击（安全版本）"""
        self.click(x, y, clicks=2, reason=reason)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None, reason: str = ""):
        """右键点击（安全版本）"""
        self.click(x, y, button='right', reason=reason)
    
    # ==================== 键盘控制（安全包装） ====================
    
    def type_text(self, text: str, confirm: bool = True, reason: str = "",
                  auto_ime: Optional[bool] = None, require_confirm: Optional[bool] = None):
        """
        键盘打字（安全版本）
        
        Args:
            text: 要输入的文本
            confirm: 是否显示预览（默认 True）
            reason: 操作原因
            auto_ime: 是否自动切换输入法（None=使用默认设置，True=英文，False=中文）
            require_confirm: 是否需要用户确认（None=使用默认设置，True=询问，False=不询问）
        """
        if self._check_stopped():
            return
        
        # 显示预览
        if confirm:
            preview = text if len(text) <= 50 else text[:50] + "..."
            print(f"⌨️ 准备输入：{preview}")
        
        # 判断是否需要用户确认
        need_confirm = require_confirm if require_confirm is not None else self.confirm_before_type
        
        # 用户确认
        if need_confirm:
            # 检测输入法状态
            if IME_SUPPORT and self.auto_ime_switch:
                is_chinese_content = any('\u4e00' <= c <= '\u9fff' for c in text)
                target_mode = "中文" if is_chinese_content else "英文"
                print(f"🔤 将切换到 {target_mode} 输入模式")
            
            # 询问用户
            try:
                response = input("确认执行此操作吗？(y/n): ").strip().lower()
                if response != 'y':
                    print("❌ 操作已取消")
                    self._log("❌ 输入取消", f'用户取消 - {reason}')
                    return
            except Exception as e:
                print(f"⚠️ 确认失败：{e}，继续执行...")
        
        # 自动切换输入法
        if IME_SUPPORT and self.auto_ime_switch:
            if auto_ime is None:
                # 根据内容判断：纯英文/数字→英文模式，含中文→中文模式
                auto_ime = not any('\u4e00' <= c <= '\u9fff' for c in text)
            
            if auto_ime:
                print("🔤 检测到英文内容，确保英文输入模式...")
                # 按 Shift 切换到英文
                self.ime_switcher.switch_to_english(method='shift')
            else:
                print("🈶 检测到中文内容，确保中文输入模式...")
                # 按 Shift 切换到中文
                self.ime_switcher.switch_to_chinese(method='shift')
        
        interval = self.speed_settings[self.speed_mode]['type_interval']
        
        self._log("⌨️ 输入文本", f'"{text}" 间隔{interval}秒 - {reason}')
        
        try:
            pyautogui.typewrite(text, interval=interval)
        except Exception as e:
            self._log("❌ 输入异常", str(e))
    
    def press_hotkey(self, *keys, reason: str = ""):
        """
        按快捷键（安全版本）
        
        Args:
            keys: 按键列表（如 'ctrl', 's'）
            reason: 操作原因
        """
        if self._check_stopped():
            return
        
        self._log("⌨️ 快捷键", f"{'+'.join(keys)} - {reason}")
        
        try:
            pyautogui.hotkey(*keys)
        except Exception as e:
            self._log("❌ 快捷键异常", str(e))
    
    def press_key(self, key: str, presses: int = 1, reason: str = ""):
        """
        按单个键（安全版本）
        
        Args:
            key: 按键名称
            presses: 按几次
            reason: 操作原因
        """
        if self._check_stopped():
            return
        
        self._log("⌨️ 按键", f"{key} x{presses} - {reason}")
        
        try:
            pyautogui.press(key, presses=presses)
        except Exception as e:
            self._log("❌ 按键异常", str(e))
    
    # ==================== 屏幕捕获（直接调用原版） ====================
    
    def capture_screen(self, output: str = 'screenshot.png', region: Optional[Tuple] = None):
        """截取屏幕（调用原版）"""
        if self._check_stopped():
            return None
        self._log("📸 截屏", f"输出={output}")
        return capture_screen(output, region)
    
    def capture_screen_base64(self):
        """截取屏幕返回 Base64（调用原版）"""
        if self._check_stopped():
            return None
        self._log("📸 截屏", "Base64 格式")
        return capture_screen_base64()
    
    def get_screen_size(self):
        """获取屏幕分辨率（调用原版）"""
        return get_screen_size()
    
    def get_mouse_position(self):
        """获取鼠标位置（调用原版）"""
        return get_mouse_position()
    
    # ==================== 工具函数 ====================
    
    def get_status(self) -> dict:
        """获取控制器状态"""
        return {
            "stop_flag": self.stop_flag,
            "is_running": self.is_running,
            "speed_mode": self.speed_mode,
            "log_enabled": self.log_enabled,
            "log_file": self.log_file
        }
    
    def print_status(self):
        """打印控制器状态"""
        status = self.get_status()
        print("\n" + "=" * 40)
        print("📊 控制器状态")
        print("=" * 40)
        for key, value in status.items():
            print(f"   {key}: {value}")
        print("=" * 40 + "\n")
    
    def check_ime_status(self):
        """检查并打印当前输入法状态"""
        if IME_SUPPORT:
            print_ime_status()
        else:
            print("⚠️ 输入法检测不支持（仅 Windows）")
    
    def set_auto_ime(self, enabled: bool):
        """
        设置是否自动切换输入法
        
        Args:
            enabled: True=自动切换，False=手动
        """
        self.auto_ime_switch = enabled
        status = "已启用" if enabled else "已禁用"
        print(f"🈶 输入法自动切换：{status}")
        self._log("输入法设置", f"自动切换={status}")
    
    def set_confirm_before_type(self, enabled: bool):
        """
        设置打字前是否需要确认
        
        Args:
            enabled: True=每次打字前询问，False=直接执行
        """
        self.confirm_before_type = enabled
        status = "已启用" if enabled else "已禁用"
        print(f"🔒 打字前确认：{status}")
        self._log("确认设置", f"打字前确认={status}")


# ==================== 快捷函数（无需实例化） ====================

# 全局控制器实例（懒加载）
_safe_controller: Optional[SafeController] = None

def _get_controller() -> SafeController:
    """获取或创建全局控制器"""
    global _safe_controller
    if _safe_controller is None:
        _safe_controller = SafeController()
    return _safe_controller

# 快捷函数
def safe_move_mouse(x: int, y: int, reason: str = ""):
    """快捷函数：移动鼠标"""
    _get_controller().move_mouse(x, y, reason)

def safe_click(x: int = None, y: int = None, button: str = 'left', reason: str = ""):
    """快捷函数：点击"""
    _get_controller().click(x, y, button=button, reason=reason)

def safe_type_text(text: str, confirm: bool = True, reason: str = ""):
    """快捷函数：打字"""
    _get_controller().type_text(text, confirm=confirm, reason=reason)

def safe_hotkey(*keys, reason: str = ""):
    """快捷函数：快捷键"""
    _get_controller().press_hotkey(*keys, reason=reason)

def safe_emergency_stop():
    """快捷函数：紧急停止"""
    _get_controller().emergency_stop()

def safe_reset():
    """快捷函数：重置"""
    _get_controller().reset_stop()


# ==================== 测试示例 ====================

if __name__ == "__main__":
    print("🧪 SafeController 测试")
    print("=" * 60)
    
    # 创建控制器
    controller = SafeController()
    
    # 测试移动
    print("\n[测试 1] 移动鼠标...")
    controller.move_mouse(500, 300, reason="测试移动")
    time.sleep(1)
    
    # 测试点击
    print("\n[测试 2] 点击...")
    controller.click(reason="测试点击")
    time.sleep(1)
    
    # 测试打字
    print("\n[测试 3] 打字...")
    controller.type_text("Hello SafeController!", reason="测试打字")
    time.sleep(1)
    
    # 测试快捷键
    print("\n[测试 4] 快捷键...")
    controller.press_hotkey('ctrl', 'a', reason="测试全选")
    
    print("\n✅ 测试完成！")
    print("💡 按 F12 可以紧急停止，或鼠标移到角落")
