"""
OCR Static Desktop - 静态桌面 OCR 识别
针对桌面图标不怎么动的场景优化

策略：
1. 首次保存桌面截图作为参考图
2. 从参考图中识别文字和图标位置
3. 缓存识别结果
4. 定期更新参考图（如添加文件时）
5. 用完删除图片，保持干净
"""

from PIL import Image, ImageEnhance, ImageFilter
import os
import json
import time
from datetime import datetime
from typing import Optional, List, Dict
import pyautogui

# 尝试导入 PaddleOCR
try:
    from paddleocr import PaddleOCR
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("⚠️ PaddleOCR 未安装")


class StaticDesktopOCR:
    """
    静态桌面 OCR 识别器
    
    适用于桌面图标不常变化的场景
    """
    
    def __init__(self, 
                 cache_dir: str = './desktop_cache',
                 reference_image: str = 'desktop_reference.png',
                 cache_file: str = 'desktop_cache.json',
                 auto_check: bool = True,
                 check_interval: int = 60):
        """
        初始化
        
        Args:
            cache_dir: 缓存目录
            reference_image: 参考图片名称
            cache_file: 缓存文件名称
            auto_check: 是否自动检测变化
            check_interval: 检测间隔（秒），默认 60 秒
        """
        self.cache_dir = cache_dir
        self.reference_image_path = os.path.join(cache_dir, reference_image)
        self.cache_file_path = os.path.join(cache_dir, cache_file)
        self.auto_check = auto_check
        self.check_interval = check_interval
        self.last_check_time = 0
        self.change_count = 0
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
        
        # 缓存数据
        self.desktop_cache = {
            'items': [],  # 识别到的项目列表
            'last_update': None,
            'screenshot_path': None
        }
        
        # 加载缓存
        self._load_cache()
        
        # OCR 引擎
        self.ocr = None
        if HAS_OCR:
            try:
                self.ocr = PaddleOCR(lang='ch')
                print("✅ OCR 引擎已就绪")
            except Exception as e:
                print(f"⚠️ OCR 引擎初始化失败：{e}")
    
    def _load_cache(self):
        """加载缓存"""
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                    self.desktop_cache = json.load(f)
                print(f"✅ 已加载桌面缓存（{len(self.desktop_cache.get('items', []))} 个项目）")
            except Exception as e:
                print(f"⚠️ 加载缓存失败：{e}")
    
    def _save_cache(self):
        """保存缓存"""
        with open(self.cache_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.desktop_cache, f, ensure_ascii=False, indent=2)
        print(f"✅ 缓存已保存")
    
    def capture_desktop_reference(self, enhance: bool = True) -> str:
        """
        捕获桌面参考图
        
        Args:
            enhance: 是否图像增强
        
        Returns:
            图片路径
        """
        print("\n📸 正在捕获桌面参考图...")
        
        # 最小化所有窗口，显示桌面
        pyautogui.hotkey('win', 'd')
        time.sleep(1)
        
        # 截图
        screenshot = pyautogui.screenshot()
        
        # 图像增强
        if enhance:
            print("🎨 图像增强处理...")
            # 转灰度
            screenshot = screenshot.convert('L')
            # 提高对比度
            screenshot = ImageEnhance.Contrast(screenshot).enhance(1.5)
            # 提高亮度
            screenshot = ImageEnhance.Brightness(screenshot).enhance(1.2)
            # 锐化
            screenshot = ImageEnhance.Sharpness(screenshot).enhance(2.0)
            # 转回 RGB
            screenshot = screenshot.convert('RGB')
        
        # 保存参考图
        screenshot.save(self.reference_image_path, 'PNG')
        print(f"✅ 桌面参考图已保存：{self.reference_image_path}")
        
        # 更新缓存
        self.desktop_cache['screenshot_path'] = self.reference_image_path
        self.desktop_cache['last_update'] = datetime.now().isoformat()
        
        return self.reference_image_path
    
    def recognize_desktop(self, force_update: bool = False) -> List[Dict]:
        """
        识别桌面图标和文字
        
        Args:
            force_update: 是否强制更新参考图
        
        Returns:
            识别结果列表
        """
        # 检查是否需要更新
        if force_update or not os.path.exists(self.reference_image_path):
            print("📸 需要更新参考图...")
            self.capture_desktop_reference()
        
        # 检查缓存是否有效
        if self._is_cache_valid():
            print("✅ 使用缓存的识别结果")
            return self.desktop_cache.get('items', [])
        
        # OCR 识别
        if self.ocr is None:
            print("❌ OCR 引擎未就绪")
            return []
        
        print("\n🔍 正在识别桌面文字...")
        
        # 从参考图识别
        result = self.ocr.predict(self.reference_image_path)
        
        if not result or 'rec_texts' not in result:
            print("⚠️ 未识别到文字")
            return []
        
        # 整理识别结果
        items = []
        for i, text in enumerate(result.get('rec_texts', [])):
            # 获取文字位置（如果有）
            bbox = None
            if 'dt_boxes' in result and i < len(result['dt_boxes']):
                bbox = result['dt_boxes'][i].tolist()
            
            item = {
                'id': i,
                'text': text,
                'bbox': bbox,
                'type': self._guess_item_type(text),
                'confidence': result.get('rec_scores', [1.0] * len(result['rec_texts']))[i] 
                             if 'rec_scores' in result else 1.0
            }
            items.append(item)
        
        # 更新缓存
        self.desktop_cache['items'] = items
        self._save_cache()
        
        print(f"✅ 识别到 {len(items)} 个项目")
        
        return items
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.desktop_cache.get('items'):
            return False
        
        if not os.path.exists(self.reference_image_path):
            return False
        
        # 检查缓存时间（超过 24 小时建议更新）
        last_update = self.desktop_cache.get('last_update')
        if last_update:
            update_time = datetime.fromisoformat(last_update)
            hours_since_update = (datetime.now() - update_time).total_seconds() / 3600
            if hours_since_update > 24:
                print(f"⚠️ 缓存已超过 24 小时，建议更新")
                return False
        
        # 自动检测桌面变化
        if self.auto_check:
            changed = self._check_desktop_changed()
            if changed:
                print("🔍 检测到桌面有变化，自动更新中...")
                self.update_reference()
                return False
        
        return True
    
    def _check_desktop_changed(self, threshold: float = 0.02) -> bool:
        """
        检测桌面是否发生变化
        
        Args:
            threshold: 变化阈值（0-1），越小越敏感
        
        Returns:
            bool: 是否发生变化
        """
        # 检查距离上次检测的时间
        now = time.time()
        if now - self.last_check_time < self.check_interval:
            # 未到检测时间
            return False
        
        self.last_check_time = now
        
        try:
            # 截取当前桌面（最小化所有窗口）
            pyautogui.hotkey('win', 'd')
            time.sleep(0.5)
            
            current = pyautogui.screenshot()
            
            # 加载参考图
            if not os.path.exists(self.reference_image_path):
                return True
            
            reference = Image.open(self.reference_image_path)
            
            # 调整到相同尺寸
            if current.size != reference.size:
                current = current.resize(reference.size)
            
            # 转换为灰度图
            current = current.convert('L')
            reference = reference.convert('L')
            
            # 计算差异
            import numpy as np
            curr_array = np.array(current)
            ref_array = np.array(reference)
            
            diff = np.abs(curr_array.astype(float) - ref_array.astype(float))
            diff_ratio = np.mean(diff) / 255.0
            
            # 恢复桌面
            pyautogui.hotkey('win', 'd')
            
            # 判断是否超过阈值
            if diff_ratio > threshold:
                self.change_count += 1
                print(f"📊 桌面变化检测：{diff_ratio:.2%} (阈值：{threshold:.2%}) [变化次数：{self.change_count}]")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 变化检测失败：{e}")
            return False
    
    def _guess_item_type(self, text: str) -> str:
        """猜测项目类型"""
        text_lower = text.lower()
        
        # 文件类型判断
        if text_lower.endswith(('.txt', '.doc', '.docx', '.pdf')):
            return 'document'
        elif text_lower.endswith(('.jpg', '.png', '.gif', '.bmp')):
            return 'image'
        elif text_lower.endswith(('.exe', '.lnk')):
            return 'application'
        elif text_lower.endswith(('.zip', '.rar', '.7z')):
            return 'archive'
        elif '回收站' in text or 'Recycle' in text:
            return 'system'
        elif '此电脑' in text or '网络' in text:
            return 'system'
        else:
            return 'unknown'
    
    def find_item(self, keyword: str) -> Optional[Dict]:
        """
        查找项目
        
        Args:
            keyword: 关键词
        
        Returns:
            找到的项目，未找到返回 None
        """
        items = self.recognize_desktop()
        
        for item in items:
            if keyword.lower() in item['text'].lower():
                print(f"✅ 找到：{item['text']}")
                return item
        
        print(f"❌ 未找到包含\"{keyword}\"的项目")
        return None
    
    def get_item_position(self, keyword: str) -> Optional[tuple]:
        """
        获取项目位置（估算）
        
        Args:
            keyword: 关键词
        
        Returns:
            (x, y) 坐标，未找到返回 None
        """
        item = self.find_item(keyword)
        
        if item and item.get('bbox'):
            bbox = item['bbox']
            # 计算中心点
            x = int((bbox[0][0] + bbox[2][0]) / 2)
            y = int((bbox[0][1] + bbox[2][1]) / 2)
            return (x, y)
        
        return None
    
    def update_reference(self, delete_old: bool = True):
        """
        更新参考图
        
        Args:
            delete_old: 是否删除旧图片
        """
        print("\n🔄 更新桌面参考图...")
        
        # 删除旧图片
        if delete_old and os.path.exists(self.reference_image_path):
            os.remove(self.reference_image_path)
            print(f"🗑️ 已删除旧参考图")
        
        # 捕获新参考图
        self.capture_desktop_reference()
        
        # 清除旧缓存
        self.desktop_cache['items'] = []
        
        # 重新识别
        self.recognize_desktop()
        
        print(f"✅ 参考图已更新（变化次数：{self.change_count}）")
    
    def cleanup(self):
        """清理缓存文件"""
        print("\n🗑️ 清理缓存文件...")
        
        # 删除参考图
        if os.path.exists(self.reference_image_path):
            os.remove(self.reference_image_path)
            print(f"✅ 已删除：{self.reference_image_path}")
        
        # 保留缓存文件（下次可用）
        # 如果也要删除：
        # if os.path.exists(self.cache_file_path):
        #     os.remove(self.cache_file_path)
        #     print(f"✅ 已删除：{self.cache_file_path}")
    
    def print_items(self):
        """打印识别到的项目"""
        items = self.recognize_desktop()
        
        print("\n" + "=" * 60)
        print("📋 桌面项目列表")
        print("=" * 60)
        
        for item in items:
            icon = {
                'document': '📄',
                'image': '🖼️',
                'application': '📱',
                'archive': '📦',
                'system': '⚙️',
                'unknown': '📁'
            }.get(item.get('type', 'unknown'), '📁')
            
            print(f"{icon} {item['text']} ({item.get('confidence', 0):.2f})")
        
        print("=" * 60)
        print(f"共 {len(items)} 个项目")
        print("=" * 60)


# ==================== 快捷函数 ====================

_desktop_ocr: Optional[StaticDesktopOCR] = None

def _get_desktop_ocr() -> StaticDesktopOCR:
    global _desktop_ocr
    if _desktop_ocr is None:
        _desktop_ocr = StaticDesktopOCR()
    return _desktop_ocr

def desktop_init():
    """初始化桌面识别（捕获参考图 + 识别）"""
    ocr = _get_desktop_ocr()
    ocr.capture_desktop_reference()
    return ocr.recognize_desktop()

def desktop_find(keyword: str):
    """查找桌面项目"""
    return _get_desktop_ocr().find_item(keyword)

def desktop_update():
    """更新桌面参考图"""
    ocr = _get_desktop_ocr()
    ocr.update_reference()

def desktop_cleanup():
    """清理缓存文件"""
    _get_desktop_ocr().cleanup()


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("静态桌面 OCR 识别测试")
    print("=" * 60)
    
    # 创建识别器
    ocr = StaticDesktopOCR()
    
    print("\n[步骤 1] 捕获桌面参考图...")
    ocr.capture_desktop_reference()
    
    print("\n[步骤 2] 识别桌面项目...")
    items = ocr.recognize_desktop()
    
    print("\n[步骤 3] 打印项目列表...")
    ocr.print_items()
    
    print("\n[步骤 4] 查找测试...")
    item = ocr.find_item('测试')
    if item:
        print(f"找到：{item['text']}")
    
    print("\n[步骤 5] 清理缓存...")
    ocr.cleanup()
    
    print("\n✅ 测试完成！")
