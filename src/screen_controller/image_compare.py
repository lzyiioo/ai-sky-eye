"""
Image Compare - 图像对比系统
检测屏幕变化、定位差异、触发自动操作
"""

import time
import logging
from typing import Optional, List, Tuple, Callable, Dict, Any
from dataclasses import dataclass
from PIL import Image, ImageChops, ImageDraw
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from .enhanced_screenshot import capture_screen

logger = logging.getLogger(__name__)


@dataclass
class ChangeRegion:
    """变化区域"""
    x: int
    y: int
    width: int
    height: int
    change_ratio: float


@dataclass
class CompareResult:
    """对比结果"""
    changed: bool
    similarity: float
    diff_regions: List[ChangeRegion]
    diff_image: Optional[Image.Image] = None
    message: str = ""


class ImageComparator:
    """图像对比器"""
    
    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
        self.baseline: Optional[Image.Image] = None
        self.history: List[Image.Image] = []
        self.max_history = 10
    
    def set_baseline(self, image: Optional[Image.Image] = None):
        """设置基准图"""
        if image is None:
            image = capture_screen()
        self.baseline = image.copy()
        print(f"📸 基准图已设置: {image.size}")
    
    def calculate_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """计算相似度"""
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        
        if img1.mode != 'L':
            img1 = img1.convert('L')
        if img2.mode != 'L':
            img2 = img2.convert('L')
        
        # 尝试 SSIM
        try:
            from skimage.metrics import structural_similarity as ssim
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            score, _ = ssim(arr1, arr2, full=True)
            return score
        except:
            pass
        
        # 像素差异
        diff = ImageChops.difference(img1, img2)
        if diff.getbbox() is None:
            return 1.0
        
        diff_array = np.array(diff)
        non_zero = np.count_nonzero(diff_array)
        total = diff_array.size
        
        return 1 - (non_zero / total)
    
    def compare(self, new_image: Optional[Image.Image] = None) -> CompareResult:
        """与基准图对比"""
        if self.baseline is None:
            self.set_baseline()
        
        if new_image is None:
            new_image = capture_screen()
        
        similarity = self.calculate_similarity(self.baseline, new_image)
        changed = similarity < self.threshold
        
        diff_regions = []
        diff_image = None
        
        if changed:
            diff_regions = self._find_diff_regions(self.baseline, new_image)
            diff_image = self._generate_diff_image(self.baseline, new_image)
        
        self.history.append(new_image)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return CompareResult(
            changed=changed,
            similarity=similarity,
            diff_regions=diff_regions,
            diff_image=diff_image,
            message=f"{'检测到变化' if changed else '无变化'} (相似度: {similarity:.3f})"
        )
    
    def _find_diff_regions(self, img1: Image.Image, img2: Image.Image) -> List[ChangeRegion]:
        """找出变化区域"""
        regions = []
        
        if HAS_CV2:
            arr1 = np.array(img1.convert('L'))
            arr2 = np.array(img2.convert('L'))
            
            diff = cv2.absdiff(arr1, arr2)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w >= 50 and h >= 50:
                    regions.append(ChangeRegion(x, y, w, h, 1.0))
        
        return sorted(regions, key=lambda r: r.change_ratio, reverse=True)[:10]
    
    def _generate_diff_image(self, img1: Image.Image, img2: Image.Image) -> Image.Image:
        """生成差异图"""
        if img1.mode != 'RGB':
            img1 = img1.convert('RGB')
        if img2.mode != 'RGB':
            img2 = img2.convert('RGB')
        
        result = img2.copy()
        draw = ImageDraw.Draw(result)
        
        regions = self._find_diff_regions(img1, img2)
        for region in regions:
            draw.rectangle(
                [region.x, region.y, region.x + region.width, region.y + region.height],
                outline="red",
                width=3
            )
            # 中心点
            cx = region.x + region.width // 2
            cy = region.y + region.height // 2
            draw.ellipse([cx-5, cy-5, cx+5, cy+5], fill="red")
        
        return result
    
    def watch(self, on_change: Callable[[CompareResult], None],
              interval: float = 1.0, duration: Optional[float] = None):
        """监控屏幕变化"""
        print(f"👁️ 开始监控屏幕 (间隔: {interval}s)")
        start_time = time.time()
        
        while True:
            result = self.compare()
            
            if result.changed:
                print(f"   🔔 检测到 {len(result.diff_regions)} 个变化区域")
                on_change(result)
            
            if duration and time.time() - start_time > duration:
                print("   ⏹️ 监控结束")
                break
            
            time.sleep(interval)
    
    def reset(self):
        """重置"""
        self.baseline = None
        self.history.clear()
        print("🔄 已重置")


# 快捷函数
_comparator: Optional[ImageComparator] = None

def get_comparator(threshold: float = 0.95) -> ImageComparator:
    global _comparator
    if _comparator is None:
        _comparator = ImageComparator(threshold)
    return _comparator

def watch_screen(on_change: Callable, interval: float = 1.0):
    """快捷：监控屏幕"""
    get_comparator().watch(on_change, interval)

def has_screen_changed(threshold: float = 0.95) -> bool:
    """快捷：检查屏幕是否变化"""
    result = get_comparator(threshold).compare()
    return result.changed


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 图像对比测试")
    print("=" * 60)
    
    comp = ImageComparator()
    
    print("\n[测试 1] 设置基准图")
    comp.set_baseline()
    
    print("\n[测试 2] 对比")
    input("按回车截图对比...")
    result = comp.compare()
    print(f"变化: {result.changed}, 相似度: {result.similarity:.3f}")
    
    if result.diff_image:
        result.diff_image.save("diff_test.png")
        print("差异图已保存: diff_test.png")
