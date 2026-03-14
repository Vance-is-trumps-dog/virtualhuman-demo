import gradio as gr
from services.aed import detect_environmental_sound

# 浏览器震动JS代码 - 极度强烈震动模式
VIBRATE_JS = """
<script>
function triggerDangerVibration() {
    // 检查浏览器是否支持震动API
    if (navigator.vibrate) {
        // 极度强烈震动模式：震动-暂停-震动-暂停-震动循环
        // 参数：[震动ms, 暂停ms, 震动ms, 暂停ms, 震动ms, 暂停ms, ...]
        navigator.vibrate([500, 100, 500, 100, 500, 100, 500, 100, 500]);
        console.log("🔔 危险警报震动已触发");
    } else {
        console.warn("⚠️ 当前浏览器不支持震动API");
    }
}

// 页面加载完成后自动触发一次震动（用于测试）
window.addEventListener('load', function() {
    console.log("🛡️ 环境安全雷达已就绪");
});
</script>
"""

# 增强版危险警报CSS - 极度强烈红闪
DANGER_ALERT_CSS = """
<style>
@keyframes extreme-flash-red {
    0% { background-color: #ff0000; }
    10% { background-color: #ffcccc; }
    20% { background-color: #ff0000; }
    30% { background-color: #ffcccc; }
    40% { background-color: #ff0000; }
    50% { background-color: #ffcccc; }
    60% { background-color: #ff0000; }
    70% { background-color: #ffcccc; }
    80% { background-color: #ff0000; }
    90% { background-color: #ffcccc; }
    100% { background-color: #ff0000; }
}

.extreme-danger-alert {
    animation: extreme-flash-red 0.3s infinite;
    background: #ff0000 !important;
    border: 4px solid #8b0000 !important;
}

.warning-alert {
    animation: extreme-flash-red 0.5s infinite;
    background: #ff6600 !important;
    border: 4px solid #cc5200 !important;
}
</style>
"""

def create_radar_tab():
    # 先注入CSS和JS
    gr.HTML(DANGER_ALERT_CSS)
    gr.HTML(VIBRATE_JS)
    
    with gr.TabItem("🛡️ 环境安全雷达"):
        gr.HTML("""
        <div style="text-align:center; margin-bottom:20px;">
            <h2>🚨 居家/出行安全视觉护卫</h2>
            <p style="color:#666;">开启后，系统将在后台静默监听。一旦检测到火警、汽车鸣笛、门铃等关键环境音，将立即触发视觉阻断警报和强烈手机震动。</p>
        </div>
        """)

        with gr.Row():
            # 左侧：流式录音组件
            with gr.Column(scale=1):
                # streaming=True 是核心！它会每隔几秒把录音 chunk 发给后端
                audio_stream = gr.Audio(
                    sources=["microphone"],
                    streaming=True,
                    label="环境音监听麦克风",
                    show_download_button=False
                )

                gr.Markdown("### 📡 监听状态")
                status_log = gr.Textbox(label="实时日志", value="🟢 雷达已就绪，等待开启麦克风...", interactive=False)

            # 右侧：视觉阻断展示区
            with gr.Column(scale=2):
                # 初始状态是一个平静的面板
                alert_display = gr.HTML("""
                <div style="background:#f8f9fa; border:2px dashed #ccc; border-radius:16px; height:400px; display:flex; align-items:center; justify-content:center;">
                    <div style="text-align:center; color:#aaa; font-size:24px;">
                        🛡️ 环境安全无异常<br><span style="font-size:14px;">请保持麦克风开启</span>
                    </div>
                </div>
                """)

    return {
        "audio_stream": audio_stream,
        "alert_display": alert_display,
        "status_log": status_log
    }

def bind_radar_events(components):
    c = components

    def process_audio_chunk(*args):
        """流式处理音频切片，使用 *args 兼容 Gradio 4.x 的隐含状态参数"""
        if not args or args[0] is None:
         return gr.update(), gr.update(value="🟢 正在监听环境音...")

        audio_chunk = args[0]

        # 调用 AED 引擎检测
        result = detect_environmental_sound(audio_chunk)

        # 获取分贝和距离信息
        db_level = result.get("db_level", 0)
        distance_status = result.get("distance_status", "UNKNOWN")
        mode_used = result.get("mode", "NONE")
        
        # 距离状态中文映射
        distance_map = {
            "VERY_CLOSE": "⚠️ 非常近",
            "CLOSE": "⚡ 较近",
            "MEDIUM": "📍 中等距离",
            "FAR": "➡️ 较远",
            "VERY_FAR": "✅ 很远",
            "SAFE": "🛡️ 安全"
        }
        distance_text = distance_map.get(distance_status, distance_status)
        
        # 检测模式显示
        mode_text = "分贝模式" if mode_used == "DB" else "置信度模式"

        if result["is_danger"]:
            # 触发极度显眼的 UI 视觉阻断 + 浏览器震动
            css_class = result["css"]
            label = result["label"]
            danger_level = result.get("level", "MEDIUM")
            
            # 根据危险等级调整震动强度
            if danger_level == "HIGH":
                # 极度危险：强烈震动模式 (5次震动，每次500ms)
                vibrate_pattern = "[500, 100, 500, 100, 500, 100, 500, 100, 500]"
            elif danger_level == "MEDIUM":
                # 中度危险：中等震动 (3次震动，每次300ms)
                vibrate_pattern = "[300, 100, 300, 100, 300]"
            else:
                # 低危险：轻度震动 (2次震动，每次200ms)
                vibrate_pattern = "[200, 100, 200]"
            
            # 构建包含震动JS的HTML
            vibration_js = f"<script>if(navigator.vibrate){{navigator.vibrate({vibrate_pattern});console.log('Danger vibration: {danger_level}');}}</script>"
            
            html_content = f"""
            <div class="{css_class}" style="height:400px; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size: 80px; margin-bottom:20px;">⚠️</div>
                <div class="alert-giant-text">{label}</div>
                <div style="font-size:24px; font-weight:bold;">请立即注意周围环境！</div>
                <div style="font-size:20px; margin-top:15px; background:rgba(0,0,0,0.3); padding:10px; border-radius:8px;">
                    🔊 音量: <strong>{db_level:.1f} dB</strong> | {distance_text}
                </div>
                <div style="font-size:18px; margin-top:10px; color:yellow;">📳 手机震动提醒已触发</div>
                <div style="font-size:14px; margin-top:5px; opacity:0.8;">检测模式: {mode_text}</div>
            </div>
            {vibration_js}
            """
            return gr.update(value=html_content), gr.update(value=f"🚨 警告: {label}! ({db_level:.1f}dB, {distance_text})")
        else:
            # 安全状态下保持冷静的 UI，显示分贝和距离信息
            # 获取识别到的声音类型
            detected_sound = result.get("label", "安全环境音")
            
            # 判断是否是人声/日常噪音（被过滤的）
            is_filtered = "人声" in detected_sound or "对话" in detected_sound or "静音" in detected_sound or "安静" in detected_sound
            
            if is_filtered:
                # 显示已过滤的信息
                filter_info = f"""
                <div style="font-size:16px; margin-top:10px; color:#666; background:#f5f5f5; padding:8px; border-radius:8px;">
                    🔇 已过滤日常噪音: {detected_sound}
                </div>
                """
            else:
                filter_info = ""
                
            safe_html = f"""
            <div style="background:#e8f5e9; border:2px solid #28a745; border-radius:16px; height:400px; display:flex; align-items:center; justify-content:center; transition: all 0.5s;">
                <div style="text-align:center; color:#28a745; font-size:24px;">
                    🛡️ 环境安全无异常<br>
                    <span style="font-size:16px; opacity:0.7;">雷达持续扫描中...</span>
                    <div style="font-size:20px; margin-top:15px; background:rgba(40,167,69,0.1); padding:10px; border-radius:8px;">
                        🔊 音量: <strong>{db_level:.1f} dB</strong> | {distance_text}
                    </div>
                    {filter_info}
                    <div style="font-size:14px; margin-top:5px; opacity:0.6;">
                        检测模式: {mode_text}
                    </div>
                </div>
            </div>
            """
            
            if is_filtered:
                status_msg = f"🟢 环境安全 ({db_level:.1f}dB) - {detected_sound}已过滤"
            else:
                status_msg = f"🟢 环境安全 ({db_level:.1f}dB, {distance_text})"
                
            return gr.update(value=safe_html), gr.update(value=status_msg)

    # Gradio 4.x 中，streaming 模式会在用户录音时持续触发 stream 事件
    c["audio_stream"].stream(
        fn=process_audio_chunk,
        inputs=[c["audio_stream"]],
        outputs=[c["alert_display"], c["status_log"]],
        show_progress="hidden" # 隐藏烦人的加载圈，实现无感监听
    )
