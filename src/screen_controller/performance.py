"""
Performance Optimization Module - 性能优化模块
提供：单例模式、缓存机制、延迟加载
"""

import logging
import threading
from functools import lru_cache
from typing import Optional, Any, Dict, Callable
from PIL import Image

logger = logging.getLogger(__name__)


# ==================== 单例模式 ====================

class Singleton:
    """线程安全的单例基类"""
    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonMeta(type):
    """线程安全单例元类"""
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# ==================== OCR 引擎单例 ====================

class OCREngineCache:
    """
    OCR 引擎缓存 - 避免重复初始化

    用法:
        from screen_controller.performance import OCREngineCache

        # 获取单例 OCR 引擎
        ocr = OCREngineCache.get_engine("paddle", "ch")
        result = ocr.ocr(image)
    """

    _engines: Dict[str, Any] = {}
    _lock = threading.Lock()

    @classmethod
    def get_engine(cls, engine: str = "auto", lang: str = "ch") -> Optional[Any]:
        """
        获取 OCR 引擎单例

        Args:
            engine: 引擎类型 (auto/paddle/easy/tesseract)
            lang: 语言

        Returns:
            OCR 引擎实例
        """
        key = f"{engine}:{lang}"

        if key not in cls._engines:
            with cls._lock:
                if key not in cls._engines:
                    cls._engines[key] = cls._create_engine(engine, lang)

        return cls._engines.get(key)

    @classmethod
    def _create_engine(cls, engine: str, lang: str) -> Optional[Any]:
        """创建 OCR 引擎"""
        try:
            if engine == "auto":
                # 自动选择
                try:
                    from paddleocr import PaddleOCR
                    return PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
                except ImportError:
                    pass

                try:
                    import easyocr
                    lang_list = [lang] if lang != "ch" else ['ch_sim', 'en']
                    return easyocr.Reader(lang_list)
                except ImportError:
                    pass

                try:
                    import pytesseract
                    return pytesseract
                except ImportError:
                    return None

            elif engine == "paddle":
                from paddleocr import PaddleOCR
                return PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)

            elif engine == "easy":
                import easyocr
                lang_list = [lang] if lang != "ch" else ['ch_sim', 'en']
                return easyocr.Reader(lang_list)

            elif engine == "tesseract":
                import pytesseract
                return pytesseract

        except Exception as e:
            logger.warning(f"Failed to create OCR engine {engine}: {e}")

        return None

    @classmethod
    def clear(cls):
        """清理所有引擎缓存"""
        with cls._lock:
            cls._engines.clear()

    @classmethod
    def preload(cls, engines: list = None):
        """
        预加载 OCR 引擎

        Args:
            engines: 要预加载的引擎列表 [(engine, lang), ...]
        """
        if engines is None:
            engines = [("paddle", "ch"), ("easy", "ch")]

        for engine, lang in engines:
            cls.get_engine(engine, lang)


# ==================== 截图缓存 ====================

class ScreenshotCache:
    """
    截图缓存 - 避免重复截图

    用法:
        from screen_controller.performance import ScreenshotCache

        # 获取缓存的截图
        img = ScreenshotCache.get("window_name")

        # 清除缓存
        ScreenshotCache.invalidate("window_name")
    """

    _cache: Dict[str, Image.Image] = {}
    _timestamps: Dict[str, float] = {}
    _lock = threading.Lock()
    _default_ttl = 1.0  # 缓存有效期(秒)

    @classmethod
    def get(cls, key: str, ttl: float = None) -> Optional[Image.Image]:
        """
        获取缓存的截图

        Args:
            key: 缓存键
            ttl: 缓存有效期(秒)

        Returns:
            缓存的截图，如果不存在或过期返回 None
        """
        import time

        if key not in cls._cache:
            return None

        # 检查是否过期
        if ttl is None:
            ttl = cls._default_ttl

        if time.time() - cls._timestamps.get(key, 0) > ttl:
            cls.invalidate(key)
            return None

        return cls._cache.get(key)

    @classmethod
    def set(cls, key: str, image: Image.Image):
        """
        设置缓存

        Args:
            key: 缓存键
            image: 截图
        """
        import time

        with cls._lock:
            cls._cache[key] = image
            cls._timestamps[key] = time.time()

    @classmethod
    def invalidate(cls, key: str = None):
        """
        清除缓存

        Args:
            key: 缓存键，为 None 时清除所有
        """
        with cls._lock:
            if key is None:
                cls._cache.clear()
                cls._timestamps.clear()
            elif key in cls._cache:
                del cls._cache[key]
                if key in cls._timestamps:
                    del cls._timestamps[key]

    @classmethod
    def cached_capture(cls, key: str, capture_func: Callable, ttl: float = None) -> Image.Image:
        """
        带缓存的截图

        Args:
            key: 缓存键
            capture_func: 截图函数
            ttl: 缓存有效期

        Returns:
            截图
        """
        img = cls.get(key, ttl)
        if img is None:
            img = capture_func()
            cls.set(key, img)
        return img


# ==================== UI 元素缓存 ====================

class ElementCache:
    """
    UI 元素缓存 - 避免重复查找

    用法:
        from screen_controller.performance import ElementCache

        # 查找元素（带缓存）
        element = ElementCache.find("button_name", finder.find_element)

        # 清除缓存
        ElementCache.invalidate()
    """

    _cache: Dict[str, Any] = {}
    _lock = threading.Lock()

    @classmethod
    def find(cls, name: str, find_func: Callable, ttl: float = 5.0) -> Optional[Any]:
        """
        带缓存的元素查找

        Args:
            name: 元素名称
            find_func: 查找函数
            ttl: 缓存时间(秒)

        Returns:
            找到的元素或 None
        """
        import time

        # 检查缓存
        if name in cls._cache:
            cached, timestamp = cls._cache[name]
            if time.time() - timestamp < ttl:
                return cached

        # 执行查找
        element = find_func(name)

        # 更新缓存
        with cls._lock:
            cls._cache[name] = (element, time.time())

        return element

    @classmethod
    def invalidate(cls, name: str = None):
        """清除缓存"""
        with cls._lock:
            if name is None:
                cls._cache.clear()
            elif name in cls._cache:
                del cls._cache[name]


# ==================== 延迟导入 ====================

class LazyImport:
    """延迟导入 - 减少启动时间"""

    _modules: Dict[str, Any] = {}
    _lock = threading.Lock()

    @classmethod
    def get(cls, module_name: str, fromlist: tuple = ()):
        """
        延迟导入模块

        Args:
            module_name: 模块名
            fromlist: 要导入的内容

        Returns:
            导入的模块
        """
        if module_name not in cls._modules:
            with cls._lock:
                if module_name not in cls._modules:
                    cls._modules[module_name] = __import__(module_name, fromlist=fromlist)

        return cls._modules[module_name]


# ==================== 性能装饰器 ====================

def cached(ttl: float = 60.0):
    """
    缓存装饰器

    用法:
        @cached(ttl=60.0)
        def expensive_function(x):
            # 耗时计算
            return result
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        import time

        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result

        return wrapper
    return decorator


def async_cache(ttl: float = 60.0):
    """异步缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        import time
        import asyncio

        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result

            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            cache[key] = (result, time.time())
            return result

        return wrapper
    return decorator


# ==================== 批量操作优化 ====================

class BatchProcessor:
    """
    批量处理器 - 减少 I/O 操作

    用法:
        processor = BatchProcessor()

        # 添加任务
        processor.add(task_func, args)

        # 批量执行
        results = processor.execute()
    """

    def __init__(self, batch_size: int = 10, delay: float = 0.1):
        self.batch_size = batch_size
        self.delay = delay
        self._tasks = []
        self._lock = threading.Lock()

    def add(self, func: Callable, *args, **kwargs):
        """添加任务"""
        with self._lock:
            self._tasks.append((func, args, kwargs))

    def execute(self):
        """执行所有任务"""
        results = []
        with self._lock:
            tasks = self._tasks.copy()
            self._tasks.clear()

        for func, args, kwargs in tasks:
            try:
                result = func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch task failed: {e}")
                results.append(None)

        return results


# ==================== 预热函数 ====================

def warmup():
    """
    预热 - 初始化常用组件

    用法:
        from screen_controller.performance import warmup
        warmup()  # 在主程序开始时调用
    """
    logger.info("Warming up...")

    # 预加载 OCR 引擎
    OCREngineCache.preload([("paddle", "ch"), ("easy", "ch")])

    # 预热截图模块
    try:
        from . import enhanced_screenshot
        # 触发模块加载
        _ = enhanced_screenshot.capture_screen
    except Exception as e:
        logger.warning(f"Screenshot warmup failed: {e}")

    # 预热 UI 元素查找
    try:
        from . import ui_element_finder
        _ = ui_element_finder.get_finder
    except Exception as e:
        logger.warning(f"UI finder warmup failed: {e}")

    logger.info("Warmup complete")


# ==================== 性能监控 ====================

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self._timings: Dict[str, list] = {}
        self._lock = threading.Lock()

    def record(self, name: str, duration: float):
        """记录执行时间"""
        with self._lock:
            if name not in self._timings:
                self._timings[name] = []
            self._timings[name].append(duration)

    def get_stats(self, name: str) -> Dict[str, float]:
        """获取统计信息"""
        with self._lock:
            if name not in self._timings:
                return {}

            timings = self._timings[name]
            return {
                "count": len(timings),
                "total": sum(timings),
                "avg": sum(timings) / len(timings),
                "min": min(timings),
                "max": max(timings)
            }

    def report(self) -> str:
        """生成报告"""
        lines = ["Performance Report:", "=" * 40]

        with self._lock:
            for name, timings in self._timings.items():
                avg = sum(timings) / len(timings)
                lines.append(f"{name}: {avg:.3f}s (n={len(timings)})")

        return "\n".join(lines)


# 全局性能监控器
_perf_monitor = PerformanceMonitor()


def get_perf_monitor() -> PerformanceMonitor:
    """获取性能监控器"""
    return _perf_monitor
