"""
Enhanced OCR - OCR 增强系统
支持多语言、多引擎、智能区域识别
"""

import logging
import re
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import io

# OCR 引擎
try:
    from paddleocr import PaddleOCR
    HAS_PADDLE = True
except ImportError:
    HAS_PADDLE = False

try:
    import easyocr
    HAS_EASY = True
except ImportError:
    HAS_EASY = False

try:
    import pytesseract
    HAS_TESS = True
except ImportError:
    HAS_TESS = False

from .enhanced_screenshot import capture_screen

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """OCR 识别结果"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    language: str = ""


class EnhancedOCR:
    """
    增强 OCR 系统
    
    特性：
    - 多引擎支持（PaddleOCR / EasyOCR / Tesseract）
    - 多语言支持（中文、英文、日文等）
    - 智能图像预处理
    - 区域识别
    - 表格识别
    """
    
    # 支持的语言
    LANGUAGES = {
        "ch": "中文",
        "en": "英文",
        "japan": "日文",
        "korean": "韩文",
        "french": "法文",
        "german": "德文",
        "spanish": "西班牙文"
    }
    
    def __init__(self, engine: str = "auto", lang: str = "ch"):
        """
        初始化 OCR

        Args:
            engine: OCR 引擎（auto/paddle/easy/tesseract）
            lang: 语言代码
        """
        self.engine_name = engine
        self.lang = lang
        self._engines = {}
        self._engine_instance = None  # 缓存的引擎实例

        # 自动选择引擎
        if engine == "auto":
            if HAS_PADDLE:
                self.engine_name = "paddle"
            elif HAS_EASY:
                self.engine_name = "easy"
            elif HAS_TESS:
                self.engine_name = "tesseract"
            else:
                raise RuntimeError("No OCR engine available")

        # 使用性能优化模块的 OCR 缓存
        try:
            from .performance import OCREngineCache
            self._engine_instance = OCREngineCache.get_engine(self.engine_name, self.lang)
        except ImportError:
            self._engine_instance = None

        self._init_engine()

    def _init_engine(self):
        """初始化 OCR 引擎 - 使用缓存"""
        if self._engine_instance is not None:
            # 已通过缓存获取引擎
            return

        # 回退到直接创建
        if self.engine_name == "paddle" and HAS_PADDLE:
            if "paddle" not in self._engines:
                self._engines["paddle"] = PaddleOCR(
                    use_angle_cls=True,
                    lang=self.lang,
                    show_log=False
                )

        elif self.engine_name == "easy" and HAS_EASY:
            if "easy" not in self._engines:
                lang_list = [self.lang] if self.lang != "ch" else ['ch_sim', 'en']
                self._engines["easy"] = easyocr.Reader(lang_list)

        elif self.engine_name == "tesseract" and HAS_TESS:
            # Tesseract 配置
            pass
    
    def preprocess(self, img: Image.Image) -> Image.Image:
        """
        图像预处理
        
        优化步骤：
        1. 转灰度
        2. 提高对比度
        3. 锐化
        4. 去噪
        """
        # 转灰度
        if img.mode != 'L':
            img = img.convert('L')
        
        # 自适应对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # 锐化
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # 二值化（提高文字清晰度）
        img = img.point(lambda x: 0 if x < 128 else 255, '1')
        
        return img.convert('L')
    
    def recognize(
        self,
        image: Optional[Image.Image] = None,
        region: Optional[Tuple] = None,
        preprocess: bool = True
    ) -> List[OCRResult]:
        """
        识别图片中的文字
        
        Args:
            image: PIL Image（None=截图）
            region: 识别区域
            preprocess: 是否预处理
            
        Returns:
            OCRResult 列表
        """
        # 获取图片
        if image is None:
            image = capture_screen(region=region)
        
        # 预处理
        if preprocess:
            image = self.preprocess(image)
        
        # 执行 OCR
        results = []
        
        if self.engine_name == "paddle" and HAS_PADDLE:
            results = self._recognize_paddle(image)
        elif self.engine_name == "easy" and HAS_EASY:
            results = self._recognize_easy(image)
        elif self.engine_name == "tesseract" and HAS_TESS:
            results = self._recognize_tesseract(image)
        
        return results
    
    def _recognize_paddle(self, img: Image.Image) -> List[OCRResult]:
        """PaddleOCR 识别"""
        engine = self._engines.get("paddle")
        if not engine:
            return []
        
        result = engine.ocr(np.array(img), cls=True)
        results = []
        
        for line in result[0]:
            if line:
                bbox = line[0]
                text = line[1][0]
                conf = line[1][1]
                
                # 计算 bbox
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
                
                results.append(OCRResult(
                    text=text,
                    confidence=conf,
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    language=self.lang
                ))
        
        return results
    
    def _recognize_easy(self, img: Image.Image) -> List[OCRResult]:
        """EasyOCR 识别"""
        engine = self._engines.get("easy")
        if not engine:
            return []
        
        result = engine.readtext(np.array(img))
        results = []
        
        for item in result:
            bbox = item[0]
            text = item[1]
            conf = item[2]
            
            x1 = min(p[0] for p in bbox)
            y1 = min(p[1] for p in bbox)
            x2 = max(p[0] for p in bbox)
            y2 = max(p[1] for p in bbox)
            
            results.append(OCRResult(
                text=text,
                confidence=conf,
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                language=self.lang
            ))
        
        return results
    
    def _recognize_tesseract(self, img: Image.Image) -> List[OCRResult]:
        """Tesseract 识别"""
        if not HAS_TESS:
            return []
        
        text = pytesseract.image_to_string(img, lang=self.lang)
        
        # Tesseract 不提供置信度，默认返回一个结果
        return [OCRResult(text=text.strip(), confidence=0.8, bbox=(0, 0, 0, 0))]
    
    def find_text(self, keyword: str, image: Optional[Image.Image] = None) -> List[OCRResult]:
        """
        查找包含关键词的文字
        
        Args:
            keyword: 关键词
            image: 图片
            
        Returns:
            匹配的结果
        """
        results = self.recognize(image)
        keyword_lower = keyword.lower()
        
        return [r for r in results if keyword_lower in r.text.lower()]
    
    def extract_all_text(self, image: Optional[Image.Image] = None) -> str:
        """
        提取所有文字
        
        Returns:
            合并后的文字
        """
        results = self.recognize(image)
        return "\n".join([r.text for r in results])
    
    def switch_language(self, lang: str):
        """
        切换语言
        
        Args:
            lang: 语言代码（ch/en/japan等）
        """
        if lang in self.LANGUAGES:
            self.lang = lang
            self._init_engine()  # 重新初始化
            print(f"🌐 OCR 语言已切换为: {self.LANGUAGES[lang]}")
        else:
            print(f"⚠️ 不支持的语言: {lang}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言"""
        return self.LANGUAGES.copy()


# ==================== 快捷函数 ====================

_ocr: Optional[EnhancedOCR] = None

def get_ocr(engine: str = "auto", lang: str