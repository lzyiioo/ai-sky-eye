"""
AI Enhancements - AI 增强功能系统
整合：智能等待、异常恢复、操作链、OCR增强、图像对比
"""

import time
import json
import base64
import io
import logging
from typing import Optional, List, Dict, Any, Callable, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from PIL import Image, ImageChops
import numpy as np

# 可选依赖
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

from .enhanced_screenshot import capture_screen, capture_to_base64
from .ui_element_finder import get_finder, find_element

logger = logging.getLogger(__name__)


# ==================== 11. 智能等待 ====================

class WaitCondition(Enum):
    """等待条件类型"""
    ELEMENT_APPEAR = "element_appear"      # 元素出现
    ELEMENT_DISAPPEAR = "element_disappear" # 元素消失
    TEXT_APPEAR = "text_appear"            # 文字出现
    TEXT_DISAPPEAR = "text_disappear"      # 文字消失
    IMAGE_STABLE = "image_stable"          # 画面稳定（无变化）
    IMAGE_CHANGE = "image_change"          # 画面变化
    CUSTOM = "custom"                      # 自定义条件


@dataclass
class WaitResult:
    """等待结果"""
    success: bool
    condition: str
    duration: float
    message: str = ""
    data: Dict = field(default_factory=dict)


class SmartWaiter:
    """
    智能等待器
    
    功能：
    - 等待元素出现/消失
    - 等待文字出现/消失（OCR）
    - 等待画面稳定/变化
    - 自定义条件等待
    """
    
    def __init__(self, check_interval: float = 0.5):
        """
        初始化
        
        Args:
            check_interval: 检查间隔（秒）
        """
        self.check_interval = check_interval
        self.finder = get_finder()
        self._ocr = None

    def _get_ocr(self):
        """延迟初始化 OCR - 使用缓存"""
        if self._ocr is None:
            # 使用性能优化模块的 OCR 缓存
            try:
                from .performance import OCREngineCache
                self._ocr = OCREngineCache.get_engine("paddle", "ch")
                if self._ocr is None:
                    self._ocr = OCREngineCache.get_engine("easy", "ch")
            except ImportError:
                # 回退到直接创建
                if HAS_PADDLEOCR:
                    self._ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
                elif HAS_EASYOCR:
                    self._ocr = easyocr.Reader(['ch_sim', 'en'])
        return self._ocr
    
    def wait_for_element(
        self,
        name: str,
        timeout: float = 10.0,
        disappear: bool = False
    ) -> WaitResult:
        """
        等待元素出现或消失
        
        Args:
            name: 元素名称
            timeout: 超时时间
            disappear: True=等待消失, False=等待出现
            
        Returns:
            WaitResult
        """
        start_time = time.time()
        condition = "消失" if disappear else "出现"
        print(f"⏳ 等待元素'{name}'{condition} (超时: {timeout}s)")
        
        while time.time() - start_time < timeout:
            elements = self.finder.find_by_name(name)
            exists = len(elements) > 0
            
            if disappear and not exists:
                duration = time.time() - start_time
                print(f"   ✅ 元素已{condition} (耗时: {duration:.2f}s)")
                return WaitResult(True, f"element_{condition}", duration)
            
            if not disappear and exists:
                duration = time.time() - start_time
                elem = elements[0]
                print(f"   ✅ 元素已{condition} @ {elem.center} (耗时: {duration:.2f}s)")
                return WaitResult(True, f"element_{condition}", duration, data={"element": elem.to_dict()})
            
            time.sleep(self.check_interval)
            self.finder.clear_cache()
        
        duration = time.time() - start_time
        print(f"   ❌ 等待超时 ({duration:.2f}s)")
        return WaitResult(False, f"element_{condition}", duration, "Timeout")
    
    def wait_for_text(
        self,
        text: str,
        timeout: float = 10.0,
        disappear: bool = False,
        region: Optional[Tuple] = None
    ) -> WaitResult:
        """
        等待文字出现或消失（使用 OCR）
        
        Args:
            text: 要等待的文字
            timeout: 超时时间
            disappear: True=等待消失
            region: 限定区域
            
        Returns:
            WaitResult
        """
        start_time = time.time()
        condition = "消失" if disappear else "出现"
        print(f"⏳ 等待文字'{text}'{condition} (超时: {timeout}s)")
        
        ocr = self._get_ocr()
        if not ocr:
            return WaitResult(False, f"text_{condition}", 0, "OCR not available")
        
        while time.time() - start_time < timeout:
            # 截图
            img = capture_screen(region=region)
            
            # OCR 识别
            if HAS_PADDLEOCR:
                result = ocr.ocr(np.array(img), cls=True)
                detected_text = " ".join([line[1][0] for line in result[0] if line])
            elif HAS_EASYOCR:
                result = ocr.readtext(np.array(img))
                detected_text = " ".join([item[1] for item in result])
            else:
                return WaitResult(False, f"text_{condition}", 0, "No OCR engine")
            
            exists = text.lower() in detected_text.lower()
            
            if disappear and not exists:
                duration = time.time() - start_time
                print(f"   ✅ 文字已{condition} (耗时: {duration:.2f}s)")
                return WaitResult(True, f"text_{condition}", duration)
            
            if not disappear and exists:
                duration = time.time() - start_time
                print(f"   ✅ 文字已{condition} (耗时: {duration:.2f}s)")
                return WaitResult(True, f"text_{condition}", duration)
            
            time.sleep(self.check_interval)
        
        duration = time.time() - start_time
        return WaitResult(False, f"text_{condition}", duration, "Timeout")
    
    def wait_for_stable(
        self,
        timeout: float = 10.0,
        stability_duration: float = 1.0,
        threshold: float = 0.99
    ) -> WaitResult:
        """
        等待画面稳定（无变化）
        
        Args:
            timeout: 超时时间
            stability_duration: 稳定持续时间
            threshold: 相似度阈值
            
        Returns:
            WaitResult
        """
        print(f"⏳ 等待画面稳定 (持续 {stability_duration}s, 相似度 > {threshold})")
        
        start_time = time.time()
        last_img = None
        stable_start = None
        
        while time.time() - start_time < timeout:
            current_img = capture_screen()
            
            if last_img is not None:
                similarity = self._calculate_similarity(last_img, current_img)
                
                if similarity >= threshold:
                    if stable_start is None:
                        stable_start = time.time()
                    elif time.time() - stable_start >= stability_duration:
                        duration = time.time() - start_time
                        print(f"   ✅ 画面已稳定 (耗时: {duration:.2f}s)")
                        return WaitResult(True, "image_stable", duration)
                else:
                    stable_start = None
            
            last_img = current_img
            time.sleep(self.check_interval)
        
        duration = time.time() - start_time
        return WaitResult(False, "image_stable", duration, "Timeout")
    
    def wait_for_change(
        self,
        timeout: float = 10.0,
        threshold: float = 0.9
    ) -> WaitResult:
        """
        等待画面变化
        
        Args:
            timeout: 超时时间
            threshold: 变化阈值（低于此值认为有变化）
            
        Returns:
            WaitResult
        """
        print(f"⏳ 等待画面变化 (相似度 < {threshold})")
        
        start_time = time.time()
        baseline = capture_screen()
        
        while time.time() - start_time < timeout:
            current = capture_screen()
            similarity = self._calculate_similarity(baseline, current)
            
            if similarity < threshold:
                duration = time.time() - start_time
                print(f"   ✅ 画面已变化 (相似度: {similarity:.3f}, 耗时: {duration:.2f}s)")
                return WaitResult(True, "image_change", duration, data={"similarity": similarity})
            
            time.sleep(self.check_interval)
        
        duration = time.time() - start_time
        return WaitResult(False, "image_change", duration, "Timeout")
    
    def _calculate_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """计算两张图片的相似度"""
        if HAS_CV2:
            # 使用 OpenCV 计算 SSIM
            try:
                from skimage.metrics import structural_similarity as ssim
                img1_array = np.array(img1.convert('L'))
                img2_array = np.array(img2.convert('L'))
                
                # 确保尺寸相同
                if img1_array.shape != img2_array.shape:
                    img2_array = cv2.resize(img2_array, (img1_array.shape[1], img1_array.shape[0]))
                
                score, _ = ssim(img1_array, img2_array, full=True)
                return score
            except:
                pass
        
        # 回退：简单的像素差异
        diff = ImageChops.difference(img1, img2)
        if diff.getbbox() is None:
            return 1.0
        
        # 计算差异比例
        diff_array = np.array(diff)
        non_zero = np.count_nonzero(diff_array)
        total = diff_array.size
        similarity = 1 - (non_zero / total)
        
        return similarity
    
    def wait_for_custom(
        self,
        condition_func: Callable[[], bool],
        timeout: float = 10.0,
        description: str = "custom"
    ) -> WaitResult:
        """
        自定义条件等待
        
        Args:
            condition_func: 返回 bool 的条件函数
            timeout: 超时时间
            description: 条件描述
            
        Returns:
            WaitResult
        """
        print(f"⏳ 等待条件: {description} (超时: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    duration = time.time() - start_time
                    print(f"   ✅ 条件满足 (耗时: {duration:.2f}s)")
                    return WaitResult(True, description, duration)
            except Exception as e:
                logger.warning(f"Condition check failed: {e}")
            
            time.sleep(self.check_interval)
        
        duration = time.time() - start_time
        return WaitResult(False, description, duration, "Timeout")


# ==================== 12. 异常恢复 ====================

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    retry_interval: float = 1.0
    backoff_factor: float = 2.0  # 指数退避
    recover_actions: List[Dict] = field(default_factory=list)  # 恢复操作


@dataclass
class ActionResult:
    """操作结果"""
    success: bool
    action: str
    attempts: int
    duration: float
    error: Optional[str] = None
    recover_attempted: bool = False


class ExceptionRecovery:
    """
    异常恢复系统
    
    功能：
    - 操作失败自动重试
    - 指数退避
    - 恢复操作
    - 操作回滚
    """
    
    def __init__(self):
        self.action_history: List[Dict] = []
        self.rollback_stack: List[Callable] = []
    
    def execute_with_retry(
        self,
        action_func: Callable[[], Any],
        action_name: str = "action",
        config: Optional[RetryConfig] = None,
        rollback_func: Optional[Callable] = None
    ) -> ActionResult:
        """
        带重试的执行
        
        Args:
            action_func: 要执行的函数
            action_name: 操作名称
            config: 重试配置
            rollback_func: 回滚函数
            
        Returns:
            ActionResult
        """
        config = config or RetryConfig()
        start_time = time.time()
        
        # 注册回滚
        if rollback_func:
            self.rollback_stack.append(rollback_func)
        
        last_error = None
        
        for attempt in range(config.max_retries):
            try:
                print(f"🔄 执行 '{action_name}' (尝试 {attempt + 1}/{config.max_retries})")
                result = action_func()
                
                duration = time.time() - start_time
                print(f"   ✅ 成功 (耗时: {duration:.2f}s)")
                
                return ActionResult(True, action_name, attempt + 1, duration)
                
            except Exception as e:
                last_error = str(e)
                print(f"   ❌ 失败: {last_error}")
                
                if attempt < config.max_retries - 1:
                    # 计算等待时间（指数退避）
                    wait_time = config.retry_interval * (config.backoff_factor ** attempt)
                    print(f"   ⏳ {wait_time:.1f}s 后重试...")
                    
                    # 执行恢复操作
                    if config.recover_actions:
                        self._execute_recover_actions(config.recover_actions)
                    
                    time.sleep(wait_time)
                else:
                    break
        
        # 所有重试失败
        duration = time.time() - start_time
        return ActionResult(
            False, action_name, config.max_retries, duration, last_error
        )
    
    def _execute_recover_actions(self, actions: List[Dict]):
        """执行恢复操作"""
        print("   🔄 执行恢复操作...")
        for action in actions:
            try:
                action_type = action.get("type")
                if action_type == "screenshot":
                    capture_screen().save("recovery_screenshot.png")
                elif action_type == "wait":
                    time.sleep(action.get("duration", 1))
                elif action_type == "click":
                    # 点击指定位置
                    pass
                print(f"      ✓ {action_type}")
            except Exception as e:
                print(f"      ✗ {action_type}: {e}")
    
    def rollback(self) -> List[bool]:
        """
        执行回滚
        
        Returns:
            每个回滚操作的结果
        """
        print("⏪ 执行回滚操作...")
        results = []
        
        while self.rollback_stack:
            rollback_func = self.rollback_stack.pop()
            try:
                rollback_func()
                results.append(True)
                print("   ✓ 回滚成功")
            except Exception as e:
                results.append(False)
                print(f"   ✗ 回滚失败: {e}")
        
        return results
    
    def clear_history(self):
        """清除历史"""
        self.action_history.clear()
        self.rollback_stack.clear()


# ==================== 13. 操作链 ====================

@dataclass
class ChainStep:
    """操作链步骤"""
    action: str                          # 操作类型
    params: Dict = field(default_factory=dict)  # 参数
    condition: Optional[str] = None      # 执行条件
    on_success: Optional[str] = None     # 成功后的跳转
    on_failure: Optional[str] = None     # 失败后的跳转
    retry: int = 1                       # 重试次数
    delay: float = 0.5                   # 执行后延迟


class ActionChain:
    """
    操作链系统
    
    功能：
    - 顺序执行操作
    - 条件分支
    - 循环支持
    - 错误处理
    """
    
    def __init__(self):
        self.steps: Dict[str, ChainStep] = {}
        self.variables: Dict[str, Any] = {}  # 变量存储
        self.results: List[Dict] = []
    
    def add_step(self, step_id: str, step: ChainStep):
        """添加步骤"""
        self.steps[step_id] = step
        return self
    
    def set_variable(self, name: str, value: Any):
        """设置变量"""
        self.variables[name] = value
        return self
    
    def execute(self, start_step: str = "start") -> Dict[str, Any]:
        """
        执行操作链
        
        Args:
            start_step: 起始步骤ID
            
        Returns:
            执行结果
        """
        print(f"🚀 开始执行操作链，起始: {start_step}")
        
        current_step = start_step
        executed_steps = []
        
        while current_step and current_step in self.steps:
            step = self.steps[current_step]
            
            # 检查条件
            if step.condition and not self._evaluate_condition(step.condition):
                print(f"⏭️ 步骤 '{current_step}' 条件不满足，跳过")
                current_step = step.on_failure or self._get_next_step(current_step)
                continue
            
            # 执行步骤
            print(f"▶️ 执行步骤 '{current_step}': {step.action}")
            result = self._execute_step(step)
            
            executed_steps.append({
                "step": current_step,
                "action": step.action,
                "success": result.get("success", False),
                "result": result
            })
            
            # 确定下一步
            if result.get("success", False):
                current_step = step.on_success or self._get_next_step(current_step)
            else:
                if step.retry > 1:
                    print(f"   🔄 重试步骤 '{current_step}'")
                    step.retry -= 1
                    time.sleep(step.delay)
                    continue
                current_step = step.on_failure or self._get_next_step(current_step)
            
            # 延迟
            if step.delay > 0:
                time.sleep(step.delay)
        
        print(f"✅ 操作链执行完成，共 {len(executed_steps)} 步")
        
        return {
            "success": all(s["success"] for s in executed_steps),
            "steps": executed_steps,
            "variables": self.variables
        }
    
    def _execute_step(self, step: ChainStep) -> Dict[str, Any]:
        """执行单个步骤"""
        action = step.action
        params = step.params
        
        try:
            if action == "click":
                from .smart_controller_v2 import ai_click
                return ai_click(params["target"])
            
            elif action == "type":
                from .smart_controller_v2 import ai_type
                return ai_type(params["target"], params["text"])
            
            elif action == "wait":
                time.sleep(params.get("duration", 1))
                return {"success": True, "action": "wait"}
            
            elif action == "wait_for_element":
                waiter = SmartWaiter()
                result = waiter.wait_for_element(
                    params["name"],
                    timeout=params.get("timeout", 10)
                )
                return {"success": result.success, "result": asdict(result)}
            
            elif action == "if":
                # 条件分支
                condition = params.get("condition", "")
                if self._evaluate_condition(condition):
                    return {"success": True, "branch": "true"}
                else:
                    return {"success": True, "branch": "false"}
            
            elif action == "set_variable":
                self.variables[params["name"]] = params["value"]
                return {"success": True}
            
            elif action == "screenshot":
                img = capture_screen()
                return {"success": True, "image_size": img.size}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件"""
        try:
            # 简单的条件评估，支持变量
            # 例如: "变量名 == 值" 或 "元素存在"
            
            if "存在" in condition or "exists" in condition.lower():
                # 检查元素是否存在
                element_name = condition.replace("存在", "").replace("exists", "").strip()
                elements = get_finder().find_by_name(element_name)
                return len(elements) > 0
            
            if "==" in condition:
                left, right = condition.split("==", 1)
                left = left.strip()
                right = right.strip().strip('"\'')
                return self.variables.get(left) == right
            
            # 默认尝试 eval
            return bool(eval(condition, {"__builtins__": {}}, self.variables))
            
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False
    
    def _get_next_step(self, current: str) -> Optional[str]:
        """获取下一个步骤（按字母顺序）"""
        step_ids = sorted(self.steps.keys())
        try:
            idx = step_ids.index(current)
            if idx + 1 < len(step_ids):
                return step_ids[idx + 1]
        except ValueError:
            pass
        return None


# ==================== 快捷函数 ====================

def smart_wait_for_element(name: str, timeout: float = 10.0) -> WaitResult:
    """快捷：等待元素"""
    waiter = SmartWaiter()
    return waiter.wait_for_element(name, timeout)

def smart_wait_for_text(text: str, timeout: float = 10.0) -> WaitResult:
    """快捷：等待文字"""
    waiter = SmartWaiter()
    return waiter.wait_for_text(text, timeout)

def smart_wait_for_stable(timeout: float = 10.0) -> WaitResult:
    """快捷：等待画面稳定"""
    waiter = SmartWaiter()
    return waiter.wait_for_stable(timeout)

def execute_with_recovery(
    func: Callable,
    name: str = "action",
    max_retries: int = 3
) -> ActionResult:
    """快捷：带恢复的执行"""
    recovery = ExceptionRecovery()
    config = RetryConfig(max_retries=max_retries)
    return recovery.execute_with_retry(func, name, config)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 AI 增强功能测试")
    print("=" * 70)
    
    # 测试智能等待
    print("\n[测试 1] 智能等待 - 等待元素")
    waiter = SmartWaiter()
    # result = waiter.wait_for_element("确定", timeout=5)
    # print(f"结果: {result}")
    
    # 测试异常恢复
    print("\n[测试 2] 异常恢复")
    recovery = ExceptionRecovery()
    def failing_action():
        raise Exception("模拟失败")
    # result = recovery.execute_with_retry(failing_action, "test_action", RetryConfig(max_retries=2))
    # print(f"结果: {result}")
    
    # 测试操作链
    print("\n[测试 3] 操作链")
    chain = ActionChain()
    chain.add_step("start", ChainStep(
        action="set_variable",
        params={"name": "status", "value": "ready"}
    ))
    chain.add_step("check", ChainStep(
        action="if",
        params={"condition": "status == ready"},
        on_success="success_step",
        on_failure="fail_step"
    ))
    chain.add_step("success_step", ChainStep(action="screenshot"))
    chain.add_step("fail_step", ChainStep(action="wait", params={"duration": 1}))
    
    # result = chain.execute("start")
    # print(f"链执行结果: {result}")
    
    print("\n✅ AI 增强系统准备完成")
    print("   取消注释测试代码以实际运行")
