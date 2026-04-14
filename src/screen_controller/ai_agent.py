"""
AI Agent - AI 智能代理
实时观察屏幕 + 理解指令 + 自动执行

用法:
    from screen_controller.ai_agent import AIAgent

    agent = AIAgent()
    agent.run("帮我把这个表格的数据复制到Excel")
"""

import time
import json
import logging
import threading
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from PIL import Image

from .enhanced_screenshot import capture_screen, capture_to_base64
from .vision import vision_describe, vision_find, vision_analyze
from .screen_controller import click, type_text, press_hotkey, move_mouse
from .performance import ScreenshotCache

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """动作类型"""
    CLICK = "click"           # 点击
    TYPE = "type"             # 输入文字
    HOTKEY = "hotkey"         # 快捷键
    MOVE = "move"             # 移动鼠标
    WAIT = "wait"             # 等待
    SCROLL = "scroll"         # 滚动
    DRAG = "drag"             # 拖拽
    SCREENSHOT = "screenshot" # 截图
    FIND = "find"             # 查找元素
    DECISION = "decision"     # 决策点


@dataclass
class Action:
    """执行动作"""
    action_type: ActionType
    target: str = ""          # 目标描述
    params: Dict = field(default_factory=dict)
    reason: str = ""          # 执行原因
    retry: int = 3            # 重试次数


@dataclass
class Observation:
    """观察结果"""
    timestamp: float
    screenshot: Image.Image
    description: str          # AI 对屏幕的描述
    elements: List[Dict]      # 检测到的元素
    context: Dict             # 上下文信息


class AIAgent:
    """
    AI 智能代理

    核心循环: 观察 → 思考 → 行动 → 反馈

    功能:
    - 实时观察屏幕
    - 理解自然语言指令
    - 自动规划执行步骤
    - 实时反馈执行结果
    """

    def __init__(
        self,
        observation_interval: float = 2.0,  # 观察间隔(秒)
        max_steps: int = 50,                 # 最大执行步数
        auto_confirm: bool = False,          # 是否自动确认
        verbose: bool = True                 # 是否打印详细日志
    ):
        self.observation_interval = observation_interval
        self.max_steps = max_steps
        self.auto_confirm = auto_confirm
        self.verbose = verbose

        self.current_task: Optional[str] = None
        self.action_history: List[Action] = []
        self.observation_history: List[Observation] = []
        self.step_count = 0
        self._running = False
        self._lock = threading.Lock()

        # 回调函数
        self.on_observation: Optional[Callable] = None
        self.on_action: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    def observe(self) -> Observation:
        """
        观察当前屏幕状态

        Returns:
            Observation 对象
        """
        # 截图
        screenshot = capture_screen()

        # 使用 Vision 模块分析屏幕
        description = vision_describe(screenshot)

        # 检测界面元素
        elements = self._detect_elements(screenshot)

        obs = Observation(
            timestamp=time.time(),
            screenshot=screenshot,
            description=description,
            elements=elements,
            context=self._build_context()
        )

        self.observation_history.append(obs)

        if self.verbose:
            print(f"\n👁️ 观察: {description[:100]}...")

        if self.on_observation:
            self.on_observation(obs)

        return obs

    def think(self, observation: Observation, task: str) -> List[Action]:
        """
        根据观察和任务，思考下一步行动

        Args:
            observation: 当前观察结果
            task: 任务描述

        Returns:
            行动计划列表
        """
        # 构建提示词
        prompt = self._build_think_prompt(observation, task)

        # 这里调用 AI 模型进行思考
        # 实际实现中，可以通过已有的 AI 集成调用 Claude/OpenClaw 等
        actions = self._parse_task_to_actions(task, observation)

        if self.verbose:
            print(f"\n🧠 思考: 计划执行 {len(actions)} 个动作")
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action.action_type.value}: {action.target}")

        return actions

    def act(self, action: Action) -> bool:
        """
        执行动作

        Args:
            action: 要执行的动作

        Returns:
            是否执行成功
        """
        if self.verbose:
            print(f"\n🤖 执行: {action.action_type.value} - {action.target}")
            if action.reason:
                print(f"   原因: {action.reason}")

        success = False

        try:
            if action.action_type == ActionType.CLICK:
                success = self._execute_click(action)
            elif action.action_type == ActionType.TYPE:
                success = self._execute_type(action)
            elif action.action_type == ActionType.HOTKEY:
                success = self._execute_hotkey(action)
            elif action.action_type == ActionType.MOVE:
                success = self._execute_move(action)
            elif action.action_type == ActionType.WAIT:
                success = self._execute_wait(action)
            elif action.action_type == ActionType.SCROLL:
                success = self._execute_scroll(action)
            elif action.action_type == ActionType.FIND:
                success = self._execute_find(action)
            elif action.action_type == ActionType.SCREENSHOT:
                success = self._execute_screenshot(action)
            else:
                logger.warning(f"未知动作类型: {action.action_type}")
                success = False

            if success:
                self.action_history.append(action)
                if self.on_action:
                    self.on_action(action, success)

            return success

        except Exception as e:
            logger.error(f"执行动作失败: {e}")
            if self.on_error:
                self.on_error(action, e)
            return False

    def run(self, task: str) -> Dict:
        """
        运行任务

        Args:
            task: 自然语言描述的任务

        Returns:
            执行结果
        """
        print(f"\n{'='*50}")
        print(f"🎯 任务: {task}")
        print(f"{'='*50}\n")

        self.current_task = task
        self.step_count = 0
        self._running = True

        result = {
            "task": task,
            "success": False,
            "steps": 0,
            "actions": [],
            "message": ""
        }

        try:
            while self._running and self.step_count < self.max_steps:
                # 1. 观察
                observation = self.observe()

                # 2. 思考
                actions = self.think(observation, task)

                if not actions:
                    print("\n✅ 任务完成！")
                    result["success"] = True
                    result["message"] = "任务执行成功"
                    break

                # 3. 行动
                for action in actions:
                    if not self._running:
                        break

                    # 如果不是自动确认，询问用户
                    if not self.auto_confirm:
                        if not self._confirm_action(action):
                            print("\n⏹️ 用户取消")
                            result["message"] = "用户取消"
                            self._running = False
                            break

                    success = self.act(action)

                    if not success and action.retry > 0:
                        print(f"   重试中... ({action.retry}次剩余)")
                        action.retry -= 1
                        time.sleep(1)
                        success = self.act(action)

                    if success:
                        time.sleep(self.observation_interval)

                self.step_count += 1

                # 检查任务是否完成
                if self._is_task_complete(task):
                    print("\n✅ 任务完成！")
                    result["success"] = True
                    result["message"] = "任务执行成功"
                    break

            if self.step_count >= self.max_steps:
                result["message"] = f"达到最大步数限制 ({self.max_steps})"

        except Exception as e:
            logger.error(f"任务执行异常: {e}")
            result["message"] = f"执行异常: {e}"

        finally:
            self._running = False
            result["steps"] = self.step_count
            result["actions"] = [a.action_type.value for a in self.action_history]

            if self.on_complete:
                self.on_complete(result)

        print(f"\n{'='*50}")
        print(f"📊 结果: {'成功' if result['success'] else '失败'}")
        print(f"   执行了 {result['steps']} 步")
        print(f"   共 {len(result['actions'])} 个动作")
        print(f"{'='*50}\n")

        return result

    def stop(self):
        """停止执行"""
        self._running = False
        print("\n⏹️ 停止执行")

    # ============ 内部方法 ============

    def _detect_elements(self, screenshot: Image.Image) -> List[Dict]:
        """检测屏幕元素"""
        # 使用 UI 元素查找器
        from .ui_element_finder import get_finder
        finder = get_finder()

        elements = []
        # 这里可以集成更多的元素检测逻辑
        # 例如：按钮、输入框、文本等

        return elements

    def _build_context(self) -> Dict:
        """构建上下文信息"""
        return {
            "step_count": self.step_count,
            "action_history": [a.action_type.value for a in self.action_history[-5:]],
            "current_task": self.current_task
        }

    def _build_think_prompt(self, observation: Observation, task: str) -> str:
        """构建思考提示词"""
        return f"""
任务: {task}

当前屏幕描述:
{observation.description}

检测到的元素:
{json.dumps(observation.elements, ensure_ascii=False, indent=2)}

历史动作:
{observation.context['action_history']}

请分析当前状态，规划下一步行动。
"""

    def _parse_task_to_actions(self, task: str, observation: Observation) -> List[Action]:
        """
        将任务解析为动作序列

        这是一个简化版本，实际应该调用 AI 模型进行解析
        """
        actions = []
        task_lower = task.lower()

        # 简单的规则匹配（实际应该用 AI 模型）
        if "点击" in task or "打开" in task:
            target = task.replace("点击", "").replace("打开", "").strip()
            actions.append(Action(
                action_type=ActionType.FIND,
                target=target,
                reason=f"查找目标: {target}"
            ))
            actions.append(Action(
                action_type=ActionType.CLICK,
                target=target,
                reason=f"点击: {target}"
            ))

        elif "输入" in task or "填写" in task:
            actions.append(Action(
                action_type=ActionType.TYPE,
                target="输入框",
                params={"text": task},
                reason="输入文本"
            ))

        elif "复制" in task:
            actions.append(Action(
                action_type=ActionType.HOTKEY,
                target="ctrl+c",
                reason="复制选中内容"
            ))

        elif "粘贴" in task:
            actions.append(Action(
                action_type=ActionType.HOTKEY,
                target="ctrl+v",
                reason="粘贴内容"
            ))

        elif "截图" in task:
            actions.append(Action(
                action_type=ActionType.SCREENSHOT,
                target="screen",
                reason="截取屏幕"
            ))

        else:
            # 默认动作：截图观察
            actions.append(Action(
                action_type=ActionType.SCREENSHOT,
                target="screen",
                reason="观察当前状态"
            ))

        return actions

    def _confirm_action(self, action: Action) -> bool:
        """询问用户确认"""
        print(f"\n🤔 即将执行: {action.action_type.value} - {action.target}")
        if action.reason:
            print(f"   原因: {action.reason}")

        response = input("   确认执行? [Y/n/s(stop)]: ").strip().lower()

        if response == 's':
            self.stop()
            return False

        return response in ['', 'y', 'yes']

    def _is_task_complete(self, task: str) -> bool:
        """检查任务是否完成"""
        # 简化判断：如果最近几步没有新动作，认为完成
        if len(self.action_history) < 3:
            return False

        recent = self.action_history[-3:]
        # 检查是否有重复动作
        return len(set(a.action_type for a in recent)) == 1

    # ============ 动作执行方法 ============

    def _execute_click(self, action: Action) -> bool:
        """执行点击"""
        try:
            # 如果 target 是坐标
            if ',' in action.target:
                x, y = map(int, action.target.split(','))
                move_mouse(x, y)
                click(x, y)
            else:
                # 使用 vision 查找元素位置
                pos = vision_find(action.target)
                if pos:
                    click(pos[0], pos[1])
                    return True
                return False
            return True
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False

    def _execute_type(self, action: Action) -> bool:
        """执行输入"""
        try:
            text = action.params.get("text", action.target)
            type_text(text)
            return True
        except Exception as e:
            logger.error(f"输入失败: {e}")
            return False

    def _execute_hotkey(self, action: Action) -> bool:
        """执行快捷键"""
        try:
            keys = action.target.split('+')
            press_hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"快捷键失败: {e}")
            return False

    def _execute_move(self, action: Action) -> bool:
        """执行移动"""
        try:
            if ',' in action.target:
                x, y = map(int, action.target.split(','))
                move_mouse(x, y)
                return True
            return False
        except Exception as e:
            logger.error(f"移动失败: {e}")
            return False

    def _execute_wait(self, action: Action) -> bool:
        """执行等待"""
        try:
            seconds = action.params.get("seconds", 1)
            time.sleep(seconds)
            return True
        except Exception as e:
            logger.error(f"等待失败: {e}")
            return False

    def _execute_scroll(self, action: Action) -> bool:
        """执行滚动"""
        try:
            # 使用 pyautogui 或类似库实现滚动
            import pyautogui
            amount = action.params.get("amount", 3)
            pyautogui.scroll(amount * 100)
            return True
        except Exception as e:
            logger.error(f"滚动失败: {e}")
            return False

    def _execute_find(self, action: Action) -> bool:
        """执行查找"""
        try:
            pos = vision_find(action.target)
            return pos is not None
        except Exception as e:
            logger.error(f"查找失败: {e}")
            return False

    def _execute_screenshot(self, action: Action) -> bool:
        """执行截图"""
        try:
            capture_screen()
            return True
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return False


# ==================== 便捷函数 ====================

def ai_do(task: str, auto: bool = False) -> Dict:
    """
    快速执行 AI 任务

    Args:
        task: 任务描述
        auto: 是否自动执行（不询问确认）

    Returns:
        执行结果

    示例:
        >>> ai_do("点击确定按钮")
        >>> ai_do("帮我把这个表格复制到Excel", auto=True)
    """
    agent = AIAgent(auto_confirm=auto)
    return agent.run(task)


class VoiceAIAgent(AIAgent):
    """
    语音 AI 代理
    支持语音输入指令
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_enabled = False
        self._init_voice()

    def _init_voice(self):
        """初始化语音识别"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.voice_enabled = True
            print("🎤 语音识别已启用")
        except ImportError:
            print("⚠️ 未安装语音识别库，使用文字输入")
            print("   pip install SpeechRecognition pyaudio")

    def listen(self) -> str:
        """监听语音输入"""
        if not self.voice_enabled:
            return input("请输入指令: ")

        try:
            import speech_recognition as sr

            with self.microphone as source:
                print("🎤 正在聆听...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10)

            print("📝 识别中...")
            text = self.recognizer.recognize_google(audio, language="zh-CN")
            print(f"👂 听到: {text}")
            return text

        except Exception as e:
            print(f"语音识别失败: {e}")
            return input("请输入指令: ")

    def run_interactive(self):
        """交互式运行"""
        print("\n" + "="*50)
        print("🤖 AI 智能代理 - 交互模式")
        print("="*50)
        print("说 '退出' 或 'quit' 结束\n")

        while True:
            task = self.listen()

            if task.lower() in ['退出', 'quit', 'exit', 'q']:
                print("👋 再见！")
                break

            if task.strip():
                self.run(task)
                print("\n" + "-"*50 + "\n")


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例 1: 简单任务
    result = ai_do("截图并描述当前屏幕")
    print(result)

    # 示例 2: 语音交互模式
    # agent = VoiceAIAgent()
    # agent.run_interactive()
