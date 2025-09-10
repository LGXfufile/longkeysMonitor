#!/usr/bin/env python3
"""
Business Value Analyzer for Keyword Changes
关键词变化商业价值分析器

自动分析关键词变化文件，生成商业价值分析报告
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class KeywordInsight:
    """关键词洞察数据结构"""
    keyword: str
    category: str
    business_value: int  # 1-10 商业价值评分
    competition_level: str  # "low", "medium", "high"
    market_size: str  # "niche", "medium", "large"
    monetization_potential: List[str]
    technical_difficulty: str  # "easy", "medium", "hard"
    user_intent: str  # "informational", "commercial", "transactional"
    urgency: str  # "low", "medium", "high"


class BusinessAnalyzer:
    """商业价值分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.logger = logging.getLogger(__name__)
        
        # 分类关键词字典
        self.category_keywords = {
            '电商/商业': ['ecommerce', 'shop', 'store', 'business', 'sale', 'sell', 'buy', 'product', 'brand', 'marketing'],
            '视频制作': ['video', 'youtube', 'tiktok', 'shorts', 'movie', 'film', 'animation', 'vlog', 'livestream'],
            '编程开发': ['code', 'programming', 'developer', 'js', 'html', 'css', 'json', 'api', 'database', 'software'],
            '演示文稿': ['ppt', 'presentation', 'slide', 'powerpoint', 'pitch', 'deck', 'meeting'],
            '数据分析': ['excel', 'data', 'report', 'analytics', 'chart', 'graph', 'dashboard', 'statistics'],
            '设计创意': ['design', 'art', 'logo', 'illustration', 'ui', 'ux', 'graphic', 'creative', 'visual'],
            '音频制作': ['voice', 'speech', 'audio', 'song', 'music', 'sound', 'podcast', 'narration'],
            '图像生成': ['photo', 'image', 'picture', 'avatar', 'headshot', 'portrait', 'visual', 'graphic'],
            '教育培训': ['course', 'tutorial', 'learn', 'education', 'training', 'teach', 'lesson', 'study'],
            '社交媒体': ['social', 'instagram', 'facebook', 'twitter', 'linkedin', 'post', 'content'],
            '办公自动化': ['office', 'productivity', 'workflow', 'automation', 'document', 'template'],
            '娱乐游戏': ['game', 'entertainment', 'fun', 'anime', 'character', 'story', 'fiction'],
            '健康医疗': ['health', 'medical', 'fitness', 'wellness', 'therapy', 'diet', 'mental'],
            '金融科技': ['finance', 'money', 'payment', 'crypto', 'investment', 'trading', 'bank'],
            '房地产': ['real estate', 'property', 'house', 'room', 'interior', 'architecture', 'home'],
            '免费工具': ['free', 'no cost', 'gratis', 'complimentary', 'zero cost'],
        }
        
        # 竞争度评估关键词
        self.competition_indicators = {
            'high': ['chatgpt', 'openai', 'google', 'microsoft', 'adobe', 'canva', 'figma'],
            'medium': ['generator', 'maker', 'creator', 'builder', 'tool', 'app'],
            'low': ['specific niche terms', 'new technologies', 'emerging needs']
        }
        
        # 商业价值评估关键词
        self.high_value_indicators = ['professional', 'business', 'enterprise', 'commercial', 'premium', 'pro']
        self.monetization_models = {
            'SaaS订阅': ['tool', 'platform', 'software', 'service'],
            'API服务': ['api', 'integration', 'automation', 'batch'],
            '一次性付费': ['template', 'pack', 'bundle', 'download'],
            '广告模式': ['free', 'viewer', 'user', 'content'],
            '咨询服务': ['professional', 'custom', 'bespoke', 'consultation'],
            '培训课程': ['course', 'tutorial', 'training', 'education']
        }

    def analyze_keyword_changes(self, changes_file_path: str) -> Dict:
        """
        分析关键词变化文件
        
        Args:
            changes_file_path: 变化文件路径
            
        Returns:
            Dict: 分析结果
        """
        try:
            # 读取变化数据
            with open(changes_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            changes = data.get('changes', {})
            statistics = data.get('statistics', {})
            
            # 分析新增关键词
            new_keywords = changes.get('new_keywords', [])
            new_insights = self._analyze_new_keywords(new_keywords)
            
            # 分析消失关键词
            disappeared_keywords = changes.get('disappeared_keywords', [])
            disappeared_analysis = self._analyze_disappeared_keywords(disappeared_keywords)
            
            # 生成综合报告
            analysis_result = {
                'metadata': {
                    'main_keyword': metadata.get('main_keyword', ''),
                    'current_date': metadata.get('current_date', ''),
                    'previous_date': metadata.get('previous_date', ''),
                    'analysis_time': datetime.now().isoformat(),
                    'total_new': len(new_keywords),
                    'total_disappeared': len(disappeared_keywords)
                },
                'statistics': statistics,
                'new_keyword_insights': new_insights,
                'disappeared_analysis': disappeared_analysis,
                'business_opportunities': self._generate_business_opportunities(new_insights),
                'risk_warnings': self._generate_risk_warnings(disappeared_analysis),
                'strategic_recommendations': self._generate_strategic_recommendations(new_insights, disappeared_analysis)
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"分析关键词变化文件失败: {e}")
            raise

    def _analyze_new_keywords(self, keywords: List[str]) -> Dict:
        """分析新增关键词"""
        insights = {
            'categories': defaultdict(list),
            'high_value_opportunities': [],
            'quick_wins': [],
            'market_trends': {},
            'competition_analysis': {},
            'monetization_opportunities': defaultdict(list)
        }
        
        for keyword in keywords:
            # 分类
            category = self._categorize_keyword(keyword)
            insights['categories'][category].append(keyword)
            
            # 商业价值评估
            business_value = self._evaluate_business_value(keyword)
            competition_level = self._assess_competition_level(keyword)
            monetization_models = self._identify_monetization_models(keyword)
            
            keyword_insight = {
                'keyword': keyword,
                'category': category,
                'business_value': business_value,
                'competition_level': competition_level,
                'monetization_models': monetization_models,
                'market_signals': self._extract_market_signals(keyword)
            }
            
            # 高价值机会
            if business_value >= 7:
                insights['high_value_opportunities'].append(keyword_insight)
            
            # 快速变现机会
            if business_value >= 5 and competition_level == 'low':
                insights['quick_wins'].append(keyword_insight)
            
            # 变现机会分类
            for model in monetization_models:
                insights['monetization_opportunities'][model].append(keyword)
        
        # 市场趋势分析
        insights['market_trends'] = self._analyze_market_trends(insights['categories'])
        
        # 竞争格局分析
        insights['competition_analysis'] = self._analyze_competition_landscape(keywords)
        
        return dict(insights)

    def _analyze_disappeared_keywords(self, keywords: List[str]) -> Dict:
        """分析消失关键词"""
        analysis = {
            'categories': defaultdict(list),
            'disappearance_reasons': {},
            'risk_signals': [],
            'market_shifts': {},
            'affected_business_areas': set()
        }
        
        for keyword in keywords:
            category = self._categorize_keyword(keyword)
            analysis['categories'][category].append(keyword)
            
            # 分析消失原因
            reasons = self._analyze_disappearance_reasons(keyword)
            analysis['disappearance_reasons'][keyword] = reasons
            
            # 风险信号
            if any(reason in ['market_saturation', 'tech_obsolete'] for reason in reasons):
                analysis['risk_signals'].append({
                    'keyword': keyword,
                    'risk_level': 'high',
                    'reasons': reasons
                })
        
        return dict(analysis)

    def _categorize_keyword(self, keyword: str) -> str:
        """关键词分类"""
        keyword_lower = keyword.lower()
        
        for category, indicators in self.category_keywords.items():
            for indicator in indicators:
                if indicator in keyword_lower:
                    return category
        
        return '其他'

    def _evaluate_business_value(self, keyword: str) -> int:
        """评估商业价值 (1-10)"""
        score = 5  # 基础分数
        keyword_lower = keyword.lower()
        
        # 高价值指标
        for indicator in self.high_value_indicators:
            if indicator in keyword_lower:
                score += 2
        
        # 免费工具通常商业价值较低
        if 'free' in keyword_lower:
            score -= 1
        
        # 专业术语提升价值
        if any(term in keyword_lower for term in ['api', 'automation', 'enterprise', 'professional']):
            score += 1
        
        # 确保在合理范围内
        return max(1, min(10, score))

    def _assess_competition_level(self, keyword: str) -> str:
        """评估竞争水平"""
        keyword_lower = keyword.lower()
        
        # 检查高竞争指标
        for indicator in self.competition_indicators['high']:
            if indicator in keyword_lower:
                return 'high'
        
        # 检查中等竞争指标
        for indicator in self.competition_indicators['medium']:
            if indicator in keyword_lower:
                return 'medium'
        
        return 'low'

    def _identify_monetization_models(self, keyword: str) -> List[str]:
        """识别变现模式"""
        models = []
        keyword_lower = keyword.lower()
        
        for model, indicators in self.monetization_models.items():
            if any(indicator in keyword_lower for indicator in indicators):
                models.append(model)
        
        return models or ['SaaS订阅']  # 默认模式

    def _extract_market_signals(self, keyword: str) -> List[str]:
        """提取市场信号"""
        signals = []
        keyword_lower = keyword.lower()
        
        if 'free' in keyword_lower:
            signals.append('价格敏感市场')
        if any(term in keyword_lower for term in ['professional', 'enterprise', 'business']):
            signals.append('B2B市场需求')
        if any(term in keyword_lower for term in ['auto', 'batch', 'bulk']):
            signals.append('自动化需求强烈')
        if 'api' in keyword_lower:
            signals.append('集成需求')
        
        return signals

    def _analyze_market_trends(self, categories: Dict) -> Dict:
        """分析市场趋势"""
        trends = {}
        
        # 计算各分类的增长情况
        for category, keywords in categories.items():
            count = len(keywords)
            if count >= 10:
                trends[category] = {'status': '快速增长', 'keywords_count': count}
            elif count >= 5:
                trends[category] = {'status': '稳定增长', 'keywords_count': count}
            else:
                trends[category] = {'status': '轻微增长', 'keywords_count': count}
        
        return trends

    def _analyze_competition_landscape(self, keywords: List[str]) -> Dict:
        """分析竞争格局"""
        competition = {'low': 0, 'medium': 0, 'high': 0}
        
        for keyword in keywords:
            level = self._assess_competition_level(keyword)
            competition[level] += 1
        
        total = len(keywords)
        return {
            'distribution': competition,
            'percentages': {k: round(v/total*100, 1) for k, v in competition.items()},
            'recommendation': '低竞争领域占比高，存在较多机会' if competition['low'] > competition['high'] else '需要差异化策略应对激烈竞争'
        }

    def _analyze_disappearance_reasons(self, keyword: str) -> List[str]:
        """分析关键词消失原因"""
        reasons = []
        keyword_lower = keyword.lower()
        
        # 技术过时
        if any(tech in keyword_lower for tech in ['old', 'legacy', 'deprecated']):
            reasons.append('技术过时')
        
        # 市场饱和
        if 'generator' in keyword_lower and len(keyword_lower.split()) > 3:
            reasons.append('市场饱和')
        
        # 用户兴趣转移
        if any(trend in keyword_lower for trend in ['basic', 'simple', 'easy']):
            reasons.append('用户需求升级')
        
        # 产品失败
        if 'beta' in keyword_lower or 'test' in keyword_lower:
            reasons.append('产品可能失败')
        
        return reasons or ['自然波动']

    def _generate_business_opportunities(self, insights: Dict) -> List[Dict]:
        """生成商业机会建议"""
        opportunities = []
        
        # 基于高价值关键词生成机会
        for opportunity in insights.get('high_value_opportunities', [])[:10]:
            opportunities.append({
                'title': f"开发{opportunity['keyword']}相关工具",
                'category': opportunity['category'],
                'business_value': opportunity['business_value'],
                'competition_level': opportunity['competition_level'],
                'suggested_models': opportunity['monetization_models'],
                'priority': 'high' if opportunity['business_value'] >= 8 else 'medium'
            })
        
        return opportunities

    def _generate_risk_warnings(self, disappeared_analysis: Dict) -> List[Dict]:
        """生成风险预警"""
        warnings = []
        
        for signal in disappeared_analysis.get('risk_signals', []):
            warnings.append({
                'title': f"{signal['keyword']} 相关市场可能衰退",
                'risk_level': signal['risk_level'],
                'reasons': signal['reasons'],
                'suggestion': '建议重新评估相关投资和资源配置'
            })
        
        return warnings

    def _generate_strategic_recommendations(self, new_insights: Dict, disappeared_analysis: Dict) -> Dict:
        """生成战略建议"""
        recommendations = {
            'immediate_actions': [],
            'medium_term_strategy': [],
            'long_term_vision': [],
            'resource_allocation': {}
        }
        
        # 立即行动建议
        quick_wins = new_insights.get('quick_wins', [])
        for win in quick_wins[:5]:
            recommendations['immediate_actions'].append({
                'action': f"启动{win['keyword']}项目",
                'reason': '低竞争、高价值机会',
                'timeline': '1-3个月'
            })
        
        # 中期策略
        top_categories = sorted(new_insights.get('market_trends', {}).items(), 
                               key=lambda x: x[1]['keywords_count'], reverse=True)[:3]
        for category, info in top_categories:
            recommendations['medium_term_strategy'].append({
                'strategy': f"布局{category}领域",
                'keywords_count': info['keywords_count'],
                'timeline': '6-12个月'
            })
        
        return recommendations

    def generate_html_report(self, analysis_result: Dict, output_dir: str = None) -> str:
        """生成HTML报告"""
        if output_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            output_dir = os.path.join(project_root, "reports")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        metadata = analysis_result['metadata']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        main_keyword = metadata['main_keyword'].replace(' ', '_')
        filename = f"business_analysis_{main_keyword}_{timestamp}.html"
        file_path = os.path.join(output_dir, filename)
        
        # 生成HTML内容
        html_content = self._generate_html_content(analysis_result)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已生成: {file_path}")
        return file_path

    def _generate_html_content(self, analysis: Dict) -> str:
        """生成HTML内容"""
        metadata = analysis['metadata']
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI关键词商业价值分析报告 - {metadata['main_keyword']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.7;
            color: #1a1a1a;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .report-header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 48px;
            margin-bottom: 32px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .report-title {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 16px;
            letter-spacing: -0.02em;
        }}
        
        .report-subtitle {{
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 32px;
            font-weight: 400;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
            margin-top: 24px;
        }}
        
        .meta-item {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 16px;
            border-left: 4px solid #667eea;
        }}
        
        .meta-label {{
            font-size: 0.875rem;
            color: #666;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .meta-value {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 4px;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            margin-bottom: 32px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .section-title {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 24px;
            color: #1a1a1a;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .section-icon {{
            font-size: 2rem;
        }}
        
        .grid {{
            display: grid;
            gap: 24px;
        }}
        
        .grid-2 {{
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        }}
        
        .grid-3 {{
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }}
        
        .card {{
            background: #f8fafc;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
            border-color: #667eea;
        }}
        
        .card-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #1a1a1a;
        }}
        
        .card-content {{
            color: #666;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
        
        .badge-high {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .badge-medium {{
            background: #fef3c7;
            color: #d97706;
        }}
        
        .badge-low {{
            background: #dcfce7;
            color: #16a34a;
        }}
        
        .badge-primary {{
            background: #dbeafe;
            color: #2563eb;
        }}
        
        .opportunity-item {{
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            border: 1px solid #0ea5e9;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
        }}
        
        .opportunity-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #0c4a6e;
            margin-bottom: 8px;
        }}
        
        .keyword-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }}
        
        .keyword-tag {{
            background: rgba(255, 255, 255, 0.8);
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            border: 1px solid rgba(102, 126, 234, 0.2);
            color: #4c1d95;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
        }}
        
        .stat-number {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #667eea;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 4px;
        }}
        
        .trend-indicator {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-left: 8px;
        }}
        
        .trend-up {{
            background: #dcfce7;
            color: #16a34a;
        }}
        
        .trend-down {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .category-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .category-name {{
            font-weight: 500;
            color: #1a1a1a;
        }}
        
        .category-count {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .action-item {{
            background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
            border-left: 4px solid #22c55e;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 16px;
        }}
        
        .action-title {{
            font-weight: 600;
            color: #15803d;
            margin-bottom: 8px;
        }}
        
        .action-timeline {{
            font-size: 0.9rem;
            color: #16a34a;
            font-weight: 500;
        }}
        
        .footer {{
            text-align: center;
            padding: 48px 0;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px 16px;
            }}
            
            .report-header {{
                padding: 32px 24px;
            }}
            
            .report-title {{
                font-size: 2.2rem;
            }}
            
            .section {{
                padding: 28px 20px;
            }}
            
            .grid-2, .grid-3 {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1 class="report-title">🚀 AI关键词商业价值分析报告</h1>
            <p class="report-subtitle">基于搜索趋势变化的商业机会洞察与战略建议</p>
            
            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">关键词根</div>
                    <div class="meta-value">{metadata['main_keyword']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">分析日期</div>
                    <div class="meta-value">{metadata['current_date']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">对比日期</div>
                    <div class="meta-value">{metadata['previous_date']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">报告生成时间</div>
                    <div class="meta-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-number">{metadata['total_new']}</span>
                    <div class="stat-label">新增关键词</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{metadata['total_disappeared']}</span>
                    <div class="stat-label">消失关键词</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(analysis.get('business_opportunities', []))}</span>
                    <div class="stat-label">商业机会</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(analysis.get('risk_warnings', []))}</span>
                    <div class="stat-label">风险预警</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">💎</span>
                核心商业机会
            </h2>
            <div class="grid">
                {self._generate_opportunities_html(analysis.get('business_opportunities', []))}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">📈</span>
                市场趋势分析
            </h2>
            <div class="grid grid-2">
                {self._generate_trends_html(analysis.get('new_keyword_insights', {}))}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">⚠️</span>
                风险预警
            </h2>
            <div class="grid">
                {self._generate_warnings_html(analysis.get('risk_warnings', []))}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">🎯</span>
                战略建议
            </h2>
            <div class="grid grid-3">
                {self._generate_recommendations_html(analysis.get('strategic_recommendations', {}))}
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🤖 由Google长尾词监控系统自动生成 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>基于AI关键词趋势变化的智能商业分析</p>
    </div>
</body>
</html>
"""
        return html

    def _generate_opportunities_html(self, opportunities: List[Dict]) -> str:
        """生成商业机会HTML"""
        if not opportunities:
            return '<div class="card"><div class="card-title">暂无明显商业机会</div><div class="card-content">建议持续监控市场变化</div></div>'
        
        html = ""
        for opp in opportunities[:8]:  # 显示前8个机会
            priority_badge = f'<span class="badge badge-{"high" if opp["priority"] == "high" else "medium"}">{opp["priority"].upper()}</span>'
            models_badges = "".join([f'<span class="badge badge-primary">{model}</span>' for model in opp['suggested_models'][:3]])
            
            html += f"""
            <div class="opportunity-item">
                <div class="opportunity-title">{opp['title']} {priority_badge}</div>
                <div class="card-content">
                    <strong>分类:</strong> {opp['category']}<br>
                    <strong>商业价值:</strong> {opp['business_value']}/10<br>
                    <strong>竞争程度:</strong> <span class="badge badge-{opp['competition_level']}">{opp['competition_level']}</span><br>
                    <strong>建议模式:</strong><br>
                    <div style="margin-top: 8px;">{models_badges}</div>
                </div>
            </div>
            """
        
        return html

    def _generate_trends_html(self, insights: Dict) -> str:
        """生成趋势分析HTML"""
        categories = insights.get('categories', {})
        trends = insights.get('market_trends', {})
        
        # 分类趋势
        categories_html = '<div class="card"><div class="card-title">关键词分类分布</div><div class="card-content">'
        for category, keywords in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:8]:
            categories_html += f'<div class="category-item"><span class="category-name">{category}</span><span class="category-count">{len(keywords)}</span></div>'
        categories_html += '</div></div>'
        
        # 市场趋势
        trends_html = '<div class="card"><div class="card-title">市场趋势洞察</div><div class="card-content">'
        for category, info in trends.items():
            status_class = "trend-up" if info['status'] in ['快速增长', '稳定增长'] else "trend-down"
            trends_html += f'<div class="category-item"><span class="category-name">{category}</span><span class="trend-indicator {status_class}">{info["status"]}</span></div>'
        trends_html += '</div></div>'
        
        return categories_html + trends_html

    def _generate_warnings_html(self, warnings: List[Dict]) -> str:
        """生成风险预警HTML"""
        if not warnings:
            return '<div class="card"><div class="card-title">暂无重大风险</div><div class="card-content">当前市场表现稳定</div></div>'
        
        html = ""
        for warning in warnings:
            risk_badge = f'<span class="badge badge-high">{warning["risk_level"].upper()}</span>'
            reasons = ", ".join(warning['reasons'])
            
            html += f"""
            <div class="card" style="border-left: 4px solid #dc2626;">
                <div class="card-title">{warning['title']} {risk_badge}</div>
                <div class="card-content">
                    <strong>风险原因:</strong> {reasons}<br>
                    <strong>建议:</strong> {warning['suggestion']}
                </div>
            </div>
            """
        
        return html

    def _generate_recommendations_html(self, recommendations: Dict) -> str:
        """生成战略建议HTML"""
        html = ""
        
        # 立即行动
        immediate = recommendations.get('immediate_actions', [])
        if immediate:
            html += '<div class="card"><div class="card-title">🚀 立即行动建议</div><div class="card-content">'
            for action in immediate[:5]:
                html += f'<div class="action-item"><div class="action-title">{action["action"]}</div><div>{action["reason"]}</div><div class="action-timeline">时间线: {action["timeline"]}</div></div>'
            html += '</div></div>'
        
        # 中期策略
        medium_term = recommendations.get('medium_term_strategy', [])
        if medium_term:
            html += '<div class="card"><div class="card-title">📊 中期战略布局</div><div class="card-content">'
            for strategy in medium_term[:5]:
                html += f'<div class="action-item"><div class="action-title">{strategy["strategy"]}</div><div>关键词数量: {strategy["keywords_count"]}</div><div class="action-timeline">时间线: {strategy["timeline"]}</div></div>'
            html += '</div></div>'
        
        # 资源分配建议
        html += '<div class="card"><div class="card-title">💰 资源配置建议</div><div class="card-content">建议优先投入高价值、低竞争的领域，同时布局未来趋势方向。</div></div>'
        
        return html


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI关键词商业价值分析器")
    parser.add_argument("changes_file", help="关键词变化文件路径")
    parser.add_argument("-o", "--output", help="输出目录", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # 初始化分析器
        analyzer = BusinessAnalyzer()
        
        # 执行分析
        print(f"🔍 开始分析文件: {args.changes_file}")
        analysis_result = analyzer.analyze_keyword_changes(args.changes_file)
        
        # 生成HTML报告
        print("📝 生成HTML报告...")
        report_path = analyzer.generate_html_report(analysis_result, args.output)
        
        print(f"✅ 分析完成！")
        print(f"📊 报告已保存: {report_path}")
        print(f"🌐 请在浏览器中打开查看详细报告")
        
        return 0
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())