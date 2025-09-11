#!/usr/bin/env python3
"""
智能自适应监控系统完整测试脚本
测试语义漂移检测、关键词自动扩展和配置管理的集成功能
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.semantic_drift_analyzer import SemanticDriftAnalyzer
from src.keyword_auto_expander import KeywordAutoExpander
from src.enhanced_business_analyzer import generate_enhanced_analysis_report

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdaptiveMonitoringTester:
    """自适应监控系统测试器"""
    
    def __init__(self):
        self.project_root = Path(project_root)
        self.config_manager = ConfigManager()
        self.test_data_dir = self.project_root / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # 初始化测试数据
        self.test_keywords = [
            "how to use ai",
            "ai writing tools", 
            "best ai platforms"
        ]
        
        logger.info("自适应监控系统测试器初始化完成")
    
    def create_test_comparison_data(self) -> str:
        """创建测试用的对比分析数据"""
        logger.info("创建测试对比分析数据...")
        
        # 模拟真实的关键词变化数据
        test_comparison_data = {
            "metadata": {
                "main_keyword": "how to use ai",
                "current_date": "2025-09-12",
                "previous_date": "2025-09-11",
                "analysis_timestamp": datetime.now().isoformat()
            },
            "statistics": {
                "new_count": 125,
                "disappeared_count": 87,
                "stable_count": 1142,
                "total_current": 1267,
                "total_previous": 1229,
                "change_rate": 0.103
            },
            "changes": {
                "new_keywords": [
                    # AI平台访问相关 - 高价值漂移模式
                    "how to access ai builder in power platform",
                    "how to access ai tools for free",
                    "how to access ai writing assistant",
                    "how to access 15 ai platforms",
                    "how to access ai in microsoft office",
                    "how to access openai playground",
                    
                    # AI创作相关 - 高价值模式
                    "how to create ai generated content",
                    "how to create ai avatars online",
                    "how to create ai music generator",
                    "how to create ai powered websites",
                    
                    # AI集成相关 - 技术价值模式
                    "how to connect ai to your business",
                    "how to connect ai with databases",
                    "how to connect ai apis together",
                    "how to add ai features to apps",
                    "how to add ai to existing workflow",
                    
                    # 学习相关 - 教育价值
                    "how to learn ai programming fast",
                    "how to learn ai development online",
                    "how to learn ai without coding",
                    
                    # 一些噪音数据
                    "how to take ai out of photos",
                    "how to put ai generated text",
                    "how to set up airpods with iphone",
                    "how to aim better in fps games",
                    "how to work with adobe illustrator"
                ],
                "disappeared_keywords": [
                    "how to use ai for basic tasks",
                    "how to use ai writing tools 2024",
                    "how to use ai chatbots effectively",
                    "how to use ai for content creation"
                ],
                "stable_keywords": [
                    "how to use ai to write essays",
                    "how to use ai for business",
                    "how to use ai in marketing"
                ]
            }
        }
        
        # 保存测试数据
        test_file = self.test_data_dir / "test_comparison_how_to_use_ai.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_comparison_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试对比数据已创建: {test_file}")
        return str(test_file)
    
    def test_semantic_drift_analysis(self, comparison_file: str) -> dict:
        """测试语义漂移分析"""
        logger.info("🔍 测试语义漂移分析...")
        
        try:
            analyzer = SemanticDriftAnalyzer()
            
            # 读取测试数据
            with open(comparison_file, 'r', encoding='utf-8') as f:
                comparison_data = json.load(f)
            
            # 执行语义漂移分析
            drift_analysis = analyzer.analyze_semantic_drift(comparison_data)
            
            # 验证结果
            assert 'drift_patterns' in drift_analysis
            assert 'filtered_keywords' in drift_analysis
            assert 'analysis_summary' in drift_analysis
            
            drift_patterns = drift_analysis['drift_patterns']
            logger.info(f"✅ 检测到 {len(drift_patterns)} 个语义漂移模式")
            
            # 验证高价值模式
            high_value_patterns = [p for p in drift_patterns if p.get('value_level') == 'high']
            logger.info(f"✅ 高价值模式: {len(high_value_patterns)} 个")
            
            for pattern in high_value_patterns[:3]:
                logger.info(f"  - {pattern.get('original_verb', '')} → {pattern.get('new_verb', '')} "
                          f"(频次: {pattern.get('frequency', 0)}, 相关性: {pattern.get('relevance_score', 0):.3f})")
            
            return drift_analysis
            
        except Exception as e:
            logger.error(f"❌ 语义漂移分析测试失败: {e}")
            raise
    
    def test_enhanced_business_analysis(self, comparison_file: str) -> dict:
        """测试增强商业分析"""
        logger.info("💼 测试增强商业分析...")
        
        try:
            # 执行增强分析
            reports = generate_enhanced_analysis_report(
                comparison_file, 
                output_dir=str(self.test_data_dir),
                generate_html=True
            )
            
            # 验证生成的报告
            assert reports['json_report'] is not None
            assert reports['html_report'] is not None
            assert os.path.exists(reports['json_report'])
            assert os.path.exists(reports['html_report'])
            
            logger.info(f"✅ 增强分析JSON报告: {reports['json_report']}")
            logger.info(f"✅ 增强分析HTML报告: {reports['html_report']}")
            
            # 读取JSON报告验证内容
            with open(reports['json_report'], 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # 验证关键字段
            assert 'semantic_drift_analysis' in analysis_data
            assert 'business_opportunities' in analysis_data
            assert 'market_insights' in analysis_data
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"❌ 增强商业分析测试失败: {e}")
            raise
    
    def test_keyword_auto_expansion(self, analysis_json_file: str, source_keyword: str) -> list:
        """测试关键词自动扩展"""
        logger.info("🚀 测试关键词自动扩展...")
        
        try:
            # 备份当前配置
            original_config = self.config_manager.load_config()
            original_keywords_count = len(original_config.get('keywords', []))
            
            # 创建扩展器
            expander = KeywordAutoExpander(
                config_manager=self.config_manager,
                logger=logger
            )
            
            # 执行自动扩展
            new_keywords = expander.analyze_and_expand(analysis_json_file, source_keyword)
            
            # 验证结果
            logger.info(f"✅ 自动添加了 {len(new_keywords)} 个关键词: {new_keywords}")
            
            # 验证配置文件更新
            updated_config = self.config_manager.load_config()
            updated_keywords_count = len(updated_config.get('keywords', []))
            
            assert updated_keywords_count > original_keywords_count
            logger.info(f"✅ 配置文件已更新: {original_keywords_count} → {updated_keywords_count} 个关键词")
            
            # 验证自动添加的关键词包含元数据
            auto_added_keywords = [
                kw for kw in updated_config['keywords'] 
                if kw.get('auto_added', False)
            ]
            
            logger.info(f"✅ 自动添加的关键词包含完整元数据:")
            for kw in auto_added_keywords[-len(new_keywords):]:  # 显示最新添加的
                logger.info(f"  - {kw['main_keyword']}")
                logger.info(f"    源关键词: {kw.get('source_keyword', 'N/A')}")
                logger.info(f"    发现模式: {kw.get('discovery_pattern', 'N/A')}")
                logger.info(f"    置信度: {kw.get('confidence_score', 0):.3f}")
                logger.info(f"    商业价值: {kw.get('business_value', 'N/A')}")
            
            return new_keywords
            
        except Exception as e:
            logger.error(f"❌ 关键词自动扩展测试失败: {e}")
            raise
    
    def test_expansion_performance_tracking(self) -> dict:
        """测试扩展性能追踪"""
        logger.info("📊 测试扩展性能追踪...")
        
        try:
            expander = KeywordAutoExpander(
                config_manager=self.config_manager,
                logger=logger
            )
            
            # 获取扩展统计信息
            stats = self.config_manager.get_auto_added_keywords_stats()
            logger.info(f"✅ 扩展统计信息:")
            logger.info(f"  - 总关键词: {stats['total_keywords']}")
            logger.info(f"  - 自动添加: {stats['auto_added_count']}")
            logger.info(f"  - 手动添加: {stats['manual_count']}")
            logger.info(f"  - 自动添加比例: {stats['auto_added_percentage']:.1f}%")
            
            # 获取性能报告
            performance_report = expander.get_expansion_performance_report()
            logger.info(f"✅ 扩展效果评分: {performance_report.get('effectiveness_score', 0):.3f}")
            
            # 显示建议
            recommendations = performance_report.get('recommendations', [])
            logger.info(f"✅ 系统建议:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")
            
            return performance_report
            
        except Exception as e:
            logger.error(f"❌ 扩展性能追踪测试失败: {e}")
            raise
    
    def test_quality_control_and_cleanup(self) -> bool:
        """测试质量控制和清理功能"""
        logger.info("🧹 测试质量控制和清理功能...")
        
        try:
            expander = KeywordAutoExpander(
                config_manager=self.config_manager,
                logger=logger
            )
            
            # 测试低效关键词清理 (使用较短的天数进行测试)
            cleaned_keywords = expander.cleanup_low_performance_keywords(days=0)  # 立即清理
            logger.info(f"✅ 清理了 {len(cleaned_keywords)} 个低效关键词")
            
            if cleaned_keywords:
                logger.info("清理的关键词:")
                for kw in cleaned_keywords:
                    logger.info(f"  - {kw}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 质量控制测试失败: {e}")
            return False
    
    def test_complete_workflow(self) -> bool:
        """测试完整的自适应监控工作流"""
        logger.info("🎯 开始完整工作流测试...")
        
        try:
            # 1. 创建测试数据
            comparison_file = self.create_test_comparison_data()
            
            # 2. 语义漂移分析
            drift_analysis = self.test_semantic_drift_analysis(comparison_file)
            
            # 3. 增强商业分析
            business_analysis = self.test_enhanced_business_analysis(comparison_file)
            
            # 4. 关键词自动扩展
            source_keyword = "how to use ai"
            json_report_file = self.test_data_dir / "enhanced_analysis_how_to_use_ai_*.json"
            import glob
            json_files = glob.glob(str(json_report_file))
            if json_files:
                new_keywords = self.test_keyword_auto_expansion(json_files[0], source_keyword)
            else:
                logger.warning("未找到增强分析JSON报告，跳过关键词扩展测试")
                new_keywords = []
            
            # 5. 性能追踪
            performance_report = self.test_expansion_performance_tracking()
            
            # 6. 质量控制
            cleanup_success = self.test_quality_control_and_cleanup()
            
            # 总结测试结果
            logger.info("🎉 完整工作流测试完成!")
            logger.info("=" * 60)
            logger.info("📊 测试总结:")
            logger.info(f"  ✅ 语义漂移模式检测: {len(drift_analysis.get('drift_patterns', []))} 个")
            logger.info(f"  ✅ 商业机会识别: {len(business_analysis.get('business_opportunities', []))} 个")
            logger.info(f"  ✅ 自动添加关键词: {len(new_keywords)} 个")
            logger.info(f"  ✅ 扩展效果评分: {performance_report.get('effectiveness_score', 0):.3f}")
            logger.info(f"  ✅ 质量控制: {'通过' if cleanup_success else '失败'}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 完整工作流测试失败: {e}")
            return False
        finally:
            # 清理测试数据
            self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """清理测试数据"""
        try:
            import shutil
            if self.test_data_dir.exists():
                shutil.rmtree(self.test_data_dir)
            logger.info("🧹 测试数据清理完成")
        except Exception as e:
            logger.warning(f"清理测试数据失败: {e}")

def main():
    """主测试函数"""
    logger.info("🚀 开始智能自适应监控系统测试")
    logger.info("=" * 60)
    
    try:
        tester = AdaptiveMonitoringTester()
        success = tester.test_complete_workflow()
        
        if success:
            logger.info("🎉 所有测试通过！智能自适应监控系统运行正常")
            return 0
        else:
            logger.error("❌ 测试失败，请检查系统配置")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⏹️  测试被用户中断")
        return 1
    except Exception as e:
        logger.error(f"❌ 测试过程异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())