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

/* 🛡️ 无障碍 UI：危险警报呼吸闪烁红框 */
.danger-alert {
    border: 3px solid #ff0000 !important;
    background: rgba(255, 0, 0, 0.1) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    animation: danger-pulse 1.5s ease-in-out infinite !important;
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.5) !important;
}

@keyframes danger-pulse {
    0%, 100% {
        border-color: #ff0000;
        box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7);
        background: rgba(255, 0, 0, 0.1);
    }
    50% {
        border-color: #ff6666;
        box-shadow: 0 0 30px 15px rgba(255, 0, 0, 0);
        background: rgba(255, 0, 0, 0.2);
    }
}

/* 🛡️ 无障碍 UI：职场摘要突出显示 */
.workplace-summary {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%) !important;
    border: 2px solid #ff8c00 !important;
    padding: 16px !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3) !important;
    margin: 8px 0 !important;
}

/* 🛡️ 无障碍 UI：警觉状态指示器 */
.alert-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #ff0000;
    animation: alert-blink 1s ease-in-out infinite;
    margin-right: 8px;
}

@keyframes alert-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* 🛡️ 无障碍 UI：情感警报文本 */
.emotion-alert-text {
    color: #ff0000 !important;
    font-weight: bold !important;
    font-size: 18px !important;
    text-shadow: 0 0 10px rgba(255, 0, 0, 0.5) !important;
}

/* ====================================================
   环境安全视觉阻断 UI (Accessibility Alert)
   ==================================================== */

/* 致命危险：全屏血红频闪（火警、汽车鸣笛） */
.extreme-danger-alert {
    background: rgba(255, 0, 0, 0.9) !important;
    border: 5px solid #8b0000 !important;
    border-radius: 16px !important;
    padding: 30px !important;
    color: white !important;
    text-align: center !important;
    box-shadow: 0 0 50px rgba(255, 0, 0, 1) !important;
    animation: strobe-flash 0.3s infinite !important; /* 极快频闪 */
    position: relative;
    z-index: 9999;
}

@keyframes strobe-flash {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.02); }
    100% { opacity: 1; transform: scale(1); }
}

/* 提示级安全提醒：黄色/蓝色柔和呼吸（门铃、闹钟） */
.safe-notice-alert {
    background: rgba(0, 123, 255, 0.2) !important;
    border: 3px solid #007bff !important;
    border-radius: 16px !important;
    padding: 20px !important;
    color: #004085 !important;
    text-align: center !important;
    animation: gentle-breathe 2s infinite !important;
}

@keyframes gentle-breathe {
    0% { box-shadow: 0 0 0px rgba(0,123,255,0); }
    50% { box-shadow: 0 0 20px rgba(0,123,255,0.6); }
    100% { box-shadow: 0 0 0px rgba(0,123,255,0); }
}

/* 中等警告：橙色频闪（婴儿啼哭等） */
.warning-alert {
    background: rgba(255, 165, 0, 0.9) !important;
    border: 5px solid #ff8c00 !important;
    border-radius: 16px !important;
    padding: 30px !important;
    color: white !important;
    text-align: center !important;
    animation: strobe-flash 0.6s infinite !important;
}

/* 屏幕接管文字大字号 */
.alert-giant-text {
    font-size: 48px !important;
    font-weight: 900 !important;
    margin: 10px 0 !important;
    line-height: 1.2 !important;
}

/* 心理辅导大字体聊天界面 */
.large-text-chat .message {
    font-size: 18px !important;
    line-height: 1.6 !important;
}

/* 针对无声树洞的聊天气泡加大字号 */
.large-text-chat .message-wrap .message {
    font-size: 20px !important;
    line-height: 1.6 !important;
    padding: 12px 18px !important;
}

/* 确保求助通道的文字清晰可见 */
.large-text-chat .message-wrap .message p {
    color: #333 !important;
}
"""
