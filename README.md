# 🌟 VirtualHumanApp — AI 数字人陪伴系统

> 魔搭社区 AI 应用大赛参赛作品

基于 Multi-Agent 架构的多模态 AI 数字人陪伴系统。集成文字聊天、语音聊天、视频聊天三大核心功能，通过阿里云 wan2.2-s2v 大模型实现云端数字人视频生成，支持多模态情感融合引擎与记忆系统。

## 🎭 自定义你的专属数字人

**重要提示**：本项目内置的虚拟人设定（如"灵音"）仅用于快速测试和演示。你可以完全自定义：

- **人设与性格**：修改 System Prompt，定义数字人的身份、说话风格、专业领域
- **音色选择**：5 种 CosyVoice V3 高品质音色（4女1男），匹配不同性格
- **外貌形象**：上传任意正脸照片作为数字人形象（视频聊天功能）
- **记忆与情感**：系统会自动学习对话历史，生成个性化记忆卡片

**快速开始自定义**：
1. 在界面左侧找到"设定 (System Prompt)"输入框
2. 输入你想要的人设描述，例如：
   - `你是一位资深心理咨询师，擅长倾听和共情`
   - `你是一个二次元萝莉，说话带"喵~"尾音`
   - `你是我的私人健身教练，严格但充满鼓励`
3. 选择匹配的音色和上传对应的参考图片
4. 开始对话，系统会按照你的设定生成回复

---

## 🏆 核心技术特性

- **云端无缝视频合成**：全面接入阿里云 `wan2.2-s2v` 视频大模型，实现单张照片+声音的影视级对口型数字人驱动
- **智能降级容错机制**：TTS 语音合成自带"高级音色 → 基础音色"平滑降级；当所选音色未开通权限时，自动切换到基础女声（龙小淳 V3），保证聊天不中断
- **异步轮询与体验优化**：针对云端视频生成耗时，设计了"前端先出字出声、后台静默生成视频"的分段式 UI 反馈流，极大缓解用户等待焦虑

## ✨ 三大核心功能

### 💬 文字聊天
| 特性 | 说明 |
|------|------|
| 多角色 AI 对话 | 可自定义虚拟人人设与性格 |
| 情感分析 | Qwen AI 情感识别 + 关键词 fallback，支持 8 种情感 |
| TTS 语音合成 | CosyVoice V3 Flash，5 种高品质音色 |
| 记忆系统 | 每 5 轮对话自动生成记忆卡片 |

### 🎤 语音聊天
| 特性 | 说明 |
|------|------|
| 完整语音管线 | 录音 → ASR 识别 → 情感分析 → AI 回复 → TTS 合成 |
| 管线状态可视化 | 实时显示每个步骤的执行状态 |
| SenseVoice / Paraformer ASR | DashScope 语音识别 |

### 📹 数字人视频聊天（旗舰功能）
| 子功能 | 说明 |
|--------|------|
| 📸 参考图上传 | 上传一张正脸照片作为数字人形象 |
| 🔬 多模态情感融合 | 面部 + 语音 + 文本三通道加权融合 |
| 🎬 云端视频生成 | wan2.2-s2v 大模型生成说话视频 |
| 🔊 先声后画 | TTS 语音即时播放，视频后台生成，体验流畅 |

## 🎨 可用音色列表（CosyVoice V3）

| 音色名称 | Voice ID | 特点 |
|---------|----------|------|
| 👩 龙小淳 | `longxiaochun_v3` | 知性积极女声，适合专业场景 |
| 👩 YUMI | `longyumi_v3` | 正经青年女声，清晰标准 |
| 👩 龙安温 | `longanwen_v3` | 优雅知性女声，温柔大方 |
| 👩 龙安台 | `longantai_v3` | 嗲甜台湾女声，活泼可爱 |
| 👦 龙安洋 | `longanyang` | 阳光大男孩，元气满满 |

**自定义音色**：在 `config/settings.py` 中修改 `AVAILABLE_VOICES` 字典即可添加更多音色。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────┐
│               用户交互层 (Gradio)             │
│      文字输入 / 语音录入 / 摄像头 / 视频播放   │
├─────────────────────────────────────────────┤
│               Agent 协同层                    │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │对话Agent│ │情感Agent│ │记忆Agent│          │
│  │Qwen对话 │ │多模态融合│ │摘要生成 │          │
│  └────────┘ └────────┘ └────────┘          │
│  ┌────────┐ ┌──────────┐                    │
│  │语音Agent│ │视频生成   │                    │
│  │ASR + TTS│ │wan2.2-s2v│                    │
│  └────────┘ └──────────┘                    │
├─────────────────────────────────────────────┤
│               云端服务层                      │
│  Qwen-turbo / Paraformer / CosyVoice V3     │
│  wan2.2-s2v / 阿里云 OSS                    │
│            (DashScope API)                   │
└─────────────────────────────────────────────┘
```

## 🔬 多模态情感融合算法

```
面部通道 (40%) ──┐
                  ├── 加权融合 → Valence/Arousal → 情感标签
语音通道 (20%) ──┤
                  │   时间平滑 (EMA, 衰减 0.7)
文本通道 (40%) ──┘
                    → 情感上下文注入 → AI 回复生成 → TTS → 视频生成
```

## 🛠️ 使用的模型 & 服务

| 服务 | 模型 | 用途 |
|------|------|------|
| 通义千问 | Qwen-turbo | AI 对话、情感分析、记忆摘要 |
| Paraformer | paraformer-v2 | 语音识别 (ASR) |
| CosyVoice | cosyvoice-v3-flash | 语音合成（5 种高品质音色） |
| wan2.2-s2v | wan2.2-s2v | 云端数字人视频生成 |
| 阿里云 OSS | - | 本地文件中转（音频/图片上传） |

## 🚀 本地运行

### 前置条件

- Python 3.10+
- ffmpeg（音视频处理）
- DashScope API Key（[获取地址](https://dashscope.console.aliyun.com/apiKey)）
- **必须开通以下权限**：
  - ✅ Qwen-turbo（对话）
  - ✅ CosyVoice V3 Flash（语音合成）
  - ✅ Paraformer V2（语音识别）
  - ✅ wan2.2-s2v（视频生成，**仅北京地域**）
- 阿里云 OSS Bucket（建议华北2北京地域，与 wan2.2-s2v 同区）

### 安装

```bash
cd modelscope-demo
python -m venv venv310
venv310\Scripts\activate        # Windows
# source venv310/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 环境变量配置

```bash
# DashScope (必填)
set DASHSCOPE_API_KEY=sk-your-key-here

# 阿里云 OSS (视频聊天必填)
set OSS_ACCESS_KEY_ID=your-ak
set OSS_ACCESS_KEY_SECRET=your-sk
set OSS_BUCKET_NAME=your-bucket
set OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

### 启动

```bash
python app.py
```

访问 http://localhost:7860 即可使用。

## 📁 项目结构

```
modelscope-demo/
├── app.py                      # 主入口
├── requirements.txt            # Python 依赖
├── configuration.json          # 魔搭创空间配置
├── config/
│   └── settings.py             # 全局配置与常量（音色列表在这里）
├── services/
│   ├── api_client.py           # DashScope API 封装
│   ├── asr.py                  # 语音识别 (Paraformer)
│   ├── chat.py                 # AI 对话 (Qwen)
│   ├── emotion.py              # 情感分析与融合引擎
│   ├── oss_upload.py           # 阿里云 OSS 文件上传
│   ├── tts.py                  # 语音合成 (CosyVoice V3)
│   ├── video.py                # 视频处理 (ffmpeg)
│   └── video_gen.py            # 数字人视频生成 (wan2.2-s2v)
├── ui/
│   ├── components.py           # UI 组件与 HTML 格式化
│   ├── styles.py               # CSS 样式
│   └── tabs/
│       ├── __init__.py         # Tab 组装与 demo 创建
│       ├── text_chat.py        # 文字聊天 Tab
│       ├── voice_chat.py       # 语音聊天 Tab
│       ├── video_chat.py       # 数字人视频聊天 Tab
│       ├── architecture.py     # 架构说明 Tab
│       └── troubleshoot.py     # 故障排查 Tab
├── tests/                      # 单元测试
└── assets/                     # 静态资源
```

## ☁️ 魔搭创空间部署

1. 在 [ModelScope 创空间](https://modelscope.cn/studios) 创建新项目（SDK 选 Gradio）
2. 配置环境变量：`DASHSCOPE_API_KEY`、`OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`、`OSS_BUCKET_NAME`、`OSS_ENDPOINT`
3. 上传项目文件
4. 等待构建完成

## 🔧 常见问题

### Q: 为什么只能听到男声/女声无法使用？
**A**: 这是因为你的 API Key 未开通所选音色的权限。系统已自动降级到基础女声（龙小淳 V3）。请前往 [阿里云百炼控制台](https://bailian.console.aliyun.com/) → 模型广场 → 搜索 `CosyVoice` → 开通权限。

### Q: 控制台报错 "Model not found" 或 "voice not found"？
**A**: 确保你使用的是 CosyVoice V3 模型的音色（带 `_v3` 后缀或官方 V3 音色列表中的音色）。不要混用 V2 音色和 V3 模型。

### Q: 如何添加更多音色？
**A**: 编辑 `config/settings.py` 中的 `AVAILABLE_VOICES` 字典，添加符合 CosyVoice V3 规范的音色 ID。参考[官方文档](https://help.aliyun.com/zh/model-studio/developer-reference/cosyvoice-api)。

### Q: 视频生成失败？
**A**:
1. 确保 API Key 已开通 `wan2.2-s2v` 权限（仅北京地域）
2. 确保 OSS Bucket 在北京地域（`oss-cn-beijing`）
3. 检查参考图是否清晰、正脸、无版权问题

## 📄 License

MIT

---

**💡 提示**：内置的"灵音"等虚拟人设定仅为演示用途，请根据你的需求自由修改 System Prompt 和音色，打造专属于你的 AI 数字人！
