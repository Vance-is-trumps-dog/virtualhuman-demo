"""
UI helper functions: HTML formatting, pipeline visualization.
"""

from config.settings import EMOJI_MAP


def format_emotion_timeline(em_hist):
    """Format emotion history as emoji timeline."""
    if not em_hist:
        return "<div style='color:#aaa;font-size:13px;padding:8px;'>暂无情感记录</div>"
    html = "<div style='display:flex;flex-wrap:wrap;gap:4px;padding:4px;'>"
    for em in em_hist[-20:]:
        emoji = EMOJI_MAP.get(em, "😐")
        html += f"<span title='{em}' style='font-size:18px;cursor:default;'>{emoji}</span>"
    html += "</div>"
    return html


def format_memory_cards(cards):
    """Format memory cards as HTML."""
    if not cards:
        return "<div style='color:#aaa;font-size:13px;padding:8px;'>暂无记忆卡片（每 5 轮对话自动生成）</div>"
    html = ""
    for i, card in enumerate(cards):
        html += f"<div class='memory-card'>🧠 记忆 #{i+1}: {card}</div>"
    return html


def format_stats(history, em_hist, mem_cards):
    """Format conversation statistics as HTML."""
    rounds = len(history) // 2
    emotions = len(em_hist)
    memories = len(mem_cards)
    dist = {}
    for em in em_hist:
        dist[em] = dist.get(em, 0) + 1
    dist_html = ""
    if dist:
        total = len(em_hist)
        for em, count in sorted(dist.items(), key=lambda x: -x[1]):
            pct = int(count / total * 100)
            emoji = EMOJI_MAP.get(em, "😐")
            dist_html += (
                f"<div style='display:flex;align-items:center;gap:6px;margin:2px 0;font-size:12px;'>"
                f"<span>{emoji} {em}</span>"
                f"<div style='flex:1;height:8px;background:#eee;border-radius:4px;overflow:hidden;'>"
                f"<div style='width:{pct}%;height:100%;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:4px;'></div>"
                f"</div><span>{pct}%</span></div>"
            )
    return f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;">
      <div class="stat-box"><div class="num">{rounds}</div><div class="label">对话轮数</div></div>
      <div class="stat-box"><div class="num">{emotions}</div><div class="label">情感记录</div></div>
      <div class="stat-box"><div class="num">{memories}</div><div class="label">记忆卡片</div></div>
    </div>
    <div style="padding:8px;">{dist_html}</div>
    """


def format_pipeline_status(steps):
    """Format pipeline visualization steps."""
    html = ""
    for step in steps:
        icon = step.get("icon", "")
        label = step.get("label", "")
        status = step.get("status", "pending")
        detail = step.get("detail", "")
        cls = "pipeline-step"
        if status == "active":
            cls += " active"
            marker = "⏳"
        elif status == "done":
            cls += " done"
            marker = "✅"
        else:
            marker = "⬜"
        html += f"<div class='{cls}'>{marker} {icon} {label}"
        if detail:
            html += f" <span style='color:#888;font-size:12px;'>— {detail}</span>"
        html += "</div>"
    return f"<div style='padding:4px;'>{html}</div>"


def format_fusion_result(result):
    """Format multimodal fusion result as HTML with danger alert support."""
    em = result.get("emotion", "neutral")
    val = result.get("valence", 0)
    aro = result.get("arousal", 0)
    conf = result.get("confidence", 0)
    tag = result.get("action_tag", "idle")
    tag_label = result.get("action_label", "🧘 待机")
    suggestion = result.get("suggestion", "")
    emoji = EMOJI_MAP.get(em, "😐")

    val_pct = int((val + 1) / 2 * 100)
    aro_pct = int((aro + 1) / 2 * 100)
    conf_pct = int(conf * 100)

    # 🛡️ 检测危险情感，应用警报样式
    is_danger = em in ["angry", "fearful"]
    container_class = "danger-alert" if is_danger else ""
    alert_indicator = '<span class="alert-indicator"></span>' if is_danger else ''
    emotion_class = "emotion-alert-text" if is_danger else ""

    return f"""
    <div class="{container_class}" style="padding:16px;border-radius:12px;background:linear-gradient(135deg,rgba(102,126,234,0.08),rgba(118,75,162,0.08));border:1px solid rgba(102,126,234,0.2);">
      <div class="{emotion_class}" style="font-size:18px;font-weight:bold;margin-bottom:10px;">{alert_indicator}🎯 融合情感: {emoji} {em}</div>
      {('<div style="background:#ff0000;color:#fff;padding:8px;border-radius:6px;margin-bottom:10px;font-weight:bold;text-align:center;">⚠️ 警觉状态：检测到对方情绪异常，请注意防范！</div>' if is_danger else '')}
      <div style="margin:6px 0;">
        <div style="font-size:13px;color:#666;">📊 效价 (Valence): {val:.2f}</div>
        <div class="fusion-bar"><div class="fusion-bar-fill" style="width:{val_pct}%;"></div></div>
      </div>
      <div style="margin:6px 0;">
        <div style="font-size:13px;color:#666;">📊 唤醒 (Arousal): {aro:.2f}</div>
        <div class="fusion-bar"><div class="fusion-bar-fill" style="width:{aro_pct}%;"></div></div>
      </div>
      <div style="margin:6px 0;">
        <div style="font-size:13px;color:#666;">📊 置信度: {conf_pct}%</div>
        <div class="fusion-bar"><div class="fusion-bar-fill" style="width:{conf_pct}%;"></div></div>
      </div>
      <div style="margin-top:10px;padding:8px;border-radius:8px;background:rgba(255,255,255,0.5);">
        <div>🎬 动作标签: {tag_label}</div>
        <div style="color:#888;font-size:12px;margin-top:4px;">💡 {suggestion}</div>
      </div>
    </div>
    """


def format_workplace_summary(asr_text, ai_reply, emotion="neutral"):
    """Format workplace summary with highlight style for accessibility."""
    from config.settings import EMOJI_MAP # 确保引入
    emoji = EMOJI_MAP.get(emotion, "😐")
    is_danger = emotion in ["angry", "fearful"]

    # 🛡️ 新增：极其醒目的"对方原话"展示区块
    original_speech_html = f"""
    <div style="background: rgba(255, 255, 255, 0.8); padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #667eea; box-shadow: inset 0 0 5px rgba(0,0,0,0.05);">
        <div style="font-size: 13px; color: #666; margin-bottom: 4px; font-weight: normal;">🗣️ 对方原话：</div>
        <div style="font-size: 18px; color: #222; font-weight: normal; letter-spacing: 0.5px;">{asr_text}</div>
    </div>
    """

    if is_danger:
        return f"""
        <div class="workplace-summary danger-alert">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span class="alert-indicator"></span>
                <span style="font-size:20px;">{emoji}</span>
                <span style="font-size:18px;font-weight:bold;">⚠️ 职场警报</span>
            </div>
            {original_speech_html}
            <div style="line-height:1.6;">{ai_reply}</div>
        </div>
        """
    else:
        return f"""
        <div class="workplace-summary">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="font-size:20px;">{emoji}</span>
                <span style="font-size:18px;font-weight:bold;">📋 职场同传摘要</span>
            </div>
            {original_speech_html}
            <div style="line-height:1.6;">{ai_reply}</div>
        </div>
        """
