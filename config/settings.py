"""
VirtualHumanApp - Configuration & Constants
"""

import os

# ---------------------------------------------------------------------------
# Core API Configuration
# ---------------------------------------------------------------------------
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DEFAULT_MODEL = "qwen-turbo"
MAX_HISTORY_ROUNDS = 20

# Meshy API for image-to-3D
MESHY_API_BASE = "https://api.meshy.ai/openapi/v1/image-to-3d"
MESHY_API_KEY = os.getenv("MESHY_API_KEY", "")

# GLB/GLTF 3D Avatar model URL
AVATAR_GLB_URL = os.environ.get("AVATAR_GLB_URL", "")

# Default avatar image path
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_AVATAR_PATH = os.path.join(_BASE_DIR, "default_avatar.png")
if not os.path.exists(DEFAULT_AVATAR_PATH):
    DEFAULT_AVATAR_PATH = None

# HDR Panorama URLs for scene backgrounds
HDR_PANORAMA_URLS = {
    "星空夜境": os.environ.get("HDR_STARRY", ""),
    "翠绿森林": os.environ.get("HDR_FOREST", ""),
    "金色海滩": os.environ.get("HDR_BEACH", ""),
    "霓虹都市": os.environ.get("HDR_NEON", ""),
    "温馨客厅": os.environ.get("HDR_LIVING", ""),
    "樱花庭院": os.environ.get("HDR_SAKURA", ""),
    "冰雪世界": os.environ.get("HDR_ICE", ""),
    "火山熔岩": os.environ.get("HDR_VOLCANO", ""),
    "默认空间": os.environ.get("HDR_DEFAULT", ""),
}

# 替换原有的 TTS_VOICE_MAP 和 PERSONA_PRESETS
# 升级到 CosyVoice V3 Flash 音色（更自然、更稳定）
AVAILABLE_VOICES = {
    "👩 龙小淳 (知性积极女)": "longxiaochun_v3",
    "👩 YUMI (正经青年女)": "longyumi_v3",
    "👩 龙安温 (优雅知性女)": "longanwen_v3",
    "👩 龙安台 (嗲甜台湾女)": "longantai_v3",
    "👦 龙安洋 (阳光男声)": "longanyang",
}

# ---------------------------------------------------------------------------
# Emotion keywords mapping (fallback)
# ---------------------------------------------------------------------------
EMOTION_KEYWORDS = {
    "happy": ["happy", "glad", "joy", "excited", "love", "great", "wonderful",
              "开心", "高兴", "快乐", "喜欢", "太好了", "哈哈", "棒", "赞", "幸福", "愉快"],
    "sad": ["sad", "unhappy", "depressed", "lonely", "miss", "cry",
            "难过", "伤心", "哭", "失落", "孤独", "想念", "悲伤", "不开心", "委屈"],
    "angry": ["angry", "furious", "hate", "annoyed", "mad",
              "生气", "愤怒", "讨厌", "烦", "恼火", "气死"],
    "surprised": ["wow", "surprise", "amazing", "incredible", "unbelievable",
                  "哇", "天哪", "居然", "惊讶", "不可思议", "没想到"],
    "fearful": ["afraid", "scared", "fear", "worried", "anxious",
                "害怕", "担心", "恐惧", "焦虑", "紧张", "慌"],
    "excited": ["兴奋", "激动", "太棒了", "超级", "amazing", "awesome", "incredible"],
    "thinking": ["想想", "思考", "嗯", "让我想", "考虑", "think", "wonder", "hmm"],
    "neutral": [],
}

EMOJI_MAP = {
    "happy": "😊", "sad": "😢", "angry": "😠",
    "surprised": "😮", "fearful": "😰", "neutral": "😐",
    "excited": "🤩", "thinking": "🤔",
}

VALID_EMOTIONS = list(EMOJI_MAP.keys())

# ---------------------------------------------------------------------------
# ActionTag definitions
# ---------------------------------------------------------------------------
ACTION_TAGS = {
    "idle":              {"label": "🧘 待机",       "head": "轻微摇摆", "body": "呼吸",     "face": "中性"},
    "windchime_gentle":  {"label": "🎐 风铃轻晃",   "head": "轻微点头", "body": "轻微摇摆", "face": "微笑"},
    "windchime_strong":  {"label": "🎊 风铃强晃",   "head": "大幅点头", "body": "明显摇摆", "face": "大笑"},
    "comfort_nod":       {"label": "🤗 安慰点头",   "head": "缓慢点头", "body": "前倾",     "face": "关切"},
    "alert_attention":   {"label": "⚡ 警觉注意",   "head": "抬头",     "body": "挺直",     "face": "严肃"},
    "curious_tilt":      {"label": "🔍 好奇歪头",   "head": "歪头",     "body": "前倾",     "face": "好奇"},
    "thinking_pause":    {"label": "💭 思考停顿",   "head": "微低头",   "body": "静止",     "face": "沉思"},
    "mirror_smile":      {"label": "😊 镜像微笑",   "head": "轻微点头", "body": "放松",     "face": "微笑"},
    "empathy_sigh":      {"label": "😔 共情叹息",   "head": "缓慢低头", "body": "轻微下沉", "face": "悲伤"},
}

EMOTION_VA_MAP = {
    "happy":     {"valence": 0.8,  "arousal": 0.6},
    "excited":   {"valence": 0.9,  "arousal": 0.9},
    "sad":       {"valence": -0.7, "arousal": -0.3},
    "angry":     {"valence": -0.8, "arousal": 0.8},
    "surprised": {"valence": 0.3,  "arousal": 0.8},
    "fearful":   {"valence": -0.6, "arousal": 0.7},
    "thinking":  {"valence": 0.1,  "arousal": 0.2},
    "neutral":   {"valence": 0.0,  "arousal": 0.0},
}

DEFAULT_FUSION_WEIGHTS = {"facial": 0.4, "voice": 0.2, "text": 0.4}

# ---------------------------------------------------------------------------
# Scene presets
# ---------------------------------------------------------------------------
SCENE_PRESETS = {
    "星空夜境": {"bg1": "#0a0a2e", "bg2": "#1a1a4e", "bg3": "#0f0f3d", "particle": "#8888ff", "label": "🌌 星空夜境", "hdr": HDR_PANORAMA_URLS.get("星空夜境", ""), "bg_image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800"},
    "翠绿森林": {"bg1": "#0a2e0a", "bg2": "#1a4e1a", "bg3": "#0f3d0f", "particle": "#44ff88", "label": "🌲 翠绿森林", "hdr": HDR_PANORAMA_URLS.get("翠绿森林", ""), "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800"},
    "金色海滩": {"bg1": "#2e2a0a", "bg2": "#4e3a1a", "bg3": "#3d2f0f", "particle": "#ffcc44", "label": "🏖️ 金色海滩", "hdr": HDR_PANORAMA_URLS.get("金色海滩", ""), "bg_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"},
    "霓虹都市": {"bg1": "#1a0a2e", "bg2": "#2e1a4e", "bg3": "#240f3d", "particle": "#ff44ff", "label": "🌃 霓虹都市", "hdr": HDR_PANORAMA_URLS.get("霓虹都市", ""), "bg_image": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800"},
    "温馨客厅": {"bg1": "#2e1a0a", "bg2": "#4e2a1a", "bg3": "#3d1f0f", "particle": "#ffaa44", "label": "🏠 温馨客厅", "hdr": HDR_PANORAMA_URLS.get("温馨客厅", ""), "bg_image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"},
    "樱花庭院": {"bg1": "#2e0a1a", "bg2": "#4e1a2a", "bg3": "#3d0f1f", "particle": "#ff88aa", "label": "🌸 樱花庭院", "hdr": HDR_PANORAMA_URLS.get("樱花庭院", ""), "bg_image": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=800"},
    "冰雪世界": {"bg1": "#0a1a2e", "bg2": "#1a2a4e", "bg3": "#0f1f3d", "particle": "#aaddff", "label": "❄️ 冰雪世界", "hdr": HDR_PANORAMA_URLS.get("冰雪世界", ""), "bg_image": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800"},
    "火山熔岩": {"bg1": "#2e0a0a", "bg2": "#4e1a0a", "bg3": "#3d0f0a", "particle": "#ff4422", "label": "🌋 火山熔岩", "hdr": HDR_PANORAMA_URLS.get("火山熔岩", ""), "bg_image": "https://images.unsplash.com/photo-1462332420958-a05d1e002413?w=800"},
    "默认空间": {"bg1": "#0f0c29", "bg2": "#302b63", "bg3": "#24243e", "particle": "#4169E1", "label": "🔮 默认空间", "hdr": HDR_PANORAMA_URLS.get("默认空间", ""), "bg_image": ""},
}
