"""
Smart Brain - 智能决策大脑
理解上下文、分析情况、做出决策

功能:
1. 屏幕上下文理解 - 不只是识别元素，而是理解"当前在什么界面"
2. 异常检测与处理 - 发现错误弹窗、加载失败等
3. 智能决策 - 根据情况决定下一步
4. 策略学习 - 从成功/失败中学习

用法:
    from screen_controller.smart_brain import SmartBrain

    brain = SmartBrain()

    # 分析当前屏幕
    context = brain.analyze_context()
    print(context.state)  # "登录界面" / "主界面" / "错误弹窗"

    # 检测异常
    if brain.detect_anomaly():
        decision = brain.decide_action()
        print(decision)  # "重试" / "跳过" / "等待"
"""

import json
import time
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from PIL import Image

from .enhanced_screenshot import capture_screen
from .vision import vision_describe, vision_find, vision_errors
from .ui_element_finder import get_finder
from .performance import ScreenshotCache

logger = logging.getLogger(__name__)


class ScreenState(Enum):
    """屏幕状态"""
    UNKNOWN = "unknown"           # 未知
    LOGIN = "login"               # 登录界面
    MAIN = "main"                 # 主界面
    LOADING = "loading"           # 加载中
    ERROR = "error"               # 错误
    POPUP = "popup"               # 弹窗
    SUCCESS = "success"           # 成功提示
    CONFIRM = "confirm"           # 确认对话框
    MENU = "menu"                 # 菜单
    FORM = "form"                 # 表单


class AnomalyType(Enum):
    """异常类型"""
    NONE = "none"
    ERROR_DIALOG = "error_dialog"     # 错误对话框
    TIMEOUT = "timeout"               # 超时
    CRASH = "crash"                   # 崩溃
    NETWORK_ERROR = "network_error"   # 网络错误
    NOT_FOUND = "not_found"           # 元素未找到
    UNEXPECTED = "unexpected"         # 意外状态


class DecisionType(Enum):
    """决策类型"""
    CONTINUE = "continue"         # 继续
    RETRY = "retry"               # 重试
    SKIP = "skip"                 # 跳过
    WAIT = "wait"                 # 等待
    ABORT = "abort"               # 中止
    ADAPT = "adapt"               # 调整策略


@dataclass
class Context:
    """屏幕上下文"""
    state: ScreenState            # 当前状态
    description: str              # 描述
    elements: List[Dict]          # 检测到的元素
    text_content: str             # 文字内容
    layout: str                   # 布局类型
    confidence: float             # 置信度
    timestamp: float              # 时间戳


@dataclass
class Anomaly:
    """异常信息"""
    type: AnomalyType
    severity: str                 # "low" / "medium" / "high"
    description: str
    suggestion: str               # 处理建议
    screenshot: Optional[Image.Image] = None


@dataclass
class Decision:
    """决策结果"""
    type: DecisionType
    reason: str                   # 决策原因
    action: Optional[str]         # 建议动作
    params: Dict = field(default_factory=dict)
    confidence: float = 0.0       # 决策置信度


class SmartBrain:
    """
    智能决策大脑

    核心能力:
    - 理解屏幕上下文 (不只是识别，而是理解"这是什么场景")
    - 检测异常 (错误、超时、意外情况)
    - 智能决策 (根据情况选择最佳策略)
    - 学习优化 (从经验中学习)
    """

    def __init__(self):
        self.context_history: List[Context] = []
        self.anomaly_history: List[Anomaly] = []
        self.decision_history: List[Decision] = []
        self._state_transitions: Dict = {}  # 状态转移统计
        self._success_patterns: List = []   # 成功模式
        self._failure_patterns: List = []   # 失败模式

    def analyze_context(self, screenshot: Optional[Image.Image] = None) -> Context:
        """
        分析屏幕上下文

        不只是识别元素，而是理解"当前在什么场景"

        Args:
            screenshot: 截图，为None则自动截图

        Returns:
            Context 对象
        """
        if screenshot is None:
            screenshot = capture_screen()

        # 1. 获取视觉描述
        description = vision_describe(screenshot)

        # 2. 检测界面元素
        elements = self._detect_elements(screenshot)

        # 3. 提取文字内容
        text_content = self._extract_text(screenshot)

        # 4. 分析布局
        layout = self._analyze_layout(elements)

        # 5. 判断状态
        state, confidence = self._determine_state(
            description, elements, text_content
        )

        context = Context(
            state=state,
            description=description,
            elements=elements,
            text_content=text_content,
            layout=layout,
            confidence=confidence,
            timestamp=time.time()
        )

        self.context_history.append(context)

        # 记录状态转移
        if len(self.context_history) >= 2:
            prev = self.context_history[-2].state
            curr = context.state
            key = f"{prev.value}->{curr.value}"
            self._state_transitions[key] = self._state_transitions.get(key, 0) + 1

        logger.info(f"Context analyzed: {state.value} (confidence: {confidence:.2f})")

        return context

    def detect_anomaly(self, context: Optional[Context] = None) -> Optional[Anomaly]:
        """
        检测异常

        检测各种异常情况：错误弹窗、超时、崩溃等

        Args:
            context: 上下文，为None则自动分析

        Returns:
            Anomaly 对象，如果没有异常返回 None
        """
        if context is None:
            context = self.analyze_context()

        # 1. 检查错误对话框
        if self._is_error_dialog(context):
            return Anomaly(
                type=AnomalyType.ERROR_DIALOG,
                severity="high",
                description="检测到错误对话框",
                suggestion="点击确定或关闭按钮，然后重试"
            )

        # 2. 检查超时
        if self._is_timeout(context):
            return Anomaly(
                type=AnomalyType.TIMEOUT,
                severity="medium",
                description="操作超时",
                suggestion="等待或刷新页面"
            )

        # 3. 检查崩溃
        if self._is_crash(context):
            return Anomaly(
                type=AnomalyType.CRASH,
                severity="high",
                description="应用可能已崩溃",
                suggestion="重启应用"
            )

        # 4. 检查网络错误
        if self._is_network_error(context):
            return Anomaly(
                type=AnomalyType.NETWORK_ERROR,
                severity="medium",
                description="网络连接错误",
                suggestion="检查网络连接后重试"
            )

        # 5. 检查意外状态
        unexpected = self._check_unexpected_state(context)
        if unexpected:
            return Anomaly(
                type=AnomalyType.UNEXPECTED,
                severity="low",
                description=f"意外状态: {unexpected}",
                suggestion="等待或重新操作"
            )

        return None

    def decide_action(
        self,
        goal: str,
        context: Optional[Context] = None,
        last_action: Optional[str] = None,
        retry_count: int = 0
    ) -> Decision:
        """
        智能决策

        根据当前情况，决定下一步最佳行动

        Args:
            goal: 目标
            context: 当前上下文
            last_action: 上一步动作
            retry_count: 重试次数

        Returns:
            Decision 对象
        """
        if context is None:
            context = self.analyze_context()

        # 1. 先检查异常
        anomaly = self.detect_anomaly(context)
        if anomaly:
            return self._handle_anomaly(anomaly, retry_count)

        # 2. 检查是否已完成目标
        if self._is_goal_achieved(goal, context):
            return Decision(
                type=DecisionType.CONTINUE,
                reason="目标已达成",
                action="complete",
                confidence=1.0
            )

        # 3. 检查是否需要等待
        if context.state == ScreenState.LOADING:
            return Decision(
                type=DecisionType.WAIT,
                reason="正在加载中",
                action="wait",
                params={"duration": 2.0},
                confidence=0.9
            )

        # 4. 检查重试次数
        if retry_count >= 3:
            return Decision(
                type=DecisionType.ADAPT,
                reason="多次重试失败，需要调整策略",
                action="change_strategy",
                confidence=0.7
            )

        # 5. 根据状态决策
        decision = self._state_based_decision(context, goal)

        self.decision_history.append(decision)

        return decision

    def learn_from_result(
        self,
        context: Context,
        decision: Decision,
        success: bool,
        duration: float
    ):
        """
        从结果中学习

        记录成功/失败模式，用于未来优化

        Args:
            context: 执行时的上下文
            decision: 做出的决策
            success: 是否成功
            duration: 执行耗时
        """
        pattern = {
            "state": context.state.value,
            "decision": decision.type.value,
            "success": success,
            "duration": duration,
            "timestamp": time.time()
        }

        if success:
            self._success_patterns.append(pattern)
            logger.info(f"Learned success pattern: {pattern}")
        else:
            self._failure_patterns.append(pattern)
            logger.info(f"Learned failure pattern: {pattern}")

    def get_insights(self) -> Dict:
        """
        获取洞察

        分析历史数据，提供优化建议

        Returns:
            洞察报告
        """
        insights = {
            "total_contexts": len(self.context_history),
            "total_anomalies": len(self.anomaly_history),
            "total_decisions": len(self.decision_history),
            "state_transitions": self._state_transitions,
            "success_rate": self._calculate_success_rate(),
            "common_anomalies": self._get_common_anomalies(),
            "suggestions": self._generate_suggestions()
        }

        return insights

    # ============ 内部方法 ============

    def _detect_elements(self, screenshot: Image.Image) -> List[Dict]:
        """检测界面元素"""
        finder = get_finder()
        elements = []

        # 检测常见元素类型
        element_types = [
            ("button", "按钮"),
            ("input", "输入框"),
            ("link", "链接"),
            ("text", "文本"),
            ("image", "图片"),
            ("icon", "图标")
        ]

        for elem_type, name in element_types:
            # 这里可以集成具体的元素检测逻辑
            pass

        return elements

    def _extract_text(self, screenshot: Image.Image) -> str:
        """提取文字内容"""
        # 使用 OCR 提取文字
        try:
            from .enhanced_ocr import EnhancedOCR
            ocr = EnhancedOCR()
            result = ocr.recognize(screenshot)
            return result.get("text", "")
        except:
            return ""

    def _analyze_layout(self, elements: List[Dict]) -> str:
        """分析布局"""
        if not elements:
            return "empty"

        # 根据元素分布判断布局
        # 例如：表单布局、列表布局、网格布局等
        return "standard"

    def _determine_state(
        self,
        description: str,
        elements: List[Dict],
        text: str
    ) -> Tuple[ScreenState, float]:
        """
        判断屏幕状态

        根据描述、元素、文字综合判断
        """
        text_lower = text.lower()
        desc_lower = description.lower()

        # 错误检测
        error_keywords = ["错误", "error", "失败", "fail", "异常", "exception"]
        if any(kw in text_lower or kw in desc_lower for kw in error_keywords):
            return ScreenState.ERROR, 0.9

        # 登录检测
        login_keywords = ["登录", "login", "用户名", "username", "密码", "password"]
        if any(kw in text_lower or kw in desc_lower for kw in login_keywords):
            return ScreenState.LOGIN, 0.85

        # 加载检测
        loading_keywords = ["加载", "loading", "请稍候", "please wait", "..."]
        if any(kw in text_lower or kw in desc_lower for kw in loading_keywords):
            return ScreenState.LOADING, 0.8

        # 成功检测
        success_keywords = ["成功", "success", "完成", "done", "✓", "✔"]
        if any(kw in text_lower or kw in desc_lower for kw in success_keywords):
            return ScreenState.SUCCESS, 0.85

        # 弹窗检测
        if "弹窗" in desc_lower or "dialog" in desc_lower:
            return ScreenState.POPUP, 0.75

        # 确认对话框
        confirm_keywords = ["确定", "确认", "confirm", "ok", "yes", "no"]
        if any(kw in text_lower for kw in confirm_keywords):
            return ScreenState.CONFIRM, 0.7

        # 表单检测
        form_keywords = ["输入", "input", "填写", "form"]
        if any(kw in text_lower for kw in form_keywords):
            return ScreenState.FORM, 0.7

        # 默认主界面
        return ScreenState.MAIN, 0.5

    def _is_error_dialog(self, context: Context) -> bool:
        """是否是错误对话框"""
        error_indicators = [
            context.state == ScreenState.ERROR,
            "错误" in context.text_content,
            "error" in context.text_content.lower(),
            "exception" in context.text_content.lower()
        ]
        return any(error_indicators)

    def _is_timeout(self, context: Context) -> bool:
        """是否超时"""
        # 检查是否长时间处于加载状态
        if len(self.context_history) < 3:
            return False

        recent = self.context_history[-3:]
        if all(c.state == ScreenState.LOADING for c in recent):
            # 如果连续3次都是加载状态，认为超时
            time_span = recent[-1].timestamp - recent[0].timestamp
            return time_span > 10.0  # 10秒

        return False

    def _is_crash(self, context: Context) -> bool:
        """是否崩溃"""
        # 检测应用无响应、白屏等
        crash_indicators = [
            "无响应" in context.text_content,
            "not responding" in context.text_content.lower(),
            context.layout == "empty" and len(context.elements) == 0
        ]
        return any(crash_indicators)

    def _is_network_error(self, context: Context) -> bool:
        """是否网络错误"""
        network_keywords = [
            "网络", "network", "连接", "connection",
            "超时", "timeout", "无法访问", "unreachable"
        ]
        return any(kw in context.text_content.lower() for kw in network_keywords)

    def _check_unexpected_state(self, context: Context) -> Optional[str]:
        """检查意外状态"""
        # 检查是否与预期状态不符
        if len(self.context_history) < 2:
            return None

        # 简单的意外检测：状态频繁跳变
        recent_states = [c.state for c in self.context_history[-5:]]
        unique_states = set(recent_states)

        if len(unique_states) > 3:
            return f"状态频繁跳变: {[s.value for s in recent_states]}"

        return None

    def _handle_anomaly(self, anomaly: Anomaly, retry_count: int) -> Decision:
        """处理异常"""
        if anomaly.type == AnomalyType.ERROR_DIALOG:
            if retry_count < 3:
                return Decision(
                    type=DecisionType.RETRY,
                    reason=f"遇到错误对话框: {anomaly.description}",
                    action="dismiss_dialog_and_retry",
                    confidence=0.7
                )
            else:
                return Decision(
                    type=DecisionType.ABORT,
                    reason="多次重试仍遇到错误",
                    action="abort",
                    confidence=0.9
                )

        elif anomaly.type == AnomalyType.TIMEOUT:
            return Decision(
                type=DecisionType.WAIT,
                reason="操作超时，继续等待",
                action="wait",
                params={"duration": 5.0},
                confidence=0.6
            )

        elif anomaly.type == AnomalyType.CRASH:
            return Decision(
                type=DecisionType.ABORT,
                reason="应用崩溃",
                action="restart_application",
                confidence=0.95
            )

        elif anomaly.type == AnomalyType.NETWORK_ERROR:
            return Decision(
                type=DecisionType.RETRY,
                reason="网络错误",
                action="retry_with_delay",
                params={"delay": 3.0},
                confidence=0.6
            )

        else:
            return Decision(
                type=DecisionType.ADAPT,
                reason=f"未知异常: {anomaly.description}",
                action="analyze_and_adapt",
                confidence=0.5
            )

    def _is_goal_achieved(self, goal: str, context: Context) -> bool:
        """检查目标是否达成"""
        # 简单的目标检测
        goal_keywords = goal.lower().split()
        text_lower = context.text_content.lower()

        # 如果目标关键词都在文本中，认为达成
        success_indicators = ["成功", "完成", "done", "success", "saved"]
        return any(ind in text_lower for ind in success_indicators)

    def _state_based_decision(self, context: Context, goal: str) -> Decision:
        """基于状态的决策"""
        state_decisions = {
            ScreenState.LOGIN: Decision(
                type=DecisionType.CONTINUE,
                reason="在登录界面，需要输入凭证",
                action="fill_credentials",
                confidence=0.8
            ),
            ScreenState.POPUP: Decision(
                type=DecisionType.CONTINUE,
                reason="有弹窗需要处理",
                action="handle_popup",
                confidence=0.75
            ),
            ScreenState.CONFIRM: Decision(
                type=DecisionType.CONTINUE,
                reason="需要确认操作",
                action="confirm",
                confidence=0.8
            ),
            ScreenState.FORM: Decision(
                type=DecisionType.CONTINUE,
                reason="需要填写表单",
                action="fill_form",
                confidence=0.8
            )
        }

        return state_decisions.get(
            context.state,
            Decision(
                type=DecisionType.CONTINUE,
                reason="继续执行",
                action="proceed",
                confidence=0.6
            )
        )

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        total = len(self._success_patterns) + len(self._failure_patterns)
        if total == 0:
            return 0.0
        return len(self._success_patterns) / total

    def _get_common_anomalies(self) -> List[Dict]:
        """获取常见异常"""
        from collections import Counter

        types = [a.type.value for a in self.anomaly_history]
        counter = Counter(types)

        return [
            {"type": t, "count": c}
            for t, c in counter.most_common(5)
        ]

    def _generate_suggestions(self) -> List[str]:
        """生成优化建议"""
        suggestions = []

        # 基于成功率
        success_rate = self._calculate_success_rate()
        if success_rate < 0.5:
            suggestions.append("成功率较低，建议检查操作步骤或增加等待时间")
        elif success_rate > 0.9:
            suggestions.append("成功率很高，可以考虑减少确认步骤")

        # 基于常见异常
        common = self._get_common_anomalies()
        if common:
            top_anomaly = common[0]
            suggestions.append(f"常见异常 '{top_anomaly['type']}' 出现 {top_anomaly['count']} 次，建议针对性优化")

        # 基于状态转移
        if len(self._state_transitions) > 10:
            suggestions.append("状态跳变较多，建议增加稳定性检查")

        return suggestions


# ==================== 便捷函数 ====================

def analyze_screen() -> Context:
    """快速分析屏幕"""
    brain = SmartBrain()
    return brain.analyze_context()


def check_anomaly() -> Optional[Anomaly]:
    """快速检查异常"""
    brain = SmartBrain()
    return brain.detect_anomaly()


def make_decision(goal: str) -> Decision:
    """快速决策"""
    brain = SmartBrain()
    return brain.decide_action(goal)
