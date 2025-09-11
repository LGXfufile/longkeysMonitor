#!/usr/bin/env python3
"""
Enhanced Business Analyzer with Semantic Drift Detection
集成语义漂移检测的增强商业分析器
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# 添加src目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from business_analyzer import BusinessAnalyzer
from semantic_drift_analyzer import SemanticDriftAnalyzer

logger = logging.getLogger(__name__)


class EnhancedBusinessAnalyzer(BusinessAnalyzer):
    """增强版商业分析器 - 集成语义漂移检测"""
    
    def __init__(self):
        """初始化增强分析器"""
        super().__init__()
        self.drift_analyzer = SemanticDriftAnalyzer()
        self.logger = logging.getLogger(__name__)
        
    def analyze_keyword_changes(self, changes_file_path: str) -> Dict:
        """
        分析关键词变化 - 增强版
        
        Args:
            changes_file_path: 变化文件路径
            
        Returns:
            Dict: 增强分析结果
        """
        try:
            # 读取变化数据
            with open(changes_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info("开始增强商业分析...")
            
            # 1. 执行原有的商业分析
            basic_analysis = super().analyze_keyword_changes(changes_file_path)
            
            # 2. 执行语义漂移分析
            self.logger.info("执行语义漂移分析...")
            drift_analysis = self.drift_analyzer.analyze_semantic_drift(data)
            
            # 3. 融合分析结果
            enhanced_analysis = self._merge_analyses(basic_analysis, drift_analysis)
            
            return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"增强分析失败: {e}")
            raise
    
    def _merge_analyses(self, business_analysis: Dict, drift_analysis: Dict) -> Dict:
        """融合商业分析和语义漂移分析结果"""
        
        # 基础结构保持不变
        enhanced_analysis = business_analysis.copy()
        
        # 添加语义漂移分析结果
        enhanced_analysis['semantic_drift_analysis'] = drift_analysis
        
        # 重新分类新增关键词
        enhanced_keywords = self._enhance_keyword_classification(
            business_analysis.get('new_keyword_insights', []),
            drift_analysis.get('filtered_keywords', {})
        )
        enhanced_analysis['new_keyword_insights'] = enhanced_keywords
        
        # 增强商业机会识别
        enhanced_analysis['enhanced_business_opportunities'] = self._identify_enhanced_opportunities(
            drift_analysis.get('drift_patterns', []),
            drift_analysis.get('filtered_keywords', {})
        )
        
        # 添加数据质量评估
        enhanced_analysis['data_quality_assessment'] = self._assess_data_quality(drift_analysis)
        
        # 更新战略建议
        enhanced_analysis['strategic_recommendations'] = self._generate_enhanced_recommendations(
            business_analysis.get('strategic_recommendations', {}),
            drift_analysis.get('recommendations', {})
        )
        
        return enhanced_analysis
    
    def _enhance_keyword_classification(self, business_insights: List, filtered_keywords: Dict) -> List:
        """增强关键词分类"""
        enhanced_insights = []
        
        # 获取高价值关键词 - 转换为列表避免JSON序列化问题
        high_value_keywords = list(filtered_keywords.get('high_value', []))
        medium_value_keywords = list(filtered_keywords.get('medium_value', []))
        noise_keywords = list(filtered_keywords.get('noise', []))
        
        for insight in business_insights:
            # 处理不同类型的insight数据结构
            if isinstance(insight, dict):
                keyword = insight.get('keyword', '')
                enhanced_insight = insight.copy()
            else:
                # 如果insight是其他类型，跳过或创建基础结构
                continue
            
            # 根据语义分析调整商业价值评分
            if keyword in high_value_keywords:
                enhanced_insight['semantic_quality'] = 'high'
                enhanced_insight['overall_business_value'] = min(10, enhanced_insight.get('overall_business_value', 5) + 2)
            elif keyword in medium_value_keywords:
                enhanced_insight['semantic_quality'] = 'medium'
                enhanced_insight['overall_business_value'] = min(10, enhanced_insight.get('overall_business_value', 5) + 1)
            elif keyword in noise_keywords:
                enhanced_insight['semantic_quality'] = 'noise'
                enhanced_insight['overall_business_value'] = max(1, enhanced_insight.get('overall_business_value', 5) - 3)
                enhanced_insight['recommended_action'] = 'filter_out'
            else:
                enhanced_insight['semantic_quality'] = 'unknown'
            
            enhanced_insights.append(enhanced_insight)
        
        return enhanced_insights
    
    def _identify_enhanced_opportunities(self, drift_patterns: List, filtered_keywords: Dict) -> Dict:
        """识别增强商业机会"""
        opportunities = {
            'ai_platform_access_opportunities': [],
            'ai_learning_market_opportunities': [],
            'emerging_ai_tools_opportunities': [],
            'integration_opportunities': []
        }
        
        # 分析漂移模式中的机会
        for pattern in drift_patterns:
            if pattern.get('value_level') in ['high', 'medium']:
                context = pattern.get('context_category', '')
                
                if context == 'ai_platform_access':
                    opportunities['ai_platform_access_opportunities'].append({
                        'pattern': f"{pattern['original_verb']} → {pattern['new_verb']}",
                        'frequency': pattern['frequency'],
                        'examples': pattern['examples'][:3],
                        'opportunity': '用户在寻找AI平台访问方法，存在教育和工具机会'
                    })
                
                elif context == 'ai_skill_learning':
                    opportunities['ai_learning_market_opportunities'].append({
                        'pattern': f"{pattern['original_verb']} → {pattern['new_verb']}",
                        'frequency': pattern['frequency'],
                        'examples': pattern['examples'][:3],
                        'opportunity': 'AI技能学习需求强烈，在线教育市场机会'
                    })
                
                elif context == 'ai_tool_usage':
                    opportunities['emerging_ai_tools_opportunities'].append({
                        'pattern': f"{pattern['original_verb']} → {pattern['new_verb']}",
                        'frequency': pattern['frequency'],
                        'examples': pattern['examples'][:3],
                        'opportunity': '新兴AI工具使用需求，SaaS产品机会'
                    })
                
                elif context == 'tech_integration':
                    opportunities['integration_opportunities'].append({
                        'pattern': f"{pattern['original_verb']} → {pattern['new_verb']}",
                        'frequency': pattern['frequency'],
                        'examples': pattern['examples'][:3],
                        'opportunity': 'AI技术集成需求，API和中间件机会'
                    })
        
        return opportunities
    
    def _assess_data_quality(self, drift_analysis: Dict) -> Dict:
        """评估数据质量"""
        stats = drift_analysis.get('value_statistics', {})
        recommendations = drift_analysis.get('recommendations', {})
        
        total_keywords = stats.get('total_keywords', 0)
        noise_count = stats.get('noise', {}).get('count', 0)
        high_value_count = stats.get('high_value', {}).get('count', 0)
        
        quality_assessment = {
            'overall_quality': recommendations.get('summary', {}).get('data_quality', 'unknown'),
            'signal_to_noise_ratio': float(stats.get('signal_to_noise_ratio', 0)),
            'quality_score': float(stats.get('quality_score', 0)),
            'noise_percentage': float(stats.get('noise', {}).get('percentage', 0)),
            'high_value_percentage': float(stats.get('high_value', {}).get('percentage', 0)),
            'actionable_insights': int(high_value_count),
            'filtered_noise': int(noise_count),
            'data_health': self._calculate_data_health(stats)
        }
        
        return quality_assessment
    
    def _calculate_data_health(self, stats: Dict) -> str:
        """计算数据健康度"""
        quality_score = stats.get('quality_score', 0)
        noise_percentage = stats.get('noise', {}).get('percentage', 0)
        
        if quality_score >= 60 and noise_percentage <= 20:
            return '优秀'
        elif quality_score >= 40 and noise_percentage <= 35:
            return '良好'
        elif quality_score >= 20 and noise_percentage <= 50:
            return '一般'
        else:
            return '需要改进'
    
    def _generate_enhanced_recommendations(self, business_recs: Dict, drift_recs: Dict) -> Dict:
        """生成增强版战略建议"""
        enhanced_recs = business_recs.copy()
        
        # 添加数据质量改进建议
        enhanced_recs['data_quality_improvements'] = []
        
        for filter_rule in drift_recs.get('filter_rules', []):
            enhanced_recs['data_quality_improvements'].append({
                'action': 'implement_filter',
                'rule': filter_rule['rule'],
                'reason': filter_rule['reason'],
                'impact': 'reduce_noise_improve_signal'
            })
        
        # 添加语义监控建议
        enhanced_recs['semantic_monitoring'] = []
        
        for suggestion in drift_recs.get('monitoring_suggestions', []):
            enhanced_recs['semantic_monitoring'].append({
                'action': 'monitor_pattern',
                'pattern': suggestion['pattern'],
                'reason': suggestion['reason'],
                'recommended_action': suggestion['action']
            })
        
        # 合并立即行动建议
        immediate_actions = enhanced_recs.get('immediate_actions', [])
        
        # 根据数据质量添加建议
        data_quality = drift_recs.get('summary', {}).get('data_quality', '')
        if data_quality == '差 - 噪音过多':
            immediate_actions.append('立即实施噪音过滤，提高数据质量')
        elif data_quality == '中等 - 需要优化':
            immediate_actions.append('优化关键词过滤规则，减少噪音干扰')
        
        enhanced_recs['immediate_actions'] = immediate_actions
        
        return enhanced_recs


def generate_enhanced_analysis_report(changes_file_path: str, output_dir: str = "reports", generate_html: bool = True) -> Dict:
    """
    生成增强分析报告
    
    Args:
        changes_file_path: 变化文件路径
        output_dir: 输出目录
        generate_html: 是否生成HTML报告
        
    Returns:
        Dict: 生成的报告路径信息
    """
    analyzer = EnhancedBusinessAnalyzer()
    
    # 执行分析
    analysis_result = analyzer.analyze_keyword_changes(changes_file_path)
    
    # 保存JSON结果
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    main_keyword = analysis_result['metadata']['main_keyword']
    safe_keyword = main_keyword.replace(' ', '_').replace('/', '_')
    timestamp = analysis_result['metadata'].get('analysis_time', 'unknown')[:10]
    
    json_file = output_path / f"enhanced_business_analysis_{safe_keyword}_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"增强商业分析报告已保存: {json_file}")
    
    result = {
        'json_report': str(json_file),
        'html_report': None
    }
    
    # 生成HTML报告
    if generate_html:
        try:
            from html_report_generator import generate_html_from_json
            html_file = generate_html_from_json(str(json_file), output_dir)
            result['html_report'] = html_file
            logger.info(f"HTML报告已生成: {html_file}")
        except ImportError:
            logger.warning("HTML报告生成器未找到，跳过HTML生成")
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='增强版商业分析器')
    parser.add_argument('changes_file', help='变化数据文件路径')
    parser.add_argument('-o', '--output', help='输出目录', default='reports')
    parser.add_argument('--no-html', action='store_true', help='不生成HTML报告')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    try:
        result = generate_enhanced_analysis_report(
            args.changes_file, 
            args.output, 
            generate_html=not args.no_html
        )
        
        print(f"🚀 增强商业分析完成!")
        print(f"📊 JSON报告: {result['json_report']}")
        
        if result['html_report']:
            print(f"🌐 HTML报告: {result['html_report']}")
            print(f"🔗 请在浏览器中打开HTML文件查看详细报告")
        
        # 读取并显示关键统计
        with open(result['json_report'], 'r', encoding='utf-8') as f:
            analysis_result = json.load(f)
        
        quality_assessment = analysis_result.get('data_quality_assessment', {})
        print(f"📈 数据健康度: {quality_assessment.get('data_health', 'unknown')}")
        print(f"🎯 高价值关键词: {quality_assessment.get('actionable_insights', 0)} 个")
        print(f"🗑️ 过滤噪音: {quality_assessment.get('filtered_noise', 0)} 个")
        print(f"📊 质量得分: {quality_assessment.get('quality_score', 0):.1f}/100")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        exit(1)