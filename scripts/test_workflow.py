#!/usr/bin/env python3
"""
简化测试脚本 - 测试完整的搜索流程但跳过通知
"""

import sys
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def test_full_workflow():
    """测试完整工作流程"""
    print("🔍 Google Long-tail Keyword Monitor - 完整流程测试")
    print("=" * 60)
    
    try:
        # 1. 初始化组件
        print("\n📋 1. 初始化系统组件...")
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
        
        print("✅ 所有组件初始化成功")
        
        # 2. 测试关键词
        test_keyword = "AI写作"
        print(f"\n🔍 2. 开始处理关键词: {test_keyword}")
        
        # 生成查询 - 限制数量用于测试
        all_queries = query_generator.generate_all_queries(test_keyword)
        test_queries = all_queries[:10]  # 只测试前10个查询
        print(f"   生成查询总数: {len(all_queries)}")
        print(f"   测试查询数: {len(test_queries)}")
        
        # 3. 执行搜索
        print(f"\n🚀 3. 执行搜索查询...")
        
        def progress_callback(completed: int, total: int, current_query: str):
            progress = completed / total * 100
            print(f"   进度: {completed}/{total} ({progress:.1f}%) - {current_query}")
        
        with SearchSession(search_executor, test_keyword) as session:
            results = session.execute_queries(
                test_queries,
                execution_mode="sequential",
                progress_callback=progress_callback
            )
            
            execution_stats = session.get_session_summary()
        
        print(f"✅ 搜索完成，获得 {len(results)} 个结果")
        
        # 4. 处理结果
        print(f"\n💾 4. 处理和保存数据...")
        
        if results:
            # 显示结果示例
            print("   搜索结果示例:")
            count = 0
            for query, suggestions in results.items():
                if suggestions and count < 3:
                    print(f"   - {query}: {suggestions[:3]}")
                    count += 1
            
            # 创建关键词数据
            keyword_data = data_processor.create_keyword_data(
                test_keyword,
                results,
                execution_stats.get("execution_stats", {})
            )
            
            # 保存数据
            file_path = data_processor.save_keyword_data(keyword_data)
            print(f"✅ 数据已保存到: {file_path}")
            
            # 5. 对比分析
            print(f"\n📊 5. 对比分析...")
            comparison_result = compare_analyzer.compare_with_previous_day(keyword_data)
            
            if comparison_result:
                print(f"   新增关键词: {comparison_result.new_count} 个")
                print(f"   消失关键词: {comparison_result.disappeared_count} 个")
                print(f"   变化率: {comparison_result.change_rate}%")
            else:
                print("   暂无历史数据进行对比")
            
            # 6. 执行统计
            stats = search_executor.get_execution_stats()
            print(f"\n📈 6. 执行统计:")
            print(f"   总请求数: {stats.get('total_requests', 0)}")
            print(f"   成功请求数: {stats.get('successful_requests', 0)}")
            print(f"   成功率: {stats.get('success_rate', 0)}%")
            print(f"   平均建议数: {stats.get('avg_suggestions_per_query', 0)}")
            
            print(f"\n🎉 测试完成！系统运行正常")
            return True
        else:
            print("❌ 未获取到搜索结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)