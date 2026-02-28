"""Tests for services/emotion.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.emotion import (
    analyze_emotion_keywords, derive_action_tag, MultimodalEmotionFusion,
)


def test_analyze_emotion_keywords_happy():
    assert analyze_emotion_keywords("我好开心啊") == "happy"


def test_analyze_emotion_keywords_sad():
    assert analyze_emotion_keywords("我好难过") == "sad"


def test_analyze_emotion_keywords_angry():
    assert analyze_emotion_keywords("气死我了") == "angry"


def test_analyze_emotion_keywords_neutral():
    assert analyze_emotion_keywords("今天天气不错") == "neutral"


def test_analyze_emotion_keywords_mixed():
    # "excited" keywords present
    result = analyze_emotion_keywords("太棒了，我好兴奋")
    assert result in ("excited", "happy")


def test_derive_action_tag_happy_high_arousal():
    assert derive_action_tag("happy", arousal=0.8, confidence=0.9) == "windchime_strong"


def test_derive_action_tag_happy_low_arousal():
    assert derive_action_tag("happy", arousal=0.3, confidence=0.9) == "windchime_gentle"


def test_derive_action_tag_sad_low_arousal():
    assert derive_action_tag("sad", arousal=0.1, confidence=0.8) == "empathy_sigh"


def test_derive_action_tag_low_confidence():
    assert derive_action_tag("angry", arousal=0.9, confidence=0.1) == "idle"


def test_derive_action_tag_thinking():
    assert derive_action_tag("thinking", arousal=0.2, confidence=0.7) == "thinking_pause"


def test_fusion_no_input():
    engine = MultimodalEmotionFusion()
    result = engine.fuse()
    assert result["emotion"] == "neutral"
    assert result["confidence"] == 0.0


def test_fusion_single_channel():
    engine = MultimodalEmotionFusion()
    result = engine.fuse(text={"emotion": "happy", "confidence": 0.9})
    assert result["emotion"] == "happy"
    assert result["confidence"] > 0


def test_fusion_multi_channel():
    engine = MultimodalEmotionFusion()
    result = engine.fuse(
        facial={"emotion": "happy", "confidence": 0.8},
        voice={"emotion": "happy", "confidence": 0.7},
        text={"emotion": "sad", "confidence": 0.6},
    )
    # happy should win with 2 channels
    assert result["emotion"] == "happy"
    assert "action_tag" in result
    assert "suggestion" in result


def test_fusion_ema_smoothing():
    engine = MultimodalEmotionFusion()
    r1 = engine.fuse(text={"emotion": "happy", "confidence": 0.9})
    r2 = engine.fuse(text={"emotion": "sad", "confidence": 0.9})
    # EMA should smooth the valence transition
    assert r2["valence"] != r1["valence"]
