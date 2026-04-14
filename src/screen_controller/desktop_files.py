"""
Desktop Files Manager - 桌面文件管理器
基于配置文件的桌面文件定位

适用于桌面图标不常变化的场景
"""

import json
import os
import time
import pyautogui
from typing import Optional, Dict, List
from datetime import datetime


class DesktopFilesManager:
    """
    桌面文件管理器
    
    通过配置文件保存桌面文件位置
    无需 OCR，直接使用坐标定位
    """
    
    def __init__(self, config_file: str = None):
        """
        初始化
        
        Args:
            config_file: 配置文件路径
        """
        if config_file is None:
            # 默认使用脚本所在目录的配置文件
            config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'desktop_files.json')
        
        self.config_file = config_file
        self.files_config = self._load_config()
        
        # 屏幕尺寸
        self.screen_w, self.screen_h = pyautogui.size()
        
        # 图标网格配置
        self.grid_config = {
            'start_x': 20,
            'start_y': 20,
            'col_spacing': 120,
            'row_spacing': 150,
            'cols': int(self.screen_w / 120),
            'rows': int(self.screen_h / 150)
        }
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ 已加载桌面文件配置（{len(config)} 个文件）")
                return config
        else:
            print("📝 创建新的桌面文件配置...")
            return {}
    
    def _save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.files_config, f, ensure_ascii=False, indent=2)
        print(f"✅ 配置已保存：{self.config_file}")
    
    def register_file(self, name: str, x: int, y: int, auto_save: bool = True):
        """
        注册文件位置
        
        Args:
            name: 文件名（关键词）
            x: X 坐标
            y: Y 坐标
            auto_save: 是否自动保存配置
        """
        self.files_config[name] = {
            'x': x,
            'y': y,
            'last_update': datetime.now().isoformat()
        }
        
        if auto_save:
            self._save_config()
        
        print(f"✅ 已注册：{name} -> ({x}, {y})")
    
    def find_file(self, keyword: str) -> Optional[Dict]:
        """
        查找文件
        
        Args:
            keyword: 文件名关键词
        
        Returns:
            文件信息（包含坐标），未找到返回 None
        """
        # 精确匹配
        if keyword in self.files_config:
            print(f"✅ 找到：{keyword}")
            return self.files_config[keyword]
        
        # 模糊匹配
        for name, info in self.files_config.items():
            if keyword.lower() in name.lower():
                print(f"✅ 找到（模糊匹配）：{name}")
                return info
        
        print(f"❌ 未找到：{keyword}")
        return None
    
    def get_position(self, keyword: str) -> Optional[tuple]:
        """
        获取文件位置
        
        Args:
            keyword: 文件名关键词
        
        Returns:
            (x, y) 坐标，未找到返回 None
        """
        info = self.find_file(keyword)
        if info:
            return (info['x'], info['y'])
        return None
    
    def list_files(self) -> List[str]:
        """列出所有已注册的文件"""
        return list(self.files_config.keys())
    
    def remove_file(self, keyword: str):
        """
        移除文件
        
        Args:
            keyword: 文件名关键词
        """
        if keyword in self.files_config:
            del self.files_config[keyword]
            self._save_config()
            print(f"✅ 已移除：{keyword}")
        else:
            print(f"❌ 未找到：{keyword}")
    
    def scan_desktop_grid(self) -> Dict[str, tuple]:
        """
        扫描桌面网格位置（用于初始化）
        
        Returns:
            网格位置字典
        """
        grid = {}
        
        for row in range(self.grid_config['rows']):
            for col in range(self.grid_config['cols']):
                x = self.grid_config['start_x'] + col * self.grid_config['col_spacing']
                y = self.grid_config['start_y'] + row * self.grid_config['row_spacing']
                grid[f"pos_{row}_{col}"] = (x, y)
        
        return grid
    
    def print_files(self):
        """打印所有已注册的文件"""
        print("\n" + "=" * 60)
        print("📋 桌面文件列表")
        print("=" * 60)
        
        if not self.files_config:
            print("（空）")
        else:
            for name, info in self.files_config.items():
                print(f"📁 {name}")
                print(f"   位置：({info['x']}, {info['y']})")
                print(f"   更新时间：{info.get('last_update', '未知')}")
        
        print("=" * 60)
        print(f"共 {len(self.files_config)} 个文件")
        print("=" * 60)
    
    def quick_open(self, keyword: str, controller):
        """
        快速打开文件
        
        Args:
            keyword: 文件名关键词
            controller: 键盘鼠标控制器
        """
        pos = self.get_position(keyword)
        
        if not pos:
            print(f"❌ 未找到文件：{keyword}")
            return False
        
        x, y = pos
        
        print(f"🖱️ 移动到 ({x}, {y})...")
        controller.move_mouse(x, y, reason=f"定位到{keyword}")
        time.sleep(0.5)
        
        print(f"🖱️ 双击打开...")
        controller.double_click(x, y, reason=f"打开{keyword}")
        time.sleep(2)
        
        print(f"✅ 文件应该已打开")
        return True


# ==================== 快捷函数 ====================

_manager: Optional[DesktopFilesManager] = None

def _get_manager() -> DesktopFilesManager:
    global _manager
    if _manager is None:
        _manager = DesktopFilesManager()
    return _manager

def desktop_register(name: str, x: int, y: int):
    """注册文件位置"""
    _get_manager().register_file(name, x, y)

def desktop_find(keyword: str):
    """查找文件"""
    return _get_manager().find_file(keyword)

def desktop_get_position(keyword: str):
    """获取文件位置"""
    return _get_manager().get_position(keyword)

def desktop_list():
    """列出所有文件"""
    return _get_manager().list_files()

def desktop_print():
    """打印文件列表"""
    _get_manager().print_files()

def desktop_quick_open(keyword: str, controller):
    """快速打开文件"""
    return _get_manager().quick_open(keyword, controller)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("桌面文件管理器测试")
    print("=" * 60)
    
    # 创建管理器
    manager = DesktopFilesManager()
    
    # 注册测试文件
    print("\n[测试 1] 注册文件...")
    manager.register_file('测试文件.txt', 20, 20)
    manager.register_file('回收站', 20, 170)
    
    # 查找文件
    print("\n[测试 2] 查找文件...")
    info = manager.find_file('测试文件')
    if info:
        print(f"找到：位置 ({info['x']}, {info['y']})")
    
    # 获取位置
    print("\n[测试 3] 获取位置...")
    pos = manager.get_position('回收站')
    if pos:
        print(f"回收站位置：{pos}")
    
    # 列出所有文件
    print("\n[测试 4] 列出所有文件...")
    files = manager.list_files()
    print(f"已注册 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f}")
    
    # 打印文件列表
    print("\n[测试 5] 打印文件列表...")
    manager.print_files()
    
    print("\n✅ 测试完成！")
