# 🚀 快速启动指南

## 📋 前置准备

### 1. 环境要求
- Python 3.10+
- ffmpeg（音视频处理）
- DashScope API Key

### 2. 获取 API Key
1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 点击右上角个人头像 → **API-KEY**
3. 创建并复制你的 API Key

### 3. 开通必需权限
在"模型广场"搜索并开通：
- ✅ **Qwen-turbo**（对话）
- ✅ **CosyVoice V3 Flash**（语音合成）
- ✅ **qwen3-asr-flash-filetrans**（语音识别）
- ✅ **Qwen-VL**（视觉理解）
- ✅ **wan2.2-s2v**（视频生成，仅北京地域）

---

## 🔧 安装步骤

### Windows
```bash
cd C:\Users\administer\Desktop\VirtualHumanApp\modelscope-demo

# 激活虚拟环境（如果已创建）
venv310\Scripts\activate

# 或创建新虚拟环境
python -m venv venv310
venv310\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置 API Key
set DASHSCOPE_API_KEY=sk-your-key-here

# 启动应用
python app.py
```

### Linux/Mac
```bash
cd ~/Desktop/VirtualHumanApp/modelscope-demo

# 激活虚拟环境
source venv310/bin/activate

# 或创建新虚拟环境
python -m venv venv310
source venv310/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置 API Key
export DASHSCOPE_API_KEY=sk-your-key-here

# 启动应用
python app.py
```

---

## 🌐 访问应用

启动成功后，访问：
```
http://localhost:7860
```

---

## 🎯 功能测试指南

### 测试 1：🎤 职场情绪同传雷达

#### 步骤：
1. 点击 **"🎤 职场同传助手"** Tab
2. 在左侧填写 API Key（如果环境变量未设置）
3. 点击 **"点击录音捕捉同事发言"** 按钮
4. 说一句话（可以带情绪，如愤怒的语气）
5. 停止录音

#### 预期结果：
- ✅ 管线状态显示：录音 → 千问语音解析 → 生成同传摘要
- ✅ 显示捕捉到的情感（如：😠 angry）
- ✅ 显示职场摘要（金色背景框）：
  ```
  📝 【核心意图】：...
  💡 【应对建议】：...
  ```
- ✅ 如果是愤怒/恐惧情感，显示红色呼吸闪烁警报框

#### 测试用例：
| 说话内容 | 预期情感 | 预期警报 |
|---------|---------|---------|
| "这个项目进度太慢了！" | angry | 🔴 红色警报 |
| "我很担心这个方案" | fearful | 🔴 红色警报 |
| "今天天气不错" | neutral | 🟡 金色摘要 |
| "太棒了！" | happy | 🟡 金色摘要 |

---

### 测试 2：👁️ 面对面多模态扫描仪

#### 步骤：
1. 点击 **"📹 数字人聊天 (Wan2.2)"** Tab
2. 在左侧上传一张正脸参考图
3. 填写 API Key（如果环境变量未设置）
4. 点击 **"录制您的说话视频"** 按钮
5. 对着摄像头说话（可以做出表情）
6. 停止录制
7. 点击 **"🚀 发送并生成对话"**

#### 预期结果：
- ✅ 管线状态显示：接收视频 → 多模态分析 → AI 推理与TTS → 生成视频
- ✅ **秒级响应**：文字和语音立即显示
- ✅ 显示情感融合结果：
  ```
  🎯 融合情感: 😠 angry
  📊 效价 (Valence): -0.80
  📊 唤醒 (Arousal): 0.80
  📊 置信度: 85%
  🎬 动作标签: ⚡ 警觉注意
  ```
- ✅ 如果检测到愤怒/恐惧，显示红色警报：
  ```
  ⚠️ 警觉状态：检测到对方情绪异常，请注意防范！
  ```
- ✅ 视频在后台生成（约1-3分钟）

#### 测试用例：
| 表情 + 语气 | 预期融合情感 | 预期警报 |
|-----------|------------|---------|
| 愤怒表情 + 愤怒语气 | angry (高置信度) | 🔴 红色警报 |
| 微笑 + 平静语气 | happy | 无警报 |
| 皱眉 + 担忧语气 | fearful | 🔴 红色警报 |

---

## 🔍 故障排查

### 问题 1：摄像头/麦克风无法访问
**原因**：浏览器权限未开启或非 HTTPS 环境

**解决方案**：
1. 检查浏览器地址栏是否有摄像头/麦克风权限提示
2. 点击允许访问
3. 如果是远程访问，需要使用 HTTPS 或 SSH 隧道

### 问题 2：API 调用失败
**原因**：API Key 未设置或权限未开通

**解决方案**：
1. 检查环境变量 `DASHSCOPE_API_KEY` 是否设置
2. 或在界面左侧输入 API Key
3. 确认已在阿里云百炼控制台开通所需模型权限

### 问题 3：语音识别失败
**原因**：音频文件格式不支持或 OSS 上传失败

**解决方案**：
1. 检查 `services/oss_upload.py` 是否正确配置
2. 确认 OSS Bucket 在北京地域
3. 检查 OSS 访问权限

### 问题 4：视频生成失败
**原因**：wan2.2-s2v 权限未开通或参考图不合规

**解决方案**：
1. 确认 API Key 已开通 wan2.2-s2v 权限（仅北京地域）
2. 使用清晰的正脸照片作为参考图
3. 避免使用有版权争议的图片

### 问题 5：CSS 样式未生效
**原因**：浏览器缓存

**解决方案**：
1. 按 Ctrl+F5 强制刷新页面
2. 清除浏览器缓存
3. 使用无痕模式测试

---

## 📊 性能优化建议

### 1. 视频生成速度
- 使用 480P 分辨率（已默认设置）
- 避免高峰时段使用
- 考虑使用专用 API Key

### 2. 语音识别准确度
- 在安静环境录音
- 说话清晰，语速适中
- 避免背景噪音

### 3. 情感识别准确度
- 视频聊天：确保光线充足，面部清晰
- 语音聊天：语气要明显
- 文本聊天：使用明确的情感词汇

---

## 🎨 自定义配置

### 修改情感融合权重
文件：`ui/tabs/video_chat.py:80-82`
```python
w_f = gr.Slider(0, 1, value=0.4, label="面部权重")  # 默认 40%
w_v = gr.Slider(0, 1, value=0.2, label="语音权重")  # 默认 20%
w_t = gr.Slider(0, 1, value=0.4, label="文本权重")  # 默认 40%
```

### 修改警报样式
文件：`ui/styles.py:67-82`
```css
.danger-alert {
    border: 3px solid #ff0000 !important;  /* 边框颜色 */
    animation: danger-pulse 1.5s ease-in-out infinite !important;  /* 动画速度 */
}
```

### 修改职场 Prompt
文件：`services/chat.py:25-39`
```python
_EMOTION_SUFFIX = (
    "\n\n[严格输出格式要求]\n"
    "你现在的身份是听障人士的【职场无障碍同传助理】。..."
)
```

---

## 📞 技术支持

### 遇到问题？
1. 查看控制台日志：`python app.py` 的输出
2. 检查浏览器控制台（F12）的错误信息
3. 运行验证脚本：`python check_accessibility.py`

### 反馈渠道
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- 项目文档：`COMPLETION_REPORT.md`

---

## 🎉 开始使用

现在你已经准备好了！运行以下命令启动应用：

```bash
python app.py
```

然后访问 http://localhost:7860 开始体验无障碍职场辅助功能！

---

**祝使用愉快！** 🚀
