"""
TTS (Text-to-Speech) service with temporary file lifecycle management.
Bug 4 fix: temp files are now tracked and cleaned up.
Upgraded to CosyVoice V3 Flash with AIGC tag support.
"""

import os
import re
import atexit
import tempfile
import logging
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat

logger = logging.getLogger("virtualhuman.tts")

# ---------------------------------------------------------------------------
# Temp file manager (Bug 4 fix)
# ---------------------------------------------------------------------------
_temp_files: list[str] = []
_MAX_TEMP_FILES = 50


def _register_temp(path: str):
    """Track a temp file; evict oldest if over limit."""
    _temp_files.append(path)
    if len(_temp_files) > _MAX_TEMP_FILES:
        old = _temp_files.pop(0)
        try:
            os.unlink(old)
        except OSError:
            pass


def cleanup_all():
    """Remove all tracked temp files (called at exit)."""
    for f in list(_temp_files):
        try:
            os.unlink(f)
        except OSError:
            pass
    _temp_files.clear()


atexit.register(cleanup_all)


# ---------------------------------------------------------------------------
# TTS synthesis
# ---------------------------------------------------------------------------
def synthesize_speech(text: str, voice_id: str = "longxiaochun_v3", api_key: str = "") -> str | None:
    """
    调用 CosyVoice 合成语音，并将其保存为临时本地文件。
    返回:
        str: 临时音频文件的绝对路径 (例如: /tmp/xxxx.wav)，如果失败则返回 None。
    """
    if not text.strip():
        logger.warning("TTS 文本为空，跳过合成。")
        return None

    try:
        from services.api_client import resolve_api_key

        actual_key = resolve_api_key(api_key)
        if not actual_key:
            logger.error("TTS 缺少 API Key！")
            return None

        # 核心修复 1：新版 SDK 必须通过全局变量设置 API Key
        dashscope.api_key = actual_key

        safe_voice = voice_id.strip() if voice_id and voice_id.strip() else "longxiaochun_v3"
        clean_text = re.sub(r'[*#`\[\]()]', '', text)[:500]

        logger.info(f"开始 TTS 合成: 音色={safe_voice}, 文本长度={len(clean_text)}")

        # 核心修复：把 enable_aigc_tag 放到 additional_params 字典中初始化
        try:
            synthesizer = SpeechSynthesizer(
                model="cosyvoice-v3-flash",
                voice=safe_voice,
                format=AudioFormat.WAV_16000HZ_MONO_16BIT,
                additional_params={"enable_aigc_tag": True}
            )

            # call() 方法只需传入 text
            audio_data = synthesizer.call(text=clean_text)

        except Exception as e:
            error_msg = str(e)
            if "Model not found" in error_msg or "ModelNotFound" in error_msg or "voice" in error_msg.lower():
                logger.warning(f"⚠️ 音色 {safe_voice} 失败，自动降级到基础女声 longxiaochun_v3")
                fallback_synthesizer = SpeechSynthesizer(
                    model="cosyvoice-v3-flash",
                    voice="longxiaochun_v3",
                    format=AudioFormat.WAV_16000HZ_MONO_16BIT,
                    additional_params={"enable_aigc_tag": True}
                )
                try:
                    audio_data = fallback_synthesizer.call(text=clean_text)
                except Exception as fallback_e:
                    logger.error(f"🚨 降级合成也失败了，请检查 CosyVoice-v3-flash 模型是否开通调用权限: {fallback_e}")
                    return None
            else:
                raise

        # 检查是否因为权限或网络原因返回了空数据
        if not audio_data:
            logger.error("TTS 合成失败，未获取到二进制数据，请检查 API Key 权限！")
            return None

        # 核心修复 3：稳健地生成并保存临时文件
        # delete=False 保证文件不会在函数运行完立马被系统删掉
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with open(temp_audio.name, "wb") as f:
            f.write(audio_data)

        _register_temp(temp_audio.name)
        logger.info(f"✅ TTS 合成成功，保存路径: {temp_audio.name}")
        return temp_audio.name

    except ImportError:
        logger.warning("dashscope.audio.tts_v2 not available")
    except Exception as e:
        logger.error("🚨 TTS synthesis 代码执行崩溃: %s", e, exc_info=True)
    return None
