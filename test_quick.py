#!/usr/bin/env python3
"""
快速测试修复后的功能
使用少量查询快速验证
"""

import os
import sys
import json
import time

# 添加src路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.config_manager import ConfigManager
from src.query_generator import QueryGenerator
from src.anti_spider import AntiSpiderManager
from src.search_executor import SearchExecutor, SearchSession
from src.data_processor import DataProcessor
from src.compare_analyzer import CompareAnalyzer
from src.feishu_notifier import FeishuNotifier

def test_quick_monitoring():
    """快速测试关键词监控功能"""
    print("🚀 开始快速测试...")
    
    main_keyword = "ai generate"
    
    try:
        # 初始化组件
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 初始化反爬虫管理器
        anti_spider = AntiSpiderManager(
            config_manager.get_proxy_settings(),
            config_manager.get_request_settings()
        )
        
        # 初始化搜索执行器
        search_executor = SearchExecutor(
            anti_spider,
            config_manager.get_search_settings()
        )
        
        # 初始化查询生成器 - 只生成少量查询进行测试
        query_generator = QueryGenerator(config_manager.get_search_settings())
        
        # 生成测试查询 - 只使用基础查询和一些单字母后缀
        test_queries = [
            main_keyword,
            f"{main_keyword} a",
            f"{main_keyword} b", 
            f"{main_keyword} c",
            f"a {main_keyword}",
            f"b {main_keyword}",
        ]
        
        print(f"📋 生成了 {len(test_queries)} 个测试查询")
        
        # 执行搜索
        with SearchSession(search_executor, main_keyword) as session:
            results = session.execute_queries(test_queries, progress_callback=print_progress)
            execution_stats = session.get_session_summary()
        
        if results:
            print(f"✅ 获得 {len(results)} 个有效结果")
            
            # 显示一些结果样例
            print("\n📝 结果样例:")
            count = 0
            for query, suggestions in results.items():
                if count >= 3:  # 只显示前3个
                    break
                print(f"  • {query}: {suggestions[:3]}...")  # 只显示前3个建议
                count += 1
            
            # 处理数据
            data_processor = DataProcessor()
            keyword_data = data_processor.create_keyword_data(
                main_keyword,
                results,
                execution_stats.get("execution_stats", {})
            )
            
            # 保存数据
            file_path = data_processor.save_keyword_data(keyword_data)
            print(f"💾 数据已保存到: {file_path}")
            
            # 发送测试通知
            feishu_notifier = FeishuNotifier(
                config_manager.get_feishu_webhook(),
                config.get("notification_settings", {})
            )
            
            print("📱 发送测试通知...")
            success = feishu_notifier.send_success_notification(
                keyword_data,
                None,  # 没有对比结果
                file_path
            )
            
            if success:
                print("✅ 飞书通知发送成功!")
            else:
                print("❌ 飞书通知发送失败")
            
            return True
            
        else:
            print("❌ 未获得任何结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def print_progress(completed, total, current_query):
    """打印进度"""
    progress = completed / total * 100
    print(f"⏳ 进度: {completed}/{total} ({progress:.1f}%) - {current_query}")

if __name__ == "__main__":
    success = test_quick_monitoring()
    if success:
        print("\n🎉 快速测试成功! 系统修复完成。")
    else:
        print("\n💥 快速测试失败，需要进一步检查。")