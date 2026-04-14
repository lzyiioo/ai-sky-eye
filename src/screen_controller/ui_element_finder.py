"""
UI Element Finder - UI 元素识别系统
基于 Windows UI Automation，让 AI 可以"看懂"界面
"""

import logging
from typing import Optional, List, Dict, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import time

# 可选依赖
try:
    import uiautomation as uia
    HAS_UIA = True
except ImportError:
    HAS_UIA = False
    uia = None

logger = logging.getLogger(__name__)


class ElementType(Enum):
    """UI 元素类型"""
    BUTTON = "Button"
    EDIT = "Edit"  # 输入框
    COMBOBOX = "ComboBox"
    LIST = "List"
    LISTITEM = "ListItem"
    MENU = "Menu"
    MENUITEM = "MenuItem"
    TAB = "Tab"
    TABITEM = "TabItem"
    TOOLBAR = "ToolBar"
    STATUSBAR = "StatusBar"
    TREE = "Tree"
    TREEITEM = "TreeItem"
    WINDOW = "Window"
    PANE = "Pane"
    DOCUMENT = "Document"
    HYPERLINK = "Hyperlink"
    CHECKBOX = "CheckBox"
    RADIOBUTTON = "RadioButton"
    SLIDER = "Slider"
    PROGRESSBAR = "ProgressBar"
    SCROLLBAR = "ScrollBar"
    IMAGE = "Image"
    TEXT = "Text"
    GROUP = "Group"
    CUSTOM = "Custom"
    UNKNOWN = "Unknown"


@dataclass
class UIElement:
    """UI 元素数据类"""
    name: str                           # 元素名称（如"确定"）
    control_type: str                   # 控件类型（如"Button"）
    automation_id: str = ""            # 自动化ID
    class_name: str = ""               # 类名
    rect: Tuple[int, int, int, int] = field(default_factory=lambda: (0, 0, 0, 0))  # (left, top, right, bottom)
    center: Tuple[int, int] = field(default_factory=lambda: (0, 0))  # 中心点坐标
    enabled: bool = True                # 是否可用
    visible: bool = True                # 是否可见
    focused: bool = False               # 是否聚焦
    selected: bool = False              # 是否选中
    value: str = ""                    # 当前值（如输入框内容）
    description: str = ""              # 描述信息
    parent: Optional['UIElement'] = None  # 父元素
    children: List['UIElement'] = field(default_factory=list)  # 子元素
    path: str = ""                     # 元素路径（如"窗口/面板/按钮"）
    
    @property
    def x(self) -> int:
        """中心点 X 坐标"""
        return self.center[0]
    
    @property
    def y(self) -> int:
        """中心点 Y 坐标"""
        return self.center[1]
    
    @property
    def width(self) -> int:
        """宽度"""
        return self.rect[2] - self.rect[0]
    
    @property
    def height(self) -> int:
        """高度"""
        return self.rect[3] - self.rect[1]
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "name": self.name,
            "control_type": self.control_type,
            "automation_id": self.automation_id,
            "class_name": self.class_name,
            "rect": self.rect,
            "center": self.center,
            "enabled": self.enabled,
            "visible": self.visible,
            "focused": self.focused,
            "value": self.value,
            "description": self.description,
            "path": self.path,
            "has_children": len(self.children) > 0
        }
    
    def __repr__(self) -> str:
        return f"UIElement({self.control_type}: '{self.name}' @ {self.center})"


class UIFinder:
    """
    UI 元素查找器
    
    功能：
    - 获取完整 UI 树
    - 通过名称、类型、ID 查找元素
    - 支持模糊匹配
    - 缓存机制
    """
    
    def __init__(self):
        self._cache: Dict[str, List[UIElement]] = {}
        self._cache_time: float = 0
        self._cache_duration: float = 1.0  # 缓存有效期（秒）
        self._tree_depth: int = 10  # 最大遍历深度
        
        if not HAS_UIA:
            logger.warning("uiautomation not installed. UI element finding unavailable.")
            logger.info("Install with: pip install uiautomation")
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return HAS_UIA
    
    def _build_element(self, control, parent: Optional[UIElement] = None, 
                       depth: int = 0, path: str = "") -> Optional[UIElement]:
        """
        从 uiautomation 控件构建 UIElement
        
        Args:
            control: uiautomation 控件
            parent: 父元素
            depth: 当前深度
            path: 元素路径
            
        Returns:
            UIElement 或 None
        """
        if not control:
            return None
        
        try:
            # 获取控件矩形
            rect = control.BoundingRectangle
            if rect:
                left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2
            else:
                left = top = right = bottom = center_x = center_y = 0
            
            # 构建元素
            element = UIElement(
                name=control.Name or "",
                control_type=control.ControlTypeName or "Unknown",
                automation_id=control.AutomationId or "",
                class_name=control.ClassName or "",
                rect=(left, top, right, bottom),
                center=(center_x, center_y),
                enabled=control.IsEnabled,
                visible=control.IsVisible,
                focused=control.HasKeyboardFocus if hasattr(control, 'HasKeyboardFocus') else False,
                value=getattr(control, 'Value', ""),
                description=control.HelpText if hasattr(control, 'HelpText') else "",
                parent=parent,
                path=path
            )
            
            # 递归获取子元素
            if depth < self._tree_depth:
                try:
                    children = control.GetChildren()
                    for i, child in enumerate(children):
                        child_path = f"{path}/{child.Name or child.ControlTypeName}" if path else (child.Name or child.ControlTypeName)
                        child_element = self._build_element(child, element, depth + 1, child_path)
                        if child_element:
                            element.children.append(child_element)
                except Exception as e:
                    logger.debug(f"Failed to get children: {e}")
            
            return element
            
        except Exception as e:
            logger.debug(f"Failed to build element: {e}")
            return None
    
    def get_ui_tree(self, refresh: bool = False) -> Optional[UIElement]:
        """
        获取完整 UI 树
        
        Args:
            refresh: 强制刷新，不使用缓存
            
        Returns:
            根元素（桌面）
        """
        if not self.is_available():
            return None
        
        # 检查缓存
        if not refresh and time.time() - self._cache_time < self._cache_duration:
            return self._cache.get("root")
        
        try:
            # 获取桌面根
            desktop = uia.GetRootControl()
            root = self._build_element(desktop, None, 0, "Desktop")
            
            # 更新缓存
            self._cache["root"] = root
            self._cache_time = time.time()
            
            return root
            
        except Exception as e:
            logger.error(f"Failed to get UI tree: {e}")
            return None
    
    def _flatten_tree(self, element: UIElement, result: List[UIElement] = None) -> List[UIElement]:
        """将树扁平化为列表"""
        if result is None:
            result = []
        
        if element:
            result.append(element)
            for child in element.children:
                self._flatten_tree(child, result)
        
        return result
    
    def find_by_name(self, name: str, fuzzy: bool = True, 
                     control_type: Optional[str] = None) -> List[UIElement]:
        """
        通过名称查找元素
        
        Args:
            name: 元素名称
            fuzzy: 是否模糊匹配
            control_type: 限定控件类型（可选）
            
        Returns:
            匹配的元素列表
        """
        root = self.get_ui_tree()
        if not root:
            return []
        
        all_elements = self._flatten_tree(root)
        results = []
        
        name_lower = name.lower()
        
        for elem in all_elements:
            # 检查名称
            elem_name_lower = elem.name.lower()
            
            if fuzzy:
                match = name_lower in elem_name_lower or elem_name_lower in name_lower
            else:
                match = elem.name == name
            
            if match:
                # 检查控件类型
                if control_type and elem.control_type != control_type:
                    continue
                
                # 只返回可见且可用的元素
                if elem.visible and elem.enabled:
                    results.append(elem)
        
        # 按匹配度排序（精确匹配优先）
        results.sort(key=lambda e: (
            0 if e.name == name else 1,  # 精确匹配优先
            -len(e.name),  # 名称短的优先
            abs(len(e.name) - len(name))  # 长度相近的优先
        ))
        
        return results
    
    def find_by_type(self, control_type: str) -> List[UIElement]:
        """
        通过类型查找元素
        
        Args:
            control_type: 控件类型（如"Button"）
            
        Returns:
            匹配的元素列表
        """
        root = self.get_ui_tree()
        if not root:
            return []
        
        all_elements = self._flatten_tree(root)
        return [e for e in all_elements if e.control_type == control_type and e.visible]
    
    def find_by_automation_id(self, automation_id: str) -> Optional[UIElement]:
        """
        通过自动化 ID 查找元素（最精确）
        
        Args:
            automation_id: 自动化 ID
            
        Returns:
            匹配的元素或 None
        """
        root = self.get_ui_tree()
        if not root:
            return None
        
        all_elements = self._flatten_tree(root)
        for elem in all_elements:
            if elem.automation_id == automation_id:
                return elem
        
        return None
    
    def find_clickable(self, name: str) -> Optional[UIElement]:
        """
        查找可点击元素（按钮、菜单等）
        
        Args:
            name: 元素名称
            
        Returns:
            匹配的元素或 None
        """
        clickable_types = ["Button", "MenuItem", "Hyperlink", "TabItem", "TreeItem", "ListItem"]
        
        root = self.get_ui_tree()
        if not root:
            return None
        
        all_elements = self._flatten_tree(root)
        name_lower = name.lower()
        
        candidates = []
        for elem in all_elements:
            if elem.control_type in clickable_types and elem.visible and elem.enabled:
                elem_name_lower = elem.name.lower()
                if name_lower in elem_name_lower or elem_name_lower in name_lower:
                    candidates.append(elem)
        
        if candidates:
            # 返回最匹配的一个
            candidates.sort(key=lambda e: (
                0 if e.name == name else 1,
                -len(e.name)
            ))
            return candidates[0]
        
        return None
    
    def find_input(self, name_or_hint: str = "") -> Optional[UIElement]:
        """
        查找输入框
        
        Args:
            name_or_hint: 输入框名称或提示文字
            
        Returns:
            匹配的输入框元素或 None
        """
        input_types = ["Edit", "ComboBox"]
        
        root = self.get_ui_tree()
        if not root:
            return None
        
        all_elements = self._flatten_tree(root)
        
        # 先找所有输入框
        inputs = [e for e in all_elements if e.control_type in input_types and e.visible]
        
        if not name_or_hint:
            # 返回第一个可见输入框
            return inputs[0] if inputs else None
        
        # 按名称匹配
        hint_lower = name_or_hint.lower()
        for inp in inputs:
            if hint_lower in inp.name.lower() or hint_lower in inp.value.lower():
                return inp
        
        # 没找到，返回第一个
        return inputs[0] if inputs else None
    
    def get_foreground_window(self) -> Optional[UIElement]:
        """获取当前活动窗口"""
        if not self.is_available():
            return None
        
        try:
            window = uia.GetForegroundControl()
            return self._build_element(window, None, 0, "Foreground")
        except Exception as e:
            logger.error(f"Failed to get foreground window: {e}")
            return None
    
    def get_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """获取指定坐标的元素"""
        if not self.is_available():
            return None
        
        try:
            control = uia.ControlFromPoint(x, y)
            if control:
                return self._build_element(control)
            return None
        except Exception as e:
            logger.error(f"Failed to get element at position: {e}")
            return None
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._cache_time = 0
    
    def print_tree(self, element: Optional[UIElement] = None, 
                   indent: int = 0, max_depth: int = 3):
        """打印 UI 树（用于调试）"""
        if element is None:
            element = self.get_ui_tree()
        
        if not element:
            print("No UI tree available")
            return
        
        if indent > max_depth:
            return
        
        prefix = "  " * indent
        print(f"{prefix}{element.control_type}: '{element.name}' @ {element.center}")
        
        for child in element.children[:10]:  # 最多显示10个子元素
            self.print_tree(child, indent + 1, max_depth)
        
        if len(element.children) > 10:
            print(f"{prefix}  ... and {len(element.children) - 10} more")


# ==================== 快捷函数 ====================

_finder: Optional[UIFinder] = None

def get_finder() -> UIFinder:
    """获取全局查找器"""
    global _finder
    if _finder is None:
        _finder = UIFinder()
    return _finder

def find_element(name: str, fuzzy: bool = True) -> Optional[UIElement]:
    """快捷：通过名称查找元素"""
    results = get_finder().find_by_name(name, fuzzy)
    return results[0] if results else None

def find_button(name: str) -> Optional[UIElement]:
    """快捷：查找按钮"""
    return get_finder().find_clickable(name)

def find_input(name: str = "") -> Optional[UIElement]:
    """快捷：查找输入框"""
    return get_finder().find_input(name)

def get_active_window() -> Optional[UIElement]:
    """快捷：获取活动窗口"""
    return get_finder().get_foreground_window()

def print_ui_tree(max_depth: int = 3):
    """快捷：打印 UI 树"""
    get_finder().print_tree(max_depth=max_depth)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 UI 元素识别系统测试")
    print("=" * 70)
    
    finder = UIFinder()
    
    if not finder.is_available():
        print("\n❌ uiautomation 未安装")
        print("   运行: pip install uiautomation")
        exit(1)
    
    print("\n✅ uiautomation 已安装\n")
    
    # 测试1: 获取活动窗口
    print("[测试 1] 获取活动窗口...")
    window = finder.get_foreground_window()
    if window:
        print(f"   活动窗口: {window.name} ({window.control_type})")
        print(f"   位置: {window.rect}")
    
    # 测试2: 打印 UI 树
    print("\n[测试 2] 打印 UI 树（前3层）...")
    finder.print_tree(max_depth=2)
    
    # 测试3: 查找按钮
    print("\n[测试 3] 查找按钮...")
    buttons = finder.find_by_type("Button")
    print(f"   找到 {len(buttons)} 个按钮")
    for btn in buttons[:5]:
        print(f"   - '{btn.name}' @ {btn.center}")
    
    # 测试4: 查找输入框
    print("\n[测试 4] 查找输入框...")
    inputs = finder.find_by_type("Edit")
    print(f"   找到 {len(inputs)} 个输入框")
    for inp in inputs[:3]:
        print(f"   - '{inp.name}' @ {inp.center}, 值: '{inp.value}'")
    
    print("\n✅ 测试完成!")
