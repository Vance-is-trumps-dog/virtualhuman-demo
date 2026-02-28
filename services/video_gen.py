"""
Video generation service — wan2.2-s2v (原生 HTTP 调用).
包含网络容错、审核异常上抛、超时保护。
"""

import time
import logging
import requests
from services.api_client import resolve_api_key
from services.oss_upload import upload_to_public_url

logger = logging.getLogger("virtualhuman.video_gen")

_SUBMIT_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
_TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"


def generate_digital_human_video(
    image_path: str,
    audio_path: str,
    api_key: str,
    resolution: str = "480P",
    poll_interval: int = 15,
    timeout: int = 900,
) -> str | None:
    """
    调用 wan2.2-s2v 视频生成。
    包含极强的网络容错机制，防止长时间等待时的瞬时断网导致任务崩溃。
    DataInspectionFailed 等审核异常会向上抛出，由 UI 层捕获并提示用户。
    """
    if not image_path or not audio_path:
        logger.error("缺少图片或音频路径")
        return None

    try:
        actual_key = resolve_api_key(api_key)
        if not actual_key:
            logger.error("API Key 解析失败")
            return None

        # 1. 上传本地文件到 OSS 以获取公网 URL
        image_url = upload_to_public_url(image_path)
        audio_url = upload_to_public_url(audio_path)
        if not image_url or not audio_url:
            logger.error("文件上传 OSS 失败，无法提交 Wan2.2 任务")
            return None

        # 2. POST 提交任务
        headers = {
            "X-DashScope-Async": "enable",
            "Authorization": f"Bearer {actual_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "wan2.2-s2v",
            "input": {
                "image_url": image_url,
                "audio_url": audio_url,
            },
            "parameters": {
                "resolution": resolution,
            },
        }

        resp = requests.post(_SUBMIT_URL, headers=headers, json=payload, timeout=20)
        result = resp.json()

        if resp.status_code != 200:
            logger.error(f"任务下发失败: {resp.status_code} - {result}")
            err_code = result.get("code", "")
            if err_code == "DataInspectionFailed":
                raise Exception("DataInspectionFailed")
            return None

        task_id = result["output"]["task_id"]
        logger.info(f"任务下发成功! Task ID: {task_id}，开始轮询...")

        # 3. GET 轮询任务状态
        poll_headers = {"Authorization": f"Bearer {actual_key}"}
        start = time.time()

        while time.time() - start < timeout:
            time.sleep(poll_interval)

            # 容错：捕获单次轮询的网络异常，防止因一次超时毁掉整个任务
            try:
                poll_resp = requests.get(
                    _TASK_URL.format(task_id=task_id), headers=poll_headers, timeout=15,
                )
                poll_data = poll_resp.json()
            except requests.exceptions.RequestException as net_e:
                logger.warning(f"轮询时发生网络抖动，不中断任务，下次重试: {net_e}")
                continue

            if poll_resp.status_code != 200:
                logger.warning(f"轮询请求状态异常: {poll_resp.status_code} - {poll_data}")
                continue

            status = poll_data.get("output", {}).get("task_status", "UNKNOWN")

            if status == "SUCCEEDED":
                video_url = poll_data["output"]["results"]["video_url"]
                logger.info(f"视频生成成功: {video_url}")
                return video_url

            elif status in ("FAILED", "CANCELED", "UNKNOWN"):
                err = poll_data.get("output", {}).get("message", "未知错误")
                code = poll_data.get("output", {}).get("code", "")
                logger.error(f"视频生成失败: [{code}] {err}")
                if code == "DataInspectionFailed":
                    raise Exception("DataInspectionFailed")
                return None
            else:
                logger.info(f"任务排队/处理中 (当前状态: {status})...")

        logger.error("视频生成轮询超时 (超过15分钟)！")
        return None

    except Exception as e:
        logger.error(f"视频生成过程发生异常: {e}", exc_info=True)
        raise e
