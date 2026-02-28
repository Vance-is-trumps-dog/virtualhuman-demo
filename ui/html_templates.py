"""
HTML templates: Architecture diagram, device diagnostic, troubleshooting guide.
Bug 7 fix: false claims corrected (MediaPipe -> Qwen-VL, React Native -> Gradio + Three.js).
"""

# ---------------------------------------------------------------------------
# Architecture Diagram HTML (Bug 7: corrected false claims)
# ---------------------------------------------------------------------------
ARCH_HTML = """
<div style="padding:20px;font-family:sans-serif;">
  <h3 style="text-align:center;color:#555;margin-bottom:24px;">🏗️ 三大功能管线 & Multi-Agent 协同架构</h3>

  <div style="margin-bottom:20px;padding:16px;border-radius:12px;background:linear-gradient(135deg,rgba(102,126,234,0.08),rgba(118,75,162,0.08));border:1px solid rgba(102,126,234,0.15);">
    <h4 style="color:#667eea;margin:0 0 10px;">💬 文字聊天管线</h4>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;">
      <span style="padding:6px 12px;border-radius:16px;background:#667eea;color:#fff;">新建虚拟人</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#f093fb;color:#fff;">用户输入</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#4facfe;color:#fff;">情感分析</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#43e97b;color:#fff;">记忆检索</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#ffd700;color:#333;">AI 回复</span>
    </div>
  </div>

  <div style="margin-bottom:20px;padding:16px;border-radius:12px;background:linear-gradient(135deg,rgba(67,233,123,0.08),rgba(56,249,215,0.08));border:1px solid rgba(67,233,123,0.15);">
    <h4 style="color:#43e97b;margin:0 0 10px;">🎤 语音聊天管线</h4>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;">
      <span style="padding:6px 12px;border-radius:16px;background:#43e97b;color:#fff;">新建虚拟人</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#38f9d7;color:#333;">录音</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#f093fb;color:#fff;">ASR 识别</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#667eea;color:#fff;">情感分析</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#f5576c;color:#fff;">AI 回复</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#ffd700;color:#333;">TTS 合成</span>
    </div>
  </div>

  <div style="margin-bottom:20px;padding:16px;border-radius:12px;background:linear-gradient(135deg,rgba(240,147,251,0.08),rgba(245,87,108,0.08));border:1px solid rgba(240,147,251,0.15);">
    <h4 style="color:#f093fb;margin:0 0 10px;">📹 视频聊天管线 (旗舰向导流)</h4>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;">
      <span style="padding:6px 12px;border-radius:16px;background:#f093fb;color:#fff;">新建虚拟人</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#f5576c;color:#fff;">3D建模形象</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#667eea;color:#fff;">已有视频输入</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#4facfe;color:#fff;">已有三通道融合</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#43e97b;color:#fff;">虚拟人动画</span><span style="color:#999;">→</span>
      <span style="padding:6px 12px;border-radius:16px;background:#ffd700;color:#333;">AI + TTS + 动画输出</span>
    </div>
  </div>

  <div style="padding:16px;border-radius:12px;background:rgba(102,126,234,0.04);border:1px solid rgba(102,126,234,0.1);">
    <h4 style="color:#555;text-align:center;margin:0 0 12px;">🛠️ 技术栈</h4>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;">
      <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
        <strong>🧠 AI 模型</strong><br/><small style="color:#777;">Qwen-turbo (对话/情感/记忆)</small>
      </div>
      <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
        <strong>🎤 语音识别</strong><br/><small style="color:#777;">Paraformer-realtime-v2</small>
      </div>
      <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
        <strong>🔊 语音合成</strong><br/><small style="color:#777;">Sambert TTS (4种音色)</small>
      </div>
      <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
        <strong>🧊 3D 渲染</strong><br/><small style="color:#777;">Three.js + 9种ActionTag</small>
      </div>
      <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
        <strong>📹 视觉分析</strong><br/><small style="color:#777;">Qwen-VL 多模态视觉分析</small>
      </div>
      <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.5);border:1px solid #eee;">
        <strong>📱 前端框架</strong><br/><small style="color:#777;">Gradio + Three.js 3D 渲染</small>
      </div>
    </div>
  </div>
</div>
"""


# ---------------------------------------------------------------------------
# Device Diagnostic HTML
# ---------------------------------------------------------------------------
DEVICE_DIAGNOSTIC_HTML = """
<div style="padding:12px;border-radius:10px;background:rgba(102,126,234,0.06);border:1px solid rgba(102,126,234,0.12);">
  <div id="diag-result" style="font-size:13px;color:#555;line-height:1.8;">⏳ 正在检测设备...</div>
</div>
<script>
(async function(){
  const results = [];
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      results.push('❌ 浏览器不支持 mediaDevices API（请使用 Chrome/Edge/Firefox 最新版）');
      document.getElementById('diag-result').innerHTML = results.join('<br>');
      return;
    }
    results.push('✅ mediaDevices API 可用');
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter(d => d.kind === 'videoinput');
    const mics = devices.filter(d => d.kind === 'audioinput');
    results.push('📷 检测到 ' + cameras.length + ' 个摄像头');
    results.push('🎤 检测到 ' + mics.length + ' 个麦克风');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({video:true, audio:true});
      results.push('✅ 摄像头+麦克风权限已获取');
      stream.getTracks().forEach(t => t.stop());
    } catch(e) {
      if (e.name === 'NotAllowedError')
        results.push('⚠️ 用户拒绝了权限，请点击地址栏锁图标重新允许');
      else if (e.name === 'NotFoundError')
        results.push('❌ 未找到摄像头或麦克风设备');
      else if (e.name === 'NotReadableError')
        results.push('❌ 设备被占用或驱动异常（请关闭其他使用摄像头的程序）');
      else
        results.push('❌ ' + e.name + ': ' + e.message);
    }
    if (location.protocol !== 'https:' && !['localhost','127.0.0.1'].includes(location.hostname))
      results.push('⚠️ 非 HTTPS 环境，浏览器会阻止摄像头/麦克风访问。请使用 share=True 启动或配置 SSL');
    else
      results.push('✅ 安全上下文 (' + location.protocol + '//' + location.hostname + ')');
  } catch(err) {
    results.push('❌ 检测异常: ' + err.message);
  }
  document.getElementById('diag-result').innerHTML = results.join('<br>');
})();
</script>
"""


# --- TROUBLESHOOT_PLACEHOLDER ---

# ---------------------------------------------------------------------------
# Browser Troubleshooting Guide HTML
# ---------------------------------------------------------------------------
TROUBLESHOOT_HTML = """
<div style="padding:20px;font-family:sans-serif;">
  <h3 style="text-align:center;color:#555;margin-bottom:20px;">🔧 浏览器环境排查指南</h3>
  <div style="margin-bottom:20px;padding:16px;border-radius:12px;background:linear-gradient(135deg,rgba(240,147,251,0.08),rgba(245,87,108,0.08));border:1px solid rgba(240,147,251,0.15);">
    <h4 style="color:#f093fb;margin:0 0 12px;">📷 摄像头打不开排查</h4>
    <table style="width:100%;font-size:13px;border-collapse:collapse;">
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;width:30%;">1. 检查 HTTPS</td>
        <td style="padding:8px;color:#666;">非 localhost 必须用 HTTPS。启动时用 <code>share=True</code> 或配置 SSL 证书</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;">2. 浏览器权限</td>
        <td style="padding:8px;color:#666;">Chrome: 地址栏左侧锁图标 → 网站设置 → 摄像头 → 允许</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;">3. 设备管理器</td>
        <td style="padding:8px;color:#666;">Windows: 设备管理器 → 图像设备 → 确认摄像头驱动正常</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;">4. 占用检查</td>
        <td style="padding:8px;color:#666;">关闭其他使用摄像头的程序（Teams/Zoom/微信等）</td>
      </tr>
      <tr>
        <td style="padding:8px;font-weight:bold;">5. 浏览器测试</td>
        <td style="padding:8px;color:#666;">访问 <a href="https://webcamtests.com" target="_blank">webcamtests.com</a> 验证摄像头是否正常</td>
      </tr>
    </table>
  </div>
  <div style="margin-bottom:20px;padding:16px;border-radius:12px;background:linear-gradient(135deg,rgba(67,233,123,0.08),rgba(56,249,215,0.08));border:1px solid rgba(67,233,123,0.15);">
    <h4 style="color:#43e97b;margin:0 0 12px;">🎤 麦克风找不到排查</h4>
    <table style="width:100%;font-size:13px;border-collapse:collapse;">
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;width:30%;">1. 检查 HTTPS</td>
        <td style="padding:8px;color:#666;">同上，非 localhost 必须 HTTPS</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;">2. 浏览器权限</td>
        <td style="padding:8px;color:#666;">Chrome: 地址栏锁图标 → 网站设置 → 麦克风 → 允许</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;">3. 系统设置</td>
        <td style="padding:8px;color:#666;">Windows: 设置 → 系统 → 声音 → 输入设备 → 确认有麦克风</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(0,0,0,0.06);">
        <td style="padding:8px;font-weight:bold;">4. 隐私设置</td>
        <td style="padding:8px;color:#666;">Windows: 设置 → 隐私 → 麦克风 → 允许应用访问</td>
      </tr>
      <tr>
        <td style="padding:8px;font-weight:bold;">5. 测试录音</td>
        <td style="padding:8px;color:#666;">Windows 搜索「录音机」测试麦克风是否正常工作</td>
      </tr>
    </table>
  </div>
</div>
"""