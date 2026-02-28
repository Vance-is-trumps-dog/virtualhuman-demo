"""
Tab 3: Video Chat — Cloud video generation via wan2.2-s2v.
"""

import gradio as gr

from config.settings import AVAILABLE_VOICES, DASHSCOPE_API_KEY
from services.chat import chat_with_model
from services.emotion import analyze_emotion_with_confidence, MultimodalEmotionFusion
from services.video import (
    extract_audio_from_video, extract_keyframe_from_video,
    analyze_facial_emotion_from_image, analyze_voice_emotion_from_audio,
)
from services.video_gen import generate_digital_human_video
from ui.components import format_pipeline_status

fusion_engine = MultimodalEmotionFusion()


def create_video_chat_tab():
    with gr.TabItem("📹 数字人聊天 (Wan2.2)"):
        with gr.Accordion("📢 首次使用必看配置指南 (点击展开)", open=False):
            gr.Markdown("""
            ### 🔑 第一步：获取 API Key
            1. 登录 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
            2. 点击右上角个人头像 → **API-KEY**
            3. 创建并复制你的 API Key

            ### 🎤 第二步：开通语音及视频权限
            必须手动在"模型广场"搜索并勾选开通：
            - **语音合成**：搜索 `CosyVoice` 或 `Sambert`，点击"立即开通"
            - **视频生成**：搜索 `wan2.2-s2v`，点击"立即开通"（⚠️ 仅支持**北京地域**）

            ### 🔊 关于高级音色与自动降级机制
            - 下拉菜单中提供了多种高级情感音色（基于 `CosyVoice V3` 模型）
            - **降级保护**：如果系统检测到你的账号无权调用所选音色，**将自动降级使用基础免费的知性女声 (龙小淳 V3)**，以保证聊天不中断

            ### ⚠️ 内容审核说明
            - 参考图需使用背景干净、面部清晰且无版权争议的个人照片
            - 若触发 `DataInspectionFailed` 错误，说明内容未通过安全审核，请更换参考图或输入文本

            ### ☁️ 关于数据与存储
            - **零配置**：上传的参考图和录音会自动加密传输至阿里云临时节点，并在视频生成后自动销毁，保护隐私且全程免费中转
            """)

        with gr.Group():
            gr.Markdown("### 1️⃣ 第一步：设定数字人灵魂与外貌")
            with gr.Row():
                with gr.Column(scale=2):
                    vh_name = gr.Textbox(label="姓名", value="灵音")
                    vh_voice = gr.Dropdown(
                        choices=list(AVAILABLE_VOICES.keys()),
                        value=list(AVAILABLE_VOICES.keys())[0],
                        label="音色 (需匹配图片性别)",
                    )
                    vh_prompt = gr.Textbox(
                        label="设定 (System Prompt)", lines=3,
                        value="你是'灵音'，一个温暖的陪伴者。请用简短口语化的语气回复，每次限制50字以内。",
                    )
                    global_api_key = gr.Textbox(
                        label="🔑 阿里云 API Key (必须有北京地域 wan2.2-s2v 权限)",
                        type="password", value=DASHSCOPE_API_KEY, placeholder="sk-...",
                    )
                with gr.Column(scale=1):
                    ref_image = gr.Image(
                        label="📸 上传参考图 (正脸、光线好)",
                        type="filepath", height=240,
                    )

        with gr.Group():
            gr.Markdown("### 2️⃣ 第二步：沉浸式视频对话")
            with gr.Row():
                with gr.Column(scale=1):
                    fusion_video_input = gr.Video(
                        label="录制您的说话视频",
                        sources=["webcam"], include_audio=True, height=300,
                    )
                    fusion_btn = gr.Button("🚀 发送并生成对话", variant="primary")
                    with gr.Accordion("⚙️ 情感融合权重 (可选)", open=False):
                        w_f = gr.Slider(0, 1, value=0.4, label="面部权重")
                        w_v = gr.Slider(0, 1, value=0.2, label="语音权重")
                        w_t = gr.Slider(0, 1, value=0.4, label="文本权重")

                with gr.Column(scale=1):
                    fusion_pipeline_html = gr.HTML(
                        value="<div style='padding:8px;color:#aaa;'>等待交互...</div>"
                    )
                    fusion_video_output = gr.Video(
                        label="🎬 AI 数字人回复", autoplay=True, height=300,
                    )
                    with gr.Row():
                        fusion_audio_output = gr.Audio(
                            label="语音抢先听", autoplay=True, visible=False,
                        )
                        fusion_reply = gr.Textbox(
                            label="🤖 AI 文本回复", interactive=False, lines=2,
                        )

            fusion_chat_history = gr.State([])
            fusion_memory_cards = gr.State([])

    return {
        "vh_name": vh_name, "vh_voice": vh_voice, "vh_prompt": vh_prompt,
        "global_api_key": global_api_key, "ref_image": ref_image,
        "fusion_video_input": fusion_video_input, "fusion_btn": fusion_btn,
        "w_f": w_f, "w_v": w_v, "w_t": w_t,
        "fusion_pipeline_html": fusion_pipeline_html,
        "fusion_reply": fusion_reply,
        "fusion_audio_output": fusion_audio_output,
        "fusion_video_output": fusion_video_output,
        "fusion_chat_history": fusion_chat_history,
        "fusion_memory_cards": fusion_memory_cards,
    }


# --- CALLBACKS ---


def bind_video_chat_events(components, fusion_state):
    c = components

    def on_video_fusion(video_path, w_f, w_v, w_t, api_key,
                        vh_prompt, vh_voice_key, ref_img_path,
                        chat_history_f, mem_cards_f, fstate):
        import time

        if not ref_img_path:
            yield (format_pipeline_status([{"icon": "❌", "label": "错误", "status": "done", "detail": "请先上传参考图!"}]),
                   "请先上传参考图。", None, None, chat_history_f, mem_cards_f, fstate)
            return

        # 等待浏览器将视频文件彻底写完（防止 FFmpeg 读取时文件截断）
        if video_path:
            time.sleep(1.2)

        actual_voice_id = AVAILABLE_VOICES.get(vh_voice_key, "longxiaochun_v3")
        prompt_text = vh_prompt.strip() if vh_prompt.strip() else "你是一个友好的陪伴者。"

        steps = [
            {"icon": "📹", "label": "接收视频", "status": "done"},
            {"icon": "🔬", "label": "多模态分析", "status": "active"},
            {"icon": "🤖", "label": "AI 推理与TTS", "status": "pending"},
            {"icon": "🎬", "label": "生成视频 (耗时排队中)", "status": "pending"},
            {"icon": "✅", "label": "完成", "status": "pending"},
        ]
        yield (format_pipeline_status(steps), "", None, None, chat_history_f, mem_cards_f, fstate)

        if not video_path:
            yield (format_pipeline_status([{"icon": "❌", "label": "错误", "status": "done", "detail": "没有检测到视频输入!"}]),
                   "", None, None, chat_history_f, mem_cards_f, fstate)
            return

        # 1. 提取与情感融合
        audio_path = extract_audio_from_video(video_path)
        frame_path = extract_keyframe_from_video(video_path)
        f_data = analyze_facial_emotion_from_image(frame_path, api_key) if frame_path else {"emotion": "neutral"}

        v_data = analyze_voice_emotion_from_audio(audio_path, api_key) if audio_path else {"emotion": "neutral", "text": ""}
        if isinstance(v_data, str):
            v_data = {"emotion": "neutral", "text": v_data}

        combined_text = v_data.get("text", "").strip()
        t_data = analyze_emotion_with_confidence(combined_text, api_key) if combined_text else {"emotion": "neutral"}

        total_w = w_f + w_v + w_t
        fusion_engine.weights = {"facial": w_f / total_w, "voice": w_v / total_w, "text": w_t / total_w}
        fusion_result = fusion_engine.fuse(facial=f_data, voice=v_data, text=t_data)

        steps[1] = {"icon": "🔬", "label": "多模态分析", "status": "done"}
        steps[2] = {"icon": "🤖", "label": "AI 推理与TTS", "status": "active"}
        yield (format_pipeline_status(steps), "", None, None, chat_history_f, mem_cards_f, fstate)

        # 2. 调用大模型与 TTS
        emotion_ctx = {"emotion": fusion_result.get("emotion")}
        reply, reply_em, tts_path, mem_cards_f, _ = chat_with_model(
            combined_text if combined_text else "你好",
            chat_history_f, prompt_text, actual_voice_id, api_key, mem_cards_f, emotion_ctx,
        )
        # 确保路径是纯字符串，避免 PosixPath 等对象导致序列化崩溃
        if tts_path:
            tts_path = str(tts_path)

        steps[2] = {"icon": "🤖", "label": "AI 推理与TTS", "status": "done"}
        steps[3] = {"icon": "🎬", "label": "生成视频 (正在云端排队，请稍候...)", "status": "active"}

        chat_history_f = chat_history_f + [
            {"role": "user", "content": combined_text},
            {"role": "assistant", "content": reply},
        ]

        # 第一次 Yield：让文字和语音先出来安抚用户
        yield (format_pipeline_status(steps), str(reply), tts_path, None, chat_history_f, mem_cards_f, fusion_result)

        # 3. 阻塞调用 wan2.2-s2v (480P 控制成本和速度)
        try:
            video_url = generate_digital_human_video(ref_img_path, tts_path, api_key, resolution="480P")
            # 确保 video_url 是纯字符串或 None
            if video_url:
                video_url = str(video_url)
        except Exception as e:
            import logging
            logging.error("视频生成失败: %s", e, exc_info=True)
            error_msg = str(e)
            # 检测是否为内容审核失败
            if "DataInspectionFailed" in error_msg or "inappropriate content" in error_msg:
                steps[3] = {"icon": "🎬", "label": "生成视频", "status": "done", "detail": "内容合规检查未通过，请更换参考图或输入"}
            else:
                steps[3] = {"icon": "🎬", "label": "生成视频", "status": "done", "detail": f"生成失败: {error_msg[:30]}"}
            steps[4] = {"icon": "❌", "label": "完成", "status": "done"}
            yield (format_pipeline_status(steps), str(reply), tts_path, None, chat_history_f, mem_cards_f, fusion_result)
            return

        if video_url:
            steps[3] = {"icon": "🎬", "label": "生成视频", "status": "done"}
            steps[4] = {"icon": "✅", "label": "完成", "status": "done"}
        else:
            steps[3] = {"icon": "🎬", "label": "生成视频", "status": "done", "detail": "云端生成失败"}
            steps[4] = {"icon": "❌", "label": "完成", "status": "done"}

        # 第二次 Yield：视频渲染完毕
        yield (format_pipeline_status(steps), str(reply), tts_path, video_url, chat_history_f, mem_cards_f, fusion_result)

    fusion_inputs = [
        c["fusion_video_input"], c["w_f"], c["w_v"], c["w_t"],
        c["global_api_key"], c["vh_prompt"], c["vh_voice"], c["ref_image"],
        c["fusion_chat_history"], c["fusion_memory_cards"], fusion_state,
    ]
    fusion_outputs = [
        c["fusion_pipeline_html"], c["fusion_reply"], c["fusion_audio_output"],
        c["fusion_video_output"], c["fusion_chat_history"], c["fusion_memory_cards"], fusion_state,
    ]
    c["fusion_btn"].click(on_video_fusion, inputs=fusion_inputs, outputs=fusion_outputs, api_name=False)
