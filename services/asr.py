"""
ASR service — Qwen3-ASR-Flash-Filetrans 语音识别 + 情感识别 (终极结构适配版)
"""

import os
import time
import json
import requests
import logging
from services.api_client import resolve_api_key
from services.oss_upload import upload_to_public_url

logger = logging.getLogger(__name__)

# 官方中文情感标签 -> 系统 ActionTag 引擎识别的英文标签
QWEN_EMOTION_MAP = {
    "愉快": "happy",
    "悲伤": "sad",
    "愤怒": "angry",
    "惊讶": "surprised",
    "恐惧": "fearful",
    "平静": "neutral",
    "厌恶": "angry"
}

def find_text_and_emotion(data):
    """递归引擎：不管阿里把数据藏多深，强行挖出 text 和 emotion"""
    if isinstance(data, list) and len(data) > 0:
        return find_text_and_emotion(data[0])
    elif isinstance(data, dict):
        if 'text' in data and data['text']:
            return data['text'], data.get('emotion', '平静')
        # 遍历所有可能的嵌套层 (新增了 'result' 单数形式)
        for wrapper in ['transcripts', 'results', 'result', 'output', 'sentence', 'sentences']:
            if wrapper in data and data[wrapper]:
                t, e = find_text_and_emotion(data[wrapper])
                if t: return t, e
    return "", "平静"

def recognize_speech_and_emotion(audio_path: str, api_key: str) -> dict:
    """使用原生 REST API 调用，完美支持千问新版 result 结构"""
    if not audio_path or not os.path.exists(audio_path):
        return {"text": "", "voice_emotion": "neutral"}

    try:
        actual_key = resolve_api_key(api_key)

        file_url = upload_to_public_url(audio_path, actual_key)
        if not file_url:
            logger.error("OSS上传失败，无法获取音频公网URL")
            return {"text": "", "voice_emotion": "neutral"}

        logger.info("正在提交 qwen3-asr-flash-filetrans 任务...")

        submit_url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription'
        headers = {
            "Authorization": f"Bearer {actual_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": "qwen3-asr-flash-filetrans",
            "input": {"file_url": file_url},
            "parameters": {
                "channel_id": [0]  # 指定读取第 0 个声道
            }
        }

        resp = requests.post(submit_url, headers=headers, json=payload, timeout=15)
        submit_res = resp.json()

        task_id = submit_res.get('output', {}).get('task_id')
        if not task_id:
            logger.error(f"任务下发失败: {submit_res}")
            return {"text": "", "voice_emotion": "neutral"}

        logger.info(f"任务下发成功! Task ID: {task_id}，开始轮询...")
        task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

        for _ in range(40): # 最多轮询约 80 秒
            time.sleep(2)
            poll_resp = requests.get(task_url, headers=headers, timeout=10)
            poll_data = poll_resp.json()

            status = poll_data.get('output', {}).get('task_status')

            if status == 'SUCCEEDED':
                logger.info(f"🎉 阿里云端处理成功! 正在提取结果...")
                output = poll_data.get('output', {})

                transcription_url = output.get('transcription_url')
                if not transcription_url:
                    # 🚀 核心修复：精准捕获最新的 'result' 单数结构
                    if 'result' in output and isinstance(output['result'], dict):
                        transcription_url = output['result'].get('transcription_url')
                    # 兼容老版本 'results' 复数结构
                    elif 'results' in output:
                        if isinstance(output['results'], list) and len(output['results']) > 0:
                            transcription_url = output['results'][0].get('transcription_url')
                        elif isinstance(output['results'], dict):
                            transcription_url = output['results'].get('transcription_url')

                data_to_parse = output
                if transcription_url:
                    logger.info(f"🔗 成功获取到结果下载链接，正在下载 JSON...")
                    res = requests.get(transcription_url, timeout=15)
                    data_to_parse = res.json()

                text, raw_emotion = find_text_and_emotion(data_to_parse)
                mapped_emotion = QWEN_EMOTION_MAP.get(raw_emotion, "neutral")

                if text:
                    logger.info(f"✅ 完美识别成功: [{mapped_emotion}] {text[:20]}...")
                    return {"text": text, "voice_emotion": mapped_emotion}
                else:
                    logger.warning(f"⚠️ 未提取到文本，阿里原始返回数据: {json.dumps(data_to_parse, ensure_ascii=False)[:800]}")
                    return {"text": "", "voice_emotion": "neutral"}

            elif status in ['FAILED', 'CANCELED', 'UNKNOWN']:
                logger.error(f"🚨 阿里云端 ASR 任务失败: {poll_data}")
                return {"text": "", "voice_emotion": "neutral"}

        logger.error("⏳ ASR 任务轮询超时")
        return {"text": "", "voice_emotion": "neutral"}

    except Exception as e:
        logger.error("千问 ASR 识别发生异常: %s", e, exc_info=True)
        return {"text": "", "voice_emotion": "neutral"}
