"""
Chat service with memory system and merged API call optimization.
Performance: emotion tag embedded in reply to reduce API calls from 3 to 1.
"""

import re
import logging
from concurrent.futures import ThreadPoolExecutor

from config.settings import (
    DASHSCOPE_API_KEY, MAX_HISTORY_ROUNDS,
    ACTION_TAGS, EMOJI_MAP, EMOTION_VA_MAP,
)
from services.api_client import call_generation
from services.emotion import (
    analyze_emotion, analyze_emotion_with_confidence, derive_action_tag,
)
from services.tts import synthesize_speech

logger = logging.getLogger("virtualhuman.chat")

_memory_executor = ThreadPoolExecutor(max_workers=1)

# Suffix appended to system prompt for merged emotion extraction (perf optimization)
_EMOTION_SUFFIX = (
    "\n\n[多模态输出要求]\n"
    "请务必结合你的【系统设定】、上下文【记忆】以及刚刚接收到的【用户多模态情感状态】进行回复。\n"
    "在回复的最末尾（另起一行），你必须根据你此刻的回应态度，输出你的神态标签，格式严格为：\n"
    "<!--emotion:情感类型:置信度-->\n"
    "可用的情感类型（将自动映射为 3D 动作）：\n"
    "- happy (触发：面带微笑，风铃轻晃动作)\n"
    "- excited (触发：表情夸张，身体大幅摇摆激动)\n"
    "- sad (触发：面露悲伤，共情叹息动作)\n"
    "- angry (触发：面带怒容，警觉注意动作)\n"
    "- surprised (触发：惊讶表情，好奇歪头动作)\n"
    "- fearful (触发：害怕神态，身体后倾)\n"
    "- thinking (触发：皱眉沉思，思考停顿动作)\n"
    "- neutral (触发：平静待机)\n"
    "注意：置信度是 0.0 到 1.0 的数字。这行标签对系统底层动画极其重要，绝对不能省略！"
)

_EMOTION_PATTERN = re.compile(r"<!--emotion:(\w+):([\d.]+)-->")


def _extract_inline_emotion(reply: str) -> tuple[str, str, float]:
    """Extract embedded emotion tag from reply. Returns (clean_reply, emotion, confidence)."""
    match = _EMOTION_PATTERN.search(reply)
    if match:
        emotion = match.group(1)
        confidence = float(match.group(2))
        clean = _EMOTION_PATTERN.sub("", reply).rstrip()
        return clean, emotion, confidence
    return reply, "", 0.0


# ---------------------------------------------------------------------------
# Memory system (async summarization - perf optimization 4.2)
# ---------------------------------------------------------------------------
def compress_history(history: list, api_key: str = "") -> str:
    """Compress early conversation history into a summary."""
    conv_text = ""
    for msg in history[:10]:
        role = "用户" if msg.get("role") == "user" else "AI"
        conv_text += f"{role}: {msg.get('content', '')}\n"
    result = call_generation([
        {"role": "system", "content": "请用一句话概括以下对话的主要内容（不超过100字），保留关键信息。"},
        {"role": "user", "content": conv_text},
    ], api_key)
    if result["ok"]:
        return result["content"].strip()
    return ""


def generate_memory_summary(history: list, api_key: str = "") -> str:
    """Extract key memory points from recent conversation."""
    recent = history[-10:]
    conv_text = ""
    for msg in recent:
        role = "用户" if msg.get("role") == "user" else "AI"
        conv_text += f"{role}: {msg.get('content', '')}\n"
    result = call_generation([
        {"role": "system", "content": (
            "你是记忆管理Agent。请从以下对话中提取1-2条关键记忆点，"
            "格式：简短的陈述句，包含重要事实或用户偏好。每条不超过50字。"
        )},
        {"role": "user", "content": conv_text},
    ], api_key)
    if result["ok"]:
        return result["content"].strip()
    return ""


# ---------------------------------------------------------------------------
# Main chat function
# ---------------------------------------------------------------------------
def chat_with_model(message, history, system_prompt_text, voice_id, api_key, memory_cards,
                    emotion_context=None):
    """Send message to DashScope Qwen with emotion context injection."""

    # 直接使用用户在前端填写的设定，并拼接强制返回情感标签的后缀
    system_prompt = system_prompt_text + _EMOTION_SUFFIX

    # Inject memory context
    if memory_cards:
        memory_ctx = "\n".join(memory_cards[-3:])
        system_prompt += f"\n\n[记忆系统提供的上下文]\n{memory_ctx}"

    # Inject emotion context
    if emotion_context:
        em = emotion_context.get("emotion", "neutral")
        conf = emotion_context.get("confidence", 0.5)
        val = emotion_context.get("valence", 0.0)
        tag = emotion_context.get("action_tag", "idle")
        suggestion = emotion_context.get("suggestion", "")
        system_prompt += (
            f"\n\n[用户情感状态]\n"
            f"主要情感: {em} (置信度: {int(conf*100)}%)\n"
            f"情感效价: {'正面' if val >= 0 else '负面'} ({val:.2f})\n"
            f"建议回应动作: {tag} - {suggestion}\n"
        )

    messages = [{"role": "system", "content": system_prompt}]

    if len(history) > MAX_HISTORY_ROUNDS * 2:
        summary = compress_history(history, api_key)
        if summary:
            messages.append({"role": "system", "content": f"[早期对话摘要] {summary}"})
        recent_history = history[-MAX_HISTORY_ROUNDS * 2:]
    else:
        recent_history = history

    for msg in recent_history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    key = api_key.strip() if api_key and api_key.strip() else DASHSCOPE_API_KEY
    if not key:
        return (
            "请在侧边栏输入你的 DashScope API Key，或设置环境变量 DASHSCOPE_API_KEY。\n"
            "获取地址: https://dashscope.console.aliyun.com/apiKey",
            "neutral", None, memory_cards, "idle",
        )

    result = call_generation(messages, api_key)
    if result["ok"]:
        raw_reply = result["content"]
        # Try to extract inline emotion (merged API call optimization)
        reply, inline_em, inline_conf = _extract_inline_emotion(raw_reply)

        if inline_em:
            emotion = inline_em
            va = EMOTION_VA_MAP.get(emotion, {"valence": 0, "arousal": 0})
            action_tag = derive_action_tag(emotion, va["arousal"], inline_conf)
        else:
            # Fallback: separate emotion analysis
            emotion = analyze_emotion(message, reply, api_key)
            va = EMOTION_VA_MAP.get(emotion, {"valence": 0, "arousal": 0})
            action_tag = derive_action_tag(emotion, va["arousal"], 0.8)

        # 在函数末尾调用 TTS 时，传入透传过来的 voice_id
        audio_path = synthesize_speech(reply, voice_id, api_key)

        # Memory: every 5 rounds, async (perf optimization 4.2)
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]
        if len(new_history) % 10 == 0 and len(new_history) >= 10:
            future = _memory_executor.submit(generate_memory_summary, new_history, api_key)
            try:
                mem = future.result(timeout=10)
                if mem:
                    memory_cards = memory_cards + [mem]
            except Exception:
                logger.warning("Memory summary generation timed out")

        return reply, emotion, audio_path, memory_cards, action_tag

    error_msg = result.get("error", "未知错误")
    if error_msg == "missing_api_key":
        error_msg = (
            "请在侧边栏输入你的 DashScope API Key，或设置环境变量 DASHSCOPE_API_KEY。\n"
            "获取地址: https://dashscope.console.aliyun.com/apiKey"
        )
    return error_msg, "neutral", None, memory_cards, "idle"
