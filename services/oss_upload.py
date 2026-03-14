"""
OSS upload utility — 将本地文件上传至阿里云 OSS 并生成干净的公网 URL。
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
    if not local_file_path or not os.path.exists(local_file_path):
        logger.error(f"找不到需要上传的本地文件: {local_file_path}")
        return ""

    if not OSS_ACCESS_KEY_ID or not OSS_ACCESS_KEY_SECRET or not OSS_BUCKET_NAME:
        logger.error("OSS 配置缺失！")
        return ""

    try:
        auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

        file_ext = os.path.splitext(local_file_path)[-1]
        object_name = f"virtual_human_app/{uuid.uuid4().hex}{file_ext}"

        logger.info(f"正在上传 {local_file_path} 到 OSS...")
        bucket.put_object_from_file(object_name, local_file_path)

        # 核心修改：既然 Bucket 已经是"公共读"了，直接拼接出干净的 HTTPS URL！
        # 抛弃 bucket.sign_url() 生成的一大串参数
        clean_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{object_name}"

        logger.info(f"OSS 上传成功! 干净链接: {clean_url}")
        return clean_url

    except Exception as e:
        logger.error(f"OSS 上传失败: {e}", exc_info=True)
        return ""
