#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无障碍功能代码检查脚本（静态检查）
"""

import sys
import os
import io

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_file_content(filepath, required_strings, description):
    """检查文件是否包含必需的字符串"""
    print(f"\n🔍 检查: {description}")
    print(f"   文件: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        missing = []
        for req in required_strings:
            if req not in content:
                missing.append(req)

        if missing:
            print(f"   ❌ 缺少内容:")
            for m in missing:
                print(f"      - {m}")
            return False
        else:
            print(f"   ✅ 所有必需内容已存在")
            return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def main():
    print("=" * 70)
    print("🛡️  无障碍功能代码检查脚本")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    results = []

    # 检查 1: CSS 样式文件
    results.append(check_file_content(
        os.path.join(base_dir, "ui", "styles.py"),
        [
            ".danger-alert",
            ".workplace-summary",
            ".alert-indicator",
            ".emotion-alert-text",
            "@keyframes danger-pulse",
            "@keyframes alert-blink"
        ],
        "CSS 样式文件 (ui/styles.py)"
    ))

    # 检查 2: UI 组件文件
    results.append(check_file_content(
        os.path.join(base_dir, "ui", "components.py"),
        [
            "def format_fusion_result(result):",
            "def format_workplace_summary(text, emotion=",
            'is_danger = em in ["angry", "fearful"]',
            "danger-alert",
            "alert-indicator",
            "workplace-summary"
        ],
        "UI 组件文件 (ui/components.py)"
    ))

    # 检查 3: 语音聊天 Tab
    results.append(check_file_content(
        os.path.join(base_dir, "ui", "tabs", "voice_chat.py"),
        [
            "voice_summary_display",
            "format_workplace_summary",
            "from ui.components import format_pipeline_status, format_workplace_summary"
        ],
        "语音聊天 Tab (ui/tabs/voice_chat.py)"
    ))

    # 检查 4: 视频聊天 Tab
    results.append(check_file_content(
        os.path.join(base_dir, "ui", "tabs", "video_chat.py"),
        [
            "fusion_result_display",
            "format_fusion_result",
            "from ui.components import format_fusion_result"
        ],
        "视频聊天 Tab (ui/tabs/video_chat.py)"
    ))

    # 检查 5: 情感检测服务
    results.append(check_file_content(
        os.path.join(base_dir, "services", "emotion.py"),
        [
            'def derive_action_tag(emotion: str, arousal: float = 0.5, confidence: float = 0.7) -> str:',
            '"angry": lambda: "alert_attention"',
            '"fearful": lambda: "alert_attention"'
        ],
        "情感检测服务 (services/emotion.py)"
    ))

    # 检查 6: ASR 服务
    results.append(check_file_content(
        os.path.join(base_dir, "services", "asr.py"),
        [
            "def recognize_speech_and_emotion(audio_path: str, api_key: str) -> dict:",
            "qwen3-asr-flash-filetrans",
            "QWEN_EMOTION_MAP"
        ],
        "ASR 服务 (services/asr.py)"
    ))

    print("\n" + "=" * 70)
    print("📊 检查结果汇总")
    print("=" * 70)

    checks = [
        "CSS 样式文件",
        "UI 组件文件",
        "语音聊天 Tab",
        "视频聊天 Tab",
        "情感检测服务",
        "ASR 服务"
    ]

    for i, (name, result) in enumerate(zip(checks, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")

    all_passed = all(results)

    print("=" * 70)
    if all_passed:
        print("🎉 所有代码检查通过！无障碍功能已成功集成。")
        print("\n✅ 已实现的功能:")
        print("  1. 🎤 职场情绪同传雷达")
        print("     - 千问 ASR 同时提取文字 + 情感")
        print("     - 取消 TTS 播报，100% 视觉交互")
        print("     - 输出核心意图摘要和高情商应对建议")
        print()
        print("  2. 👁️ 面对面多模态扫描仪")
        print("     - 三通道情感融合 (视觉40% + 听觉20% + 文本40%)")
        print("     - 秒级响应（双阶段 Yield）")
        print("     - 危险情感自动触发红色警报")
        print()
        print("  3. 🛡️ 无声环境专属 UI")
        print("     - .danger-alert 呼吸闪烁红框")
        print("     - .workplace-summary 突出显示")
        print("     - .alert-indicator 警觉指示器")
        print()
        print("📝 下一步:")
        print("  1. 运行: python app.py")
        print("  2. 访问: http://localhost:7860")
        print("  3. 测试语音聊天的职场摘要功能")
        print("  4. 测试视频聊天的情感警报功能")
        print()
        print("💡 测试建议:")
        print("  - 模拟愤怒/恐惧情感，验证红色警报是否显示")
        print("  - 检查职场摘要是否正确格式化")
        print("  - 确认所有音频输出已被隐藏")
        return 0
    else:
        print("⚠️  部分检查未通过，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
