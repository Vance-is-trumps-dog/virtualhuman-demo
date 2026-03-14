import gradio as gr
import os
import tempfile
from config.settings import DASHSCOPE_API_KEY
from ui.components import format_pipeline_status, format_workplace_summary, format_fusion_result
from services.emotion import MultimodalEmotionFusion

# 初始化多模态情感融合引擎
fusion_engine = MultimodalEmotionFusion()

# ================================================================
# 设备检测调试功能
# ================================================================

def check_device_status(video_data):
    """检测麦克风和相机设备状态
    
    Args:
        video_data: Gradio Video 组件返回的 (filepath, ...) 元组
    
    Returns:
        dict: {
            "status": "success" | "warning" | "error",
            "video_ok": bool,
            "audio_ok": bool,
            "video_message": str,
            "audio_message": str,
            "suggestion": str
        }
    """
    result = {
        "status": "success",
        "video_ok": False,
        "audio_ok": False,
        "video_message": "",
        "audio_message": "",
        "suggestion": ""
    }
    
    # 检查视频/相机
    if video_data is None:
        result["video_message"] = "❌ 未检测到视频输入"
        result["video_ok"] = False
    else:
        # video_data 是元组 (filepath, ...)
        video_path = video_data[0] if isinstance(video_data, tuple) else video_data
        
        if not video_path or not os.path.exists(video_path):
            result["video_message"] = "❌ 视频文件无效或不存在"
            result["video_ok"] = False
        else:
            # 检查文件大小
            file_size = os.path.getsize(video_path)
            if file_size < 1000:  # 小于1KB视为无效
                result["video_message"] = "❌ 视频文件过小，可能录制失败"
                result["video_ok"] = False
            else:
                result["video_message"] = f"✅ 相机正常 (文件大小: {file_size/1024:.1f} KB)"
                result["video_ok"] = True
    
    # 尝试提取音频检测麦克风
    if result["video_ok"]:
        try:
            from services.video import extract_audio_from_video
            audio_path = extract_audio_from_video(video_path)
            
            if audio_path and os.path.exists(audio_path):
                # 检查音频文件大小
                audio_size = os.path.getsize(audio_path)
                if audio_size > 100:  # 大于100字节
                    result["audio_message"] = f"✅ 麦克风正常 (音频大小: {audio_size/1024:.1f} KB)"
                    result["audio_ok"] = True
                else:
                    result["audio_message"] = "⚠️ 麦克风可能未工作（音频文件过小）"
                    result["audio_ok"] = False
            else:
                result["audio_message"] = "⚠️ 未检测到音频流，可能麦克风未开启"
                result["audio_ok"] = False
                
        except Exception as e:
            result["audio_message"] = f"⚠️ 音频检测异常: {str(e)[:50]}"
            result["audio_ok"] = False
    
    # 生成综合状态和建议
    if result["video_ok"] and result["audio_ok"]:
        result["status"] = "success"
        result["suggestion"] = "🎉 设备检测通过！可以开始正式录制。"
    elif result["video_ok"] and not result["audio_ok"]:
        result["status"] = "warning"
        result["suggestion"] = "⚠️ 相机正常但麦克风可能未正常工作，建议检查系统麦克风权限。"
    elif not result["video_ok"] and result["audio_ok"]:
        result["status"] = "warning"
        result["suggestion"] = "⚠️ 麦克风正常但相机可能未正常工作，建议检查摄像头权限。"
    else:
        result["status"] = "error"
        result["suggestion"] = "❌ 设备检测失败！请检查：\n1. 浏览器是否允许使用麦克风和摄像头\n2. 系统中是否选择正确的输入设备\n3. 重新点击录制按钮"
    
    return result

def format_device_check_html(result):
    """格式化设备检测结果为HTML"""
    
    # 根据状态选择颜色
    if result["status"] == "success":
        color = "#28a745"
        bg_color = "#d4edda"
        border_color = "#c3e6cb"
    elif result["status"] == "warning":
        color = "#ffc107"
        bg_color = "#fff3cd"
        border_color = "#ffeeba"
    else:
        color = "#dc3545"
        bg_color = "#f8d7da"
        border_color = "#f5c6cb"
    
    html = f"""
    <div style="background:{bg_color}; border:2px solid {border_color}; border-radius:12px; padding:15px; margin:10px 0;">
        <h4 style="color:{color}; margin-top:0;">🔧 设备检测结果</h4>
        
        <div style="margin:10px 0;">
            <strong>📷 相机状态:</strong> {result["video_message"]}
        </div>
        
        <div style="margin:10px 0;">
            <strong>🎤 麦克风状态:</strong> {result["audio_message"]}
        </div>
        
        <div style="margin:15px 0; padding:10px; background:rgba(255,255,255,0.5); border-radius:8px;">
            <strong>💡 建议:</strong><br>
            <span style="white-space:pre-line;">{result["suggestion"]}</span>
        </div>
    </div>
    """
    return html

def create_voice_chat_tab():
    with gr.TabItem("🚀 职场多模态同传"):
        gr.HTML("""
        <div id="voice-api-alert" style="background-color: #e3f2fd; color: #0d47a1; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #90caf9; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>🎯 多模态职场雷达：</strong> 专为听障人士设计的面对面沟通助手。<br>
                <span style="font-size: 0.9em;">✨ 上传或录制视频，AI将同步拆解<b>面部表情、语气和文字内容</b>，深度剖析对方意图并给出高情商回复建议。</span>
            </div>
        </div>
        """)

        with gr.Row():
            # 左侧：设定与状态区
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### ✨ 助手设定与处理状态")
                vh_prompt = gr.Textbox(
                    label="助手角色设定", lines=3,
                    value="你是听障人士的职场同传助理。请根据同事的发言文本、面部表情动作和捕捉到的情绪，推测说话人的真实意图，并给出1条高情商应对建议。"
                )
                voice_api_key = gr.Textbox(
                    label="🔑 DashScope API Key",
                    type="password", value=DASHSCOPE_API_KEY, placeholder="sk-..."
                )
                
                # 滑块权重：用户可以根据现场情况调整对图像还是声音更敏感
                with gr.Accordion("⚙️ 情感融合权重分析 (可选)", open=False):
                    w_f = gr.Slider(0, 1, value=0.4, label="面部微表情权重")
                    w_v = gr.Slider(0, 1, value=0.2, label="语气情感权重")
                    w_t = gr.Slider(0, 1, value=0.4, label="文字语义权重")

                voice_pipeline_status = gr.HTML(
                    value=format_pipeline_status([
                        {"icon": "📹", "label": "接收视频输入", "status": "pending"},
                        {"icon": "🔬", "label": "音视特征分离", "status": "pending"},
                        {"icon": "🎭", "label": "多模态情感融合", "status": "pending"},
                        {"icon": "🤖", "label": "意图推测与建议", "status": "pending"},
                    ])
                )
                
                # 面部表情和动作的可视化看板
                fusion_result_display = gr.HTML(value="<div style='color:#aaa;padding:8px;'>等待上传视频进行分析...</div>")

            # 右侧：视频交互与输出区
            with gr.Column(scale=2):
                with gr.Row():
                    voice_video_input = gr.Video(
                        sources=["webcam", "upload"], 
                        include_audio=True, 
                        label="📷 点击录制或上传同事发言视频", 
                        height=280
                    )
                
                # 设备检测调试区
                with gr.Row():
                    device_check_btn = gr.Button("🔧 设备检测", variant="secondary")
                
                # 设备检测结果显示区
                device_check_display = gr.HTML(value="""
                <div style="background:#f8f9fa; border:2px dashed #dee2e6; border-radius:12px; padding:15px; margin:10px 0; text-align:center; color:#6c757d;">
                    点击上方"设备检测"按钮，先测试麦克风和相机是否正常工作
                </div>
                """, visible=True)
                
                analyze_btn = gr.Button("🚀 开始多模态分析", variant="primary")
                
                # 职场同传结果
                voice_summary_display = gr.HTML(value="<div style='color:#aaa;padding:8px; text-align:center;'>尚未开始分析...</div>", label="")
                voice_chatbot = gr.Chatbot(value=[], label="📝 历史同传记录", height=300, type="messages")

    return {
        "vh_prompt": vh_prompt, "voice_api_key": voice_api_key,
        "w_f": w_f, "w_v": w_v, "w_t": w_t,
        "voice_pipeline_status": voice_pipeline_status,
        "fusion_result_display": fusion_result_display,
        "voice_video_input": voice_video_input,
        "device_check_btn": device_check_btn,
        "device_check_display": device_check_display,
        "analyze_btn": analyze_btn,
        "voice_summary_display": voice_summary_display,
        "voice_chatbot": voice_chatbot
    }

def bind_voice_chat_events(components, voice_chat_history, voice_emotion_history, voice_memory_cards):
    c = components

    def on_video_input(video_path, history, prompt_text, api_key, w_f, w_v, w_t, em_hist, mem_cards):
        from services.asr import recognize_speech_and_emotion
        from services.chat import chat_with_model
        from services.video import extract_audio_from_video, extract_keyframe_from_video, analyze_facial_emotion_from_image, analyze_voice_emotion_from_audio
        from services.emotion import analyze_emotion_with_confidence
        from ui.components import format_pipeline_status, format_workplace_summary, format_fusion_result

        if not video_path:
            pipe = format_pipeline_status([{"icon": "❌", "label": "错误", "status": "done", "detail": "请先录制或上传视频"}])
            return (history, history, em_hist, mem_cards, pipe, "<div style='color:#aaa;'>无视频输入</div>", "<div style='color:red;'>上传失败</div>")

        steps = [
            {"icon": "📹", "label": "接收视频输入", "status": "done"},
            {"icon": "🔬", "label": "音视特征分离", "status": "active"},
            {"icon": "🎭", "label": "多模态情感融合", "status": "pending"},
            {"icon": "🤖", "label": "意图推测与建议", "status": "pending"},
        ]
        
        try:
            # 1. 音视特征分离提取
            audio_path = extract_audio_from_video(video_path)
            frame_path = extract_keyframe_from_video(video_path)
            
            steps[1] = {"icon": "🔬", "label": "音视特征分离", "status": "done"}
            steps[2] = {"icon": "🎭", "label": "多模态情感融合", "status": "active"}

            # 2. 面部情感分析 (Qwen-VL)
            f_data = analyze_facial_emotion_from_image(frame_path, api_key) if frame_path else {"emotion": "neutral"}
            
            # 3. 语音 ASR 与情感分析 (Paraformer)
            asr_result = recognize_speech_and_emotion(audio_path, api_key) if audio_path else {"text": "", "voice_emotion": "neutral"}
            text = asr_result.get("text", "")
            v_data = {"emotion": asr_result.get("voice_emotion", "neutral"), "text": text}
            
            # 4. 纯文本语义情感分析 (兜底校验)
            t_data = analyze_emotion_with_confidence(text, api_key) if text else {"emotion": "neutral"}

            # 5. 执行三通道加权融合
            total_w = w_f + w_v + w_t
            if total_w > 0:
                fusion_engine.weights = {"facial": w_f / total_w, "voice": w_v / total_w, "text": w_t / total_w}
            fusion_result = fusion_engine.fuse(facial=f_data, voice=v_data, text=t_data)
            
            # 生成带动作推测和警戒提示的 HTML 结果
            fusion_html = format_fusion_result(fusion_result)
            final_emotion = fusion_result.get("emotion", "neutral")

            steps[2] = {"icon": "🎭", "label": "融合完毕", "status": "done", "detail": f"确信度: {fusion_result.get('confidence', 0)*100:.0f}%"}
            steps[3] = {"icon": "🤖", "label": "生成高情商建议", "status": "active"}

            if not text:
                steps[3] = {"icon": "❌", "label": "无法生成建议", "status": "done", "detail": "未听清说话内容"}
                return (history, history, em_hist, mem_cards, format_pipeline_status(steps), fusion_html, "<div style='color:#aaa;padding:8px;'>未检测到有效语音文字</div>")

            # 6. 大模型推理：推测意图和建议
            emotion_context = {"emotion": final_emotion, "confidence": fusion_result.get("confidence", 0.9)}
            actual_prompt = prompt_text.strip() if prompt_text.strip() else "你是听障人士的职场同传助理。"
            
            # 不用传入 voice_id
            reply, _, _, mem_cards, _ = chat_with_model(
                text.strip(), history, actual_prompt, "", api_key, mem_cards, emotion_context
            )

            steps[3] = {"icon": "✅", "label": "分析完成", "status": "done"}

            # 将对话存入历史记录
            history = history + [
                {"role": "user", "content": f"📹 [影像捕捉: {final_emotion}] {text.strip()}"},
                {"role": "assistant", "content": reply}
            ]
            em_hist = em_hist + [final_emotion]

            # 7. 格式化职场摘要卡片
            summary_html = format_workplace_summary(text.strip(), reply, final_emotion)

            return (history, history, em_hist, mem_cards, format_pipeline_status(steps), fusion_html, summary_html)

        except Exception as e:
            import logging
            logging.error("Multimodal analysis error: %s", e, exc_info=True)
            steps[1] = {"icon": "❌", "label": "系统错误", "status": "done", "detail": str(e)[:30]}
            return (history, history, em_hist, mem_cards, format_pipeline_status(steps), "<div style='color:red;'>渲染崩溃</div>", f"<div style='color:red;'>错误: {str(e)[:50]}</div>")

    inputs = [
        c["voice_video_input"], voice_chat_history, c["vh_prompt"], c["voice_api_key"], 
        c["w_f"], c["w_v"], c["w_t"], voice_emotion_history, voice_memory_cards
    ]
    outputs = [
        c["voice_chatbot"], voice_chat_history, voice_emotion_history, voice_memory_cards, 
        c["voice_pipeline_status"], c["fusion_result_display"], c["voice_summary_display"]
    ]

    c["analyze_btn"].click(on_video_input, inputs=inputs, outputs=outputs, api_name=False)

    # ================================================================
    # 设备检测事件绑定
    # ================================================================
    
    def on_device_check(video_data):
        """设备检测处理函数"""
        # 如果没有录制视频，提示用户先录制
        if video_data is None:
            return format_device_check_html({
                "status": "error",
                "video_ok": False,
                "audio_ok": False,
                "video_message": "❌ 请先点击录制按钮，录制一段测试视频",
                "audio_message": "⚠️ 无法检测（无视频）",
                "suggestion": "请在上方点击红色的录制按钮，录制5-10秒的测试视频后再进行设备检测。"
            })
        
        # 执行设备检测
        result = check_device_status(video_data)
        return format_device_check_html(result)
    
    # 绑定设备检测按钮事件
    c["device_check_btn"].click(
        fn=on_device_check,
        inputs=[c["voice_video_input"]],
        outputs=[c["device_check_display"]],
        api_name=False
    )