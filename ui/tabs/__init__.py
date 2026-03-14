"""
UI Tabs package - provides create_demo() that assembles all tabs.
"""
import gradio as gr
from ui.styles import CUSTOM_CSS
from ui.tabs.voice_chat import create_voice_chat_tab, bind_voice_chat_events
from ui.tabs.radar_tab import create_radar_tab, bind_radar_events
from ui.tabs.psychology_tab import create_psychology_tab, bind_psychology_events
from ui.tabs.zijian_tab import create_zijian_tab
from ui.tabs.troubleshoot import create_troubleshoot_tab

def create_demo():
    """Assemble the full Gradio demo with all tabs and callbacks."""
    with gr.Blocks(
        title="SilentBridge 无声之桥",
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="blue"),
    ) as demo:
        # Header
        gr.Markdown(
            """
            # 🌉 SilentBridge 无声之桥
            **专为听障群体打造的多模态智能辅助系统** | *用科技补全缺失的情绪，用AI重构安全的边界*
            """
        )

        gr.HTML("""
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
        voice_chat_history = gr.State([])
        voice_emotion_history = gr.State([])
        voice_memory_cards = gr.State([])
        psy_history = gr.State([])
        psy_memory = gr.State([])

        # Build tabs
        with gr.Tabs():
            # 1. 职场同传助手 (多模态升级版)
            voice_components = create_voice_chat_tab()
            # 2. 环境安全雷达
            radar_components = create_radar_tab()
            # 3. 无声树洞 (心理辅导)
            psychology_components = create_psychology_tab()
            # 4. 字见 (无障碍识字) - Iframe 嵌入外部应用
            create_zijian_tab()
            # 5. 新的系统架构图 Tab
            create_new_architecture_tab()
            # 6. 故障排查
            create_troubleshoot_tab()

        # Bind callbacks
        bind_voice_chat_events(voice_components, voice_chat_history, voice_emotion_history, voice_memory_cards)
        bind_radar_events(radar_components)
        bind_psychology_events(psychology_components, psy_history, psy_memory, voice_components["voice_api_key"])

    return demo

def create_new_architecture_tab():
    with gr.TabItem("🏗️ 核心架构体系"):
        gr.Markdown("""
        ### 🌉 SilentBridge 核心架构图

        我们构建了以**多模态情感计算**和**环境声学感知**为核心的三大防御网络：

        #### 1. 职场多模态同传引擎 (Workplace Empathy Engine)
        - **视觉与听觉融合**: 提取视频关键帧进行面部微表情分析，同时通过 ASR 提取声带震动频率中的真实情感。
        - **双擎验证**: 结合 `Qwen-Turbo` 文本大模型进行交叉验证，推翻虚假情感，生成直白的【核心意图】与【应对建议】。

        #### 2. 环境安全阻断网 (Environmental Radar)
        - **底层基建**: ModelScope 轻量级声学分类模型 (`audio-classification`)
        - **交互创新**: 一旦侦测到危险，系统无视当前操作，执行**全屏高对比度视觉阻断闪烁**，保障听障者物理安全。

        #### 3. 无声心理树洞 (Silent Sanctuary)
        - **底层基建**: `Qwen-Turbo` 结合深度定制的 Deaf-Friendly Prompt
        - **干预机制**: 内置多轮记忆胶囊与毫秒级危机词扫描，在检测到自毁倾向时，第一时间弹出视觉求助通道。
        """)