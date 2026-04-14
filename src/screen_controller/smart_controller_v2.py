"""
Smart Controller - 智能控制器（完整版）
结合 UI 元素识别 + 键鼠控制，告别坐标！
"""

import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .ui_element_finder import (
    get_finder, UIElement, find_element, 
    find_button, find_input, get_active_window
)
from .enhanced_safety_controller import EnhancedSafeController
from .enhanced_screenshot import capture_screen


@dataclass
class SmartAction:
    """智能操作记录"""
    action: str
    target: str
    success: bool
    duration: float
    message: str = ""


class SmartController:
    """智能控制器 - 让 AI 通过名称操作界面"""
    
    def __init__(self, safety_level: str = "normal"):
        self.finder = get_finder()
        self.controller = EnhancedSafeController(safety_level)
        self.default_timeout = 10.0
        self.retry_interval = 0.5
        self.action_history: List[SmartAction] = []
    
    def _find_element_with_retry(self, name: str, element_type: str = "any",
                                  max_retries: int = 3) -> Optional[UIElement]:
        """带重试的元素查找"""
        for attempt in range(max_retries):
            element = None
            if element_type == "button":
                element = self.finder.find_clickable(name)
            elif element_type == "edit":
                element = self.finder.find_input(name)
            else:
                results = self.finder.find_by_name(name)
                element = results[0] if results else None
            
            if element:
                return element
            
            if attempt < max_retries - 1:
                time.sleep(self.retry_interval)
                self.finder.clear_cache()
        return None
    
    def click(self, target: str, element_type: str = "any") -> Dict[str, Any]:
        """智能点击"""
        start_time = time.time()
        print(f"🔍 查找并点击: '{target}'")
        
        element = self._find_element_with_retry(target, element_type)
        if not element:
            return {"success": False, "error": f"未找到元素: '{target}'"}
        
        print(f"   ✅ 找到: {element.control_type} '{element.name}' @ {element.center}")
        result = self.controller.click(element.x, element.y, reason=f"点击 '{target}'")
        
        return {
            "success": result.get("success", False),
            "target": target,
            "element": element.to_dict(),
            "duration": time.time() - start_time
        }
    
    def type_text(self, target: str, text: str, clear_first: bool = True) -> Dict[str, Any]:
        """智能输入"""
        start_time = time.time()
        print(f"🔍 查找输入框: '{target}'")
        
        element = self._find_element_with_retry(target, "edit")
        if not element:
            return {"success": False, "error": f"未找到输入框: '{target}'"}
        
        print(f"   ✅ 找到: {element.control_type} '{element.name}' @ {element.center}")
        
        # 聚焦
        self.controller.click(element.x, element.y, reason=f"聚焦 '{target}'")
        time.sleep(0.2)
        
        # 清空
        if clear_first:
            self.controller.press_hotkey('ctrl', 'a')
            self.controller.press_key('delete')
            time.sleep(0.1)
        
        # 输入
        result = self.controller.type_text(text, reason=f"输入到 '{target}'")
        
        return {
            "success": result.get("success", False),
            "target": target,
            "text": text,
            "element": element.to_dict(),
            "duration": time.time() - start_time
        }
    
    def select_menu(self, *menu_items: str) -> Dict[str, Any]:
        """智能选择菜单"""
        start_time = time.time()
        print(f"🔍 选择菜单: {' > '.join(menu_items)}")
        
        for item in menu_items:
            result = self.click(item, element_type="button")
            if not result["success"]:
                return result
            time.sleep(0.3)
        
        return {
            "success": True,
            "menu": " > ".join(menu_items),
            "duration": time.time() - start_time
        }
    
    def wait_for_element(self, name: str, timeout: float = 10.0) -> Optional[UIElement]:
        """等待元素出现"""
        print(f"⏳ 等待元素: '{name}' (超时: {timeout}s)")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            element = self._find_element_with_retry(name, max_retries=1)
            if element:
                print(f"   ✅ 元素已出现: '{name}'")
                return element
            time.sleep(0.5)
            self.finder.clear_cache()
        
        print(f"   ❌ 等待超时: '{name}'")
        return None
    
    def screenshot_with_highlight(self, target: str = None) -> str:
        """截图并高亮显示元素"""
        from PIL import ImageDraw
        import io
        import base64
        
        img = capture_screen()
        
        if target:
            element = self._find_element_with_retry(target)
            if element:
                draw = ImageDraw.Draw(img)
                left, top, right, bottom = element.rect
                draw.rectangle([left, top, right, bottom], outline="red", width=3)
                draw.ellipse([element.x-5, element.y-5, element.x+5, element.y+5], fill="red")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


# 快捷函数
_smart_ctrl: Optional[SmartController] = None

def get_smart_ctrl() -> SmartController:
    global _smart_ctrl
    if _smart_ctrl is None:
        _smart_ctrl = SmartController("normal")
    return _smart_ctrl

def ai_click(target: str) -> Dict[str, Any]:
    """AI 智能点击"""
    return get_smart_ctrl().click(target)

def ai_type(target: str, text: str) -> Dict[str, Any]:
    """AI 智能输入"""
    return get_smart_ctrl().type_text(target, text)

def ai_menu(*items: str) -> Dict[str, Any]:
    """AI 智能选择菜单"""
    return get_smart_ctrl().select_menu(*items)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 智能控制器 - 使用示例")
    print("=" * 60)
    print("""
# 传统方式（需要坐标）
click(x=500, y=300)  # 按钮在哪？

# 智能方式（通过名称）
ai_click("确定")  # 自动查找并点击！

# 智能输入
ai_type("用户名", "admin")
ai_type("密码", "123456")

# 选择菜单
ai_menu("文件", "打开")

# 等待元素出现
elem = get_smart_ctrl().wait_for_element("保存按钮", timeout=10)

# 截图高亮
capture_with_highlight = get_smart_ctrl().screenshot_with_highlight("搜索框")
    """)
