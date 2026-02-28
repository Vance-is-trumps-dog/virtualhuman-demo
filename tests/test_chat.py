"""Tests for services/chat.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from services.chat import _extract_inline_emotion, _EMOTION_PATTERN


def test_extract_inline_emotion_present():
    reply = "你好呀，很高兴认识你！\n<!--emotion:happy:0.85-->"
    clean, emotion, confidence = _extract_inline_emotion(reply)
    assert emotion == "happy"
    assert abs(confidence - 0.85) < 0.01
    assert "<!--" not in clean
    assert clean.strip() == "你好呀，很高兴认识你！"


def test_extract_inline_emotion_absent():
    reply = "你好呀，很高兴认识你！"
    clean, emotion, confidence = _extract_inline_emotion(reply)
    assert emotion == ""
    assert confidence == 0.0
    assert clean == reply


def test_extract_inline_emotion_mid_text():
    reply = "一些文字 <!--emotion:sad:0.72--> 更多文字"
    clean, emotion, confidence = _extract_inline_emotion(reply)
    assert emotion == "sad"
    assert abs(confidence - 0.72) < 0.01
    assert "<!--" not in clean


def test_emotion_pattern_regex():
    assert _EMOTION_PATTERN.search("<!--emotion:neutral:0.50-->") is not None
    assert _EMOTION_PATTERN.search("no emotion here") is None
    match = _EMOTION_PATTERN.search("text <!--emotion:excited:0.95--> more")
    assert match.group(1) == "excited"
    assert match.group(2) == "0.95"
