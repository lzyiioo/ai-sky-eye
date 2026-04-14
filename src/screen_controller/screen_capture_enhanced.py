"""
Enhanced Screen Capture - 增强版屏幕捕获
提高屏幕识别率，让 AI 看得更清楚

功能：
- 高清截图（无损压缩）
- 多显示器支持
- 区域截图优化
- 图像增强（对比度/亮度）
- OCR 文字识别准备
- 屏幕变化检测
"""

import pyautogui
import mss
import mss.tools
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import time
import os
from typing import Optional, Tuple, List
import numpy as np

class EnhancedScreenCapture:
    """
    增强版屏幕捕获器
    
    提高屏幕识别率的功能：
    1. 高清截图 - 无损 PNG 格式
    2. 图像增强 - 提高对比度/亮度
    3. 多显示器 - 支持多屏捕获
    4. 区域优化 - 只捕获需要的区域
    5. 变化检测 - 检测屏幕变化
    """
    
    def __init__(self, quality: str = 'high'):
        """
        初始化
        
        Args:
            quality: 图片质量（low/medium/high/best）
        """
        self.quality = quality
        
        # 质量设置
        self.quality_settings = {
            'low': {'compress_level': 6, 'optimize': True},
            'medium': {'compress_level': 3, 'optimize': True},
            'high': {'compress_level': 1, 'optimize': True},
            'best': {'compress_level': 0, 'optimize': False}  # 无损
        }
        
        # MSS 截图工具
        self.sct = mss.mss()
        
        # 获取所有显示器
        self.monitors = self.sct.monitors
        
        # 上次截图（用于变化检测）
        self.last_screenshot = None
        self.last_screenshot_time = None
    
    def capture_full_screen(self, monitor: int = 1, 
                            enhance: bool = True,
                            save_path: Optional[str] = None) -> Image.Image:
        """
        捕获整个屏幕（高清）
        
        Args:
            monitor: 显示器编号（1=主显示器，0=所有显示器）
            enhance: 是否图像增强
            save_path: 保存路径（可选）
        
        Returns:
            PIL Image 对象
        """
        # 获取显示器信息
        if monitor >= len(self.monitors):
            monitor = 1
        
        monitor_info = self.monitors[monitor]
        
        # 高清截图（使用 MSS，比 pyautogui 更快更清晰）
        screenshot = self.sct.grab(monitor_info)
        
        # 转换为 PIL Image
        img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
        
        # 图像增强
        if enhance:
            img = self._enhance_image(img)
        
        # 保存
        if save_path:
            self._save_image(img, save_path)
        
        return img
    
    def capture_region(self, left: int, top: int, 
                       width: int, height: int,
                       enhance: bool = True,
                       save_path: Optional[str] = None) -> Image.Image:
        """
        捕获指定区域（高清）
        
        Args:
            left: 左边界
            top: 上边界
            width: 宽度
            height: 高度
            enhance: 是否图像增强
            save_path: 保存路径
        
        Returns:
            PIL Image 对象
        """
        # 定义区域
        region = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        
        # 高清截图
        screenshot = self.sct.grab(region)
        
        # 转换为 PIL Image
        img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
        
        # 图像增强
        if enhance:
            img = self._enhance_image(img)
        
        # 保存
        if save_path:
            self._save_image(img, save_path)
        
        return img
    
    def capture_all_monitors(self, enhance: bool = True) -> List[Image.Image]:
        """
        捕获所有显示器
        
        Args:
            enhance: 是否图像增强
        
        Returns:
            PIL Image 列表
        """
        images = []
        
        for i, monitor in enumerate(self.monitors[1:], start=1):
            img = self.capture_full_screen(monitor=i, enhance=enhance)
            images.append(img)
        
        return images
    
    def _enhance_image(self, img: Image.Image, 
                       contrast: float = 1.2,
                       brightness: float = 1.1,
                       sharpness: float = 1.3) -> Image.Image:
        """
        图像增强
        
        Args:
            img: PIL Image
            contrast: 对比度（1.0=原始，>1=增强）
            brightness: 亮度（1.0=原始，>1=增亮）
            sharpness: 锐度（1.0=原始，>1=锐化）
        
        Returns:
            增强后的 PIL Image
        """
        # 提高对比度（让文字更清晰）
        img = ImageEnhance.Contrast(img).enhance(contrast)
        
        # 提高亮度（让暗部更亮）
        img = ImageEnhance.Brightness(img).enhance(brightness)
        
        # 锐化（让边缘更清晰）
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
        
        return img
    
    def _save_image(self, img: Image.Image, save_path: str):
        """
        保存图片（高质量）
        
        Args:
            img: PIL Image
            save_path: 保存路径
        """
        settings = self.quality_settings.get(self.quality, self.quality_settings['high'])
        
        # 确保目录存在
        dir_path = os.path.dirname(save_path)
        if dir_path:  # 如果有目录路径
            os.makedirs(dir_path, exist_ok=True)
        
        # 保存为 PNG（无损格式）
        img.save(save_path, 'PNG', **settings)
        print(f"✅ 截图已保存：{save_path}")
    
    def capture_to_base64(self, monitor: int = 1, 
                          enhance: bool = True) -> str:
        """
        捕获屏幕并转换为 Base64
        
        Args:
            monitor: 显示器编号
            enhance: 是否图像增强
        
        Returns:
            Base64 字符串
        """
        img = self.capture_full_screen(monitor=monitor, enhance=enhance)
        
        # 转换为 Base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', compress_level=1)
        buffer.seek(0)
        
        base64_str = base64.b64encode(buffer.read()).decode('utf-8')
        
        return base64_str
    
    def has_screen_changed(self, threshold: float = 0.01) -> bool:
        """
        检测屏幕是否发生变化
        
        Args:
            threshold: 变化阈值（0-1，越小越敏感）
        
        Returns:
            bool: 是否发生变化
        """
        # 捕获当前屏幕
        current_img = self.capture_full_screen(enhance=False)
        current_array = np.array(current_img)
        
        # 如果有上次的截图
        if self.last_screenshot is not None:
            # 计算差异
            diff = np.abs(current_array.astype(float) - self.last_screenshot.astype(float))
            diff_ratio = np.mean(diff) / 255.0
            
            # 更新上次截图
            self.last_screenshot = current_array
            self.last_screenshot_time = time.time()
            
            return diff_ratio > threshold
        
        # 第一次截图
        self.last_screenshot = current_array
        self.last_screenshot_time = time.time()
        return True
    
    def capture_until_stable(self, timeout: float = 5.0, 
                             interval: float = 0.5) -> Image.Image:
        """
        捕获屏幕直到稳定（无变化）
        
        适用于等待页面加载完成
        
        Args:
            timeout: 超时时间（秒）
            interval: 检测间隔（秒）
        
        Returns:
            稳定后的屏幕截图
        """
        start_time = time.time()
        stable_count = 0
        required_stable = 2  # 需要连续 2 次无变化
        
        while time.time() - start_time < timeout:
            # 检测变化
            changed = self.has_screen_changed()
            
            if not changed:
                stable_count += 1
                if stable_count >= required_stable:
                    print("✅ 屏幕已稳定")
                    return self.capture_full_screen(enhance=True)
            else:
                stable_count = 0
            
            time.sleep(interval)
        
        print("⚠️ 等待超时，返回当前屏幕")
        return self.capture_full_screen(enhance=True)
    
    def capture_with_ocr_prepare(self, region: Optional[Tuple] = None,
                                 save_path: Optional[str] = None) -> Image.Image:
        """
        捕获屏幕并为 OCR 优化
        
        优化项：
        - 高对比度（黑白分明）
        - 锐化处理（文字边缘清晰）
        - 去噪（减少干扰）
        
        Args:
            region: 区域 (left, top, width, height)
            save_path: 保存路径
        
        Returns:
            优化后的 PIL Image
        """
        # 捕获屏幕
        if region:
            img = self.capture_region(*region, enhance=False)
        else:
            img = self.capture_full_screen(enhance=False)
        
        # OCR 优化处理
        # 1. 转换为灰度图
        img = img.convert('L')
        
        # 2. 提高对比度（更强）
        img = ImageEnhance.Contrast(img).enhance(1.5)
        
        # 3. 提高亮度
        img = ImageEnhance.Brightness(img).enhance(1.2)
        
        # 4. 锐化
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        
        # 5. 去噪（中值滤波）
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        # 保存
        if save_path:
            self._save_image(img, save_path)
        
        return img
    
    def get_screen_info(self) -> dict:
        """
        获取屏幕信息
        
        Returns:
            屏幕信息字典
        """
        info = {
            'monitor_count': len(self.monitors) - 1,  # 排除主区域
            'monitors': [],
            'primary_resolution': None
        }
        
        for i, monitor in enumerate(self.monitors[1:], start=1):
            monitor_info = {
                'id': i,
                'width': monitor['width'],
                'height': monitor['height'],
                'left': monitor['left'],
                'top': monitor['top']
            }
            info['monitors'].append(monitor_info)
        
        if info['monitors']:
            info['primary_resolution'] = f"{info['monitors'][0]['width']}x{info['monitors'][0]['height']}"
        
        return info
    
    def print_screen_info(self):
        """打印屏幕信息"""
        info = self.get_screen_info()
        
        print("=" * 60)
        print("📺 屏幕信息")
        print("=" * 60)
        print(f"显示器数量：{info['monitor_count']}")
        
        for monitor in info['monitors']:
            print(f"\n显示器 {monitor['id']}:")
            print(f"  分辨率：{monitor['width']}x{monitor['height']}")
            print(f"  位置：({monitor['left']}, {monitor['top']})")
        
        print("=" * 60)


# ==================== 快捷函数 ====================

_capturer: Optional[EnhancedScreenCapture] = None

def _get_capturer(quality: str = 'high') -> EnhancedScreenCapture:
    global _capturer
    if _capturer is None:
        _capturer = EnhancedScreenCapture(quality=quality)
    return _capturer

def capture_screen_hd(monitor: int = 1, save_path: Optional[str] = None):
    """高清截图"""
    return _get_capturer().capture_full_screen(monitor=monitor, save_path=save_path)

def capture_region_hd(left: int, top: int, width: int, height: int,
                      save_path: Optional[str] = None):
    """高清区域截图"""
    return _get_capturer().capture_region(left, top, width, height, save_path=save_path)

def capture_for_ocr(region: Optional[Tuple] = None, save_path: Optional[str] = None):
    """为 OCR 优化的截图"""
    return _get_capturer().capture_with_ocr_prepare(region=region, save_path=save_path)

def has_screen_changed():
    """检测屏幕变化"""
    return _get_capturer().has_screen_changed()

def get_screen_info():
    """获取屏幕信息"""
    return _get_capturer().get_screen_info()


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("增强版屏幕捕获测试")
    print("=" * 60)
    
    # 创建捕获器
    capturer = EnhancedScreenCapture(quality='best')
    
    # 测试 1：获取屏幕信息
    print("\n[测试 1] 获取屏幕信息")
    capturer.print_screen_info()
    
    # 测试 2：高清全屏截图
    print("\n[测试 2] 高清全屏截图")
    img = capturer.capture_full_screen(monitor=1, enhance=True, 
                                        save_path='test_hd_screenshot.png')
    print(f"截图尺寸：{img.size}")
    
    # 测试 3：区域截图
    print("\n[测试 3] 区域截图")
    img = capturer.capture_region(0, 0, 800, 600, enhance=True,
                                   save_path='test_region.png')
    print(f"区域截图尺寸：{img.size}")
    
    # 测试 4：OCR 优化截图
    print("\n[测试 4] OCR 优化截图")
    img = capturer.capture_with_ocr_prepare(save_path='test_ocr.png')
    print(f"OCR 优化截图尺寸：{img.size}")
    
    # 测试 5：屏幕变化检测
    print("\n[测试 5] 屏幕变化检测")
    print("等待 5 秒，检测屏幕变化...")
    for i in range(5):
        changed = capturer.has_screen_changed()
        print(f"  第{i+1}次检测：{'有变化' if changed else '无变化'}")
        time.sleep(1)
    
    print("\n✅ 测试完成！")
