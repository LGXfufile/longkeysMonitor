#!/usr/bin/env python3
"""
完整功能测试 - 包含飞书通知
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.query_generator import QueryGenerator
from src.anti_spider import AntiSpiderManager
from src.search_executor import SearchExecutor, SearchSession
from src.data_processor import DataProcessor
from src.compare_analyzer import CompareAnalyzer
from src.feishu_notifier import FeishuNotifier

def test_with_notification():
    """测试完整功能包含通知"""
    print("🔍 谷歌长尾词监控系统 - 完整功能测试")
    print("=" * 50)
    
    try:
        # 初始化
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 搜索组件
        anti_spider = AntiSpiderManager(
            config_manager.get_proxy_settings(),
            config_manager.get_request_settings()
        )
        
        search_executor = SearchExecutor(anti_spider, config_manager.get_search_settings())
        query_generator = QueryGenerator(config_manager.get_search_settings())
        data_processor = DataProcessor()
        compare_analyzer = CompareAnalyzer(data_processor)
        
        # 通知组件
        feishu_notifier = FeishuNotifier(
            config_manager.get_feishu_webhook(),
            config.get("notification_settings", {})
        )
        
        # 测试关键词
        test_keyword = "AI写作"
        print(f"\n🚀 开始监控关键词: {test_keyword}")
        
        # 生成查询（限制数量用于测试）
        all_queries = query_generator.generate_all_queries(test_keyword)
        test_queries = all_queries[:5]  # 只测试前5个
        print(f"   测试查询数: {len(test_queries)}")
        
        # 执行搜索
        with SearchSession(search_executor, test_keyword) as session:
            results = session.execute_queries(
                test_queries,
                execution_mode="sequential"
            )
            execution_stats = session.get_session_summary()
        
        if results:
            # 创建数据
            keyword_data = data_processor.create_keyword_data(
                test_keyword,
                results,
                execution_stats.get("execution_stats", {})
            )
            
            # 保存数据
            file_path = data_processor.save_keyword_data(keyword_data)
            print(f"✅ 数据已保存: {file_path}")
            
            # 对比分析
            comparison_result = compare_analyzer.compare_with_previous_day(keyword_data)
            
            # 发送飞书通知
            print(f"\n📱 发送飞书通知...")
            success = feishu_notifier.send_success_notification(
                keyword_data,
                comparison_result,
                file_path
            )
            
            if success:
                print("✅ 飞书通知发送成功！")
                print("请检查您的飞书群聊是否收到了监控报告")
            else:
                print("❌ 飞书通知发送失败")
            
            return success
        else:
            print("❌ 未获取到搜索结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_notification()
    if success:
        print("\n🎉 完整功能测试成功！")
        print("您的谷歌长尾词监控系统已经完全就绪！")
    sys.exit(0 if success else 1)