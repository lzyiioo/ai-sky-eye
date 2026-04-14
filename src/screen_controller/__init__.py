"""
Screen Controller Skill for OpenClaw
"""

from .screen_controller import (
    capture_screen,
    capture_screen_base64,
    move_mouse,
    click,
    type_text,
    press_hotkey,
    press_key,
    get_screen_size,
    get_mouse_position,
    monitor_screen,
    screen_capture,
    mouse_move,
    mouse_click,
    keyboard_type,
    keyboard_hotkey
)

# 性能优化模块
from .performance import (
    OCREngineCache,
    ScreenshotCache,
    ElementCache,
    LazyImport,
    BatchProcessor,
    warmup,
    get_perf_monitor,
    cached,
    async_cache,
    PerformanceMonitor
)

# AI 视觉理解模块
from .vision import (
    VisionAI,
    AIClient,
    get_vision,
    vision_ask,
    vision_find,
    vision_errors,
    vision_state,
    vision_describe
)

# 智能任务规划模块
from .task_planner import (
    TaskPlanner,
    TaskStep,
    TaskResult,
    ActionLibrary,
    get_planner,
    plan_task,
    execute_task,
    run
)

# AI 智能代理模块
from .ai_agent import (
    AIAgent,
    VoiceAIAgent,
    Action,
    ActionType,
    Observation,
    ai_do
)

__all__ = [
    'capture_screen',
    'capture_screen_base64',
    'move_mouse',
    'click',
    'type_text',
    'press_hotkey',
    'press_key',
    'get_screen_size',
    'get_mouse_position',
    'monitor_screen',
    'screen_capture',
    'mouse_move',
    'mouse_click',
    'keyboard_type',
    'keyboard_hotkey',
    # 性能模块
    'OCREngineCache',
    'ScreenshotCache',
    'ElementCache',
    'LazyImport',
    'BatchProcessor',
    'warmup',
    'get_perf_monitor',
    'cached',
    'async_cache',
    'PerformanceMonitor',
    # 视觉模块
    'VisionAI',
    'AIClient',
    'get_vision',
    'vision_ask',
    'vision_find',
    'vision_errors',
    'vision_state',
    'vision_describe',
    # 任务规划模块
    'TaskPlanner',
    'TaskStep',
    'TaskResult',
    'ActionLibrary',
    'get_planner',
    'plan_task',
    'execute_task',
    'run',
    # AI 智能代理模块
    'AIAgent',
    'VoiceAIAgent',
    'Action',
    'ActionType',
    'Observation',
    'ai_do',
    # 智能决策大脑模块
    'SmartBrain',
    'Context',
    'Anomaly',
    'Decision',
    'ScreenState',
    'AnomalyType',
    'DecisionType',
    'analyze_screen',
    'check_anomaly',
    'make_decision',
    # 学习记忆模块
    'LearningEngine',
    'ActionRecord',
    'FlowPattern',
    'LearningResult',
    'record_flow',
    'replay_flow',
    'optimize_flow'
]
# AI 智能代理模块
from .ai_agent import (
    AIAgent,
    VoiceAIAgent,
    Action,
    ActionType,
    Observation,
    ai_do
)

# 智能决策大脑模块
from .smart_brain import (
    SmartBrain,
    Context,
    Anomaly,
    Decision,
    ScreenState,
    AnomalyType,
    DecisionType,
    analyze_screen,
    check_anomaly,
    make_decision
)

# 学习记忆模块
from .learning import (
    LearningEngine,
    ActionRecord,
    FlowPattern,
    LearningResult,
    record_flow,
    replay_flow,
    optimize_flow
)

__version__ = '1.0.0'
