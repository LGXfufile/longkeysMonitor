#!/usr/bin/env python3
"""
快速测试版本 - 只处理前50个查询用于演示
"""

import sys
import os
import argparse
import logging

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

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def quick_run(keyword: str, query_limit: int = 50):
    """快速运行版本"""
    print(f"🔍 快速测试 - 谷歌长尾词监控")
    print(f"关键词: {keyword}")
    print(f"查询限制: {query_limit} 个")
    print("=" * 50)
    
    try:
        # 初始化组件
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        anti_spider = AntiSpiderManager(
            config_manager.get_proxy_settings(),
            config_manager.get_request_settings()
        )
        
        search_executor = SearchExecutor(
            anti_spider,
            config_manager.get_search_settings()
        )
        
        query_generator = QueryGenerator(
            config_manager.get_search_settings()
        )
        
        data_processor = DataProcessor()
        compare_analyzer = CompareAnalyzer(data_processor)
        
        feishu_notifier = FeishuNotifier(
            config_manager.get_feishu_webhook(),
            config.get("notification_settings", {})
        )
        
        # 生成查询（限制数量）
        all_queries = query_generator.generate_all_queries(keyword)
        limited_queries = all_queries[:query_limit]
        
        print(f"📊 生成了 {len(all_queries)} 个查询，测试前 {len(limited_queries)} 个")
        
        # 进度回调
        def progress_callback(completed: int, total: int, current_query: str):
            progress = completed / total * 100
            if completed % 10 == 0 or completed == total:  # 每10个显示一次
                print(f"   进度: {completed}/{total} ({progress:.1f}%)")
        
        # 执行搜索
        with SearchSession(search_executor, keyword) as session:
            results = session.execute_queries(
                limited_queries,
                execution_mode="sequential",
                progress_callback=progress_callback
            )
            
            execution_stats = session.get_session_summary()
        
        print(f"\n✅ 搜索完成，获得 {len(results)} 个有效结果")
        
        if results:
            # 显示部分结果
            print("\n📋 结果示例:")
            count = 0
            for query, suggestions in results.items():
                if suggestions and count < 5:
                    print(f"   {query}: {suggestions[:3]}")
                    count += 1
            
            # 创建和保存数据
            keyword_data = data_processor.create_keyword_data(
                keyword,
                results,
                execution_stats.get("execution_stats", {})
            )
            
            file_path = data_processor.save_keyword_data(keyword_data)
            print(f"\n💾 数据已保存: {file_path}")
            
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
            else:
                print("❌ 飞书通知发送失败")
            
            # 统计信息
            stats = search_executor.get_execution_stats()
            print(f"\n📈 执行统计:")
            print(f"   总请求: {stats.get('total_requests', 0)}")
            print(f"   成功: {stats.get('successful_requests', 0)}")
            print(f"   成功率: {stats.get('success_rate', 0)}%")
            print(f"   执行时间: {execution_stats.get('duration_seconds', 0):.1f}秒")
            
            return True
        else:
            print("❌ 未获取到任何结果")
            return False
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="快速测试版谷歌长尾词监控")
    parser.add_argument("-k", "--keyword", required=True, help="监控关键词")
    parser.add_argument("-n", "--num", type=int, default=50, help="查询数量限制")
    
    args = parser.parse_args()
    
    setup_logging()
    
    success = quick_run(args.keyword, args.num)
    
    if success:
        print(f"\n🎉 快速测试完成！")
        print(f"💡 完整监控请运行: python3 src/main.py run -k \"{args.keyword}\"")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()