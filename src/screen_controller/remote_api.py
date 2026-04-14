"""
Remote API - 远程控制 API
HTTP 接口远程控制桌面
"""

import json
import logging
from typing import Dict, Optional, Callable
from dataclasses import dataclass
import threading

try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

logger = logging.getLogger(__name__)


@dataclass
class APIRequest:
    """API 请求"""
    method: str
    path: str
    params: Dict
    body: Optional[Dict] = None


@dataclass
class APIResponse:
    """API 响应"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None


class RemoteAPI:
    """远程 API 服务器"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        self.host = host
        self.port = port
        self.app: Optional[Flask] = None
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._handlers: Dict[str, Callable] = {}
        
        if HAS_FLASK:
            self.app = Flask(__name__)
            self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        if not self.app:
            return
        
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "ok", "service": "ai-sky-eye"})
        
        @self.app.route('/click', methods=['POST'])
        def click():
            data = request.json or {}
            x = data.get('x')
            y = data.get('y')
            
            if x is None or y is None:
                return jsonify({"success": False, "error": "Missing x or y"}), 400
            
            try:
                from .safe_controller import click
                click(x, y)
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/type', methods=['POST'])
        def type_text():
            data = request.json or {}
            text = data.get('text', '')
            
            try:
                from .safe_controller import type_text as _type
                _type(text)
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/screenshot', methods=['GET'])
        def screenshot():
            try:
                from .enhanced_screenshot import capture_to_base64
                base64_img = capture_to_base64()
                return jsonify({"success": True, "image": base64_img})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/find', methods=['POST'])
        def find_element():
            data = request.json or {}
            name = data.get('name', '')
            
            try:
                from .ui_element_finder import find_element as _find
                elem = _find(name)
                if elem:
                    return jsonify({
                        "success": True,
                        "element": {
                            "name": elem.name,
                            "x": elem.x,
                            "y": elem.y,
                            "center": elem.center
                        }
                    })
                return jsonify({"success": False, "error": "Not found"}), 404
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/ai_click', methods=['POST'])
        def ai_click():
            data = request.json or {}
            target = data.get('target', '')
            
            try:
                from .smart_controller_v2 import ai_click as _click
                result = _click(target)
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/windows', methods=['GET'])
        def list_windows():
            try:
                from .window_manager import list_all_windows
                windows = list_all_windows()
                return jsonify({
                    "success": True,
                    "windows": [
                        {"title": w.title, "hwnd": w.hwnd, "rect": w.rect}
                        for w in windows[:20]
                    ]
                })
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
    
    def start(self):
        """启动 API 服务器"""
        if not HAS_FLASK:
            print("❌ Flask not installed. Run: pip install flask")
            return False
        
        if self.running:
            return True
        
        self.running = True
        
        def run_server():
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        
        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()
        
        print(f"🌐 远程 API 已启动: http://{self.host}:{self.port}")
        print(f"   可用接口:")
        print(f"   - GET  /health      健康检查")
        print(f"   - POST /click       点击坐标")
        print(f"   - POST /type        输入文字")
        print(f"   - GET  /screenshot  截图")
        print(f"   - POST /find        查找元素")
        print(f"   - POST /ai_click    AI 点击")
        print(f"   - GET  /windows     列出窗口")
        
        return True
    
    def stop(self):
        """停止服务器"""
        self.running = False
        print("⏹️ 远程 API 已停止")
    
    def register_handler(self, path: str, handler: Callable):
        """注册自定义处理器"""
        self._handlers[path] = handler


# 快捷函数
_api: Optional[RemoteAPI] = None

def get_api(host: str = "0.0.0.0", port: int = 8888) -> RemoteAPI:
    global _api
    if _api is None:
        _api = RemoteAPI(host, port)
    return _api

def start_remote_api(host: str = "0.0.0.0", port: int = 8888) -> bool:
    """启动远程 API"""
    return get_api(host, port).start()

def stop_remote_api():
    """停止远程 API"""
    if _api:
        _api.stop()
