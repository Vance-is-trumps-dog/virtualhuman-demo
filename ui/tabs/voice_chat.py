import gradio as gr
from config.settings import AVAILABLE_VOICES, EMOJI_MAP, DASHSCOPE_API_KEY
from ui.components import format_pipeline_status

def create_voice_chat_tab():
    with gr.TabItem("🎤 语音聊天"):
        # 可关闭的权限提示横幅
        gr.HTML("""
        <div id="voice-api-alert" style="background-color: #fff3cd; color: #856404; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #ffeeba; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>📢 语音权限提醒：</strong> 如果您听到的是普通的男/女声，说明 API Key 尚未开通 <b>CosyVoice</b> 权限，系统已自动降级。<br>
                <span style="font-size: 0.9em;">👉 请前往 <b>阿里云百炼 → 模型广场</b> 搜索并开通 CosyVoice。</span>
            </div>
            <button onclick="document.getElementById('voice-api-alert').style.display='none'" style="cursor: pointer; background: transparent; border: 1px solid #856404; color: #856404; border-radius: 4px; padding: 4px 8px;">不再提示 ✖</button>
        </div>
        """)

        with gr.Row():
            # 左侧：设定与管线区
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### ✨ 虚拟人设定")
                vh_voice = gr.Dropdown(
                    choices=list(AVAILABLE_VOICES.keys()),
                    value=list(AVAILABLE_VOICES.keys())[0],
                    label="音色", info="需开通 CosyVoice 权限"
                )
                vh_prompt = gr.Textbox(
                    label="设定 (System Prompt)", lines=3,
                    value="你是'灵音'，一个热心、傲娇的测试员。请用简短生动的口语回复。"
                )

                # 🚨 注意：这里是语音聊天专属的 API Key 输入框，已默认填入环境变量
                voice_api_key = gr.Textbox(
                    label="🔑 DashScope API Key (语音聊天专属)",
                    type="password", value=DASHSCOPE_API_KEY, placeholder="sk-..."
                )

                voice_pipeline_status = gr.HTML(
                    value=format_pipeline_status([
                        {"icon": "🎤", "label": "录音", "status": "pending"},
                        {"icon": "📝", "label": "ASR 识别", "status": "pending"},
                        {"icon": "❤️", "label": "情感分析", "status": "pending"},
                        {"icon": "🤖", "label": "AI 回复", "status": "pending"},
                        {"icon": "🔊", "label": "TTS 合成", "status": "pending"},
                    ])
                )

            # 右侧：语音交互区
            with gr.Column(scale=2):
                voice_chatbot = gr.Chatbot(value=[], label="🎤 语音对话", height=350, type="messages")
                with gr.Row():
                    voice_audio_input = gr.Audio(sources=["microphone"], type="filepath", label="点击录音", scale=3)
                    voice_audio_output = gr.Audio(label="🔊 语音回复", autoplay=True, scale=3)
                voice_emotion_display = gr.Textbox(label="❤️ 当前情感", value="😐 neutral", interactive=False)

    return {
        "vh_voice": vh_voice, "vh_prompt": vh_prompt, "voice_api_key": voice_api_key,
        "voice_pipeline_status": voice_pipeline_status, "voice_chatbot": voice_chatbot,
        "voice_audio_input": voice_audio_input, "voice_audio_output": voice_audio_output,
        "voice_emotion_display": voice_emotion_display
    }

def bind_voice_chat_events(components, voice_chat_history, voice_emotion_history, voice_memory_cards):
    c = components

    def on_voice_input(audio_path, history, prompt_text, voice_key, api_key, em_hist, mem_cards):
        from ui.components import format_pipeline_status
        from services.asr import recognize_speech
        from services.chat import chat_with_model
        from services.emotion import analyze_emotion_with_confidence
        from config.settings import AVAILABLE_VOICES, EMOJI_MAP

        if not audio_path:
            pipe = format_pipeline_status([{"icon": "🎤", "label": "录音", "status": "pending", "detail": "等待录音"}])
            return (history, history, "😐 neutral", em_hist, mem_cards, None, pipe)

        steps = [
            {"icon": "🎤", "label": "录音", "status": "done"},
            {"icon": "📝", "label": "ASR 识别", "status": "active"},
            {"icon": "❤️", "label": "情感分析", "status": "pending"},
            {"icon": "🤖", "label": "AI 回复", "status": "pending"},
            {"icon": "🔊", "label": "TTS 合成", "status": "pending"},
        ]

        try:
            # 1. 调用极速版 HTTP ASR
            asr_result = recognize_speech(audio_path, api_key)
            text = asr_result.get("text", "") if isinstance(asr_result, dict) else str(asr_result)

            hallucinations = ["うん。", "嗯。", "啊。", "음.", "mhm.", ""]
            if not text or text.strip() in hallucinations or len(text.strip()) < 2:
                steps[1] = {"icon": "📝", "label": "ASR 识别", "status": "done", "detail": "未听到有效语音 (请检查左侧API Key)"}
                return (history, history, "😐 neutral", em_hist, mem_cards, None, format_pipeline_status(steps))

            steps[1] = {"icon": "📝", "label": "ASR 识别", "status": "done", "detail": text.strip()[:20]}
            steps[2] = {"icon": "❤️", "label": "情感分析", "status": "active"}

            # 2. 情感分析
            pre_emotion = analyze_emotion_with_confidence(text.strip(), api_key)
            steps[2] = {"icon": "❤️", "label": "情感分析", "status": "done", "detail": pre_emotion["emotion"]}
            steps[3] = {"icon": "🤖", "label": "AI 回复", "status": "active"}

            # 3. 大模型对话与 TTS
            actual_prompt = prompt_text.strip() if prompt_text.strip() else "你是一个友好的AI助手。"
            actual_voice_id = AVAILABLE_VOICES.get(voice_key, "longxiaochun_v3")

            reply, emotion, audio_out, mem_cards, _ = chat_with_model(
                text.strip(), history, actual_prompt, actual_voice_id, api_key, mem_cards,
                {"emotion": pre_emotion["emotion"]}
            )
            # 确保音频路径是纯字符串
            if audio_out:
                audio_out = str(audio_out)

            steps[3] = {"icon": "🤖", "label": "AI 回复", "status": "done", "detail": reply[:20]}
            steps[4] = {"icon": "🔊", "label": "TTS 合成", "status": "done"}

            history = history + [{"role": "user", "content": f"🎤 {text.strip()}"}, {"role": "assistant", "content": reply}]
            em_hist = em_hist + [emotion]

            return (history, history, f"{EMOJI_MAP.get(emotion, '😐')} {emotion}", em_hist, mem_cards, audio_out, format_pipeline_status(steps))

        except Exception as e:
            import logging
            logging.error("Voice chat error: %s", e, exc_info=True)
            steps[1] = {"icon": "❌", "label": "系统错误", "status": "done", "detail": str(e)[:30]}
            return (history, history, "😐 neutral", em_hist, mem_cards, None, format_pipeline_status(steps))

    inputs = [c["voice_audio_input"], voice_chat_history, c["vh_prompt"], c["vh_voice"], c["voice_api_key"], voice_emotion_history, voice_memory_cards]
    outputs = [c["voice_chatbot"], voice_chat_history, c["voice_emotion_display"], voice_emotion_history, voice_memory_cards, c["voice_audio_output"], c["voice_pipeline_status"]]

    c["voice_audio_input"].stop_recording(on_voice_input, inputs=inputs, outputs=outputs, api_name=False)
