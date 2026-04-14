"""
AI Sky Eye - Performance Optimization Examples
===============================================
Demonstrates caching and performance optimization features.

Author: Xiao Liangzi
Version: 2.5
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_controller import (
    OCREngineCache,
    ScreenshotCache,
    ElementCache,
    PerformanceMonitor,
    get_perf_monitor,
    cached,
    warmup
)


def example_1_ocr_cache():
    """Example 1: OCR Engine Caching"""
    print("\n" + "="*60)
    print("📖 Example 1: OCR Engine Caching")
    print("="*60)

    print("\n1. Without caching (slow):")
    print("   Each OCR call initializes the engine (2-5 seconds)")

    print("\n2. With OCREngineCache (fast):")

    # Get cache instance
    cache = OCREngineCache()

    print("   cache = OCREngineCache()")
    print("   ocr = cache.get_engine('paddle')")
    print("   # First call: initializes engine (~3s)")

    # Simulate first call
    start = time.time()
    print(f"   Initializing... (simulated)")
    time.sleep(0.1)  # Simulated delay
    init_time = time.time() - start

    print(f"   First initialization: {init_time:.3f}s")

    print("\n   ocr2 = cache.get_engine('paddle')")
    print("   # Second call: returns cached instance (<0.01s)")

    # Simulate cached call
    start = time.time()
    print(f"   Retrieving from cache... (simulated)")
    cached_time = time.time() - start

    print(f"   Cached retrieval: {cached_time:.6f}s")
    print(f"   Speedup: {init_time/cached_time if cached_time > 0 else 'N/A'}x")

    print("\n3. Supported OCR engines:")
    print("   - paddle (PaddleOCR)")
    print("   - easy (EasyOCR)")
    print("   - tesseract (Tesseract)")


def example_2_screenshot_cache():
    """Example 2: Screenshot Caching"""
    print("\n" + "="*60)
    print("📸 Example 2: Screenshot Caching")
    print("="*60)

    print("\n1. Creating screenshot cache...")
    cache = ScreenshotCache(ttl=1.0)  # 1 second TTL

    print("   cache = ScreenshotCache(ttl=1.0)")
    print("   # TTL = Time to live in seconds")

    print("\n2. Cache behavior:")
    print("-"*60)

    # Simulate captures
    print("\n   First capture (not cached):")
    start = time.time()
    time.sleep(0.05)  # Simulate capture
    t1 = time.time() - start
    print(f"   Time: {t1:.3f}s")

    print("\n   Second capture (within TTL, cached):")
    start = time.time()
    time.sleep(0.001)  # Almost instant
    t2 = time.time() - start
    print(f"   Time: {t2:.3f}s")

    print(f"\n   Speedup: {t1/t2 if t2 > 0 else 'N/A'}x")

    print("\n3. Cache invalidation:")
    print("   cache.clear()  # Clear all cached screenshots")
    print("   # Or wait for TTL to expire")


def example_3_element_cache():
    """Example 3: UI Element Caching"""
    print("\n" + "="*60)
    print("🎯 Example 3: UI Element Caching")
    print("="*60)

    print("\n1. Creating element cache...")
    cache = ElementCache(ttl=5.0)

    print("   cache = ElementCache(ttl=5.0)")

    print("\n2. Caching element locations:")

    elements = [
        ("login_button", (100, 200)),
        ("username_field", (100, 150)),
        ("submit_button", (200, 300))
    ]

    print("\n   Storing elements:")
    for name, position in elements:
        print(f"   cache.set('{name}', {position})")

    print("\n   Retrieving elements:")
    for name, _ in elements:
        print(f"   pos = cache.get('{name}')  # Fast lookup")

    print("\n3. Benefits:")
    print("   - Avoid repeated element detection")
    print("   - Faster automation execution")
    print("   - Reduced CPU usage")


def example_4_performance_monitoring():
    """Example 4: Performance Monitoring"""
    print("\n" + "="*60)
    print("📊 Example 4: Performance Monitoring")
    print("="*60)

    print("\n1. Getting performance monitor...")
    monitor = get_perf_monitor()

    print("   monitor = get_perf_monitor()")

    print("\n2. Recording operations:")

    operations = [
        ("screenshot", 0.05),
        ("ocr_recognize", 0.8),
        ("element_find", 0.3),
        ("mouse_click", 0.01),
        ("keyboard_type", 0.02)
    ]

    print("\n   Simulated operations:")
    for op, duration in operations:
        start = time.time()
        time.sleep(duration / 10)  # Scaled down for demo
        actual = time.time() - start
        monitor.record(op, actual)
        print(f"   {op:20} - {actual*1000:.2f}ms")

    print("\n3. Getting statistics:")
    stats = monitor.get_stats()

    print("\n   Performance Statistics:")
    for op, data in stats.items():
        print(f"   {op}:")
        print(f"     - Calls: {data.get('count', 0)}")
        print(f"     - Avg: {data.get('avg', 0)*1000:.2f}ms")
        print(f"     - Total: {data.get('total', 0)*1000:.2f}ms")


def example_5_cached_decorator():
    """Example 5: Using @cached Decorator"""
    print("\n" + "="*60)
    print("🎨 Example 5: Using @cached Decorator")
    print("="*60)

    print("\n1. Basic caching with decorator:")
    print("-"*60)

    print("""
   from screen_controller import cached

   @cached(ttl=60)  # Cache for 60 seconds
   def expensive_operation(param):
       # This will only run once for same param
       # within the TTL period
       time.sleep(2)
       return param * 2

   result1 = expensive_operation(5)  # Takes 2s
   result2 = expensive_operation(5)  # Instant (cached)
   result3 = expensive_operation(10) # Takes 2s (different param)
    """)

    print("\n2. Cache key customization:")
    print("""
   @cached(ttl=300, key_func=lambda args: args[0])
   def find_element(element_name):
       # Custom cache key based on element_name
       return locate_on_screen(element_name)
    """)

    print("\n3. Cache statistics:")
    print("""
   @cached(ttl=60)
   def my_function():
       pass

   # Access cache info
   print(my_function.cache_info())
   # CacheInfo(hits=10, misses=2, maxsize=128, currsize=2)
    """)


def example_6_warmup():
    """Example 6: System Warmup"""
    print("\n" + "="*60)
    print("🔥 Example 6: System Warmup")
    print("="*60)

    print("\n1. Why warmup is important:")
    print("   - OCR engines take time to initialize")
    print("   - First screenshot may be slower")
    print("   - Pre-loading improves responsiveness")

    print("\n2. Using warmup:")
    print("-"*60)

    print("""
   from screen_controller import warmup

   # Warmup all systems
   warmup()

   # Or warmup specific components
   warmup(components=['ocr', 'screenshot'])
    """)

    print("\n3. What warmup does:")
    print("   ✓ Initializes OCR engine")
    print("   ✓ Pre-loads ML models")
    print("   ✓ Takes initial screenshot")
    print("   ✓ Warms up element finder")

    print("\n4. Best practices:")
    print("   - Call warmup() at application start")
    print("   - Use before time-sensitive operations")
    print("   - Consider async warmup for UI apps")


def example_7_batch_processing():
    """Example 7: Batch Processing"""
    print("\n" + "="*60)
    print("📦 Example 7: Batch Processing")
    print("="*60)

    print("\n1. Batch processing for efficiency:")
    print("-"*60)

    print("""
   from screen_controller.performance import BatchProcessor

   processor = BatchProcessor(batch_size=10)

   # Add tasks
   for i in range(100):
       processor.add_task(process_screenshot, args=(i,))

   # Execute all tasks
   results = processor.execute()
    """)

    print("\n2. Benefits of batching:")
    print("   - Reduces overhead")
    print("   - Better resource utilization")
    print("   - Parallel execution support")
    print("   - Automatic error handling")

    print("\n3. Use cases:")
    print("   - Processing multiple screenshots")
    print("   - Batch OCR on multiple regions")
    print("   - Finding multiple elements")


def example_8_memory_management():
    """Example 8: Memory Management"""
    print("\n" + "="*60)
    print("💾 Example 8: Memory Management")
    print("="*60)

    print("\n1. Cache size limits:")
    print("-"*60)

    print("""
   # Limit cache size to prevent memory issues
   cache = ScreenshotCache(
       ttl=5.0,
       max_size=10  # Keep only 10 screenshots
   )
    """)

    print("\n2. Automatic cleanup:")
    print("   - Expired items removed automatically")
    print("   - LRU eviction when max_size reached")
    print("   - Manual clear() for immediate cleanup")

    print("\n3. Memory-efficient patterns:")
    print("-"*60)

    print("""
   # Good: Reuse cache instance
   cache = ScreenshotCache()
   for i in range(100):
       img = cache.get_screenshot()
       process(img)

   # Good: Clear when done
   cache.clear()

   # Good: Use context manager
   with ScreenshotCache() as cache:
       process_many_screenshots(cache)
    """)


def main():
    """Main function to run all examples"""
    print("\n" + "🦞"*30)
    print("AI Sky Eye v2.5 - Performance Optimization Examples")
    print("🦞"*30)

    try:
        example_1_ocr_cache()
        example_2_screenshot_cache()
        example_3_element_cache()
        example_4_performance_monitoring()
        example_5_cached_decorator()
        example_6_warmup()
        example_7_batch_processing()
        example_8_memory_management()

        print("\n" + "="*60)
        print("🎉 All Performance Optimization examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
