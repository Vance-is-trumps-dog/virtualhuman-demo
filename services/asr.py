"""
ASR service — Paraformer v2 录音文件识别 (需公网 URL).
"""

import os
import logging
import requests
import dashscope
from dashscope.audio.asr import Transcription
from services.api_client import resolve_api_key
from services.oss_upload import upload_to_public_url

logger = logging.getLogger(__name__)


def recognize_speech(audio_path: str, api_key: str) -> str:
    """使用 DashScope Paraformer v2 录音文件识别"""
    if not audio_path or not os.path.exists(audio_path):
        return ""

    try:
        actual_key = resolve_api_key(api_key)
        dashscope.api_key = actual_key

        # 本地文件 → 公网 URL
        file_url = upload_to_public_url(audio_path, actual_key)

        logger.info("正在提交 Paraformer 识别任务...")
        task_response = Transcription.wait(
            task=Transcription.async_call(
                model='paraformer-v2',
                file_urls=[file_url],
            )
        )

        if task_response.status_code != 200:
            logger.error(f"ASR 请求失败: {task_response.message}")
            return ""

        result_info = task_response.output.results[0]

        if result_info['subtask_status'] != 'SUCCEEDED':
            logger.error(f"ASR 子任务失败: {result_info.get('message', '未知错误')}")
            return ""

        transcription_url = result_info['transcription_url']
        res = requests.get(transcription_url, timeout=15)
        res.raise_for_status()
        data = res.json()

        if "transcripts" in data and len(data["transcripts"]) > 0:
            return data["transcripts"][0].get("text", "")
        return data.get("text", "")

    except NotImplementedError:
        logger.warning("OSS 上传未实现，ASR 跳过。请实现 services/oss_upload.py 中的 upload_to_public_url()。")
        return ""
    except Exception as e:
        logger.error("ASR 识别失败: %s", e, exc_info=True)
        return ""
