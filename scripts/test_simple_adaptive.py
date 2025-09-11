#!/usr/bin/env python3
"""
简化的自适应监控系统测试脚本
使用实际的对比数据进行测试
"""

import os
import sys
import json
import logging

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.semantic_drift_analyzer import SemanticDriftAnalyzer
from src.keyword_auto_expander import KeywordAutoExpander
from src.config_manager import ConfigManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_with_real_data():
    """使用真实数据测试自适应监控系统"""
    
    # 使用现有的对比数据文件
    comparison_file = "data/2025-09-12_how_to_use_ai_changes.json"
    
    if not os.path.exists(comparison_file):
        logger.error(f"对比文件不存在: {comparison_file}")
        return False
    
    logger.info(f"使用对比文件: {comparison_file}")
    
    try:
        # 1. 测试语义漂移分析
        logger.info("🔍 测试语义漂移分析...")
        analyzer = SemanticDriftAnalyzer()
        
        with open(comparison_file, 'r', encoding='utf-8') as f:
            comparison_data = json.load(f)
        
        drift_result = analyzer.analyze_semantic_drift(comparison_data)
        logger.info(f"✅ 检测到 {len(drift_result.get('drift_patterns', []))} 个语义漂移模式")
        
        # 显示前几个高价值模式
        high_value_patterns = [p for p in drift_result.get('drift_patterns', []) if p.get('value_level') == 'high']
        logger.info(f"✅ 高价值模式: {len(high_value_patterns)} 个")
        
        for pattern in high_value_patterns[:3]:
            logger.info(f"  - {pattern.get('original_verb', '')} → {pattern.get('new_verb', '')} "
                      f"(频次: {pattern.get('frequency', 0)})")
        
        # 2. 测试关键词自动扩展
        logger.info("🚀 测试关键词自动扩展...")
        config_manager = ConfigManager()
        expander = KeywordAutoExpander(config_manager, logger)
        
        # 保存漂移分析结果供扩展器使用
        analysis_file = "test_drift_analysis.json"
        enhanced_analysis = {
            'semantic_drift_analysis': drift_result,
            'business_opportunities': [],
            'market_insights': {}
        }
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_analysis, f, ensure_ascii=False, indent=2)
        
        # 执行关键词扩展
        source_keyword = "how to use ai" 
        new_keywords = expander.analyze_and_expand(analysis_file, source_keyword)
        
        logger.info(f"✅ 自动发现并添加 {len(new_keywords)} 个高价值关键词:")
        for kw in new_keywords:
            logger.info(f"  - {kw}")
        
        # 3. 测试性能追踪
        logger.info("📊 测试扩展性能追踪...")
        stats = config_manager.get_auto_added_keywords_stats()
        logger.info(f"✅ 当前关键词统计:")
        logger.info(f"  - 总计: {stats['total_keywords']}")
        logger.info(f"  - 自动添加: {stats['auto_added_count']}")
        logger.info(f"  - 手动添加: {stats['manual_count']}")
        
        # 清理测试文件
        if os.path.exists(analysis_file):
            os.remove(analysis_file)
        
        logger.info("🎉 所有测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_real_data()
    sys.exit(0 if success else 1)