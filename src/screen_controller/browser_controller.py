"""
Browser Controller - 浏览器自动化控制
基于 pyautogui 的键盘操作，控制浏览器
"""

import pyautogui
import time
from typing import Optional

class BrowserController:
    """
    浏览器控制器
    
    功能：
    - 打开浏览器
    - 导航到 URL
    - 标签页管理
    - 页面操作（滚动、刷新等）
    - 表单填写
    - 快捷键操作
    """
    
    def __init__(self):
        # 浏览器快捷键（适用于 Chrome/Edge/Firefox）
        self.shortcuts = {
            # 导航
            'new_tab': 'ctrl+t',           # 新建标签页
            'close_tab': 'ctrl+w',         # 关闭标签页
            'reopen_tab': 'ctrl+shift+t',  # 重新打开关闭的标签页
            'next_tab': 'ctrl+tab',        # 下一个标签页
            'prev_tab': 'ctrl+shift+tab',  # 上一个标签页
            'jump_tab': 'ctrl+{num}',      # 跳转到第 N 个标签页
            
            # 页面
            'refresh': 'f5',               # 刷新
            'hard_refresh': 'ctrl+f5',     # 硬刷新
            'home': 'alt+home',            # 主页
            'back': 'alt+left',            # 后退
            'forward': 'alt+right',        # 前进
            
            # 地址栏
            'focus_address': 'ctrl+l',     # 聚焦地址栏
            'focus_search': 'f6',          # 聚焦搜索栏
            
            # 书签
            'bookmark': 'ctrl+d',          # 添加书签
            'bookmark_manager': 'ctrl+shift+o',  # 书签管理器
            
            # 历史
            'history': 'ctrl+h',           # 历史记录
            'downloads': 'ctrl+j',         # 下载内容
            
            # 查找
            'find': 'ctrl+f',              # 查找
            'find_next': 'f3',             # 查找下一个
            
            # 缩放
            'zoom_in': 'ctrl++',           # 放大
            'zoom_out': 'ctrl+-',          # 缩小
            'zoom_reset': 'ctrl+0',        # 重置缩放
            
            # 开发者工具
            'devtools': 'f12',             # 开发者工具
            'inspect': 'ctrl+shift+i',     # 检查元素
            
            # 其他
            'fullscreen': 'f11',           # 全屏
            'print': 'ctrl+p',             # 打印
            'save': 'ctrl+s',              # 保存页面
            'find_in_page': 'ctrl+f',      # 页面内查找
        }
    
    def open_browser(self, browser: str = 'chrome') -> bool:
        """
        打开浏览器
        
        Args:
            browser: 浏览器名称（chrome/edge/firefox）
        
        Returns:
            bool: 是否成功
        """
        try:
            import subprocess
            
            browsers = {
                'chrome': 'chrome',
                'edge': 'msedge',
                'firefox': 'firefox'
            }
            
            browser_cmd = browsers.get(browser, 'chrome')
            subprocess.Popen([browser_cmd])
            
            print(f"✅ 已启动 {browser} 浏览器")
            return True
        except Exception as e:
            print(f"❌ 打开浏览器失败：{e}")
            return False
    
    def navigate_to(self, url: str, wait: float = 2.0) -> bool:
        """
        导航到 URL
        
        Args:
            url: 网址
            wait: 等待时间（秒）
        
        Returns:
            bool: 是否成功
        """
        try:
            # Ctrl+L 聚焦地址栏
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # 输入 URL
            pyautogui.typewrite(url, interval=0.05)
            time.sleep(0.5)
            
            # 回车确认
            pyautogui.press('enter')
            time.sleep(wait)
            
            print(f"✅ 已导航到：{url}")
            return True
        except Exception as e:
            print(f"❌ 导航失败：{e}")
            return False
    
    def new_tab(self, url: Optional[str] = None, wait: float = 2.0) -> bool:
        """
        新建标签页
        
        Args:
            url: 可选网址
            wait: 等待时间
        
        Returns:
            bool: 是否成功
        """
        try:
            # Ctrl+T 新建标签页
            pyautogui.hotkey('ctrl', 't')
            time.sleep(0.5)
            
            # 如果有 URL，导航过去
            if url:
                self.navigate_to(url, wait)
            else:
                time.sleep(wait)
            
            print(f"✅ 已新建标签页")
            return True
        except Exception as e:
            print(f"❌ 新建标签页失败：{e}")
            return False
    
    def close_tab(self) -> bool:
        """
        关闭当前标签页
        
        Returns:
            bool: 是否成功
        """
        try:
            pyautogui.hotkey('ctrl', 'w')
            print("✅ 已关闭标签页")
            return True
        except Exception as e:
            print(f"❌ 关闭标签页失败：{e}")
            return False
    
    def refresh(self, hard: bool = False) -> bool:
        """
        刷新页面
        
        Args:
            hard: 是否硬刷新（清除缓存）
        
        Returns:
            bool: 是否成功
        """
        try:
            if hard:
                pyautogui.hotkey('ctrl', 'f5')
                print("✅ 已硬刷新（清除缓存）")
            else:
                pyautogui.press('f5')
                print("✅ 已刷新")
            return True
        except Exception as e:
            print(f"❌ 刷新失败：{e}")
            return False
    
    def scroll_page(self, direction: str = 'down', amount: int = 1) -> bool:
        """
        滚动页面
        
        Args:
            direction: 方向（up/down/left/right）
            amount: 滚动量（页数或像素）
        
        Returns:
            bool: 是否成功
        """
        try:
            if direction == 'down':
                for _ in range(amount):
                    pyautogui.press('pagedown')
                    time.sleep(0.1)
            elif direction == 'up':
                for _ in range(amount):
                    pyautogui.press('pageup')
                    time.sleep(0.1)
            elif direction == 'top':
                pyautogui.press('home')
            elif direction == 'bottom':
                pyautogui.press('end')
            
            print(f"✅ 已滚动页面：{direction}")
            return True
        except Exception as e:
            print(f"❌ 滚动失败：{e}")
            return False
    
    def focus_address_bar(self) -> bool:
        """
        聚焦地址栏
        
        Returns:
            bool: 是否成功
        """
        try:
            pyautogui.hotkey('ctrl', 'l')
            print("✅ 已聚焦地址栏")
            return True
        except Exception as e:
            print(f"❌ 聚焦地址栏失败：{e}")
            return False
    
    def search(self, query: str, search_engine: str = 'baidu') -> bool:
        """
        搜索
        
        Args:
            query: 搜索关键词
            search_engine: 搜索引擎（baidu/google/bing）
        
        Returns:
            bool: 是否成功
        """
        try:
            # 聚焦地址栏
            self.focus_address_bar()
            time.sleep(0.5)
            
            # 构建搜索 URL
            engines = {
                'baidu': f'https://www.baidu.com/s?wd={query}',
                'google': f'https://www.google.com/search?q={query}',
                'bing': f'https://www.bing.com/search?q={query}'
            }
            
            url = engines.get(search_engine, f'https://www.baidu.com/s?wd={query}')
            
            # 输入 URL
            pyautogui.typewrite(url, interval=0.05)
            time.sleep(0.5)
            
            # 回车搜索
            pyautogui.press('enter')
            time.sleep(2)
            
            print(f"✅ 已搜索：{query} ({search_engine})")
            return True
        except Exception as e:
            print(f"❌ 搜索失败：{e}")
            return False
    
    def find_in_page(self, text: str) -> bool:
        """
        在页面内查找
        
        Args:
            text: 查找文本
        
        Returns:
            bool: 是否成功
        """
        try:
            # Ctrl+F 打开查找
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            # 输入查找内容
            pyautogui.typewrite(text, interval=0.05)
            time.sleep(1)
            
            print(f"✅ 已查找：{text}")
            return True
        except Exception as e:
            print(f"❌ 查找失败：{e}")
            return False
    
    def fill_form(self, fields: dict, submit: bool = False) -> bool:
        """
        填写表单
        
        Args:
            fields: 表单字段 {字段名：值}
            submit: 是否提交（按回车）
        
        Returns:
            bool: 是否成功
        """
        try:
            for field_name, value in fields.items():
                print(f"📝 填写字段：{field_name}")
                
                # 输入值
                pyautogui.typewrite(value, interval=0.05)
                time.sleep(0.3)
                
                # 按 Tab 到下一个字段
                pyautogui.press('tab')
                time.sleep(0.3)
            
            # 提交表单
            if submit:
                print("📤 提交表单")
                pyautogui.press('enter')
            
            print(f"✅ 已填写 {len(fields)} 个字段")
            return True
        except Exception as e:
            print(f"❌ 填写表单失败：{e}")
            return False
    
    def click_element(self, x: int, y: int, button: str = 'left') -> bool:
        """
        点击页面元素（通过坐标）
        
        Args:
            x: X 坐标
            y: Y 坐标
            button: 按钮（left/right/middle）
        
        Returns:
            bool: 是否成功
        """
        try:
            pyautogui.click(x, y, button=button)
            print(f"✅ 已点击：({x}, {y})")
            return True
        except Exception as e:
            print(f"❌ 点击失败：{e}")
            return False
    
    def get_shortcut(self, name: str) -> str:
        """
        获取快捷键
        
        Args:
            name: 快捷键名称
        
        Returns:
            str: 快捷键
        """
        return self.shortcuts.get(name, 'unknown')
    
    def press_shortcut(self, name: str) -> bool:
        """
        按快捷键
        
        Args:
            name: 快捷键名称
        
        Returns:
            bool: 是否成功
        """
        try:
            shortcut = self.shortcuts.get(name)
            if not shortcut:
                print(f"❌ 未知快捷键：{name}")
                return False
            
            # 解析快捷键
            keys = shortcut.split('+')
            if len(keys) > 1:
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(keys[0])
            
            print(f"✅ 已按快捷键：{name} ({shortcut})")
            return True
        except Exception as e:
            print(f"❌ 快捷键失败：{e}")
            return False
    
    def open_devtools(self) -> bool:
        """打开开发者工具"""
        return self.press_shortcut('devtools')
    
    def toggle_fullscreen(self) -> bool:
        """切换全屏"""
        return self.press_shortcut('fullscreen')
    
    def bookmark_page(self) -> bool:
        """添加书签"""
        return self.press_shortcut('bookmark')
    
    def open_history(self) -> bool:
        """打开历史记录"""
        return self.press_shortcut('history')
    
    def open_downloads(self) -> bool:
        """打开下载内容"""
        return self.press_shortcut('downloads')


# ==================== 快捷函数 ====================

_browser: Optional[BrowserController] = None

def _get_browser() -> BrowserController:
    global _browser
    if _browser is None:
        _browser = BrowserController()
    return _browser

def browser_open(browser: str = 'chrome'):
    """打开浏览器"""
    _get_browser().open_browser(browser)

def browser_navigate(url: str):
    """导航到 URL"""
    _get_browser().navigate_to(url)

def browser_new_tab(url: str = None):
    """新建标签页"""
    _get_browser().new_tab(url)

def browser_search(query: str, engine: str = 'baidu'):
    """搜索"""
    _get_browser().search(query, engine)

def browser_scroll(direction: str = 'down'):
    """滚动页面"""
    _get_browser().scroll_page(direction)

def browser_find(text: str):
    """页面内查找"""
    _get_browser().find_in_page(text)

def browser_refresh(hard: bool = False):
    """刷新页面"""
    _get_browser().refresh(hard)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("浏览器控制器测试")
    print("=" * 60)
    
    browser = BrowserController()
    
    # 测试 1：打开浏览器
    print("\n[测试 1] 打开 Chrome 浏览器")
    browser.open_browser('chrome')
    time.sleep(2)
    
    # 测试 2：导航到百度
    print("\n[测试 2] 导航到百度")
    browser.navigate_to('https://www.baidu.com')
    
    # 测试 3：新建标签页
    print("\n[测试 3] 新建标签页")
    browser.new_tab()
    time.sleep(1)
    
    # 测试 4：搜索
    print("\n[测试 4] 搜索测试")
    browser.search('AI 自动化测试', 'baidu')
    
    # 测试 5：滚动页面
    print("\n[测试 5] 滚动页面")
    browser.scroll_page('down', 3)
    
    # 测试 6：页面查找
    print("\n[测试 6] 页面查找")
    browser.find_in_page('AI')
    
    print("\n✅ 浏览器测试完成！")
