"""
Smart Controller - 智能控制器
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
    """
    智能控制器
    
    功能：
    - 通过名称/描述操作 UI 元素
    - 自动查找元素坐标
    - 智能等待和重试
    - 操作链支持
    """
    
    def __init__(self, safety_level: str = "normal"):
        """
        初始化智能控制器
        
        Args:
            safety_level: 安全级别 strict/normal/off
        """
        self.finder = get_finder()
        self.controller = EnhancedSafeController(safety_level)
        
        # 设置
        self.default_timeout = 10.0  # 默认超时时间
        self.retry_interval = 0.5    # 重试间隔
        self.action_history: List[SmartAction] = []
    
    def _record_action(self, action: str, target: str, success: bool, 
                       duration: float, message: str = ""):
        """记录操作"""
        self.action_history.append(SmartAction(
            action=action,
            target=target,
            success=success,
            duration=duration,
            message=message
        ))
    
    def _find_element_with_retry(self, name: str, element_type: str = "any",
                                  max_retries: int = 3) -> Optional[UIElement]:
        """
        带重试的元素查找
        
        Args:
            name: 元素名称
            element_type: 元素类型（button/edit/any）
            max_retries: 最大重试次数
            
        Returns:
            UIElement 或 None
        """
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
                self.finder.clear_cache()  # 清除缓存，重新获取
        
        return None
    
    # ==================== 核心操作 ====================
    
    def click(self, target: str, element_type: str = "any", 
              timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        智能点击
        
        Args:
            target: 元素名称（如"确定"、"Save"）
            element_type: 元素类型（button/edit/any）
            timeout: 超时时间
            
        Returns:
            操作结果
        """
        start_time = time.time()
        timeout = timeout or self.default_timeout
        
        print(f"🔍 查找并点击: '{target}'")
        
        # 查找元素
        element = self._find_element_with_retry(target, element_type)
        
        if not element:
            duration = time.time() - start_time
            self._record_action("click", target, False, duration, "Element not found")
            return {
                "success": False,
                "error": f"未找到元素: '{target}'",
                "target": target
            }
        
        print(f"   ✅ 找到: {element.control_type} '{element.name}' @ {element.center}")
        
        # 执行点击
        result = self.controller.click(element.x, element.y, reason=f"点击 '{target}'")
        
        duration = time.time() - start_time
        self._record_action("click", target, result.get("success", False), duration)
        
        return {
            "success": result.get("success", False),
            "target": target,
            "element": element.to_dict(),
            "duration": duration
        }
    
    def type_text(self, target: str, text: str, 
                  clear_first: bool = True,
                  timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        智能输入
        
        Args:
            target: 输入框名称（如"用户名"、"搜索框"）
            text: 要输入的文本
            clear_first: 是否先清空
            timeout: 超时时间
            
        Returns:
            操作结果
        """
        start_time = time.time()
        timeout = timeout or self.default_timeout
        
        print(f"🔍 查找输入框: '{target}'")
        
        # 查找输入框
        element = self._find_element_with_retry(target, "edit")
        
        if not element:
            duration = time.time() - start_time
            self._record_action("type", target, False, duration, "Input not found")
            return {
                "success": False,
                "error": f"未找到输入框: '{target}'",
                "target": target
            }
        
        print(f"   ✅ 找到: {element.control_type} '{element.name}' @ {element.center}")
        
        # 点击聚焦
        click_result = self.controller.click(element.x, element.y, 
                                             reason=f"聚焦 '{target}'")
        if not click_result.get("success"):
            return {"success": False, "error": "无法聚焦到输入框"}
        
        time.sleep(0.2)  # 等待聚焦
        
        # 清空（如果需要）
        if clear_first:
            self.controller.press_hotkey('ctrl', 'a', reason="全选")
            self.controller.press_key('delete', reason="删除")
            time.sleep(0.1)
        
        # 输入文本
        type_result = self.controller.type_text(text, reason=f"输入到 '{target}'")
        
        duration = time.time() - start_time
        self._record_action("type", target, type_result.get("success", False), duration)
        
        return {
            "success": type_result.get("success", False),
            "target": target,
            "text": text,
            "element": element.to_dict(),
            "duration": duration
        }
    
    def select_menu(self, *menu_items: str) -> Dict[str, Any]:
        """
        智能选择菜单
        
        Args:
            *menu_items: 菜单项名称（如 "文件", "打开"）
            
        Returns:
            操作结果
        """
        start_time = time.time()
        
        print(f"🔍 选择菜单: {' > '.join(menu_items)}")
        
        for item in menu_items:
            result = self.click(item, element_type="button")
            if not result["success"]:
                return result
            time.sleep(0.3)  # 等待菜单展开
        
        duration = time.time() - start_time
        self._record_action("menu", " > ".join(menu_items), True, duration)
        
        return {
            "success": True,
            "menu": " > ".join(menu_items),
            "duration": duration
        }
    
    def wait_for_element(self, name: str, timeout: float = 10.0,
                         element_type: str = "any") -> Optional[UIElement]:
        """
        等待元素出现
        
        Args:
            name: 元素名称
            timeout: 超时时间
            element_type: 元素类型
            
        Returns:
            UIElement 或 None
        """
        print(f"⏳ 等待元素: '{name}' (超时: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            element = self._find_element_with_retry(name, element_type, max_retries=1)
            if element:
                print(f"   ✅ 元素已出现: '{name}'")
                return element
            time.sleep(0.5)
            self.finder.clear_cache()
        
        print