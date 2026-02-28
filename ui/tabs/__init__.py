"""
UI Tabs package - provides create_demo() that assembles all tabs.
"""

import gradio as gr

from ui.styles import CUSTOM_CSS
from ui.tabs.text_chat import create_text_chat_tab, bind_text_chat_events
from ui.tabs.voice_chat import create_voice_chat_tab, bind_voice_chat_events
from ui.tabs.video_chat import create_video_chat_tab, bind_video_chat_events
from ui.tabs.architecture import create_architecture_tab
from ui.tabs.troubleshoot import create_troubleshoot_tab


def create_demo():
    """Assemble the full Gradio demo with all tabs and callbacks."""
    with gr.Blocks(
        title="VirtualHumanApp - AI 数字人陪伴系统",
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
    ) as demo:

        # Header
        gr.HTML("""
        <div class="app-header">
          <h1>🌟 VirtualHumanApp</h1>
          <p style="color:#888;font-size:14px;margin:0;">
            AI 虚拟人陪伴系统 — 文字聊天 · 语音聊天 · 视频聊天 · 多模态情感融合
          </p>
          <p style="color:#aaa;font-size:12px;margin:4px 0 0;">
            魔搭社区 AI 应用大赛参赛作品 | Multi-Agent 架构 · 48 个服务 · 50+ 组件
          </p>
        </div>
        <div id="security-warning" style="display:none;margin:8px auto;max-width:900px;padding:10px 16px;border-radius:8px;background:linear-gradient(135deg,rgba(255,193,7,0.15),rgba(255,152,0,0.12));border:1px solid rgba(255,152,0,0.3);font-size:13px;color:#856404;text-align:center;">
          ⚠️ 摄像头/麦克风功能需通过 <b>http://localhost:7860</b> 或 HTTPS 链接访问。
        </div>
        <script>
        (function(){
          var h = location.hostname;
          if(location.protocol !== 'https:' && h !== 'localhost' && h !== '127.0.0.1') {
            var el = document.getElementById('security-warning');
            if(el) el.style.display = 'block';
          }
        })();
        </script>
        """)

        # Shared state
        chat_history = gr.State([])
        emotion_history = gr.State([])
        memory_cards = gr.State([])
        voice_chat_history = gr.State([])
        voice_emotion_history = gr.State([])
        voice_memory_cards = gr.State([])
        fusion_state = gr.State({})

        # Build tabs
        with gr.Tabs():
            text_components = create_text_chat_tab()
            voice_components = create_voice_chat_tab()
            video_components = create_video_chat_tab()
            create_architecture_tab()
            create_troubleshoot_tab()

        # Bind callbacks
        bind_text_chat_events(text_components, chat_history, emotion_history, memory_cards)
        bind_voice_chat_events(voice_components, voice_chat_history,
                               voice_emotion_history, voice_memory_cards)
        bind_video_chat_events(video_components, fusion_state)

    return demo
