# 性能优化指南 / Performance Optimization Guide

本模块提供多种性能优化功能，帮助提升 AI 天眼通的运行效率。

---

## 性能问题分析

### 主要性能瓶颈

| 问题 | 影响 | 解决方案 |
|------|------|---------|
| OCR 引擎重复初始化 | 每次 OCR 耗时 2-5 秒 | OCR 引擎单例缓存 |
| 重复截图 | 截图耗时 0.5-2 秒 | 截图缓存 |
| UI 元素重复查找 | 查找耗时 1-3 秒 | 元素缓存 |
| 模块导入慢 | 启动慢 | 延迟导入 |

---

## 使用方法

### 1. OCR 引擎缓存

```python
from screen_controller import OCREngineCache

# 获取单例 OCR 引擎 (首次调用会初始化，之后复用)
ocr = OCREngineCache.get_engine("paddle", "ch")

# 执行 OCR
result = ocr.ocr(image)

# 预加载多个引擎
OCREngineCache.preload([("paddle", "ch"), ("easy", "ch")])

# 清理缓存
OCREngineCache.clear()
```

### 2. 截图缓存

```python
from screen_controller import ScreenshotCache

# 获取缓存的截图 (TTL=1秒)
img = ScreenshotCache.get("main_window")

# 设置缓存
ScreenshotCache.set("main_window", screenshot)

# 带缓存的截图
img = ScreenshotCache.cached_capture(
    "main_window",
    lambda: capture_screen(),
    ttl=2.0  # 缓存2秒
)

# 清除缓存
ScreenshotCache.invalidate("main_window")  # 清除指定
ScreenshotCache.invalidate()  # 清除所有
```

### 3. UI 元素缓存

```python
from screen_controller import ElementCache, get_finder

finder = get_finder()

# 带缓存的元素查找 (缓存5秒)
element = ElementCache.find(
    "login_button",
    lambda: finder.find_by_name("login_button"),
    ttl=5.0
)

# 清除缓存
ElementCache.invalidate("login_button")
```

### 4. 批量处理器

```python
from screen_controller import BatchProcessor

processor = BatchProcessor(batch_size=10, delay=0.1)

# 添加任务
processor.add(process_image, img1)
processor.add(process_image, img2)
processor.add(process_image, img3)

# 批量执行
results = processor.execute()
```

### 5. 性能监控

```python
from screen_controller import get_perf_monitor

monitor = get_perf_monitor()

# 记录执行时间
monitor.record("ocr_operation", 1.5)
monitor.record("ocr_operation", 1.2)
monitor.record("ocr_operation", 1.8)

# 获取统计
stats = monitor.get_stats("ocr_operation")
print(stats)
# {'count': 3, 'total': 4.5, 'avg': 1.5, 'min': 1.2, 'max': 1.8}

# 生成报告
print(monitor.report())
```

### 6. 缓存装饰器

```python
from screen_controller import cached

@cached(ttl=60.0)
def expensive_operation(x):
    """耗时操作，结果缓存60秒"""
    # ... 耗时计算
    return result

# 首次调用
result = expensive_operation(10)  # 执行计算

# 60秒内再次调用
result = expensive_operation(10)  # 直接返回缓存
```

### 7. 预热

```python
from screen_controller import warmup

# 在主程序开始时调用
if __name__ == "__main__":
    warmup()  # 预热 OCR 引擎等组件

    # 正常业务逻辑
    ...
```

---

## 性能对比

### OCR 引擎初始化

| 方式 | 首次 | 后续调用 |
|------|------|---------|
| 原始方式 | 2-5 秒 | 2-5 秒 (每次新建) |
| 使用缓存 | 2-5 秒 | **< 0.01 秒** |

### 截图操作

| 方式 | 耗时 |
|------|------|
| 原始方式 | 0.5-2 秒/次 |
| 使用缓存 | **< 0.001 秒** (缓存命中) |

---

## 最佳实践

1. **启动时预热**: 在程序入口调用 `warmup()`

2. **批量 OCR**: 使用 `BatchProcessor` 批量处理

3. **频繁操作**: 使用缓存避免重复计算

4. **监控性能**: 使用 `PerformanceMonitor` 发现瓶颈

---

## 版本要求

- Python 3.8+
- numpy (推荐最新版本)

如遇到 numpy 版本问题:
```bash
pip install --upgrade numpy
```
