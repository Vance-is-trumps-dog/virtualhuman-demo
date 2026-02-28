"""
VirtualHumanApp Demo - ModelScope Creative Space
=================================================
多模态数字人陪伴系统 - 魔搭AI应用大赛参赛作品

三大核心功能:
- 💬 文字聊天: AI 对话 + 情感分析 + TTS
- 🎤 语音聊天: ASR 语音识别 → AI 对话 → TTS 语音合成
- 📹 数字人视频聊天: 参考图 + 多模态情感融合 + wan2.2-s2v 云端视频生成
"""

import logging
import sys
import os
import gradio as gr
import gradio_client.utils as client_utils

# ====================================================================
# [究极热修复补丁] 拦截 Gradio 所有 4.x 版本 _json_schema_to_python_type 的解析崩溃
# 原因：管线输出的 fusion_result 字典会让 Pydantic 生成 additionalProperties: true，
# Gradio 底层 _json_schema_to_python_type 不处理布尔型 schema 导致 TypeError
# ====================================================================
if hasattr(client_utils, '_json_schema_to_python_type'):
    _orig_json_schema_to_python_type = client_utils._json_schema_to_python_type

    def _safe_json_schema_to_python_type(schema, defs):
        if isinstance(schema, bool) or not isinstance(schema, dict):
            return "Any"
        try:
            return _orig_json_schema_to_python_type(schema, defs)
        except Exception:
            return "Any"

    client_utils._json_schema_to_python_type = _safe_json_schema_to_python_type

# 同时保留 get_type 层的防御
if hasattr(client_utils, 'get_type'):
    _original_get_type = client_utils.get_type

    def _patched_get_type(schema):
        if isinstance(schema, bool):
            return "Any"
        return _original_get_type(schema)

    client_utils.get_type = _patched_get_type
# ====================================================================

# ====================================================================
# [加强版补丁] 强制修复 postprocess 的视频组件路径报错
# ====================================================================
from gradio.blocks import Blocks

_orig_postprocess_data = Blocks.postprocess_data

async def _patched_postprocess_data(self, block_fn, predictions, state):
    def _make_safe(x):
        if hasattr(x, '__fspath__') or "Path" in str(type(x)):
            return str(x)
        return x

    if isinstance(predictions, (list, tuple)):
        predictions = type(predictions)([_make_safe(p) for p in predictions])
    else:
        predictions = _make_safe(predictions)

    try:
        return await _orig_postprocess_data(self, block_fn, predictions, state)
    except Exception as e:
        logging.getLogger(__name__).warning("Gradio postprocess error bypassed: %s", e)
        return predictions

Blocks.postprocess_data = _patched_postprocess_data
# ====================================================================

# Ensure project root is on sys.path for ModelScope Creative Space compatibility
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 获取当前项目和 assets 的绝对路径
_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_ASSETS_DIR = os.path.join(_BASE_DIR, "assets")

# 白噪音频道，直接存绝对路径
WHITENOISE_CHANNELS = [
    {"id": "fire", "label": "🔥 壁炉", "emoji": "🔥", "description": "温暖的噼啪声", "file": os.path.join(_ASSETS_DIR, "fire.mp3")},
    {"id": "rain", "label": "🌧️ 雨声", "emoji": "🌧️", "description": "窗外的细雨", "file": os.path.join(_ASSETS_DIR, "rain.mp3")},
    {"id": "forest", "label": "🌳 森林", "emoji": "🌳", "description": "鸟鸣与树叶沙沙", "file": os.path.join(_ASSETS_DIR, "forest.mp3")},
    {"id": "wave", "label": "🌊 海浪", "emoji": "🌊", "description": "轻柔的潮汐声", "file": os.path.join(_ASSETS_DIR, "wave.mp3")},
]

# Configure logging (Bug 6 fix: proper logging instead of silent except:pass)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

from ui.tabs import create_demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        allowed_paths=[_ASSETS_DIR],
    )
