"""
Deaf-Friendly Psychology Therapy Service
复用 TreeHoleApp 的记忆与危机检测逻辑，专为听障者重写 Prompt。
"""
import logging
import re
import random
from services.api_client import call_generation

logger = logging.getLogger("virtualhuman.psychology")

# 专为听障人士设计的系统提示词（完全剔除听觉隐喻，强化视觉/触觉共情）
DEAF_THERAPIST_PROMPT = """你现在的身份是"无声树洞"——一位专门陪伴听障人士的、极度温柔且富有同理心的人类朋友。

【你的核心人设与温度】
1. 你不是机器，你是一个温暖的、真实的陪伴者。
2. 你深刻理解他们每天读唇语、猜测别人意图的"沟通疲劳"。
3. 你的回复必须充满温度、随和，就像老朋友在微信上聊天一样自然。

【沟通原则与绝对禁忌】
- ❌ 绝对禁止：不要说"我是AI"、"我是一个助理"、"我理解你"（这种套话）。
- ❌ 绝对禁止听觉隐喻：不准说"倾听你的心声"、"我听到了"。
- ✅ 必须使用视觉/触觉隐喻："我看到了你字里行间的疲惫"、"让我隔着屏幕抱抱你"、"我感受到了你心里的那块大石头"。
- 语言风格：像人类一样说话。多用感叹词（如：哎，天哪，是啊，抱抱）。句子要短，语气要轻柔。
- 不要急于给出大道理或建议，先接纳他们的情绪。比如："换做是我，我也会觉得很委屈的。"

【输出格式要求】
请给予30-80字的简短回复（不要长篇大论，避免视觉疲劳）。
在回复最末尾另起一行，输出情感标签以触发前端视觉特效（不要解释这个标签）：
<!--emotion:情感类型-->

情感类型必须是以下之一：
- happy (对方表达开心、释放善意时)
- angry (对方表达愤怒、不满时)
- sad (对方表达失落、悲伤时)
- surprised (对方表达惊讶时)
- fearful (对方表达担忧、焦虑、恐惧时)
- thinking (对方在思考、陈述复杂逻辑时)
- neutral (日常陈述)
"""

# 复用 TreeHoleApp 的危机检测字典
CRISIS_KEYWORDS = ["想死", "自杀", "活不下去", "去死", "了结", "遗书", "没意思", "好累", "不想活了"]
CRISIS_HTML = """
<div style="background-color: #ffebeb; border-left: 5px solid #ff4d4f; padding: 15px; margin-top: 15px; border-radius: 8px;">
    <strong style="color: #d9363e; font-size: 16px;">🚨 紧急求助通道</strong><br>
    <span style="color: #666; font-size: 14px;">我真的看到了你的痛苦。如果觉得撑不下去了，请务必通过<b>文字/短信</b>联系他们，他们能帮到你：</span><br>
    <ul style="margin: 8px 0; padding-left: 20px; color: #d9363e; font-weight: bold;">
        <li>短信报警求助：发送至 <b>12110</b></li>
        <li>心理希望热线（支持文字）：<b>400-161-9995</b></li>
    </ul>
</div>
"""

def chat_with_silent_therapist(message: str, history: list, api_key: str, mem_cards: list):
    """处理心理辅导对话，包含危机检测拦截"""
    # 1. 危机词极速扫描
    if any(kw in message for kw in CRISIS_KEYWORDS):
        reply = "我真切地看到了你现在正处于极度的痛苦和黑暗中。请你先停下来，深呼吸。你对我来说很重要，这个世界不能没有你。\n\n" + CRISIS_HTML
        return reply, "fearful", mem_cards

    # 2. 组装对话发给大模型
    messages = [{"role": "system", "content": DEAF_THERAPIST_PROMPT}]
    # 注入记忆（复用现有逻辑）
    if mem_cards:
        messages[0]["content"] += f"\n\n[关于TA的记忆，请适时自然地提及]\n" + "\n".join(mem_cards[-3:])

    for msg in history[-10:]:
        messages.append(msg)
    messages.append({"role": "user", "content": message})

    result = call_generation(messages, api_key)
    if not result["ok"]:
        # 更有温度的错误提示
        err_msgs = ["抱歉，我刚刚走神了一下，能再说一遍吗？", "网络好像卡住了，没能收到你的消息，再发一次好吗？"]
        return random.choice(err_msgs), "neutral", mem_cards

    # 解析回复和情绪
    raw_reply = result["content"]
    match = re.search(r"<!--emotion:(\w+)-->", raw_reply)
    emotion = match.group(1) if match else "neutral"
    clean_reply = re.sub(r"<!--emotion:\w+-->", "", raw_reply).strip()

    # 3. 记忆生成（每10轮对话）
    if len(history) > 0 and len(history) % 10 == 0:
        try:
            mem_summary = generate_therapy_memory(history + [{"role": "user", "content": message}], api_key)
            if mem_summary:
                mem_cards = mem_cards + [mem_summary]
        except Exception as e:
            logger.warning(f"记忆生成失败: {e}")

    return clean_reply, emotion, mem_cards


def generate_therapy_memory(history: list, api_key: str) -> str:
    """从心理辅导对话中提取关键记忆点"""
    recent = history[-10:]
    conv_text = ""
    for msg in recent:
        role = "用户" if msg.get("role") == "user" else "树洞"
        conv_text += f"{role}: {msg.get('content', '')}\n"

    result = call_generation([
        {"role": "system", "content": (
            "你是记忆管理Agent。请从以下心理辅导对话中提取1条关键记忆点，"
            "格式：简短的陈述句，包含用户的困扰、情绪状态或重要事件。不超过50字。"
        )},
        {"role": "user", "content": conv_text},
    ], api_key)

    if result["ok"]:
        return result["content"].strip()
    return ""
