"""
OCR Controller - OCR 识别控制器
支持内存处理和文档保存两种模式
"""

from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import time
from typing import Optional, Tuple, List
from datetime import datetime

# 尝试导入 OCR 引擎
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    print("⚠️ pytesseract 未安装，OCR 功能受限")

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False

from .screen_capture_enhanced import EnhancedScreenCapture


class OCRController:
    """
    OCR 识别控制器
    
    支持两种模式：
    - 内存模式（默认）：快速、无留痕
    - 文档模式：可保存、可调试
    """
    
    def __init__(self, 
                 save_mode: str = 'memory',
                 save_dir: Optional[str] = None,
                 ocr_engine: str = 'auto'):
        """
        初始化 OCR 控制器
        
        Args:
            save_mode: 保存模式（'memory'=内存，'disk'=文档）
            save_dir: 文档保存目录
            ocr_engine: OCR 引擎（'auto'/'tesseract'/'easyocr'/'paddleocr'）
        """
        self.save_mode = save_mode
        self.save_dir = save_dir or './ocr_results'
        self.ocr_engine_name = ocr_engine
        
        # 屏幕捕获器
        self.capturer = EnhancedScreenCapture(quality='best')
        
        # 初始化 OCR 引擎
        self.ocr = self._init_ocr_engine(ocr_engine)
        
        # 统计信息
        self.stats = {
            'total_calls': 0,
            'success_count': 0,
            'fail_count': 0,
            'total_time': 0
        }
    
    def _init_ocr_engine(self, engine_name: str):
        """初始化 OCR 引擎"""
        
        # 自动选择
        if engine_name == 'auto':
            if HAS_PADDLEOCR:
                print("✅ 使用 PaddleOCR（中文识别最佳）")
                return PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            elif HAS_EASYOCR:
                print("✅ 使用 EasyOCR")
                return easyocr.Reader(['ch_sim', 'en'])
            elif HAS_TESSERACT:
                print("✅ 使用 Tesseract")
                return 'tesseract'
            else:
                print("⚠️ 无可用 OCR 引擎，请安装至少一个：")
                print("   pip install paddlepaddle paddleocr")
                print("   或 pip install easyocr")
                print("   或 pip install pytesseract")
                return None
        
        # 指定引擎
        elif engine_name == 'paddleocr':
            if HAS_PADDLEOCR:
                return PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            else:
                print("⚠️ PaddleOCR 未安装")
                return None
        
        elif engine_name == 'easyocr':
            if HAS_EASYOCR:
                return easyocr.Reader(['ch_sim', 'en'])
            else:
                print("⚠️ EasyOCR 未安装")
                return None
        
        elif engine_name == 'tesseract':
            if HAS_TESSERACT:
                return 'tesseract'
            else:
                print("⚠️ Tesseract 未安装")
                return None
        
        return None
    
    def recognize(self, 
                  region: Optional[Tuple] = None,
                  save_mode: Optional[str] = None,
                  preprocess: bool = True,
                  return_details: bool = False) -> str:
        """
        OCR 识别
        
        Args:
            region: 识别区域 (left, top, width, height)，None=全屏
            save_mode: 临时覆盖保存模式（'memory'/'disk'）
            preprocess: 是否预处理图像
            return_details: 是否返回详细信息
        
        Returns:
            str: 识别的文字内容
        """
        start_time = time.time()
        self.stats['total_calls'] += 1
        
        # 确定保存模式
        current_save_mode = save_mode or self.save_mode
        
        try:
            # 1. 捕获屏幕（内存）
            if region:
                img = self.capturer.capture_region(*region, enhance=False)
            else:
                img = self.capturer.capture_full_screen(enhance=False)
            
            # 2. 图像预处理（内存）
            if preprocess:
                img = self._preprocess_for_ocr(img)
            
            # 3. 调试模式：保存中间结果
            if current_save_mode == 'disk':
                self._save_debug_files(img)
            
            # 4. OCR 识别（内存）
            text = self._recognize_image(img)
            
            # 5. 保存结果（文档模式）
            if current_save_mode == 'disk':
                self._save_result(text)
            
            # 统计
            elapsed = time.time() - start_time
            self.stats['success_count'] += 1
            self.stats['total_time'] += elapsed
            
            if return_details:
                return {
                    'text': text,
                    'success': True,
                    'time': elapsed,
                    'mode': current_save_mode,
                    'region': region
                }
            
            return text
        
        except Exception as e:
            self.stats['fail_count'] += 1
            error_text = f"OCR 识别失败：{str(e)}"
            
            if return_details:
                return {
                    'text': error_text,
                    'success': False,
                    'error': str(e),
                    'time': time.time() - start_time
                }
            
            return error_text
    
    def _preprocess_for_ocr(self, img: Image.Image) -> Image.Image:
        """
        OCR 图像预处理（内存）
        
        Args:
            img: PIL Image
        
        Returns:
            预处理后的 PIL Image
        """
        # 1. 转灰度图
        img = img.convert('L')
        
        # 2. 提高对比度（1.5 倍）
        img = ImageEnhance.Contrast(img).enhance(1.5)
        
        # 3. 提高亮度（1.2 倍）
        img = ImageEnhance.Brightness(img).enhance(1.2)
        
        # 4. 锐化（2.0 倍）
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        
        # 5. 去噪
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img
    
    def _recognize_image(self, img: Image.Image) -> str:
        """
        识别图像中的文字（内存）
        
        Args:
            img: PIL Image
        
        Returns:
            str: 识别的文字
        """
        if self.ocr is None:
            return "❌ 未安装 OCR 引擎"
        
        # PaddleOCR
        if isinstance(self.ocr, type(PaddleOCR(lang='ch'))):
            result = self.ocr.predict(img)
            if result and 'rec_texts' in result:
                text = '\n'.join(result['rec_texts'])
                return text
            return ""
        
        # EasyOCR
        elif isinstance(self.ocr, easyocr.Reader):
            result = self.ocr.readtext(img)
            text = '\n'.join([item[1] for item in result])
            return text
        
        # Tesseract
        elif self.ocr == 'tesseract':
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return text
        
        return "❌ 未知 OCR 引擎"
    
    def _save_debug_files(self, img: Image.Image):
        """保存调试文件（文档模式）"""
        os.makedirs(self.save_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存预处理后的图像
        img.save(f'{self.save_dir}/ocr_{timestamp}_processed.png', 'PNG')
    
    def _save_result(self, text: str):
        """保存识别结果（文档模式）"""
        os.makedirs(self.save_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存文字结果
        with open(f'{self.save_dir}/ocr_{timestamp}_result.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        # 保存统计信息
        with open(f'{self.save_dir}/ocr_stats.txt', 'w', encoding='utf-8') as f:
            f.write(f"总调用：{self.stats['total_calls']}\n")
            f.write(f"成功：{self.stats['success_count']}\n")
            f.write(f"失败：{self.stats['fail_count']}\n")
            f.write(f"总耗时：{self.stats['total_time']:.2f}秒\n")
            f.write(f"平均耗时：{self.stats['total_time']/max(1, self.stats['total_calls']):.2f}秒/次\n")
    
    def recognize_quick(self, region: Optional[Tuple] = None) -> str:
        """
        快速识别（纯内存，不保存）
        
        Args:
            region: 识别区域
        
        Returns:
            str: 识别的文字
        """
        return self.recognize(region=region, save_mode='memory', preprocess=True)
    
    def recognize_and_save(self, region: Optional[Tuple] = None) -> str:
        """
        识别并保存（文档模式）
        
        Args:
            region: 识别区域
        
        Returns:
            str: 识别的文字
        """
        return self.recognize(region=region, save_mode='disk', preprocess=True)
    
    def recognize_with_details(self, region: Optional[Tuple] = None) -> dict:
        """
        识别并返回详细信息
        
        Args:
            region: 识别区域
        
        Returns:
            dict: {text, success, time, mode, region}
        """
        return self.recognize(region=region, return_details=True)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        avg_time = self.stats['total_time'] / max(1, self.stats['total_calls'])
        success_rate = self.stats['success_count'] / max(1, self.stats['total_calls']) * 100
        
        return {
            **self.stats,
            'average_time': f"{avg_time:.2f}秒/次",
            'success_rate': f"{success_rate:.1f}%"
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        
        print("=" * 60)
        print("📊 OCR 统计信息")
        print("=" * 60)
        print(f"总调用：{stats['total_calls']} 次")
        print(f"成功：{stats['success_count']} 次")
        print(f"失败：{stats['fail_count']} 次")
        print(f"成功率：{stats['success_rate']}")
        print(f"平均耗时：{stats['average_time']}")
        print(f"总耗时：{stats['total_time']:.2f}秒")
        print("=" * 60)
    
    def cleanup_old_files(self, days: int = 7):
        """清理旧文件"""
        import shutil
        
        if not os.path.exists(self.save_dir):
            return
        
        cutoff = time.time() - (days * 86400)
        
        for filename in os.listdir(self.save_dir):
            filepath = os.path.join(self.save_dir, filename)
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                print(f"🗑️ 已删除：{filename}")


# ==================== 快捷函数 ====================

_ocr: Optional[OCRController] = None

def _get_ocr() -> OCRController:
    global _ocr
    if _ocr is None:
        _ocr = OCRController(save_mode='memory')
    return _ocr

def ocr_quick(region: Optional[Tuple] = None) -> str:
    """快速识别（内存）"""
    return _get_ocr().recognize_quick(region)

def ocr_and_save(region: Optional[Tuple] = None) -> str:
    """识别并保存（文档）"""
    return _get_ocr().recognize_and_save(region)

def ocr_with_details(region: Optional[Tuple] = None) -> dict:
    """识别并返回详情"""
    return _get_ocr().recognize_with_details(region)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("OCR 控制器测试")
    print("=" * 60)
    
    # 创建控制器（内存模式）
    ocr = OCRController(save_mode='memory')
    
    print("\n[测试 1] 快速识别（内存模式）")
    text = ocr.recognize_quick()
    print(f"识别结果：{text[:100]}...")
    
    print("\n[测试 2] 识别并保存（文档模式）")
    text = ocr.recognize_and_save()
    print(f"识别结果：{text[:100]}...")
    
    print("\n[测试 3] 查看统计信息")
    ocr.print_stats()
    
    print("\n✅ 测试完成！")
