"""
OSS upload utility — 将本地文件上传至阿里云 OSS 并生成公网临时签名 URL。
wan2.2-s2v 和 Paraformer 录音文件识别都要求公网 URL，不支持本地文件直传。

必须配置以下环境变量：
  - OSS_ACCESS_KEY_ID: 你的阿里云 AccessKey ID
  - OSS_ACCESS_KEY_SECRET: 你的阿里云 AccessKey Secret
  - OSS_BUCKET_NAME: OSS 存储桶名称
  - OSS_ENDPOINT: OSS 区域端点（如 oss-cn-beijing.aliyuncs.com）
"""

import os
import uuid
import logging

import oss2

logger = logging.getLogger(__name__)

OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME")


def upload_to_public_url(local_file_path: str, api_key: str = "") -> str:
    """
    将本地文件上传至阿里云 OSS，返回带签名的 HTTPS 临时 URL (24h 有效)。
    api_key 参数保留以兼容调用方签名，实际使用 OSS 自身的 AK/SK 鉴权。
    """
    if not local_file_path or not os.path.exists(local_file_path):
        logger.error(f"找不到需要上传的本地文件: {local_file_path}")
        return ""

    if not OSS_ACCESS_KEY_ID or not OSS_ACCESS_KEY_SECRET or not OSS_BUCKET_NAME:
        logger.error(
            "OSS 配置缺失！请设置环境变量: "
            "OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_BUCKET_NAME"
        )
        return ""

    try:
        auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

        file_ext = os.path.splitext(local_file_path)[-1]
        object_name = f"virtual_human_app/{uuid.uuid4().hex}{file_ext}"

        logger.info(f"正在上传 {local_file_path} 到 OSS...")
        bucket.put_object_from_file(object_name, local_file_path)

        # 生成带签名的临时安全访问 URL (有效期 24 小时)
        signed_url = bucket.sign_url('GET', object_name, 86400)

        # 强制 https
        if signed_url.startswith("http://"):
            signed_url = signed_url.replace("http://", "https://", 1)

        logger.info(f"OSS 上传成功! 临时链接: {signed_url[:80]}...")
        return signed_url

    except Exception as e:
        logger.error(f"OSS 上传失败: {e}", exc_info=True)
        return ""
