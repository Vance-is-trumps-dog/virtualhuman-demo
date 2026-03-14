#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 AED 模型加载"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_aed_model():
    """测试 AED 模型加载"""
    print("="*50)
    print("测试 AED 模型加载")
    print("="*50)
    
    # 重新导入，清除缓存
    if 'services.aed' in sys.modules:
        del sys.modules['services.aed']
    if 'services.aed._aed_pipeline' in globals():
        global _aed_pipeline
        _aed_pipeline = None
    
    # 导入模块
    from services import aed
    
    # 重新设置全局变量
    aed._aed_pipeline = None
    
    # 尝试加载模型
    print("\n[1] 调用 load_aed_model()...")
    model = aed.load_aed_model()
    print(f"\n[2] 模型加载结果: {model}")
    
    if model == "MOCK":
        print("\n❌ 模型加载失败，使用 MOCK 模式")
        print("   原因：无法加载 damo/speech_ced_base 模型")
        print("   影响：只能基于音量判断，无法识别具体声音类型")
    else:
        print("\n✅ 模型加载成功!")
        
    return model

if __name__ == "__main__":
    result = test_aed_model()
    print(f"\n最终结果: {result}")
