"""
Thread-safe DashScope API client wrapper.
All DashScope calls go through here to avoid global api_key assignment (Bug 2 fix).
"""

import logging
from http import HTTPStatus
from dashscope import Generation

from config.settings import DASHSCOPE_API_KEY, DEFAULT_MODEL

logger = logging.getLogger("virtualhuman.api_client")


def resolve_api_key(api_key: str = "") -> str:
    """Resolve API key: user-provided takes priority over env default."""
    key = api_key.strip() if api_key and api_key.strip() else DASHSCOPE_API_KEY
    return key


def call_generation(messages: list, api_key: str = "", model: str = None) -> dict:
    """Thread-safe Generation.call wrapper with per-call api_key."""
    key = resolve_api_key(api_key)
    if not key:
        return {"ok": False, "error": "missing_api_key"}
    try:
        resp = Generation.call(
            model=model or DEFAULT_MODEL,
            messages=messages,
            result_format="message",
            api_key=key,
        )
        if resp.status_code == HTTPStatus.OK:
            content = resp.output.choices[0].message.content
            return {"ok": True, "content": content}
        logger.warning("DashScope API error: %s", resp.message)
        return {"ok": False, "error": resp.message}
    except Exception as e:
        logger.error("DashScope call failed: %s", e, exc_info=True)
        return {"ok": False, "error": str(e)}


def call_multimodal(messages: list, api_key: str = "", model: str = "qwen-vl-plus") -> dict:
    """Thread-safe MultiModalConversation.call wrapper."""
    key = resolve_api_key(api_key)
    if not key:
        return {"ok": False, "error": "missing_api_key"}
    try:
        from dashscope import MultiModalConversation
        resp = MultiModalConversation.call(
            model=model,
            messages=messages,
            api_key=key,
        )
        if resp.status_code == HTTPStatus.OK:
            content = resp.output.choices[0].message.content
            return {"ok": True, "content": content}
        logger.warning("MultiModal API error: %s", resp.message)
        return {"ok": False, "error": resp.message}
    except Exception as e:
        logger.error("MultiModal call failed: %s", e, exc_info=True)
        return {"ok": False, "error": str(e)}
