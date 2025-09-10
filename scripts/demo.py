#!/usr/bin/env python3
"""
简化测试脚本 - 用于演示Google长尾词监控系统功能
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.query_generator import QueryGenerator
from src.data_processor import DataProcessor
from src.compare_analyzer import CompareAnalyzer
from datetime import datetime

def test_demo():
    """演示系统功能"""
    print("🔍 Google Long-tail Keyword Monitor - 功能演示")
    print("=" * 50)
    
    # 1. 测试配置管理器
    print("\n📋 1. 配置管理器测试")
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        enabled_keywords = config_manager.get_enabled_keywords()
        print(f"✅ 配置加载成功")
        print(f"   启用的关键词: {len(enabled_keywords)} 个")
        for kw in enabled_keywords:
            print(f"   - {kw['main_keyword']}")
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return
    
    # 2. 测试查询生成器
    print("\n🔧 2. 查询生成器测试")
    try:
        generator = QueryGenerator()
        test_keyword = "AI写作"
        queries = generator.generate_all_queries(test_keyword)
        stats = generator.get_query_statistics(test_keyword)
        
        print(f"✅ 查询生成成功")
        print(f"   主关键词: {test_keyword}")
        print(f"   生成查询数: {len(queries)}")
        print(f"   统计信息: {stats}")
        print(f"   前5个查询示例:")
        for i, q in enumerate(queries[:5]):
            print(f"     {i+1}. {q}")
    except Exception as e:
        print(f"❌ 查询生成器测试失败: {e}")
        return
    
    # 3. 模拟搜索结果
    print("\n🔍 3. 模拟搜索结果")
    mock_results = {
        "AI写作": ["AI写作工具", "AI写作软件", "AI写作教程", "AI写作平台"],
        "AI写作 a": ["AI写作app", "AI写作api", "AI写作assistant"],
        "AI写作 b": ["AI写作bot", "AI写作browser", "AI写作book"],
        "a AI写作": ["app AI写作", "auto AI写作", "api AI写作"],
        "b AI写作": ["best AI写作", "basic AI写作", "business AI写作"]
    }
    
    print(f"✅ 模拟搜索完成")
    print(f"   成功查询: {len(mock_results)} 个")
    print(f"   总建议词: {sum(len(suggestions) for suggestions in mock_results.values())} 个")
    
    # 4. 测试数据处理器
    print("\n💾 4. 数据处理器测试")
    try:
        data_processor = DataProcessor()
        
        # 创建模拟数据
        keyword_data = data_processor.create_keyword_data(
            test_keyword,
            mock_results,
            {"duration_seconds": 125, "total_requests": 5, "successful_requests": 5}
        )
        
        # 保存数据
        file_path = data_processor.save_keyword_data(keyword_data)
        
        print(f"✅ 数据处理成功")
        print(f"   执行时间: {keyword_data.execution_time}")
        print(f"   总查询数: {keyword_data.total_queries}")
        print(f"   成功查询数: {keyword_data.successful_queries}")
        print(f"   采集关键词: {keyword_data.total_keywords_found} 个")
        print(f"   去重后: {keyword_data.unique_keywords} 个")
        print(f"   数据文件: {file_path}")
        
    except Exception as e:
        print(f"❌ 数据处理器测试失败: {e}")
        return
    
    # 5. 测试对比分析（如果有历史数据）
    print("\n📊 5. 对比分析测试")
    try:
        compare_analyzer = CompareAnalyzer(data_processor)
        
        # 尝试获取前一天的数据进行对比
        previous_data = data_processor.get_previous_day_data(test_keyword)
        
        if previous_data:
            comparison = compare_analyzer.compare_keyword_data(keyword_data, previous_data)
            print(f"✅ 对比分析完成")
            print(f"   新增关键词: {comparison.new_count} 个")
            print(f"   消失关键词: {comparison.disappeared_count} 个")
            print(f"   稳定关键词: {comparison.stable_count} 个")
            print(f"   变化率: {comparison.change_rate}%")
        else:
            print(f"ℹ️  暂无历史数据进行对比")
            
    except Exception as e:
        print(f"❌ 对比分析测试失败: {e}")
    
    # 6. 系统功能演示总结
    print("\n🎉 6. 功能演示总结")
    print("✅ 配置管理 - 支持多关键词配置")
    print("✅ 查询生成 - 1400+个查询组合")
    print("✅ 数据存储 - JSON结构化保存")
    print("✅ 对比分析 - 智能变化检测")
    print("✅ 模块化设计 - 易于扩展维护")
    
    print(f"\n📁 数据文件位置: {data_processor.data_dir}")
    print(f"📋 配置文件位置: {config_manager.config_path}")
    
    print("\n💡 使用提示:")
    print("1. 编辑 config/config.json 添加您的关键词")
    print("2. 设置正确的飞书webhook地址") 
    print("3. 运行: python src/main.py run")
    print("4. 设置定时任务: ./scripts/setup_cron.sh")

if __name__ == "__main__":
    test_demo()