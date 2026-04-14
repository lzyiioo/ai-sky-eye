"""
Vision AI - AI 视觉理解模块
调用已有的 AI 模型（Claude Code、OpenClaw 等）理解屏幕内容
"""

import os
import json
import base64
import logging
import subprocess
import tempfile
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from PIL import Image
from io import BytesIO

from .enhanced_screenshot import capture_screen, capture_to_base64

logger = logging.getLogger(__name__)


# ==================== AI 客户端 ====================

class AIClient:
    """
    AI 客户端 - 调用已配置的 AI 模型

    支持的模型:
    - claude: Claude Code / Claude API
    - openclaw: OpenClaw
    - openai: GPT-4V
    - local: 本地模型
    """

    def __init__(self, provider: str = "claude"):
        """
        初始化 AI 客户端

        Args:
            provider: AI 提供商 (claude/openclaw/openai/local)
        """
        self.provider = provider
        self._api_key = None

    def analyze_image(self, image: Image.Image, prompt: str) -> str:
        """
        分析图片

        Args:
            image: PIL 图片
            prompt: 提示词

        Returns:
            AI 的回复
        """
        # 转换为 base64
        img_base64 = image_to_base64(image)

        if self.provider == "claude":
            return self._call_claude(img_base64, prompt)
        elif self.provider == "openclaw":
            return self._call_openclaw(img_base64, prompt)
        elif self.provider == "openai":
            return self._call_openai(img_base64, prompt)
        else:
            return self._call_local(img_base64, prompt)

    def _call_claude(self, img_base64: str, prompt: str) -> str:
        """调用 Claude"""
        # 方法1: 使用 Claude Code CLI
        try:
            # 创建临时文件保存图片
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                img_path = f.name

            # 保存图片
            from PIL import Image
            img = Image.open(BytesIO(base64.b64decode(img_base64)))
            img.save(img_path)

            # 调用 Claude Code
            cmd = [
                "claude", "vision", img_path, prompt
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            os.unlink(img_path)
            return result.stdout or result.stderr

        except FileNotFoundError:
            # Claude Code 不在 PATH，尝试 API
            pass

        # 方法2: 使用 Claude API
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY") or self._get_api_key("anthropic")

            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_base64
                            }
                        }
                    ]
                }]
            )
            return message.content[0].text
        except Exception as e:
            logger.warning(f"Claude API failed: {e}")
            return f"Claude 调用失败: {e}"

    def _call_openclaw(self, img_base64: str, prompt: str) -> str:
        """调用 OpenClaw"""
        # OpenClaw 的视觉能力
        try:
            # 通过 MCP 或直接调用
            # 这里简化处理
            return "OpenClaw 视觉分析功能开发中..."
        except Exception as e:
            return f"OpenClaw 调用失败: {e}"

    def _call_openai(self, img_base64: str, prompt: str) -> str:
        """调用 OpenAI GPT-4V"""
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY") or self._get_api_key("openai")

            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        }
                    ]
                }],
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI 调用失败: {e}"

    def _call_local(self, img_base64: str, prompt: str) -> str:
        """调用本地模型"""
        # 可以接入本地部署的视觉模型
        return "本地模型功能开发中..."

    def _get_api_key(self, provider: str) -> Optional[str]:
        """获取 API Key"""
        keys = {
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
        }
        return keys.get(provider)


# ==================== 视觉理解主类 ====================

class VisionAI:
    """
    AI 视觉理解主类

    功能:
    - 屏幕问答
    - 语义元素查找
    - 异常检测
    - 状态分析
    """

    def __init__(self, provider: str = "claude"):
        """
        初始化视觉理解

        Args:
            provider: AI 提供商 (claude/openclaw/openai/local)
        """
        self.client = AIClient(provider)

    def ask(self, question: str, region: Tuple[int, int, int, int] = None) -> str:
        """
        问AI屏幕上有什么

        Args:
            question: 问题
            region: 截图区域 (x, y, w, h)，None 表示全屏

        Returns:
            AI 的回答
        """
        # 截图
        if region:
            img = capture_screen()
            x, y, w, h = region
            img = img.crop((x, y, x + w, y + h))
        else:
            img = capture_screen()

        # 构建提示词
        prompt = f"""你是一个UI分析助手。请仔细观察这张图片，然后回答用户的问题。

用户问题: {question}

请用简洁的中文回答。如果图片中找不到相关信息，请如实说明。"""

        return self.client.analyze_image(img, prompt)

    def find(self, description: str) -> Optional[Dict[str, Any]]:
        """
        语义查找元素

        Args:
            description: 元素描述，如"蓝色的确认按钮"、"红色的错误提示"

        Returns:
            元素信息 {"x": int, "y": int, "width": int, "height": int, "description": str}
            或 None
        """
        img = capture_screen()

        prompt = f"""你是一个UI元素定位助手。请在图片中找到符合描述的元素。

要查找的元素: {description}

请以JSON格式返回结果:
{{
    "found": true/false,
    "element": {{
        "x": 元素左上角x坐标,
        "y": 元素左上角y坐标,
        "width": 元素宽度,
        "height": 元素高度,
        "description": 元素的文字描述
    }},
    "reason": "为什么选择这个元素"
}}

只返回JSON，不要其他内容。"""

        result = self.client.analyze_image(img, prompt)

        # 解析 JSON 结果
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                if data.get("found"):
                    return data.get("element")
        except:
            pass

        return None

    def detect_errors(self) -> List[Dict[str, Any]]:
        """
        检测界面上的错误/警告

        Returns:
            错误列表 [{"type": "error/warning", "message": str, "position": (x, y)}]
        """
        img = capture_screen()

        prompt = """你是一个UI错误检测助手。请检测图片中的错误和警告信息。

请检测以下类型的问题:
1. 红色错误提示
2. 黄色/橙色警告
3. 弹窗中的错误消息
4. 表单验证错误
5. 网络错误提示

请以JSON格式返回:
{
    "errors": [
        {
            "type": "error/warning",
            "message": "错误信息",
            "position": {"x": x, "y": y},
            "element": "相关元素"
        }
    ]
}

只返回JSON。"""

        result = self.client.analyze_image(img, prompt)

        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("errors", [])
        except:
            pass

        return []

    def analyze_state(self, question: str) -> str:
        """
        分析界面状态

        Args:
            question: 关于状态的问题，如"登录成功了吗"

        Returns:
            状态描述
        """
        img = capture_screen()

        prompt = f"""你是一个UI状态分析助手。请分析当前界面的状态。

问题: {question}

请描述:
1. 当前界面显示什么内容
2. 回答用户的问题
3. 界面处于什么状态（正常/异常/加载中/错误）

用中文回答。"""

        return self.client.analyze_image(img, prompt)

    def compare(self, image_path: str) -> Dict[str, Any]:
        """
        对比两张图片的差异

        Args:
            image_path: 对比图片的路径

        Returns:
            差异描述
        """
        current_img = capture_screen()
        compare_img = Image.open(image_path)

        prompt = """请对比这两张图片的差异。

第一张是当前屏幕截图，第二张是参考图片。

请描述:
1. 两张图片有什么不同
2. 哪些内容发生了变化
3. 这些变化意味着什么

用中文详细描述。"""

        # 合并两张图片进行对比
        width = max(current_img.width, compare_img.width)
        height = current_img.height + compare_img.height

        combined = Image.new('RGB', (width, height))
        combined.paste(current_img, (0, 0))
        combined.paste(compare_img, (0, current_img.height))

        return self.client.analyze_image(combined, prompt)

    def describe(self) -> str:
        """
        描述当前屏幕内容

        Returns:
            屏幕描述
        """
        return self.ask("请描述这个界面是什么，包含哪些主要元素。")


# ==================== 便捷函数 ====================

# 全局实例
_vision_instance = None

def get_vision(provider: str = "claude") -> VisionAI:
    """获取 VisionAI 实例"""
    global _vision_instance
    if _vision_instance is None:
        _vision_instance = VisionAI(provider)
    return _vision_instance


def vision_ask(question: str) -> str:
    """快速问问题"""
    return get_vision().ask(question)


def vision_find(description: str):
    """快速查找元素"""
    return get_vision().find(description)


def vision_errors() -> List[Dict]:
    """快速检测错误"""
    return get_vision().detect_errors()


def vision_state(question: str) -> str:
    """快速分析状态"""
    return get_vision().analyze_state(question)


def vision_describe() -> str:
    """快速描述屏幕"""
    return get_vision().describe()


# ==================== 辅助函数 ====================

def image_to_base64(img: Image.Image) -> str:
    """PIL Image 转 base64"""
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


def base64_to_image(data: str) -> Image.Image:
    """base64 转 PIL Image"""
    return Image.open(BytesIO(base64.b64decode(data)))
