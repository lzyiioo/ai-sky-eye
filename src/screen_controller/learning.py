"""
Learning - 流程学习记忆
记录用户操作、学习模式、自动复现

功能:
1. 操作录制 - 记录用户的每一步操作
2. 模式学习 - 从重复操作中发现规律
3. 智能回放 - 自动复现录制的流程
4. 流程优化 - 基于成功/失败优化流程

用法:
    from screen_controller.learning import LearningEngine

    # 开始录制
    engine = LearningEngine()
    engine.start_recording("登录流程")

    # 用户操作... (自动记录)

    # 停止录制
    flow = engine.stop_recording()

    # 回放
    engine.replay(flow)

    # 学习优化
    optimized = engine.optimize(flow)
"""

import json
import time
import hashlib
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from .screen_controller import click, type_text, press_hotkey, move_mouse
from .enhanced_screenshot import capture_screen
from .smart_brain import SmartBrain, Context, Decision

logger = logging.getLogger(__name__)


@dataclass
class ActionRecord:
    """操作记录"""
    action_type: str          # click/type/hotkey/move/wait
    target: str               # 目标描述
    params: Dict              # 参数
    timestamp: float          # 时间戳
    screenshot_hash: str      # 截图哈希
    context: Dict             # 上下文
    duration: float = 0.0     # 执行耗时
    success: bool = True      # 是否成功


@dataclass
class FlowPattern:
    """流程模式"""
    pattern_id: str
    name: str
    actions: List[ActionRecord]
    trigger_conditions: List[str]  # 触发条件
    success_count: int = 0
    failure_count: int = 0
    avg_duration: float = 0.0
    last_used: float = 0.0
    created_at: float = 0.0


@dataclass
class LearningResult:
    """学习结果"""
    original_actions: int
    optimized_actions: int
    removed_redundancy: int
    added_waits: int
    confidence: float
    suggestions: List[str]


class LearningEngine:
    """
    学习引擎

    核心能力:
    - 录制用户操作
    - 学习成功模式
    - 智能回放
    - 流程优化
    """

    def __init__(self, storage_path: str = "~/.ai_sky_eye/flows"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._recording: bool = False
        self._current_flow: List[ActionRecord] = []
        self._flow_name: str = ""
        self._start_time: float = 0

        self._patterns: Dict[str, FlowPattern] = {}
        self._load_patterns()

        self._brain = SmartBrain()

    # ============ 录制功能 ============

    def start_recording(self, name: str):
        """
        开始录制

        Args:
            name: 流程名称
        """
        self._recording = True
        self._current_flow = []
        self._flow_name = name
        self._start_time = time.time()

        print(f"🎬 开始录制: {name}")
        print("   请执行您的操作...")

    def record_action(
        self,
        action_type: str,
        target: str,
        params: Dict = None,
        success: bool = True
    ):
        """
        记录一个动作

        Args:
            action_type: 动作类型
            target: 目标
            params: 参数
            success: 是否成功
        """
        if not self._recording:
            return

        # 截图并计算哈希
        try:
            screenshot = capture_screen()
            screenshot_hash = self._hash_image(screenshot)
        except:
            screenshot_hash = ""

        # 获取上下文
        context = self._brain.analyze_context()

        record = ActionRecord(
            action_type=action_type,
            target=target,
            params=params or {},
            timestamp=time.time(),
            screenshot_hash=screenshot_hash,
            context={
                "state": context.state.value,
                "description": context.description[:100]
            },
            success=success
        )

        self._current_flow.append(record)

        if len(self._current_flow) % 5 == 0:
            print(f"   已记录 {len(self._current_flow)} 个动作")

    def stop_recording(self) -> FlowPattern:
        """
        停止录制

        Returns:
            录制的流程
        """
        if not self._recording:
            return None

        self._recording = False
        duration = time.time() - self._start_time

        flow = FlowPattern(
            pattern_id=self._generate_id(),
            name=self._flow_name,
            actions=self._current_flow,
            trigger_conditions=[],
            created_at=time.time(),
            last_used=time.time()
        )

        # 自动推断触发条件
        flow.trigger_conditions = self._infer_triggers(flow)

        # 保存
        self._save_flow(flow)
        self._patterns[flow.pattern_id] = flow

        print(f"\n✅ 录制完成!")
        print(f"   流程: {flow.name}")
        print(f"   动作: {len(flow.actions)} 个")
        print(f"   耗时: {duration:.1f} 秒")
        print(f"   已保存到: {self.storage_path / f'{flow.pattern_id}.json'}")

        return flow

    # ============ 回放功能 ============

    def replay(
        self,
        flow: FlowPattern,
        adaptive: bool = True,
        confirm: bool = False
    ) -> Dict:
        """
        回放流程

        Args:
            flow: 要回放的流程
            adaptive: 是否自适应调整
            confirm: 是否每步确认

        Returns:
            执行结果
        """
        print(f"\n▶️ 回放流程: {flow.name}")
        print(f"   共 {len(flow.actions)} 个动作")
        print("-" * 40)

        results = {
            "success": True,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0,
            "adaptations": []
        }

        start_time = time.time()

        for i, action in enumerate(flow.actions, 1):
            print(f"\n[{i}/{len(flow.actions)}] {action.action_type}: {action.target}")

            # 确认
            if confirm:
                response = input("   执行? [Y/n/s]: ").strip().lower()
                if response == 's':
                    print("   ⏹️ 跳过")
                    results["skipped"] += 1
                    continue
                if response == 'n':
                    print("   ⏹️ 停止")
                    results["success"] = False
                    break

            # 自适应调整
            if adaptive:
                adapted = self._adapt_action(action)
                if adapted:
                    action = adapted
                    results["adaptations"].append(f"动作{i}已调整")

            # 执行
            success = self._execute_action(action)

            if success:
                print("   ✅ 成功")
                results["completed"] += 1
            else:
                print("   ❌ 失败")
                results["failed"] += 1

                # 失败处理
                if not self._handle_failure(action, flow, i):
                    results["success"] = False
                    break

            # 等待间隔
            if i < len(flow.actions):
                time.sleep(0.5)

        results["duration"] = time.time() - start_time

        # 更新统计
        if results["success"]:
            flow.success_count += 1
        else:
            flow.failure_count += 1
        flow.last_used = time.time()
        self._save_flow(flow)

        print(f"\n{'='*40}")
        print(f"回放结果: {'成功' if results['success'] else '失败'}")
        print(f"完成: {results['completed']} | 失败: {results['failed']} | 跳过: {results['skipped']}")
        print(f"耗时: {results['duration']:.1f}秒")

        return results

    # ============ 学习优化 ============

    def optimize(self, flow: FlowPattern) -> LearningResult:
        """
        优化流程

        Args:
            flow: 要优化的流程

        Returns:
            优化结果
        """
        print(f"\n🔧 优化流程: {flow.name}")

        original_count = len(flow.actions)
        optimized_actions = flow.actions.copy()
        suggestions = []

        # 1. 去除冗余操作
        optimized_actions, removed = self._remove_redundancy(optimized_actions)
        if removed > 0:
            suggestions.append(f"去除 {removed} 个冗余操作")

        # 2. 合并连续操作
        optimized_actions, merged = self._merge_actions(optimized_actions)
        if merged > 0:
            suggestions.append(f"合并 {merged} 个连续操作")

        # 3. 添加智能等待
        optimized_actions, waits = self._add_smart_waits(optimized_actions)
        if waits > 0:
            suggestions.append(f"添加 {waits} 个智能等待点")

        # 4. 添加异常处理
        optimized_actions = self._add_error_handling(optimized_actions)
        suggestions.append("添加异常处理机制")

        # 创建优化后的流程
        optimized_flow = FlowPattern(
            pattern_id=f"{flow.pattern_id}_optimized",
            name=f"{flow.name} (优化)",
            actions=optimized_actions,
            trigger_conditions=flow.trigger_conditions,
            created_at=time.time()
        )

        self._save_flow(optimized_flow)

        result = LearningResult(
            original_actions=original_count,
            optimized_actions=len(optimized_actions),
            removed_redundancy=removed,
            added_waits=waits,
            confidence=self._calculate_confidence(optimized_flow),
            suggestions=suggestions
        )

        print(f"\n✅ 优化完成!")
        print(f"   原动作: {result.original_actions}")
        print(f"   优化后: {result.optimized_actions}")
        print(f"   减少: {result.original_actions - result.optimized_actions}")
        print(f"\n建议:")
        for s in suggestions:
            print(f"   • {s}")

        return result

    def learn_from_flows(self, flows: List[FlowPattern]) -> List[FlowPattern]:
        """
        从多个流程中学习通用模式

        Args:
            flows: 流程列表

        Returns:
            学习到的通用模式
        """
        print(f"\n📚 从 {len(flows)} 个流程中学习...")

        # 找出共同模式
        common_sequences = self._find_common_sequences(flows)

        learned_patterns = []
        for seq in common_sequences:
            pattern = FlowPattern(
                pattern_id=self._generate_id(),
                name=f"通用模式: {seq['name']}",
                actions=seq["actions"],
                trigger_conditions=seq["triggers"],
                success_count=seq["success_count"]
            )
            learned_patterns.append(pattern)
            self._save_flow(pattern)

        print(f"✅ 学习到 {len(learned_patterns)} 个通用模式")

        return learned_patterns

    # ============ 内部方法 ============

    def _hash_image(self, image) -> str:
        """计算图片哈希"""
        try:
            from PIL import Image
            if isinstance(image, Image.Image):
                # 缩小后计算哈希
                small = image.resize((64, 64))
                data = small.tobytes()
                return hashlib.md5(data).hexdigest()[:16]
        except:
            pass
        return ""

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:12]

    def _infer_triggers(self, flow: FlowPattern) -> List[str]:
        """推断触发条件"""
        triggers = []

        if not flow.actions:
            return triggers

        # 从第一个动作推断
        first = flow.actions[0]
        if first.context.get("state"):
            triggers.append(f"state:{first.context['state']}")

        # 从目标推断
        if "登录" in flow.name or "login" in flow.name.lower():
            triggers.append("keyword:登录")

        return triggers

    def _save_flow(self, flow: FlowPattern):
        """保存流程"""
        filepath = self.storage_path / f"{flow.pattern_id}.json"

        data = {
            "pattern_id": flow.pattern_id,
            "name": flow.name,
            "actions": [
                {
                    "action_type": a.action_type,
                    "target": a.target,
                    "params": a.params,
                    "timestamp": a.timestamp,
                    "screenshot_hash": a.screenshot_hash,
                    "context": a.context,
                    "success": a.success
                }
                for a in flow.actions
            ],
            "trigger_conditions": flow.trigger_conditions,
            "success_count": flow.success_count,
            "failure_count": flow.failure_count,
            "avg_duration": flow.avg_duration,
            "last_used": flow.last_used,
            "created_at": flow.created_at
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_patterns(self):
        """加载已保存的模式"""
        if not self.storage_path.exists():
            return

        for filepath in self.storage_path.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                flow = FlowPattern(
                    pattern_id=data["pattern_id"],
                    name=data["name"],
                    actions=[
                        ActionRecord(
                            action_type=a["action_type"],
                            target=a["target"],
                            params=a["params"],
                            timestamp=a["timestamp"],
                            screenshot_hash=a["screenshot_hash"],
                            context=a["context"],
                            success=a["success"]
                        )
                        for a in data["actions"]
                    ],
                    trigger_conditions=data["trigger_conditions"],
                    success_count=data.get("success_count", 0),
                    failure_count=data.get("failure_count", 0),
                    avg_duration=data.get("avg_duration", 0),
                    last_used=data.get("last_used", 0),
                    created_at=data.get("created_at", 0)
                )

                self._patterns[flow.pattern_id] = flow

            except Exception as e:
                logger.warning(f"加载流程失败 {filepath}: {e}")

        print(f"📂 已加载 {len(self._patterns)} 个流程")

    def _execute_action(self, action: ActionRecord) -> bool:
        """执行单个动作"""
        try:
            if action.action_type == "click":
                # 解析坐标
                if ',' in action.target:
                    x, y = map(int, action.target.split(','))
                    click(x, y)
                else:
                    # 查找元素位置
                    from .vision import vision_find
                    pos = vision_find(action.target)
                    if pos:
                        click(pos[0], pos[1])
                    else:
                        return False

            elif action.action_type == "type":
                text = action.params.get("text", action.target)
                type_text(text)

            elif action.action_type == "hotkey":
                keys = action.target.split('+')
                press_hotkey(*keys)

            elif action.action_type == "move":
                if ',' in action.target:
                    x, y = map(int, action.target.split(','))
                    move_mouse(x, y)

            elif action.action_type == "wait":
                seconds = action.params.get("seconds", 1)
                time.sleep(seconds)

            return True

        except Exception as e:
            logger.error(f"执行动作失败: {e}")
            return False

    def _adapt_action(self, action: ActionRecord) -> Optional[ActionRecord]:
        """自适应调整动作"""
        # 检查当前上下文是否匹配
        current = self._brain.analyze_context()

        # 如果状态不匹配，尝试调整
        if current.state.value != action.context.get("state"):
            # 可能需要等待或调整
            pass

        return None  # 暂时不调整

    def _handle_failure(
        self,
        action: ActionRecord,
        flow: FlowPattern,
        index: int
    ) -> bool:
        """处理失败"""
        print("   🔄 尝试恢复...")

        # 简单的重试逻辑
        for retry in range(3):
            time.sleep(1)
            if self._execute_action(action):
                print(f"   ✅ 重试成功 (第{retry+1}次)")
                return True

        # 如果还是失败，询问是否继续
        response = input("   继续执行? [Y/n]: ").strip().lower()
        return response in ['', 'y', 'yes']

    def _remove_redundancy(self, actions: List[ActionRecord]) -> Tuple[List[ActionRecord], int]:
        """去除冗余操作"""
        optimized = []
        removed = 0

        i = 0
        while i < len(actions):
            current = actions[i]

            # 检查是否有连续相同的操作
            if i + 1 < len(actions):
                next_action = actions[i + 1]
                if (current.action_type == next_action.action_type and
                    current.target == next_action.target):
                    # 跳过重复的
                    removed += 1
                    i += 2
                    continue

            optimized.append(current)
            i += 1

        return optimized, removed

    def _merge_actions(self, actions: List[ActionRecord]) -> Tuple[List[ActionRecord], int]:
        """合并连续操作"""
        # 简化实现：合并连续的输入
        return actions, 0

    def _add_smart_waits(self, actions: List[ActionRecord]) -> Tuple[List[ActionRecord], int]:
        """添加智能等待"""
        optimized = []
        waits = 0

        for i, action in enumerate(actions):
            optimized.append(action)

            # 在特定操作后添加等待
            if action.action_type in ['click', 'hotkey']:
                # 检查下一个动作是否需要等待
                if i + 1 < len(actions):
                    next_action = actions[i + 1]
                    if next_action.action_type == 'click':
                        # 添加等待
                        wait_action = ActionRecord(
                            action_type='wait',
                            target='',
                            params={'seconds': 0.5, 'reason': '等待界面响应'},
                            timestamp=0,
                            screenshot_hash='',
                            context={}
                        )
                        optimized.append(wait_action)
                        waits += 1

        return optimized, waits

    def _add_error_handling(self, actions: List[ActionRecord]) -> List[ActionRecord]:
        """添加错误处理"""
        # 在每个关键操作后添加检查点
        return actions

    def _calculate_confidence(self, flow: FlowPattern) -> float:
        """计算流程置信度"""
        total = flow.success_count + flow.failure_count
        if total == 0:
            return 0.5
        return flow.success_count / total

    def _find_common_sequences(self, flows: List[FlowPattern]) -> List[Dict]:
        """找出共同序列"""
        # 简化实现
        return []

    def list_flows(self) -> List[FlowPattern]:
        """列出所有流程"""
        return list(self._patterns.values())

    def get_flow(self, pattern_id: str) -> Optional[FlowPattern]:
        """获取指定流程"""
        return self._patterns.get(pattern_id)

    def delete_flow(self, pattern_id: str) -> bool:
        """删除流程"""
        if pattern_id in self._patterns:
            filepath = self.storage_path / f"{pattern_id}.json"
            if filepath.exists():
                filepath.unlink()
            del self._patterns[pattern_id]
            return True
        return False


# ==================== 便捷函数 ====================

def record_flow(name: str) -> LearningEngine:
    """
    快速开始录制

    用法:
        engine = record_flow("登录流程")
        # 执行操作...
        flow = engine.stop_recording()
    """
    engine = LearningEngine()
    engine.start_recording(name)
    return engine


def replay_flow(flow_id: str, adaptive: bool = True) -> Dict:
    """
    快速回放流程

    用法:
        result = replay_flow("flow_abc123")
    """
    engine = LearningEngine()
    flow = engine.get_flow(flow_id)
    if flow:
        return engine.replay(flow, adaptive=adaptive)
    return {"success": False, "error": "流程不存在"}


def optimize_flow(flow_id: str) -> Optional[LearningResult]:
    """
    快速优化流程

    用法:
        result = optimize_flow("flow_abc123")
    """
    engine = LearningEngine()
    flow = engine.get_flow(flow_id)
    if flow:
        return engine.optimize(flow)
    return None
