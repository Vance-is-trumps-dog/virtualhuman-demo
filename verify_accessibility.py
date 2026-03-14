#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无障碍功能验证脚本
检查所有新增的 UI 组件和样式是否正确集成
"""

import sys
import os
import io

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_styles():
    """检查 CSS 样式是否正确添加"""
    print("🔍 检查 1: CSS 样式文件...")
    try:
        from ui.styles import CUSTOM_CSS

        required_classes = [
            ".danger-alert",
            ".workplace-summary",
            ".alert-indicator",
            ".emotion-alert-text",
            "@keyframes danger-pulse",
            "@keyframes alert-blink"
        ]

        missing = []
        for cls in required_classes:
            if cls not in CUSTOM_CSS:
                missing.append(cls)

        if missing:
            print(f"   ❌ 缺少样式类: {', '.join(missing)}")
            return False
        else:
            print("   ✅ 所有 CSS 样式类已正确添加")
            return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def check_components():
    """检查组件函数是否正确实现"""
    print("\n🔍 检查 2: UI 组件函数...")
    try:
        from ui.components import (
            format_fusion_result,
            format_workplace_summary,
            format_pipeline_status
        )

        # 测试 format_fusion_result 危险情感检测
        test_result_danger = {
            "emotion": "angry",
            "valence": -0.8,
            "arousal": 0.8,
            "confidence": 0.9,
            "action_tag": "alert_attention",
            "action_label": "⚡ 警觉注意",
            "suggestion": "保持冷静"
        }

        html = format_fusion_result(test_result_danger)

        if "danger-alert" in html and "alert-indicator" in html and "警觉状态" in html:
            print("   ✅ format_fusion_result() 危险警报功能正常")
        else:
            print("   ❌ format_fusion_result() 危险警报功能异常")
            return False

        # 测试 format_workplace_summary
        summary_html = format_workplace_summary("测试摘要", "angry")

        if "workplace-summary" in summary_html and "danger-alert" in summary_html:
            print("   ✅ format_workplace_summary() 功能正常")
        else:
            print("   ❌ format_workplace_summary() 功能异常")
            return False

        return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_voice_chat_tab():
    """检查语音聊天 Tab 是否正确集成"""
    print("\n🔍 检查 3: 语音聊天 Tab...")
    try:
        from ui.tabs.voice_chat import create_voice_chat_tab

        components = create_voice_chat_tab()

        required_keys = [
            "voice_summary_display",
            "voice_chatbot",
            "voice_pipeline_status",
            "voice_emotion_display"
        ]

        missing = []
        for key in required_keys:
            if key not in components:
                missing.append(key)

        if missing:
            print(f"   ❌ 缺少组件: {', '.join(missing)}")
            return False
        else:
            print("   ✅ 语音聊天 Tab 所有组件已正确添加")
            return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_video_chat_tab():
    """检查视频聊天 Tab 是否正确集成"""
    print("\n🔍 检查 4: 视频聊天 Tab...")
    try:
        from ui.tabs.video_chat import create_video_chat_tab

        components = create_video_chat_tab()

        required_keys = [
            "fusion_result_display",
            "fusion_pipeline_html",
            "fusion_video_output",
            "fusion_reply"
        ]

        missing = []
        for key in required_keys:
            if key not in components:
                missing.append(key)

        if missing:
            print(f"   ❌ 缺少组件: {', '.join(missing)}")
            return False
        else:
            print("   ✅ 视频聊天 Tab 所有组件已正确添加")
            return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_emotion_detection():
    """检查情感检测逻辑"""
    print("\n🔍 检查 5: 情感检测逻辑...")
    try:
        from services.emotion import derive_action_tag

        # 测试愤怒情感
        tag_angry = derive_action_tag("angry", 0.8, 0.9)
        if tag_angry == "alert_attention":
            print("   ✅ 愤怒情感 → alert_attention 映射正确")
        else:
            print(f"   ❌ 愤怒情感映射错误: {tag_angry}")
            return False

        # 测试恐惧情感
        tag_fearful = derive_action_tag("fearful", 0.7, 0.9)
        if tag_fearful == "alert_attention":
            print("   ✅ 恐惧情感 → alert_attention 映射正确")
        else:
            print(f"   ❌ 恐惧情感映射错误: {tag_fearful}")
            return False

        return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主验证流程"""
    print("=" * 60)
    print("🛡️  无障碍功能验证脚本")
    print("=" * 60)

    results = []

    results.append(("CSS 样式", check_styles()))
    results.append(("UI 组件函数", check_components()))
    results.append(("语音聊天 Tab", check_voice_chat_tab()))
    results.append(("视频聊天 Tab", check_video_chat_tab()))
    results.append(("情感检测逻辑", check_emotion_detection()))

    print("\n" + "=" * 60)
    print("📊 验证结果汇总")
    print("=" * 60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")

    all_passed = all(r[1] for r in results)

    print("=" * 60)
    if all_passed:
        print("🎉 所有检查通过！无障碍功能已成功集成。")
        print("\n下一步：")
        print("  1. 运行 python app.py 启动应用")
        print("  2. 测试语音聊天的职场摘要功能")
        print("  3. 测试视频聊天的情感警报功能")
        return 0
    else:
        print("⚠️  部分检查未通过，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
