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
    "\n\n[严格输出格式要求]\n"
    "你现在的身份是听障人士的【职场无障碍同传助理】。请结合上下文、捕捉到的声学情感，**以及你对这句话字面意思的深刻理解**，严格按以下格式输出：\n\n"
    "📝 【核心意图】：(用最简短的大白话总结对方真实意图，指出是否在阴阳怪气，不超过30字)\n"
    "💡 【应对建议】：(给听障用户的职场高情商回应建议，不超过30字)\n\n"
    "在回复的最末尾（另起一行），你必须输出你**综合判定后最真实的对方情绪标签**，以触发虚拟人动作，格式严格为：\n"
    "<!--emotion:情感类型:置信度-->\n"
    "情感类型必须是以下之一：\n"
    "- happy (对方释放善意时)\n"
    "- angry (对方语气愤怒/不耐烦/【阴阳怪气】/【说反话】/【批评】时，必须触发警报)\n"
    "- sad (对方表达失落时)\n"
    "- surprised (对方表达惊讶时)\n"
    "- fearful (对方表达担忧/焦虑时)\n"
    "- thinking (对方在陈述复杂逻辑时)\n"
    "- neutral (日常陈述)\n"
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
        conf = emotion_context.get("confidence", 0.9)
        system_prompt += (
            f"\n\n[⚠️ 实时声学情感侦测参考]\n"
            f"底层的声学模型初步检测到，刚才这段话的声带情绪是：【{em}】。\n"
            f"**但请注意：声学模型经常漏掉人类的'阴阳怪气'或'冷嘲热讽'。**\n"
            f"你需要结合这句话的【字面意思】进行综合判断。如果字面意思具有攻击性、反讽性（例如说别人是大笨蛋，或者明明搞砸了却夸奖），即使声学检测是 neutral，你也必须在末尾强行输出 以保护听障用户！\n"
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
