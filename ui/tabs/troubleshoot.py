"""
Tab 6: Troubleshooting - browser environment diagnostics.
"""

import gradio as gr

from ui.html_templates import TROUBLESHOOT_HTML


def create_troubleshoot_tab():
    """Create Tab 6 UI."""
    with gr.TabItem("🔧 环境排查"):
        gr.HTML(TROUBLESHOOT_HTML)
