"""
Emotion analysis service + Multimodal Emotion Fusion engine.
Bug 3 fix: confidence is now returned by the LLM, not hardcoded.
"""

import json
import logging

from config.settings import (
    EMOTION_KEYWORDS, EMOJI_MAP, VALID_EMOTIONS,
    EMOTION_VA_MAP, ACTION_TAGS, DEFAULT_FUSION_WEIGHTS,
)
from services.api_client import call_generation

logger = logging.getLogger("virtualhuman.emotion")


# ---------------------------------------------------------------------------
# Keyword-based fallback
# ---------------------------------------------------------------------------
def analyze_emotion_keywords(text: str) -> str:
    """Fallback emotion detection via keyword matching."""
    text_lower = text.lower()
    scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if emotion == "neutral":
            continue
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[emotion] = score
    return max(scores, key=scores.get) if scores else "neutral"


# ---------------------------------------------------------------------------
# AI-powered emotion analysis (Bug 3 fix: LLM returns confidence)
# ---------------------------------------------------------------------------
def analyze_emotion(user_text: str, reply_text: str = "", api_key: str = "") -> str:
    """Analyze emotion using AI, fallback to keywords."""
    combined = f"{user_text} {reply_text}".strip()
    result = call_generation([
        {"role": "system", "content": (
            "你是情感分析专家。分析以下文本的主要情感，只返回一个英文单词: "
            "happy, sad, angry, surprised, fearful, excited, thinking, neutral"
        )},
        {"role": "user", "content": combined},
    ], api_key)
    if result["ok"]:
        text_result = result["content"].strip().lower()
        for v in VALID_EMOTIONS:
            if v in text_result:
                return v
    return analyze_emotion_keywords(combined)


def analyze_emotion_with_confidence(text: str, api_key: str = "") -> dict:
    """Return emotion + real confidence from LLM (Bug 3 fix)."""
    prompt = (
        "分析以下文本的主要情感，返回JSON（不要markdown代码块）: "
        '{"emotion":"xxx","confidence":0.xx} '
        "emotion 必须是: happy/sad/angry/surprised/fearful/excited/thinking/neutral，"
        "confidence 是 0-1 的浮点数，表示你对判断的确信程度。"
    )
    result = call_generation([
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ], api_key)
    if result["ok"]:
        try:
            raw = result["content"].strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            em = parsed.get("emotion", "neutral")
            if em not in VALID_EMOTIONS:
                em = "neutral"
            conf = float(parsed.get("confidence", 0.7))
            return {"emotion": em, "confidence": max(0.0, min(1.0, conf))}
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning("Failed to parse emotion JSON: %s", e)
    # Fallback: keyword analysis with default confidence
    return {"emotion": analyze_emotion_keywords(text), "confidence": 0.5}


# ---------------------------------------------------------------------------
# ActionTag derivation
# ---------------------------------------------------------------------------
def derive_action_tag(emotion: str, arousal: float = 0.5, confidence: float = 0.7) -> str:
    """Derive ActionTag from emotion state - maps ActionTagEngine.ts."""
    if confidence < 0.3:
        return "idle"
    mapping = {
        "happy": lambda: "windchime_strong" if arousal > 0.7 else "windchime_gentle",
        "excited": lambda: "windchime_strong",
        "sad": lambda: "empathy_sigh" if arousal < 0.3 else "comfort_nod",
        "angry": lambda: "alert_attention",
        "surprised": lambda: "curious_tilt",
        "thinking": lambda: "thinking_pause",
        "fearful": lambda: "alert_attention",
        "neutral": lambda: "idle",
    }
    return mapping.get(emotion, lambda: "idle")()


# ---------------------------------------------------------------------------
# Multimodal Emotion Fusion Engine
# ---------------------------------------------------------------------------
class MultimodalEmotionFusion:
    """Weighted fusion of facial, voice, and text emotion channels."""

    def __init__(self, weights=None):
        self.weights = weights or dict(DEFAULT_FUSION_WEIGHTS)
        self.history = []
        self.decay = 0.7

    def fuse(self, facial=None, voice=None, text=None) -> dict:
        channels = {"facial": facial, "voice": voice, "text": text}
        active = {k: v for k, v in channels.items() if v and v.get("emotion")}

        if not active:
            return {
                "emotion": "neutral", "valence": 0.0, "arousal": 0.0,
                "confidence": 0.0, "action_tag": "idle",
                "suggestion": "无输入通道", "details": {},
            }

        total_w = sum(self.weights[k] for k in active)
        norm_w = {k: self.weights[k] / total_w for k in active} if total_w > 0 else {}

        valence = 0.0
        arousal = 0.0
        weighted_confidence = 0.0
        emotion_votes = {}

        for ch_name, ch_data in active.items():
            em = ch_data["emotion"]
            conf = ch_data.get("confidence", 0.7)
            w = norm_w.get(ch_name, 0)
            va = EMOTION_VA_MAP.get(em, {"valence": 0, "arousal": 0})
            valence += va["valence"] * w * conf
            arousal += va["arousal"] * w * conf
            weighted_confidence += conf * w
            emotion_votes[em] = emotion_votes.get(em, 0) + w * conf

        top_emotion = max(emotion_votes, key=emotion_votes.get) if emotion_votes else "neutral"

        # Time smoothing (EMA)
        if self.history:
            prev = self.history[-1]
            valence = self.decay * prev.get("valence", 0) + (1 - self.decay) * valence
            arousal = self.decay * prev.get("arousal", 0) + (1 - self.decay) * arousal

        action_tag = derive_action_tag(top_emotion, arousal, weighted_confidence)
        tag_info = ACTION_TAGS.get(action_tag, {})

        suggestions = {
            "happy": "用温暖的语气回应，分享快乐",
            "excited": "用热情的语气回应，保持积极能量",
            "sad": "用温柔关切的语气，给予情感支持",
            "angry": "用冷静理性的语气，帮助缓解情绪",
            "surprised": "用好奇的语气回应，探索新发现",
            "fearful": "用安抚的语气，提供安全感",
            "thinking": "给予思考空间，提供有深度的回应",
            "neutral": "保持自然友好的对话氛围",
        }

        result = {
            "emotion": top_emotion,
            "valence": round(valence, 3),
            "arousal": round(arousal, 3),
            "confidence": round(weighted_confidence, 3),
            "action_tag": action_tag,
            "action_label": tag_info.get("label", "🧘 待机"),
            "suggestion": suggestions.get(top_emotion, "保持自然对话"),
            "details": {k: v for k, v in active.items()},
        }
        self.history.append(result)
        return result
