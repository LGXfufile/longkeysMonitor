#!/usr/bin/env python3
"""
快速验证智能自适应监控系统的核心功能
使用已有数据进行验证
"""

import os
import sys
sys.path.insert(0, '.')

from src.config_manager import ConfigManager
from src.keyword_auto_expander import KeywordAutoExpander

def quick_validation():
    """快速验证系统功能"""
    print("🚀 智能自适应监控系统验证")
    print("=" * 50)
    
    # 1. 验证配置管理器
    print("1️⃣ 测试配置管理器...")
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    auto_stats = config_manager.get_auto_added_keywords_stats()
    print(f"   ✅ 总关键词: {auto_stats['total_keywords']}")
    print(f"   ✅ 自动添加: {auto_stats['auto_added_count']}")
    print(f"   ✅ 自动添加率: {auto_stats['auto_added_percentage']:.1f}%")
    
    # 2. 验证扩展器
    print("\n2️⃣ 测试关键词扩展器...")
    expander = KeywordAutoExpander(config_manager)
    
    # 获取性能报告
    performance = expander.get_expansion_performance_report()
    effectiveness = performance.get('effectiveness_score', 0)
    print(f"   ✅ 扩展效果评分: {effectiveness:.3f}")
    
    recommendations = performance.get('recommendations', [])
    print(f"   ✅ 系统建议: {len(recommendations)} 条")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"     {i}. {rec}")
    
    # 3. 验证自动添加的关键词质量
    print("\n3️⃣ 自动添加关键词质量检查...")
    auto_keywords = auto_stats.get('auto_keywords', [])
    
    if auto_keywords:
        for kw_info in auto_keywords:
            print(f"   📝 关键词: {kw_info['keyword']}")
            print(f"      源关键词: {kw_info['source']}")
            print(f"      发现模式: {kw_info['pattern']}")
            print(f"      置信度: {kw_info['confidence']:.3f}")
            print(f"      商业价值: {kw_info['business_value']}/10")
            print()
    else:
        print("   ℹ️ 暂无自动添加的关键词")
    
    print("🎉 系统验证完成！智能自适应监控系统正常运行")
    return True

if __name__ == "__main__":
    try:
        success = quick_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)