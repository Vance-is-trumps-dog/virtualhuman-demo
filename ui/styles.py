"""
Custom CSS styles for the Gradio UI.
"""

CUSTOM_CSS = """
.gradio-container {
    max-width: 1400px !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.message-wrap { max-height: 500px !important; }
.app-header { text-align: center; padding: 20px 0 10px; }
.app-header h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2em;
    margin-bottom: 5px;
}
.memory-card {
    background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 13px;
}
.stat-box {
    text-align: center; padding: 12px; border-radius: 10px;
    background: rgba(102,126,234,0.08);
    border: 1px solid rgba(102,126,234,0.15);
}
.stat-box .num {
    font-size: 24px; font-weight: bold;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-box .label { font-size: 12px; color: #888; margin-top: 4px; }
.pipeline-step {
    padding: 8px 12px; margin: 4px 0; border-radius: 8px;
    background: rgba(102,126,234,0.06); border-left: 3px solid #667eea;
    font-size: 13px; transition: all 0.3s ease;
}
.pipeline-step.active { background: rgba(102,126,234,0.15); border-left-color: #764ba2; }
.pipeline-step.done { background: rgba(67,233,123,0.1); border-left-color: #43e97b; }
.fusion-bar {
    height: 16px; border-radius: 8px; background: #eee; overflow: hidden; margin: 4px 0;
}
.fusion-bar-fill {
    height: 100%; border-radius: 8px; transition: width 0.5s ease;
    background: linear-gradient(90deg, #667eea, #764ba2);
}
@media (max-width: 768px) {
    .gradio-container { padding: 8px !important; }
    #avatar-container { height: 280px !important; }
}
/* 仅提升复选框层级，绝不破坏原生外观 */
label.container {
    z-index: 999 !important;
    pointer-events: auto !important;
}
"""
