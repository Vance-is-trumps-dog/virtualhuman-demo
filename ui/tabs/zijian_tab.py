"""
字见 (Zijian) Tab - 无障碍识字功能
通过 Iframe 嵌入部署在 Vercel 上的字见应用
"""
import gradio as gr


def create_zijian_tab():
    """
    创建字见 Tab，使用 Iframe 嵌入外部应用
    注意：需要先将字见部署到 Vercel，获取 HTTPS 域名后替换 ZIJIAN_URL
    """
    # 填入你刚刚大功告成的专属域名！
    ZIJIAN_URL = "https://zijian-main.vercel.app"
    
    with gr.TabItem("📖 字见 (无障碍识字)"):
        # 核心：配置 allow 属性，下发摄像头、麦克风和 USB 权限
        iframe_html = f"""
        <div style="width: 100%; height: 85vh; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb;">
            <iframe 
                src="{ZIJIAN_URL}" 
                width="100%" 
                height="100%" 
                frameborder="0"
                allow="camera; microphone; display-capture; fullscreen; usb"
                sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-downloads"
            ></iframe>
        </div>
        """
        gr.HTML(iframe_html)
