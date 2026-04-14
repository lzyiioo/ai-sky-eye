"""
Safety Config - 统一安全配置系统
支持三种安全级别：strict / normal / off
"""

import json
import os
import time
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime


class SafetyLevel(Enum):
    """安全级别枚举"""
    STRICT = "strict"    # 严格模式：所有操作需确认，最慢但最安全
    NORMAL = "normal"    # 正常模式：敏感操作需确认，平衡安全与效率
    OFF = "off"          # 关闭模式：最小限制，最快但风险最高（不推荐）


@dataclass
class SafetyRules:
    """安全规则配置"""
    # 操作确认
    confirm_before_click: bool = False
    confirm_before_type: bool = False
    confirm_before_hotkey: bool = False
    confirm_before_capture: bool = False
    
    # 频率限制
    max_ops_per_second: int = 10
    max_clicks_per_minute: int = 60
    max_keystrokes_per_minute: int = 500
    
    # 敏感区域保护
    enable_sensitive_areas: bool = False
    sensitive_areas: List[Tuple[int, int, int, int]] = None  # [(x, y, w, h), ...]
    
    # 审计日志
    enable_audit_log: bool = True
    log_level: str = "INFO"  # DEBUG/INFO/WARNING/ERROR
    
    # 紧急停止
    enable_emergency_stop: bool = True
    emergency_hotkey: str = "f12"
    enable_failsafe: bool = True  # 鼠标移角落停止
    
    # 输入法自动切换
    auto_ime_switch: bool = True
    
    # 操作延迟
    mouse_move_duration: float = 0.5
    type_interval: float = 0.1
    
    def __post_init__(self):
        if self.sensitive_areas is None:
            self.sensitive_areas = []


class SafetyConfig:
    """
    统一安全配置管理器
    
    三种预设模式：
    - STRICT: 适合新手、生产环境、重要操作
    - NORMAL: 适合日常使用、开发调试
    - OFF: 仅适合完全信任的环境、自动化脚本
    """
    
    # 预设配置
    PRESETS = {
        SafetyLevel.STRICT: SafetyRules(
            confirm_before_click=True,
            confirm_before_type=True,
            confirm_before_hotkey=True,
            confirm_before_capture=False,
            max_ops_per_second=2,
            max_clicks_per_minute=20,
            max_keystrokes_per_minute=100,
            enable_sensitive_areas=True,
            enable_audit_log=True,
            log_level="DEBUG",
            enable_emergency_stop=True,
            enable_failsafe=True,
            auto_ime_switch=True,
            mouse_move_duration=1.0,
            type_interval=0.2
        ),
        SafetyLevel.NORMAL: SafetyRules(
            confirm_before_click=False,
            confirm_before_type=True,
            confirm_before_hotkey=False,
            confirm_before_capture=False,
            max_ops_per_second=10,
            max_clicks_per_minute=120,
            max_keystrokes_per_minute=600,
            enable_sensitive_areas=True,
            enable_audit_log=True,
            log_level="INFO",
            enable_emergency_stop=True,
            enable_failsafe=True,
            auto_ime_switch=True,
            mouse_move_duration=0.5,
            type_interval=0.1
        ),
        SafetyLevel.OFF: SafetyRules(
            confirm_before_click=False,
            confirm_before_type=False,
            confirm_before_hotkey=False,
            confirm_before_capture=False,
            max_ops_per_second=100,
            max_clicks_per_minute=1000,
            max_keystrokes_per_minute=5000,
            enable_sensitive_areas=False,
            enable_audit_log=False,
            log_level="ERROR",
            enable_emergency_stop=True,  # 即使 OFF 也保留紧急停止
            enable_failsafe=False,
            auto_ime_switch=False,
            mouse_move_duration=0.1,
            type_interval=0.01
        )
    }
    
    def __init__(self, level: SafetyLevel = SafetyLevel.NORMAL, config_file: Optional[str] = None):
        """
        初始化安全配置
        
        Args:
            level: 安全级别（默认 NORMAL）
            config_file: 配置文件路径（可选）
        """
        self.level = level
        self.config_file = config_file or os.path.expanduser("~/.ai_eye_safety.json")
        self.rules = SafetyRules()
        
        # 加载配置
        self._load_config()
        
        # 应用预设
        self.set_level(level)
    
    def _load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.level = SafetyLevel(data.get('level', 'normal'))
                    # 加载自定义规则
                    if 'rules' in data:
                        for key, value in data['rules'].items():
                            if hasattr(self.rules, key):
                                setattr(self.rules, key, value)
                print(f"✅ 安全配置已加载：{self.config_file}")
            except Exception as e:
                print(f"⚠️ 配置加载失败：{e}，使用默认配置")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            data = {
                'level': self.level.value,
                'rules': asdict(self.rules),
                'updated_at': datetime.now().isoformat()
            }
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ 安全配置已保存：{self.config_file}")
        except Exception as e:
            print(f"❌ 配置保存失败：{e}")
    
    def set_level(self, level: SafetyLevel):
        """
        设置安全级别
        
        Args:
            level: SafetyLevel.STRICT / NORMAL / OFF
        """
        self.level = level
        # 复制预设规则
        preset = self.PRESETS[level]
        self.rules = SafetyRules(**asdict(preset))
        print(f"[Safety] Level set to: {level.value.upper()}")
        self._print_current_rules()
    
    def _print_current_rules(self):
        """打印当前规则"""
        print("   配置详情：")
        print(f"   - 点击前确认：{'是' if self.rules.confirm_before_click else '否'}")
        print(f"   - 打字前确认：{'是' if self.rules.confirm_before_type else '否'}")
        print(f"   - 最大操作频率：{self.rules.max_ops_per_second}次/秒")
        print(f"   - 审计日志：{'开启' if self.rules.enable_audit_log else '关闭'}")
        print(f"   - 敏感区域保护：{'开启' if self.rules.enable_sensitive_areas else '关闭'}")
    
    def update_rule(self, rule_name: str, value: Any):
        """
        更新单个规则（自定义配置）
        
        Args:
            rule_name: 规则名称
            value: 规则值
        """
        if hasattr(self.rules, rule_name):
            setattr(self.rules, rule_name, value)
            print(f"✅ 规则已更新：{rule_name} = {value}")
        else:
            print(f"⚠️ 未知规则：{rule_name}")
    
    def add_sensitive_area(self, x: int, y: int, w: int, h: int, name: str = ""):
        """
        添加敏感区域
        
        Args:
            x, y, w, h: 区域坐标和尺寸
            name: 区域名称（可选）
        """
        self.rules.sensitive_areas.append((x, y, w, h, name))
        print(f"[Safety] Sensitive area added: ({x}, {y}, {w}x{h}) {name}")
    
    def clear_sensitive_areas(self):
        """清空敏感区域"""
        self.rules.sensitive_areas = []
        print("🗑️ 敏感区域已清空")
    
    def is_sensitive_area(self, x: int, y: int) -> bool:
        """
        检查坐标是否在敏感区域内
        
        Args:
            x, y: 坐标
            
        Returns:
            bool: 是否在敏感区域
        """
        if not self.rules.enable_sensitive_areas:
            return False
        
        for area in self.rules.sensitive_areas:
            ax, ay, aw, ah = area[:4]
            if ax <= x <= ax + aw and ay <= y <= ay + ah:
                return True
        return False
    
    def get_status(self) -> Dict:
        """获取当前配置状态"""
        return {
            'level': self.level.value,
            'config_file': self.config_file,
            'rules': asdict(self.rules)
        }

    def __repr__(self):
        return f"SafetyConfig(level={self.level.value})"