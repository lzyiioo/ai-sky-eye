"""
Action Recorder - 操作录制回放
录制鼠标、键盘、等待操作
"""

import time
import json
import logging
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """操作类型"""
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    SCROLL = "scroll"
    KEY = "key"
    SCREENSHOT = "screenshot"


@dataclass
class RecordedAction:
    """录制的操作"""
    type: str
    params: Dict
    timestamp: float
    delay: float  # 距上个操作的延迟


class ActionRecorder:
    """操作录制器"""
    
    def __init__(self):
        self.is_recording = False
        self.actions: List[RecordedAction] = []
        self.start_time: float = 0
        self.last_action_time: float = 0
        self.on_action: Optional[Callable] = None
    
    def start(self):
        """开始录制"""
        self.is_recording = True
        self.actions = []
        self.start_time = time.time()
        self.last_action_time = self.start_time
        print("🔴 开始录制操作...")
    
    def stop(self) -> List[RecordedAction]:
        """停止录制"""
        self.is_recording = False
        print(f"⏹️ 录制结束，共 {len(self.actions)} 个操作")
        return self.actions
    
    def _record(self, action_type: ActionType, params: Dict):
        """记录操作"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        delay = current_time - self.last_action_time
        
        action = RecordedAction(
            type=action_type.value,
            params=params,
            timestamp=current_time - self.start_time,
            delay=delay
        )
        
        self.actions.append(action)
        self.last_action_time = current_time
        
        if self.on_action:
            self.on_action(action)
    
    def record_click(self, x: int, y: int, button: str = "left"):
        """记录点击"""
        self._record(ActionType.CLICK, {"x": x, "y": y, "button": button})
    
    def record_type(self, text: str):
        """记录输入"""
        self._record(ActionType.TYPE, {"text": text})
    
    def record_wait(self, duration: float):
        """记录等待"""
        self._record(ActionType.WAIT, {"duration": duration})
    
    def record_key(self, key: str):
        """记录按键"""
        self._record(ActionType.KEY, {"key": key})
    
    def save(self, filepath: str):
        """保存录制"""
        data = {
            "recorded_at": datetime.now().isoformat(),
            "actions": [asdict(a) for a in self.actions]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 已保存到: {filepath}")
    
    def load(self, filepath: str) -> List[RecordedAction]:
        """加载录制"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.actions = [
            RecordedAction(
                type=a["type"],
                params=a["params"],
                timestamp=a["timestamp"],
                delay=a["delay"]
            )
            for a in data["actions"]
        ]
        return self.actions


class ActionPlayer:
    """操作播放器"""
    
    def __init__(self):
        self.is_playing = False
        self.current_index = 0
        self.on_progress: Optional[Callable] = None
    
    def play(self, actions: List[RecordedAction], speed: float = 1.0):
        """
        播放操作
        
        Args:
            actions: 操作列表
            speed: 播放速度倍率
        """
        self.is_playing = True
        self.current_index = 0
        
        print(f"▶️ 开始播放 {len(actions)} 个操作 (速度: {speed}x)")
        
        for i, action in enumerate(actions):
            if not self.is_playing:
                break
            
            self.current_index = i
            
            # 等待延迟
            wait_time = action.delay / speed
            if wait_time > 0:
                time.sleep(wait_time)
            
            # 执行操作
            self._execute(action)
            
            if self.on_progress:
                self.on_progress(i + 1, len(actions))
        
        self.is_playing = False
        print("✅ 播放完成")
    
    def _execute(self, action: RecordedAction):
        """执行单个操作"""
        try:
            if action.type == ActionType.CLICK.value:
                from .safe_controller import click
                click(action.params["x"], action.params["y"])
                print(f"   🖱️  点击 ({action.params['x']}, {action.params['y']})")
            
            elif action.type == ActionType.TYPE.value:
                from .safe_controller import type_text
                type_text(action.params["text"])
                print(f"   ⌨️  输入: {action.params['text'][:20]}")
            
            elif action.type == ActionType.WAIT.value:
                time.sleep(action.params["duration"])
                print(f"   ⏳ 等待 {action.params['duration']}s")
            
            elif action.type == ActionType.KEY.value:
                # 简化按键处理
                print(f"   ⌨️  按键: {action.params['key']}")
            
            elif action.type == ActionType.SCREENSHOT.value:
                print(f"   📸 截图")
                
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        print("⏹️ 播放已停止")


# 快捷函数
_recorder: Optional[ActionRecorder] = None
_player: Optional[ActionPlayer] = None

def get_recorder() -> ActionRecorder:
    global _recorder
    if _recorder is None:
        _recorder = ActionRecorder()
    return _recorder

def get_player() -> ActionPlayer:
    global _player
    if _player is None:
        _player = ActionPlayer()
    return _player

# 示例用法
def demo():
    """演示录制回放"""
    print("=" * 60)
    print("🎬 操作录制演示")
    print("=" * 60)
    
    recorder = get_recorder()
    
    # 模拟录制
    print("\n[模拟录制]")
    recorder.start()
    recorder.record_click(100, 200)
    recorder.record_type("Hello")
    recorder.record_wait(1.0)
    recorder.record_click(300, 400)
    actions = recorder.stop()
    
    # 保存
    recorder.save("demo_recording.json")
    
    # 播放
    print("\n[播放录制]")
    player = get_player()
    player.play(actions, speed=2.0)


if __name__ == "__main__":
    demo()
