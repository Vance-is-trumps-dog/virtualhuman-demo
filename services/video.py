"""
Video processing service: ffmpeg-based audio/frame extraction + multimodal emotion analysis.
"""

import os
import re
import base64
import logging
import tempfile
import subprocess

from config.settings import EMOJI_MAP
from services.api_client import call_multimodal, resolve_api_key
from services.emotion import analyze_emotion_with_confidence
from services.tts import _register_temp

logger = logging.getLogger("virtualhuman.video")


def extract_audio_from_video(video_path: str) -> str:
    """Extract audio track from video file as 16kHz mono WAV using ffmpeg."""
    try:
        out_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            out_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        # 【修改后】无视 FFmpeg 的瑕疵警告，只要生成了大于100字节的有效音频文件，就强行通过
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
            _register_temp(out_path)
            return out_path
    except FileNotFoundError:
        logger.warning("ffmpeg not installed")
    except subprocess.TimeoutExpired:
        logger.warning("ffmpeg audio extraction timed out")
    except Exception as e:
        logger.error("Audio extraction failed: %s", e)
    return ""


def extract_keyframe_from_video(video_path: str) -> str:
    """Extract a keyframe from the middle of the video using ffmpeg."""
    try:
        probe_cmd = ["ffmpeg", "-i", video_path, "-f", "null", "-"]
        probe = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=15)
        duration = 1.0
        for line in (probe.stderr or "").split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = parts.split(":")
                duration = float(h) * 3600 + float(m) * 60 + float(s)
                break

        mid_time = max(0, duration / 2)
        out_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        cmd = [
            "ffmpeg", "-y", "-ss", str(mid_time), "-i", video_path,
            "-frames:v", "1", "-q:v", "2",
            out_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=15)
        # 【修改后】同理，只要有图片出来就放行
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
            _register_temp(out_path)
            return out_path
    except FileNotFoundError:
        logger.warning("ffmpeg not installed")
    except subprocess.TimeoutExpired:
        logger.warning("ffmpeg keyframe extraction timed out")
    except Exception as e:
        logger.error("Keyframe extraction failed: %s", e)
    return ""


def analyze_facial_emotion_from_image(image_path: str, api_key: str = "") -> dict:
    """Use Qwen-VL multimodal model to analyze facial emotion from a photo."""
    key = resolve_api_key(api_key)
    if not key:
        return {"emotion": "neutral", "confidence": 0.5}
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(image_path)[1].lower().lstrip(".")
        mime = "image/png" if ext == "png" else "image/jpeg"
        data_uri = f"data:{mime};base64,{img_b64}"

        result = call_multimodal(
            messages=[{
                "role": "user",
                "content": [
                    {"image": data_uri},
                    {"text": (
                        "请分析这张照片中人物的面部表情情感。"
                        "只返回一个JSON（不要markdown代码块），格式: "
                        '{"emotion":"xxx","confidence":0.xx} '
                        "emotion 必须是以下之一: happy, sad, angry, surprised, fearful, excited, thinking, neutral。"
                        "confidence 是 0-1 的浮点数。"
                    )},
                ],
            }],
            api_key=api_key,
        )
        if result["ok"]:
            content = result["content"]
            if isinstance(content, list):
                text = content[0].get("text", "") if content else ""
            else:
                text = str(content)
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text).strip()
            try:
                import json
                parsed = json.loads(text)
                em = parsed.get("emotion", "neutral")
                if em not in EMOJI_MAP:
                    em = "neutral"
                return {"emotion": em, "confidence": float(parsed.get("confidence", 0.7))}
            except (json.JSONDecodeError, ValueError):
                logger.warning("Failed to parse facial emotion JSON")
    except Exception as e:
        logger.error("Facial emotion analysis failed: %s", e)
    return {"emotion": "neutral", "confidence": 0.5}


def analyze_voice_emotion_from_audio(audio_path: str, api_key: str = "") -> dict:
    """ASR transcribe audio then analyze text emotion."""
    from services.asr import recognize_speech
    return recognize_speech(audio_path, api_key)
