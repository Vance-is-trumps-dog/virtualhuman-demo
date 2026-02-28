"""
Tab 4: Architecture - displays system architecture diagram.
"""

import gradio as gr

from ui.html_templates import ARCH_HTML


def create_architecture_tab():
    """Create Tab 4 UI."""
    with gr.TabItem("🏗️ 功能架构"):
        gr.HTML(ARCH_HTML)
        gr.HTML("""
        <div style="padding:20px;">
          <h4 style="color:#555;text-align:center;">核心功能一览</h4>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:14px;">
            <div style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
              <strong>💬 文字聊天</strong><br/>
              <small style="color:#777;">AI 对话 + 情感分析 + ActionTag + TTS</small>
            </div>
            <div style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
              <strong>🎤 语音聊天</strong><br/>
              <small style="color:#777;">ASR → AI → TTS 完整管线可视化</small>
            </div>
            <div style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
              <strong>📹 视频聊天</strong><br/>
              <small style="color:#777;">多模态融合 + 参考图建模 + 全景场景</small>
            </div>
            <div style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
              <strong>🧊 3D 虚拟人</strong><br/>
              <small style="color:#777;">Three.js 渲染 · 9 种 ActionTag 动画</small>
            </div>
            <div style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
              <strong>❤️ 情感融合</strong><br/>
              <small style="color:#777;">面部40% + 语音20% + 文本40% 加权融合</small>
            </div>
            <div style="padding:12px;border-radius:10px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
              <strong>🧠 记忆系统</strong><br/>
              <small style="color:#777;">自动摘要 · 关键信息提取 · 上下文增强</small>
            </div>
          </div>
        </div>
        """)
