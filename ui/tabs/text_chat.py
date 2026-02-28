"""
Tab 1: Text Chat - UI definition + callbacks.
"""

import gradio as gr

from config.settings import EMOJI_MAP, EMOTION_VA_MAP
from services.chat import chat_with_model
from services.emotion import analyze_emotion_with_confidence
from ui.components import format_emotion_timeline, format_memory_cards, format_stats

def create_text_chat_tab():
    with gr.TabItem("💬 文字聊天"):
        # 可关闭的 API 提示横幅（保持 UI 一致性）
        gr.HTML("""
        <div id="text-api-alert" style="background-color: #d1ecf1; color: #0c5460; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #bee5eb; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>💡 提示：</strong> 文字聊天依赖 <b>通义千问 Qwen-turbo</b> 模型。如需使用语音功能，请确保开通 <b>CosyVoice</b> 权限。
            </div>
            <button onclick="document.getElementById('text-api-alert').style.display='none'" style="cursor: pointer; background: transparent; border: 1px solid #0c5460; color: #0c5460; border-radius: 4px; padding: 4px 8px;">不再提示 ✖</button>
        </div>
        """)

        with gr.Row():
            # 左侧：设定区
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### ✨ 虚拟人设定")
                vh_name = gr.Textbox(
                    label="姓名",
                    value="灵音 (系统测试员)",
                    placeholder="例如：林黛玉"
                )
                vh_gender = gr.Radio(choices=["男", "女", "其他"], label="性别", value="女")
                vh_prompt = gr.Textbox(
                    label="设定 (System Prompt)",
                    lines=4,
                    value=(
                        "你是'灵音'，一个傲娇但热心的系统测试员。你的任务是配合开发人员验证多模态系统。"
                        "你的情绪起伏比较大：顺利时你会非常开心激动；遇到不清楚的事情你会极度惊讶或抱怨。"
                        "请用非常口语化、生动的语气回复，每次回复限制在 50 字以内，以便快速测试语音和 3D 动作。"
                    ),
                    placeholder="请输入虚拟人的性格、背景和说话方式..."
                )
                api_key_input = gr.Textbox(
                    label="🔑 DashScope API Key", type="password", placeholder="sk-...", value=""
                )
                emotion_display = gr.Textbox(label="❤️ 当前情感", value="😐 neutral", interactive=False)
                emotion_timeline = gr.HTML(value=format_emotion_timeline([]), label="情感趋势")

            # 右侧：聊天区
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(value=[], label="💬 对话", height=420, type="messages")
                with gr.Row():
                    text_input = gr.Textbox(placeholder="输入消息... (Enter 发送)", show_label=False, scale=8)
                    send_btn = gr.Button("发送", variant="primary", scale=1)
                with gr.Row():
                    clear_btn = gr.Button("🗑️ 清空对话")

        # 记忆系统 (原 Tab 5)
        with gr.TabItem("🧠 记忆系统"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 对话统计")
                    stats_html = gr.HTML(value=format_stats([], [], []))
                with gr.Column(scale=1):
                    gr.Markdown("### 🧠 记忆卡片")
                    memory_html = gr.HTML(value=format_memory_cards([]))

    return {
        "vh_prompt": vh_prompt, "api_key_input": api_key_input,
        "emotion_display": emotion_display, "emotion_timeline": emotion_timeline,
        "chatbot": chatbot, "text_input": text_input, "send_btn": send_btn, "clear_btn": clear_btn,
        "stats_html": stats_html, "memory_html": memory_html,
    }

def bind_text_chat_events(components, chat_history, emotion_history, memory_cards):
    def on_send_message(message, history, prompt_text, api_key, em_hist, mem_cards):
        try:
            print(f"[DEBUG] 收到前端请求 | 文字: {message}")

            if not message or not message.strip():
                return ("", history, history, "😐 neutral", em_hist, mem_cards,
                        format_emotion_timeline(em_hist), format_memory_cards(mem_cards), format_stats(history, em_hist, mem_cards))

            text_em = analyze_emotion_with_confidence(message, api_key)
            emotion_ctx = {"emotion": text_em["emotion"], "confidence": text_em["confidence"]}

            actual_prompt = prompt_text.strip() if prompt_text.strip() else "你是一个友好的AI助手。"

            print("[DEBUG] 正在调用 DashScope 通义千问 API...")
            reply, emotion, _, mem_cards, _ = chat_with_model(
                message, history, actual_prompt, "", api_key, mem_cards, emotion_ctx
            )
            print(f"[DEBUG] API 回复成功: {reply[:20]}...")

            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
            em_hist = em_hist + [emotion]
            emotion_text = f"{EMOJI_MAP.get(emotion, '😐')} {emotion}"

            print("[DEBUG] 数据处理完成，正在回传前端...")
            return ("", history, history, emotion_text, em_hist, mem_cards,
                    format_emotion_timeline(em_hist), format_memory_cards(mem_cards), format_stats(history, em_hist, mem_cards))

        except Exception as e:
            import traceback
            print("\n" + "=" * 40)
            print("🚨 发生致命错误 (500 Internal Error) 🚨")
            traceback.print_exc()
            print("=" * 40 + "\n")

            return (f"⚠️ 发生错误: {str(e)}", history, history, "😐 neutral", em_hist, mem_cards,
                    format_emotion_timeline(em_hist), format_memory_cards(mem_cards), format_stats(history, em_hist, mem_cards))

    def on_clear():
        return ([], [], "😐 neutral", [], [], format_emotion_timeline([]), format_memory_cards([]), format_stats([], [], []))

    c = components
    send_inputs = [c["text_input"], chat_history, c["vh_prompt"], c["api_key_input"], emotion_history, memory_cards]
    send_outputs = [c["text_input"], c["chatbot"], chat_history, c["emotion_display"],
                    emotion_history, memory_cards, c["emotion_timeline"], c["memory_html"], c["stats_html"]]

    c["send_btn"].click(on_send_message, inputs=send_inputs, outputs=send_outputs, api_name=False)
    c["text_input"].submit(on_send_message, inputs=send_inputs, outputs=send_outputs, api_name=False)
    c["clear_btn"].click(on_clear, outputs=[c["chatbot"], chat_history, c["emotion_display"], emotion_history, memory_cards, c["emotion_timeline"], c["memory_html"], c["stats_html"]], api_name=False)
