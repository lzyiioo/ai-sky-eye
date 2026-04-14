"""
Enhanced Screenshot - 多后端截图系统
支持 dxcam → mss → pillow 自动回退
"""

import logging
import os
from typing import Callable, Optional, Tuple, List
from PIL import Image, ImageGrab
from dataclasses import dataclass

# 可选依赖
try:
    import dxcam
    HAS_DXCAM = True
except ImportError:
    dxcam = None
    HAS_DXCAM = False

try:
    import mss
    HAS_MSS = True
except ImportError:
    mss = None
    HAS_MSS = False

logger = logging.getLogger(__name__)


@dataclass
class ScreenshotOptions:
    """截图选项"""
    backend: str = "auto"  # auto/dxcam/mss/pillow
    quality: int = 85      # JPEG 质量
    scale: float = 1.0     # 缩放比例
    region: Optional[Tuple[int, int, int, int]] = None  # (left, top, right, bottom)
    display_index: Optional[int] = None  # 显示器索引


class ScreenshotBackend:
    """截图后端基类"""
    
    def __init__(self):
        self.name = "base"
    
    def capture(self, options: ScreenshotOptions) -> Image.Image:
        raise NotImplementedError
    
    def is_available(self) -> bool:
        raise NotImplementedError
    
    def get_priority(self) -> int:
        """优先级（数字越小优先级越高）"""
        return 99


class DxcamBackend(ScreenshotBackend):
    """DXCam 后端 - 最高性能（基于 DXGI）"""
    
    def __init__(self):
        super().__init__()
        self.name = "dxcam"
        self._camera_cache = {}
    
    def is_available(self) -> bool:
        return HAS_DXCAM and dxcam is not None
    
    def get_priority(self) -> int:
        return 1  # 最高优先级
    
    def capture(self, options: ScreenshotOptions) -> Image.Image:
        if not self.is_available():
            raise RuntimeError("DXCam not available")
        
        # 获取或创建相机实例
        display_idx = options.display_index or 0
        
        if display_idx not in self._camera_cache:
            self._camera_cache[display_idx] = dxcam.create(
                output_idx=display_idx,
                processor_backend="numpy"
            )
        
        camera = self._camera_cache[display_idx]
        
        # 如果指定了区域，转换为 dxcam 格式
        region = None
        if options.region:
            left, top, right, bottom = options.region
            region = (left, top, right, bottom)
        
        # 捕获帧
        frame = camera.grab(region=region, copy=True, new_frame_only=False)
        
        if frame is None:
            raise RuntimeError("DXCam capture returned no frame")
        
        img = Image.fromarray(frame)
        
        # 缩放
        if options.scale != 1.0:
            width, height = img.size
            new_size = (int(width * options.scale), int(height * options.scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    
    def release(self):
        """释放资源"""
        for camera in self._camera_cache.values():
            camera.stop()
        self._camera_cache.clear()


class MssBackend(ScreenshotBackend):
    """MSS 后端 - 跨平台，稳定"""
    
    def __init__(self):
        super().__init__()
        self.name = "mss"
    
    def is_available(self) -> bool:
        return HAS_MSS and mss is not None
    
    def get_priority(self) -> int:
        return 2
    
    def capture(self, options: ScreenshotOptions) -> Image.Image:
        if not self.is_available():
            raise RuntimeError("MSS not available")
        
        with mss.mss() as sct:
            # 确定监控器
            if options.display_index is not None:
                monitor = sct.monitors[options.display_index]
            elif options.region:
                left, top, right, bottom = options.region
                monitor = {
                    "left": left,
                    "top": top,
                    "width": right - left,
                    "height": bottom - top
                }
            else:
                monitor = sct.monitors[0]  # 所有屏幕
            
            # 截图
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            # 缩放
            if options.scale != 1.0:
                width, height = img.size
                new_size = (int(width * options.scale), int(height * options.scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            return img


class PillowBackend(ScreenshotBackend):
    """Pillow 后端 - 最基础，无需额外依赖"""
    
    def __init__(self):
        super().__init__()
        self.name = "pillow"
    
    def is_available(self) -> bool:
        return True  # Pillow 是必须的
    
    def get_priority(self) -> int:
        return 3  # 最低优先级（兜底）
    
    def capture(self, options: ScreenshotOptions) -> Image.Image:
        # 构建截图参数
        grab_kwargs = {"all_screens": True}
        
        if options.region:
            left, top, right, bottom = options.region
            grab_kwargs["bbox"] = (left, top, right, bottom)
        
        try:
            # 尝试截图
            img = ImageGrab.grab(**grab_kwargs)
        except (OSError, RuntimeError, ValueError) as e:
            logger.warning(f"Pillow grab failed: {e}, trying fallback")
            # 回退到主屏幕
            img = ImageGrab.grab()
        
        # 缩放
        if options.scale != 1.0:
            width, height = img.size
            new_size = (int(width * options.scale), int(height * options.scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img


class EnhancedScreenshot:
    """
    增强截图管理器
    
    自动选择和回退：
    1. dxcam - 最高性能（适合游戏、视频）
    2. mss - 跨平台稳定
    3. pillow - 最基础，总是可用
    """
    
    def __init__(self, default_backend: str = "auto"):
        """
        初始化截图管理器
        
        Args:
            default_backend: 默认后端（auto/dxcam/mss/pillow）
        """
        self.default_backend = default_backend
        self._backends = {
            "dxcam": DxcamBackend(),
            "mss": MssBackend(),
            "pillow": PillowBackend()
        }
        
        # 按优先级排序
        self._backend_order = sorted(
            self._backends.values(),
            key=lambda b: b.get_priority()
        )
        
        logger.info(f"Screenshot backends initialized: {[b.name for b in self._backend_order if b.is_available()]}")
    
    def capture(self, options: Optional[ScreenshotOptions] = None) -> Tuple[Image.Image, str]:
        """
        截图（自动选择和回退）
        
        Args:
            options: 截图选项
            
        Returns:
            (Image, backend_name) - 图片和使用的前端名
        """
        options = options or ScreenshotOptions()
        
        # 确定使用哪些后端
        if options.backend == "auto":
            backends_to_try = self._backend_order
        else:
            backend = self._backends.get(options.backend)
            if not backend:
                raise ValueError(f"Unknown backend: {options.backend}")
            backends_to_try = [backend]
        
        # 尝试每个后端
        last_error = None
        for backend in backends_to_try:
            if not backend.is_available():
                continue
            
            try:
                img = backend.capture(options)
                logger.debug(f"Screenshot captured with {backend.name}")
                return img, backend.name
            except Exception as e:
                logger.warning(f"Backend {backend.name} failed: {e}")
                last_error = e
                continue
        
        # 所有后端都失败
        raise RuntimeError(f"All screenshot backends failed. Last error: {last_error}")
    
    def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        backend: str = "auto",
        scale: float = 1.0,
        quality: int = 85
    ) -> Image.Image:
        """
        快速截图
        
        Args:
            region: 截图区域 (left, top, right, bottom)
            backend: 使用后端
            scale: 缩放比例
            quality: JPEG 质量
            
        Returns:
            PIL Image
        """
        options = ScreenshotOptions(
            backend=backend,
            region=region,
            scale=scale,
            quality=quality
        )
        img, _ = self.capture(options)
        return img
    
    def capture_to_base64(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        backend: str = "auto",
        scale: float = 1.0,
        quality: int = 85,
        format: str = "JPEG"
    ) -> Tuple[str, str]:
        """
        截图并转为 Base64
        
        Returns:
            (base64_string, backend_name)
        """
        import io
        import base64
        
        img, backend_name = self.capture(ScreenshotOptions(
            backend=backend,
            region=region,
            scale=scale,
            quality=quality
        ))
        
        buffer = io.BytesIO()
        
        if format.upper() == "JPEG":
            # JPEG 不支持透明度，转换为 RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
        else:
            img.save(buffer, format=format)
        
        buffer.seek(0)
        base64_str = base64.b64encode(buffer.read()).decode('utf-8')
        
        return base64_str, backend_name
    
    def get_available_backends(self) -> List[str]:
        """获取所有可用的后端"""
        return [b.name for b in self._backend_order if b.is_available()]
    
    def get_backend_info(self) -> dict:
        """获取后端信息"""
        return {
            "available": self.get_available_backends(),
            "default": self.default_backend,
            "backends": {
                name: {
                    "available": backend.is_available(),
                    "priority": backend.get_priority()
                }
                for name, backend in self._backends.items()
            }
        }
    
    def release_resources(self):
        """释放资源（主要是 DXCam）"""
        if "dxcam" in self._backends:
            self._backends["dxcam"].release()


# ==================== 快捷函数 ====================

_screenshot_mgr: Optional[EnhancedScreenshot] = None

def get_screenshot_manager() -> EnhancedScreenshot:
    """获取全局截图管理器"""
    global _screenshot_mgr
    if _screenshot_mgr is None:
        _screenshot_mgr = EnhancedScreenshot()
    return _screenshot_mgr

def capture_screen(
    region: Optional[Tuple[int, int, int, int]] = None,
    backend: str = "auto",
    scale: float = 1.0,
    quality: int = 85
) -> Image.Image:
    """快速截图"""
    return get_screenshot_manager().capture_screen(
        region=region,
        backend=backend,
        scale=scale,
        quality=quality
    )

def capture_to_base64(
    region: Optional[Tuple[int, int, int, int]] = None,
    backend: str = "auto",
    scale: float = 1.0,
    quality: int = 85
) -> str:
    """截图并转为 Base64"""
    base64_str, _ = get_screenshot_manager().capture_to_base64(
        region=region,
        backend=backend,
        scale=scale,
        quality=quality
    )
    return base64_str


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 增强截图系统测试")
    print("=" * 60)
    
    mgr = EnhancedScreenshot()
    
    # 显示可用后端
    print("\n📷 可用后端：")
    info = mgr.get_backend_info()
    for name, data in info["backends"].items():
        status = "✅" if data["available"] else "❌"
        print(f"   {status} {name} (优先级: {data['priority']})")
    
    # 测试截图
    print("\n🖼️ 测试截图...")
    try:
        img, backend = mgr.capture()
        print(f"   ✅ 截图成功！后端: {backend}, 尺寸: {img.size}")
        
        # 保存测试
        img.save("test_screenshot.png")
        print(f"   💾 已保存: test_screenshot.png")
    except Exception as e:
        print(f"   ❌ 截图失败: {e}")
    
    # 测试 Base64
    print("\n📤 测试 Base64 输出...")
    try:
        base64_str, backend = mgr.capture_to_base64(scale=0.5, quality=60)
        print(f"   ✅ Base64 成功！后端: {backend}, 长度: {len(base64_str)} 字符")
    except Exception as e:
        print(f"   ❌ Base64 失败: {e}")
    
    print("\n✅ 测试完成!")
    
    # 释放资源
    mgr.release_resources()
