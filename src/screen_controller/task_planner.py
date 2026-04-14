"""
Task Planner - 智能任务规划模块
自然语言任务 → AI自动规划执行步骤 → 自动执行
"""

import json
import logging
import re
import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .vision import get_vision, vision_describe
from .enhanced_screenshot import capture_screen

logger = logging.getLogger(__name__)


# ==================== 任务类型 ====================

class TaskType(Enum):
    """任务类型"""
    CLICK = "click"           # 点击
    TYPE = "type"             # 输入
    WAIT = "wait"             # 等待
    FIND = "find"             # 查找
    CHECK = "check"           # 检查
    HOTKEY = "hotkey"         # 快捷键
    SCREENSHOT = "screenshot" # 截图
    CUSTOM = "custom"         # 自定义


# ==================== 任务步骤 ====================

@dataclass
class TaskStep:
    """任务步骤"""
    step_id: int
    action: str           # click/type/wait/find/check/hotkey
    target: str           # 目标描述
    params: Dict = field(default_factory=dict)
    retry: int = 3        # 重试次数
    timeout: float = 10.0 # 超时时间
    description: str = "" # 步骤描述


@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    steps_executed: int
    total_steps: int
    message: str
    details: List[Dict] = field(default_factory=list)
    error: Optional[str] = None


# ==================== 可用动作库 ====================

class ActionLibrary:
    """
    可用动作库
    映射 AI 规划的动作到实际函数
    """

    def __init__(self):
        self._actions: Dict[str, Callable] = {}
        self._register_default_actions()

    def _register_default_actions(self):
        """注册默认动作"""
        # 导入核心功能
        try:
            from .screen_controller import (
                click, move_mouse, type_text, press_hotkey,
                capture_screen, get_screen_size
            )
            from .smart_controller import SmartController

            # 鼠标操作
            self.register("click", click)
            self.register("move", move_mouse)
            self.register("double_click", lambda **p: click(**p, clicks=2))
            self.register("right_click", lambda **p: click(**p, button="right"))

            # 键盘操作
            self.register("type", type_text)
            self.register("hotkey", press_hotkey)
            self.register("press", press_hotkey)

            # 屏幕操作
            self.register("screenshot", capture_screen)
            self.register("wait", lambda **p: time.sleep(p.get("seconds", 1)))

            # 智能控制器
            self._smart_controller = SmartController()

        except ImportError as e:
            logger.warning(f"Failed to import some actions: {e}")

    def register(self, action_name: str, func: Callable):
        """注册动作"""
        self._actions[action_name.lower()] = func

    def execute(self, action: str, params: Dict) -> Any:
        """执行动作"""
        action_lower = action.lower()

        if action_lower not in self._actions:
            raise ValueError(f"Unknown action: {action}")

        func = self._actions[action_lower]
        return func(**params)

    def get_available_actions(self) -> List[str]:
        """获取可用动作列表"""
        return list(self._actions.keys())


# ==================== 任务规划器 ====================

class TaskPlanner:
    """
    智能任务规划器

    功能:
    - 理解用户自然语言任务
    - 自动规划执行步骤
    - 执行并处理异常
    - 自适应调整策略
    """

    def __init__(self, ai_provider: str = "claude"):
        """
        初始化任务规划器

        Args:
            ai_provider: AI 提供商
        """
        self.vision = get_vision(ai_provider)
        self.actions = ActionLibrary()
        self._history: List[Dict] = []

    def plan(self, task: str, context: Dict = None) -> List[TaskStep]:
        """
        规划任务步骤

        Args:
            task: 自然语言任务描述
            context: 额外上下文信息

        Returns:
            任务步骤列表
        """
        # 1. 理解当前屏幕状态
        screen_description = self._get_screen_context()

        # 2. 调用 AI 规划步骤
        steps = self._ai_plan(task, screen_description, context)

        return steps

    def execute(self, task: str, context: Dict = None,
                auto_confirm: bool = True) -> TaskResult:
        """
        执行任务

        Args:
            task: 自然语言任务描述
            context: 额外上下文
            auto_confirm: 是否自动确认

        Returns:
            TaskResult
        """
        logger.info(f"开始执行任务: {task}")

        # 1. 规划步骤
        steps = self.plan(task, context)
        if not steps:
            return TaskResult(
                success=False,
                steps_executed=0,
                total_steps=0,
                message="无法理解任务，请重新描述"
            )

        # 2. 确认步骤 (可选)
        if not auto_confirm:
            return TaskResult(
                success=False,
                steps_executed=0,
                total_steps=len(steps),
                message=f"任务已规划为 {len(steps)} 步，请确认执行",
                details=[{"step": s.step_id, "action": s.action, "target": s.target} for s in steps]
            )

        # 3. 执行步骤
        return self._execute_steps(steps)

    def _get_screen_context(self) -> str:
        """获取屏幕上下文"""
        try:
            return vision_describe()
        except Exception as e:
            logger.warning(f"Failed to get screen context: {e}")
            return "无法获取屏幕描述"

    def _ai_plan(self, task: str, screen_context: str,
                 context: Dict = None) -> List[TaskStep]:
        """
        AI 规划步骤

        Args:
            task: 任务描述
            screen_context: 屏幕上下文
            context: 额外上下文

        Returns:
            步骤列表
        """
        # 可用动作
        available_actions = self.actions.get_available_actions()

        prompt = f"""你是一个任务规划助手。请根据用户任务和当前屏幕状态，规划执行步骤。

## 用户任务
{task}

## 当前屏幕状态
{screen_context}

## 可用动作
{', '.join(available_actions)}

## 上下文
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

## 输出格式
请以JSON数组格式返回步骤:
[
    {{
        "step_id": 1,
        "action": "动作名",
        "target": "目标描述",
        "params": {{"参数": "值"}},
        "retry": 3,
        "timeout": 10,
        "description": "步骤描述"
    }}
]

动作说明:
- click: 点击 (params: x, y 或 name)
- type: 输入文字 (params: text)
- hotkey: 快捷键 (params: *keys)
- wait: 等待 (params: seconds)
- find: 查找元素 (params: description)
- screenshot: 截图
- move: 移动鼠标 (params: x, y)

请只返回JSON，不要其他内容。"""

        try:
            result = self.vision.client.analyze_image(
                capture_screen(),
                prompt
            )

            # 解析 JSON
            steps = self._parse_steps(result)
            return steps

        except Exception as e:
            logger.error(f"AI planning failed: {e}")
            return []

    def _parse_steps(self, result: str) -> List[TaskStep]:
        """解析 AI 返回的步骤"""
        steps = []

        try:
            # 提取 JSON
            json_match = re.search(r'\[[\s\S]*\]', result)
            if not json_match:
                return []

            data = json.loads(json_match.group())

            for item in data:
                step = TaskStep(
                    step_id=item.get("step_id", 0),
                    action=item.get("action", ""),
                    target=item.get("target", ""),
                    params=item.get("params", {}),
                    retry=item.get("retry", 3),
                    timeout=item.get("timeout", 10.0),
                    description=item.get("description", "")
                )
                steps.append(step)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse steps: {e}")

        return steps

    def _execute_steps(self, steps: List[TaskStep]) -> TaskResult:
        """执行步骤"""
        details = []
        success_count = 0

        for step in steps:
            logger.info(f"执行步骤 {step.step_id}: {step.action} - {step.target}")

            # 重试逻辑
            for attempt in range(step.retry):
                try:
                    # 执行动作
                    result = self.actions.execute(step.action, step.params)

                    details.append({
                        "step": step.step_id,
                        "action": step.action,
                        "success": True,
                        "result": str(result)
                    })
                    success_count += 1
                    break

                except Exception as e:
                    logger.warning(f"步骤 {step.step_id} 第 {attempt+1} 次失败: {e}")

                    if attempt == step.retry - 1:
                        details.append({
                            "step": step.step_id,
                            "action": step.action,
                            "success": False,
                            "error": str(e)
                        })

            # 步骤间小延迟
            time.sleep(0.3)

        # 记录到历史
        self._history.append({
            "timestamp": time.time(),
            "steps": len(steps),
            "success": success_count,
            "details": details
        })

        return TaskResult(
            success=success_count == len(steps),
            steps_executed=success_count,
            total_steps=len(steps),
            message=f"完成 {success_count}/{len(steps)} 步",
            details=details
        )

    def get_history(self) -> List[Dict]:
        """获取执行历史"""
        return self._history

    def learn_from_success(self, task: str, steps: List[TaskStep]):
        """
        从成功任务学习

        Args:
            task: 任务描述
            steps: 执行的步骤
        """
        # 可以保存到文件供后续复用
        logger.info(f"学习任务: {task}, 步骤数: {len(steps)}")


# ==================== 便捷函数 ====================

_planner_instance = None

def get_planner(ai_provider: str = "claude") -> TaskPlanner:
    """获取任务规划器实例"""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = TaskPlanner(ai_provider)
    return _planner_instance


def plan_task(task: str) -> List[TaskStep]:
    """规划任务（不执行）"""
    return get_planner().plan(task)


def execute_task(task: str, auto_confirm: bool = True) -> TaskResult:
    """执行任务"""
    return get_planner().execute(task, auto_confirm=auto_confirm)


def run(task: str) -> TaskResult:
    """快捷执行任务"""
    return execute_task(task, auto_confirm=True)
