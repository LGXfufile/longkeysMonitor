#!/usr/bin/env python3
"""
测试最有可能产生结果的查询组合
"""

import sys
sys.path.insert(0, 'src')

from config_manager import ConfigManager
from anti_spider import AntiSpiderManager
from search_executor import GoogleSuggestAPI
import time

def test_meaningful_queries():
    """测试有意义的查询组合"""
    
    # 初始化系统
    config_manager = ConfigManager('config/config.json')
    config = config_manager.get_config()
    
    proxy_settings = config.anti_spider.proxy_settings
    request_settings = config.anti_spider.request_settings
    
    anti_spider = AntiSpiderManager(proxy_settings, request_settings)
    google_api = GoogleSuggestAPI(anti_spider)
    
    # 选择有意义的查询组合
    meaningful_queries = [
        "best ai",           # 基础查询
        "best ai a",         # 后缀a（AI apps等）
        "best ai c",         # 后缀c（AI chatbot等）
        "best ai f",         # 后缀f（AI for...等）
        "best ai i",         # 后缀i（AI image等）
        "best ai t",         # 后缀t（AI tools等）
        "best ai v",         # 后缀v（AI video等）
        "free best ai",      # 前缀free
        "top best ai",       # 前缀top
    ]
    
    print(f"🔍 测试 {len(meaningful_queries)} 个有意义的查询")
    print("=" * 60)
    
    all_suggestions = set()
    successful_queries = 0
    
    for i, query in enumerate(meaningful_queries, 1):
        print(f"\n📡 {i}/{len(meaningful_queries)}: {query}")
        print("-" * 40)
        
        suggestions = google_api.search_suggestions(query, "en")
        
        if suggestions:
            successful_queries += 1
            print(f"✅ 获得 {len(suggestions)} 个建议:")
            for j, suggestion in enumerate(suggestions[:10], 1):  # 只显示前10个
                print(f"  {j:2d}. {suggestion}")
                all_suggestions.add(suggestion)
            
            if len(suggestions) > 10:
                print(f"  ... 还有 {len(suggestions) - 10} 个建议")
        else:
            print("❌ 无建议")
        
        time.sleep(0.5)  # 避免请求过快
    
    # 汇总结果
    print(f"\n🎯 汇总结果:")
    print("=" * 60)
    print(f"成功查询: {successful_queries}/{len(meaningful_queries)} ({successful_queries/len(meaningful_queries)*100:.1f}%)")
    print(f"唯一建议总数: {len(all_suggestions)}")
    
    # 分析AI相关建议
    ai_specific = []
    for suggestion in all_suggestions:
        if any(keyword in suggestion.lower() for keyword in ['ai ', 'artificial intelligence', 'machine learning', 'chatgpt', 'claude', 'gemini']):
            ai_specific.append(suggestion)
    
    print(f"AI相关建议: {len(ai_specific)} ({len(ai_specific)/len(all_suggestions)*100:.1f}%)")
    
    print(f"\n🔥 AI相关建议汇总:")
    print("-" * 40)
    for suggestion in sorted(ai_specific)[:20]:  # 显示前20个
        print(f"  • {suggestion}")
    
    # 显示统计
    stats = google_api.get_stats()
    print(f"\n📊 执行统计:")
    print("-" * 40)
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_meaningful_queries()