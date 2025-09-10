#!/usr/bin/env python3
"""
测试优化后的飞书通知功能
"""

import os
import sys
import json

# 添加src路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.config_manager import ConfigManager
from src.feishu_notifier import FeishuNotifier
from src.data_processor import KeywordData

def test_feishu_notifications():
    """测试不同级别的飞书通知"""
    print("🚀 开始测试飞书通知...")
    
    try:
        # 初始化配置
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 初始化飞书通知器
        feishu_notifier = FeishuNotifier(
            config_manager.get_feishu_webhook(),
            config.get("notification_settings", {})
        )
        
        # 测试1: 基础连接测试
        print("\n📡 测试1: 基础连接测试")
        success = feishu_notifier.test_webhook()
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
        
        # 测试2: 最小化通知
        print("\n📊 测试2: 最小化通知")
        success = feishu_notifier._send_minimal_notification()
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
        
        # 测试3: 自定义安全消息
        print("\n💬 测试3: 自定义安全消息")
        success = feishu_notifier.send_custom_message(
            "系统测试", 
            "这是一条测试消息，用于验证通知系统功能正常。",
            "success"
        )
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
        
        # 测试4: 模拟错误通知
        print("\n⚠️ 测试4: 错误通知")
        success = feishu_notifier.send_error_notification(
            "测试关键词",
            "这是一个测试错误消息",
            {"total_requests": 10, "successful_requests": 8, "failed_requests": 2}
        )
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
        
        # 测试5: 模拟成功通知（使用安全的数据）
        print("\n📈 测试5: 成功通知（安全版本）")
        
        # 创建模拟的关键词数据
        mock_keyword_data = type('KeywordData', (), {
            'main_keyword': '内容生成',  # 使用安全的关键词
            'execution_time': '2025-09-10 03:00:00',
            'execution_duration': '00:00:30',
            'total_queries': 53,
            'successful_queries': 51,
            'failed_queries': 2,
            'total_keywords_found': 500,
            'unique_keywords': 450,
            'query_results': {
                '内容生成': ['内容创作工具', '内容编写助手', '内容制作平台'],
                '内容生成 a': ['内容生成应用', '内容生成接口'],
            }
        })()
        
        success = feishu_notifier.send_success_notification(
            mock_keyword_data,
            None,  # 没有对比结果
            "test_data.json"
        )
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
        
        print("\n🎉 飞书通知测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_feishu_notifications()
    if success:
        print("\n✅ 飞书通知系统优化成功!")
    else:
        print("\n❌ 还需要进一步优化。")