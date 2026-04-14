"""
Input Method Controller - 输入法状态检测与切换
支持检测当前输入法状态（中文/英文），并自动切换
"""

import ctypes
import ctypes.wintypes
from typing import Tuple, Optional

# ==================== Windows API 输入法检测 ====================

class InputMethodDetector:
    """
    输入法检测器（Windows 专用）
    
    功能：
    - 检测当前输入法（中文/英文）
    - 检测输入法名称
    - 监听输入法切换
    """
    
    def __init__(self):
        # 加载 Windows API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # 常见中文输入法标识
        self.chinese_ime_keywords = [
            '微软拼音', '微软五笔', '五笔', '拼音',
            'QQ 拼音', 'QQ 五笔', '搜狗', '百度',
            'Rime', '小狼毫', '鼠须管'
        ]
    
    def get_current_ime(self) -> dict:
        """
        获取当前输入法信息
        
        Returns:
            dict: {
                'name': 输入法名称，
                'is_chinese': 是否中文输入法，
                'handle': 输入法句柄
            }
        """
        try:
            # 获取当前窗口
            hwnd = self.user32.GetForegroundWindow()
            
            # 获取输入法句柄
            himc = self.user32.GetWindowThreadProcessId(hwnd, None)
            ime_handle = self.user32.ImmGetContext(hwnd)
            
            # 获取输入法名称
            ime_name = self._get_ime_name(hwnd)
            
            # 判断是否中文输入法
            is_chinese = self._is_chinese_ime(ime_name)
            
            return {
                'name': ime_name,
                'is_chinese': is_chinese,
                'handle': ime_handle,
                'hwnd': hwnd
            }
        except Exception as e:
            return {
                'name': 'Unknown',
                'is_chinese': False,
                'error': str(e)
            }
    
    def _get_ime_name(self, hwnd) -> str:
        """获取输入法名称"""
        try:
            # 获取键盘布局
            kl = self.user32.GetKeyboardLayout(
                self.user32.GetWindowThreadProcessId(hwnd, None)
            )
            
            # 常见输入法 ID 映射
            ime_map = {
                0x0804: '中文 - 微软拼音',
                0x0404: '中文 - 注音',
                0x0C04: '中文 - 仓颉',
                0x1004: '中文 - 简体五笔',
                0x0409: 'English (US)',
                0x0809: 'English (UK)',
            }
            
            lang_id = kl & 0xFFFF
            return ime_map.get(lang_id, f'Unknown ({hex(lang_id)})')
        except:
            return 'Unknown'
    
    def _is_chinese_ime(self, ime_name: str) -> bool:
        """判断是否中文输入法"""
        ime_name_lower = ime_name.lower()
        for keyword in self.chinese_ime_keywords:
            if keyword.lower() in ime_name_lower:
                return True
        return False
    
    def is_english_mode(self) -> bool:
        """
        检查当前是否英文模式
        
        Returns:
            bool: True=英文模式，False=中文模式
        """
        result = self.get_current_ime()
        return not result.get('is_chinese', False)
    
    def print_status(self):
        """打印当前输入法状态"""
        info = self.get_current_ime()
        print("=" * 50)
        print("📝 输入法状态")
        print("=" * 50)
        print(f"   输入法：{info.get('name', 'Unknown')}")
        print(f"   类型：{'中文' if info.get('is_chinese') else '英文'}")
        print(f"   窗口：{info.get('hwnd', 'N/A')}")
        print("=" * 50)


# ==================== 输入法切换器 ====================

class InputMethodSwitcher:
    """
    输入法切换器
    
    功能：
    - 切换到英文模式（按 Shift）
    - 切换到中文模式（按 Shift）
    - 切换中英文状态
    """
    
    def __init__(self):
        self.detector = InputMethodDetector()
        self.user32 = ctypes.windll.user32
        
        # 切换方式：shift（默认）或 api
        self.switch_method = 'shift'  # 'shift' or 'api'
    
    def switch_to_english(self, method: str = None) -> bool:
        """
        切换到英文模式
        
        Args:
            method: 切换方式（'shift' 或 'api'，None=使用默认）
        
        Returns:
            bool: 是否成功
        """
        method = method or self.switch_method
        
        if method == 'shift':
            return self._switch_by_shift()
        else:
            return self._switch_to_english_api()
    
    def _switch_by_shift(self) -> bool:
        """
        按 Shift 切换中英文（推荐）
        
        优点：
        - 自然，和用户操作一样
        - 不改变输入法，只切换中英文状态
        - 五笔/拼音都适用
        """
        try:
            import pyautogui
            # 按 Shift 切换中英文
            pyautogui.press('shift')
            print("✅ 按 Shift 切换到英文模式")
            return True
        except Exception as e:
            print(f"⚠️ Shift 切换失败，尝试 API 方式：{e}")
            return self._switch_to_english_api()
    
    def _switch_to_english_api(self) -> bool:
        """
        使用 API 切换到英文输入法
        """
        try:
            # 英文输入法 ID (US English)
            result = self.user32.LoadKeyboardLayoutW(
                ctypes.c_wchar_p('00000409'),
                0x0001 | 0x0010
            )
            
            if result:
                print("✅ 已切换到英文输入法（API）")
                return True
            else:
                print("⚠️ 切换英文失败")
                return False
        except Exception as e:
            print(f"❌ 切换英文异常：{e}")
            return False
    
    def switch_to_chinese(self, method: str = None) -> bool:
        """
        切换到中文模式
        
        Args:
            method: 切换方式（'shift' 或 'api'，None=使用默认）
        
        Returns:
            bool: 是否成功
        """
        method = method or self.switch_method
        
        if method == 'shift':
            return self._switch_by_shift()
        else:
            return self._switch_to_chinese_api()
    
    def _switch_by_shift(self) -> bool:
        """
        按 Shift 切换中英文（推荐）
        """
        try:
            import pyautogui
            pyautogui.press('shift')
            print("✅ 按 Shift 切换到中文模式")
            return True
        except Exception as e:
            print(f"⚠️ Shift 切换失败，尝试 API 方式：{e}")
            return self._switch_to_chinese_api()
    
    def _switch_to_chinese_api(self) -> bool:
        """
        使用 API 切换到中文输入法
        """
        try:
            result = self.user32.LoadKeyboardLayoutW(
                ctypes.c_wchar_p('00000804'),
                0x0001 | 0x0010
            )
            
            if result:
                print("✅ 已切换到中文输入法（API）")
                return True
            else:
                print("⚠️ 切换中文失败")
                return False
        except Exception as e:
            print(f"❌ 切换中文异常：{e}")
            return False
    
    def toggle_caps_lock(self) -> bool:
        """
        切换 Caps Lock（大小写）
        
        Returns:
            bool: 是否成功
        """
        try:
            import pyautogui
            pyautogui.press('capslock')
            print("✅ 按 Caps Lock 切换大小写")
            return True
        except Exception as e:
            print(f"❌ Caps Lock 切换失败：{e}")
            return False
    
    def ensure_english(self) -> bool:
        """
        确保当前是英文模式
        如果不是，自动切换到英文
        
        Returns:
            bool: 最终是否英文模式
        """
        if self.detector.is_english_mode():
            print("✓ 当前已是英文模式")
            return True
        
        print("🔄 检测到中文输入法，切换到英文...")
        return self.switch_to_english()
    
    def ensure_chinese(self) -> bool:
        """
        确保当前是中文模式
        如果不是，自动切换到中文
        
        Returns:
            bool: 最终是否中文模式
        """
        if not self.detector.is_english_mode():
            print("✓ 当前已是中文模式")
            return True
        
        print("🔄 检测到英文输入法，切换到中文...")
        return self.switch_to_chinese()


# ==================== 快捷函数 ====================

_detector: Optional[InputMethodDetector] = None
_switcher: Optional[InputMethodSwitcher] = None

def _get_detector() -> InputMethodDetector:
    global _detector
    if _detector is None:
        _detector = InputMethodDetector()
    return _detector

def _get_switcher() -> InputMethodSwitcher:
    global _switcher
    if _switcher is None:
        _switcher = InputMethodSwitcher()
    return _switcher

def get_ime_status() -> dict:
    """获取输入法状态"""
    return _get_detector().get_current_ime()

def is_english_mode() -> bool:
    """是否英文模式"""
    return _get_detector().is_english_mode()

def switch_to_english() -> bool:
    """切换到英文"""
    return _get_switcher().switch_to_english()

def switch_to_chinese() -> bool:
    """切换到中文"""
    return _get_switcher().switch_to_chinese()

def ensure_english() -> bool:
    """确保英文模式"""
    return _get_switcher().ensure_english()

def ensure_chinese() -> bool:
    """确保中文模式"""
    return _get_switcher().ensure_chinese()

def print_ime_status():
    """打印输入法状态"""
    _get_detector().print_status()


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("输入法检测与切换测试")
    print("=" * 60)
    
    detector = InputMethodDetector()
    switcher = InputMethodSwitcher()
    
    # 测试 1：检测当前输入法
    print("\n[测试 1] 检测当前输入法")
    print_ime_status()
    
    # 测试 2：检查是否英文
    print("\n[测试 2] 检查是否英文模式")
    is_en = is_english_mode()
    print(f"当前是英文模式：{is_en}")
    
    # 测试 3：切换到英文
    print("\n[测试 3] 切换到英文输入法")
    switch_to_english()
    print_ime_status()
    
    # 测试 4：切换到中文
    print("\n[测试 4] 切换到中文输入法")
    switch_to_chinese()
    print_ime_status()
    
    # 测试 5：确保英文
    print("\n[测试 5] 确保英文模式")
    ensure_english()
    print_ime_status()
    
    print("\n✅ 测试完成！")
