import gradio as gr
from config.settings import EMOJI_MAP

def create_psychology_tab():
    with gr.TabItem("🌳 无声树洞 (心理辅导)"):
        gr.HTML("""
        <div style="text-align:center; padding: 20px; background: #fdfbf7; border-radius: 12px; margin-bottom: 20px;">
            <h2 style="color: #6b5d4f; margin-bottom: 10px;">这里没有任何声音，只有绝对安全的陪伴</h2>
            <p style="color: #8a7a6a; font-size: 16px;">工作累了？觉得不被理解？把心事写下来吧。所有的文字阅后即焚，不留痕迹。</p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 💖 你的情绪轨迹")
                # 视觉化情绪反馈，取代原本的声音反馈
                psy_emotion_display = gr.HTML("<div style='font-size:40px; text-align:center; margin:20px 0;'>😐</div>")
                psy_mem_display = gr.Textbox(label="树洞记下的小纸条 (AI记忆)", interactive=False, lines=5)

            with gr.Column(scale=3):
                # 调大字体，适配视觉阅读
                psy_chatbot = gr.Chatbot(height=450, show_label=False, elem_classes="large-text-chat")

                with gr.Row():
                    psy_input = gr.Textbox(show_label=False, placeholder="今天发生了什么？写下来吧...", scale=4)
                    psy_send_btn = gr.Button("发送", variant="primary", scale=1)

    return {
        "psy_chatbot": psy_chatbot, "psy_input": psy_input, "psy_send_btn": psy_send_btn,
        "psy_emotion_display": psy_emotion_display, "psy_mem_display": psy_mem_display
    }

def bind_psychology_events(components, psy_history, psy_memory, api_key_state):
    c = components

    def process_therapy(user_text, history, mem_cards, api_key):
        if not user_text.strip():
            return gr.update(), history, gr.update(), mem_cards, gr.update()

        from services.psychology import chat_with_silent_therapist

        # 格式化 history 以适配
        formatted_hist = []
        if history:
            for msg in history:
                if isinstance(msg, dict):
                    formatted_hist.append(msg)
                elif isinstance(msg, (list, tuple)) and len(msg) == 2:
                    formatted_hist.append({"role": "user", "content": msg[0]})
                    formatted_hist.append({"role": "assistant", "content": msg[1]})

        reply, emotion, new_mems = chat_with_silent_therapist(user_text, formatted_hist, api_key, mem_cards)

        # 更新聊天记录（Gradio Chatbot 格式）
        history.append([user_text, reply])

        # 更新巨型 Emoji 显示情绪
        emoji = EMOJI_MAP.get(emotion, "😐")
        emotion_html = f"<div style='font-size:80px; text-align:center; animation: pop 0.3s ease-out;'>{emoji}</div>"

        # 更新记忆展示
        mem_text = "\n".join([f"📌 {m}" for m in new_mems]) if new_mems else "暂时还没有记下太多..."

        return "", history, emotion_html, new_mems, mem_text

    c["psy_send_btn"].click(
        fn=process_therapy,
        inputs=[c["psy_input"], c["psy_chatbot"], psy_memory, api_key_state],
        outputs=[c["psy_input"], c["psy_chatbot"], c["psy_emotion_display"], psy_memory, c["psy_mem_display"]]
    )
    c["psy_input"].submit(
        fn=process_therapy,
        inputs=[c["psy_input"], c["psy_chatbot"], psy_memory, api_key_state],
        outputs=[c["psy_input"], c["psy_chatbot"], c["psy_emotion_display"], psy_memory, c["psy_mem_display"]]
    )
