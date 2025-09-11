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
    """关键词洞察数据结构 - 优化版"""
    keyword: str
    category: str
    
    # 多维度商业价值评估
    business_value_score: Dict[str, int]  # 包含：market_size, monetization_ease, user_demand, technical_feasibility
    overall_business_value: int  # 1-10 综合商业价值评分
    
    # 深度竞争分析
    competition_analysis: Dict[str, any]  # 包含：level, competitor_count, big_tech_involvement, differentiation_opportunity
    
    # 市场分析
    market_analysis: Dict[str, any]  # 包含：size_category, growth_potential, seasonal_trends, target_segments
    
    # 用户洞察
    user_insights: Dict[str, any]  # 包含：personas, pain_points, user_journey, payment_willingness
    
    # 变现模式分析
    monetization_analysis: Dict[str, any]  # 包含：recommended_models, revenue_potential, pricing_strategy
    
    # 技术与实现
    technical_analysis: Dict[str, any]  # 包含：difficulty, development_time, required_skills, infrastructure_needs
    
    # 风险评估
    risk_assessment: Dict[str, any]  # 包含：market_risks, technical_risks, competitive_risks, mitigation_strategies
    
    # 机会窗口
    opportunity_window: Dict[str, any]  # 包含：urgency, optimal_timing, market_readiness


class BusinessAnalyzer:
    """商业价值分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.logger = logging.getLogger(__name__)
        
        # 分类关键词字典 - 大幅扩充和优化
        self.category_keywords = {
            '视频制作': ['video', 'youtube', 'tiktok', 'shorts', 'movie', 'film', 'animation', 'vlog', 'livestream', 'streaming', 'clip', 'montage', 'editing', 'trailer'],
            '图像生成': ['photo', 'image', 'picture', 'avatar', 'headshot', 'portrait', 'visual', 'graphic', 'illustration', 'artwork', 'drawing', 'sketch', 'wallpaper'],
            '内容创作': ['content', 'article', 'blog', 'post', 'story', 'writing', 'copywriting', 'script', 'caption', 'description', 'text', 'paragraph'],
            '设计创意': ['design', 'art', 'logo', 'ui', 'ux', 'creative', 'banner', 'poster', 'flyer', 'card', 'layout', 'template', 'brand'],
            'AI工具': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'smart', 'intelligent', 'automated', 'auto'],
            '编程开发': ['code', 'programming', 'developer', 'js', 'javascript', 'html', 'css', 'json', 'api', 'database', 'software', 'app', 'development'],
            '商业应用': ['business', 'commercial', 'enterprise', 'professional', 'corporate', 'company', 'industry', 'b2b', 'startup'],
            '电商相关': ['ecommerce', 'shop', 'store', 'sell', 'sale', 'product', 'shopping', 'marketplace', 'retail', 'merchant'],
            '数据分析': ['data', 'analytics', 'analysis', 'report', 'chart', 'graph', 'dashboard', 'statistics', 'metric', 'insight'],
            '办公自动化': ['office', 'productivity', 'workflow', 'automation', 'document', 'excel', 'presentation', 'meeting', 'task'],
            '社交媒体': ['social', 'instagram', 'facebook', 'twitter', 'linkedin', 'media', 'influencer', 'community', 'engagement'],
            '教育培训': ['course', 'tutorial', 'learn', 'education', 'training', 'teach', 'lesson', 'study', 'skill', 'knowledge'],
            '娱乐休闲': ['game', 'entertainment', 'fun', 'music', 'song', 'anime', 'character', 'fiction', 'hobby', 'leisure'],
            '金融科技': ['finance', 'money', 'payment', 'crypto', 'investment', 'trading', 'bank', 'fintech', 'currency'],
            '健康医疗': ['health', 'medical', 'fitness', 'wellness', 'therapy', 'diet', 'mental', 'healthcare', 'medicine'],
            '房地产建筑': ['real estate', 'property', 'house', 'home', 'room', 'interior', 'architecture', 'construction', 'building'],
            '免费服务': ['free', 'no cost', 'gratis', 'complimentary', 'zero cost', 'without payment', 'no charge'],
            '高级服务': ['premium', 'pro', 'professional', 'enterprise', 'advanced', 'premium', 'paid', 'subscription'],
            '技术工具': ['tool', 'generator', 'creator', 'maker', 'builder', 'converter', 'editor', 'optimizer', 'analyzer'],
            '创意内容': ['creative', 'artistic', 'original', 'unique', 'innovative', 'imaginative', 'inspired'],
            '自动化服务': ['auto', 'automatic', 'batch', 'bulk', 'mass', 'automated', 'process', 'workflow'],
            '在线服务': ['online', 'web', 'internet', 'cloud', 'digital', 'virtual', 'remote'],
            '多媒体': ['audio', 'voice', 'sound', 'music', 'speech', 'podcast', 'radio', 'multimedia'],
            '平台服务': ['platform', 'service', 'solution', 'system', 'framework', 'infrastructure'],
            '移动应用': ['mobile', 'app', 'smartphone', 'tablet', 'android', 'ios', 'phone'],
            '网站相关': ['website', 'web', 'site', 'page', 'domain', 'hosting', 'blog', 'portal'],
            'API服务': ['api', 'integration', 'webhook', 'endpoint', 'interface', 'sdk', 'library'],
            '定制服务': ['custom', 'personalized', 'tailored', 'bespoke', 'customized', 'specific'],
            '批量处理': ['batch', 'bulk', 'mass', 'multiple', 'many', 'several', 'numerous'],
            '专业服务': ['professional', 'expert', 'specialist', 'consultant', 'agency', 'firm'],
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
            
            # 多维度分析
            business_value = self._evaluate_business_value(keyword)
            competition_analysis = self._assess_competition_level(keyword)
            market_analysis = self._analyze_market_potential(keyword)
            user_insights = self._analyze_user_insights(keyword)
            monetization_analysis = self._analyze_monetization_potential(keyword)
            technical_analysis = self._analyze_technical_requirements(keyword)
            risk_assessment = self._assess_risks(keyword)
            opportunity_window = self._analyze_opportunity_window(keyword)
            
            # 构建完整洞察数据
            keyword_insight = KeywordInsight(
                keyword=keyword,
                category=category,
                business_value_score={
                    'market_size': self._calculate_market_size_score(keyword.lower()),
                    'monetization_ease': self._calculate_monetization_ease_score(keyword.lower()),
                    'user_demand': self._calculate_user_demand_score(keyword.lower()),
                    'technical_feasibility': self._calculate_technical_feasibility_score(keyword.lower())
                },
                overall_business_value=business_value,
                competition_analysis=competition_analysis,
                market_analysis=market_analysis,
                user_insights=user_insights,
                monetization_analysis=monetization_analysis,
                technical_analysis=technical_analysis,
                risk_assessment=risk_assessment,
                opportunity_window=opportunity_window
            )
            
            # 高价值机会（基于多维度评估）
            if (business_value >= 7 and 
                competition_analysis['level'] in ['low', 'medium'] and
                market_analysis['growth_potential'] >= 6):
                insights['high_value_opportunities'].append(keyword_insight)
            
            # 快速变现机会（优化判断条件）
            if (business_value >= 5 and 
                competition_analysis['level'] == 'low' and
                technical_analysis['difficulty'] <= 5 and
                opportunity_window['urgency'] in ['high', 'medium']):
                insights['quick_wins'].append(keyword_insight)
            
            # 变现机会分类（基于深度分析）
            for model in monetization_analysis['recommended_models']:
                insights['monetization_opportunities'][model].append({
                    'keyword': keyword,
                    'revenue_potential': monetization_analysis.get('revenue_potential', {}),
                    'implementation_difficulty': technical_analysis.get('difficulty', 5),
                    'time_to_market': technical_analysis.get('development_time', 'unknown')
                })
        
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
            'affected_business_areas': []
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
        """关键词智能分类 - 优化版"""
        keyword_lower = keyword.lower()
        
        # 记录所有匹配的分类和权重
        category_scores = defaultdict(float)
        
        for category, indicators in self.category_keywords.items():
            for indicator in indicators:
                if indicator in keyword_lower:
                    # 计算匹配权重：完全匹配得分更高，长匹配得分更高
                    if keyword_lower == indicator:
                        category_scores[category] += 3.0  # 完全匹配
                    elif keyword_lower.startswith(indicator) or keyword_lower.endswith(indicator):
                        category_scores[category] += 2.0  # 前缀或后缀匹配
                    else:
                        category_scores[category] += 1.0 + len(indicator) * 0.1  # 长关键词得分更高
        
        # 特殊规则优化：组合分类
        if category_scores:
            # 如果同时匹配AI工具和其他类别，优先选择更具体的类别
            if 'AI工具' in category_scores and len(category_scores) > 1:
                ai_score = category_scores.pop('AI工具')
                # 给其他类别加权
                for cat in category_scores:
                    category_scores[cat] += ai_score * 0.5
            
            # 选择得分最高的分类
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return best_category
        
        # 如果没有匹配到任何分类，使用更智能的分析
        return self._fallback_categorization(keyword_lower)
    
    def _fallback_categorization(self, keyword_lower: str) -> str:
        """备用分类方法"""
        
        # 基于常见模式进行分类
        if any(word in keyword_lower for word in ['generate', 'create', 'make', 'build']):
            if any(word in keyword_lower for word in ['image', 'photo', 'picture']):
                return '图像生成'
            elif any(word in keyword_lower for word in ['video', 'clip']):
                return '视频制作'
            elif any(word in keyword_lower for word in ['text', 'content', 'article']):
                return '内容创作'
            else:
                return '技术工具'
        
        # 基于动作词分类
        if any(word in keyword_lower for word in ['edit', 'convert', 'transform', 'process']):
            return '技术工具'
        
        # 基于领域词分类
        if any(word in keyword_lower for word in ['marketing', 'seo', 'advertising']):
            return '商业应用'
        
        if any(word in keyword_lower for word in ['learn', 'tutorial', 'guide']):
            return '教育培训'
        
        # 基于格式词分类
        if any(word in keyword_lower for word in ['pdf', 'excel', 'ppt', 'doc']):
            return '办公自动化'
        
        # 基于平台词分类
        if any(word in keyword_lower for word in ['youtube', 'instagram', 'tiktok']):
            return '社交媒体'
        
        # 仍然无法分类的情况
        return '通用工具'  # 改为更具体的默认分类

    def _evaluate_business_value(self, keyword: str) -> int:
        """评估商业价值 (1-10)"""
        score = 5  # 基础分数
        keyword_lower = keyword.lower()
        
        # 多维度商业价值评估
        market_size_score = self._calculate_market_size_score(keyword_lower)
        monetization_ease_score = self._calculate_monetization_ease_score(keyword_lower)
        user_demand_score = self._calculate_user_demand_score(keyword_lower)
        technical_feasibility_score = self._calculate_technical_feasibility_score(keyword_lower)
        
        # 综合评分计算（权重分配）
        weights = {
            'market_size': 0.3,
            'monetization_ease': 0.25,
            'user_demand': 0.25,
            'technical_feasibility': 0.2
        }
        
        weighted_score = (
            market_size_score * weights['market_size'] +
            monetization_ease_score * weights['monetization_ease'] +
            user_demand_score * weights['user_demand'] +
            technical_feasibility_score * weights['technical_feasibility']
        )
        
        return max(1, min(10, int(weighted_score)))

    def _assess_competition_level(self, keyword: str) -> Dict[str, any]:
        """深度竞争分析"""
        keyword_lower = keyword.lower()
        
        # 基础竞争水平评估
        base_level = self._get_base_competition_level(keyword_lower)
        
        # 竞争对手数量估算
        competitor_count = self._estimate_competitor_count(keyword_lower)
        
        # 大厂参与度分析
        big_tech_involvement = self._analyze_big_tech_involvement(keyword_lower)
        
        # 差异化机会评估
        differentiation_opportunity = self._assess_differentiation_opportunity(keyword_lower)
        
        # 市场进入难度
        entry_barrier = self._calculate_entry_barrier(keyword_lower, competitor_count, big_tech_involvement)
        
        return {
            'level': base_level,
            'competitor_count': competitor_count,
            'big_tech_involvement': big_tech_involvement,
            'differentiation_opportunity': differentiation_opportunity,
            'entry_barrier': entry_barrier,
            'competitive_advantage_potential': self._assess_competitive_advantage_potential(keyword_lower)
        }

    def _identify_monetization_models(self, keyword: str) -> List[str]:
        """识别变现模式 - 优化版"""
        models = []
        keyword_lower = keyword.lower()
        
        # 基于深度分析推荐变现模式
        user_payment_willingness = self._assess_payment_willingness(keyword_lower)
        technical_scalability = self._assess_scalability(keyword_lower)
        
        # SaaS订阅模式
        if (any(indicator in keyword_lower for indicator in ['tool', 'platform', 'service']) and
            user_payment_willingness['willingness_score'] >= 6):
            models.append('SaaS订阅')
        
        # API服务模式
        if (any(indicator in keyword_lower for indicator in ['api', 'integration', 'automation']) and
            technical_scalability['score'] >= 7):
            models.append('API服务')
        
        # 一次性付费模式
        if any(indicator in keyword_lower for indicator in ['template', 'pack', 'bundle', 'download']):
            models.append('一次性付费')
        
        # 广告模式
        if ('free' in keyword_lower and 
            any(indicator in keyword_lower for indicator in ['viewer', 'user', 'content'])):
            models.append('广告模式')
        
        # 咨询服务模式
        if any(indicator in keyword_lower for indicator in ['professional', 'custom', 'consultation']):
            models.append('咨询服务')
        
        # 培训课程模式
        if any(indicator in keyword_lower for indicator in ['course', 'tutorial', 'training', 'education']):
            models.append('培训课程')
        
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
        """分析市场趋势 - 增强版"""
        trends = {}
        
        # 计算各分类的增长情况 - 更精确的分类
        total_keywords = sum(len(keywords) for keywords in categories.values())
        
        for category, keywords in categories.items():
            count = len(keywords)
            percentage = (count / total_keywords) * 100 if total_keywords > 0 else 0
            
            # 更精细的趋势分类
            if count >= 30:  # 非常高
                status = '爆发式增长'
                growth_score = 10
            elif count >= 20:  # 高
                status = '强劲增长'
                growth_score = 8
            elif count >= 10:  # 中等偏高
                status = '快速增长'
                growth_score = 6
            elif count >= 5:  # 中等
                status = '稳定增长'
                growth_score = 4
            elif count >= 2:  # 低
                status = '轻微增长'
                growth_score = 2
            else:  # 非常低
                status = '新兴趋势'
                growth_score = 1
            
            # 增加趋势预测和机会窗口分析
            trend_analysis = {
                'status': status,
                'keywords_count': count,
                'market_share': round(percentage, 1),
                'growth_score': growth_score,
                'trend_strength': self._calculate_trend_strength(count, percentage),
                'market_potential': self._assess_category_potential(category, keywords),
                'investment_priority': self._calculate_investment_priority(growth_score, percentage),
                'time_sensitivity': self._assess_time_sensitivity(status, count),
                'predicted_6m_growth': self._predict_category_growth(growth_score, count),
                'key_opportunities': self._identify_category_opportunities(keywords[:5])  # 分析前5个关键词
            }
            
            trends[category] = trend_analysis
        
        # 添加整体市场洞察
        trends['_market_overview'] = self._generate_market_overview(trends)
        
        return trends
    
    def _calculate_trend_strength(self, count: int, percentage: float) -> str:
        """计算趋势强度"""
        combined_score = count * 0.7 + percentage * 0.3
        
        if combined_score >= 25:
            return '非常强劲'
        elif combined_score >= 15:
            return '强劲'
        elif combined_score >= 8:
            return '中等'
        else:
            return '较弱'
    
    def _assess_category_potential(self, category: str, keywords: List[str]) -> Dict[str, any]:
        """评估分类潜力"""
        # 基于关键词特征分析商业潜力
        commercial_keywords = sum(1 for kw in keywords 
                                if any(term in kw.lower() for term in 
                                     ['business', 'professional', 'enterprise', 'commercial']))
        
        automation_keywords = sum(1 for kw in keywords 
                                if any(term in kw.lower() for term in 
                                     ['auto', 'api', 'batch', 'bulk']))
        
        b2b_potential = (commercial_keywords / len(keywords)) * 100 if keywords else 0
        automation_potential = (automation_keywords / len(keywords)) * 100 if keywords else 0
        
        # 综合潜力评分
        potential_score = min(10, max(1, 
            (b2b_potential * 0.4 + automation_potential * 0.3 + len(keywords) * 0.3) / 5
        ))
        
        return {
            'score': round(potential_score, 1),
            'b2b_percentage': round(b2b_potential, 1),
            'automation_percentage': round(automation_potential, 1),
            'market_size': 'large' if potential_score >= 7 else 'medium' if potential_score >= 4 else 'small'
        }
    
    def _calculate_investment_priority(self, growth_score: int, market_share: float) -> str:
        """计算投资优先级"""
        priority_score = growth_score * 0.6 + market_share * 0.4
        
        if priority_score >= 8:
            return '最高优先级'
        elif priority_score >= 6:
            return '高优先级'
        elif priority_score >= 4:
            return '中等优先级'
        else:
            return '低优先级'
    
    def _assess_time_sensitivity(self, status: str, count: int) -> str:
        """评估时间敏感性"""
        if status in ['爆发式增长', '强劲增长'] and count >= 20:
            return '紧急' # 需要立即行动
        elif status in ['快速增长', '稳定增长']:
            return '中等' # 3-6个月内行动
        else:
            return '低' # 可以观望
    
    def _predict_category_growth(self, growth_score: int, current_count: int) -> Dict[str, any]:
        """预测分类6个月增长"""
        # 基于当前增长速度预测未来增长
        growth_multiplier = {
            10: 2.5,  # 爆发式
            8: 2.0,   # 强劲
            6: 1.5,   # 快速
            4: 1.2,   # 稳定
            2: 1.1,   # 轻微
            1: 1.05   # 新兴
        }.get(growth_score, 1.0)
        
        predicted_count = int(current_count * growth_multiplier)
        growth_rate = ((predicted_count - current_count) / current_count * 100) if current_count > 0 else 0
        
        return {
            'predicted_keywords': predicted_count,
            'growth_rate_percentage': round(growth_rate, 1),
            'confidence_level': 'high' if growth_score >= 6 else 'medium' if growth_score >= 4 else 'low',
            'market_timing': '黄金窗口期' if growth_score >= 8 else '成长期' if growth_score >= 6 else '萌芽期'
        }
    
    def _identify_category_opportunities(self, keywords: List[str]) -> List[Dict[str, any]]:
        """识别分类内的关键机会"""
        opportunities = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 快速机会识别
            opportunity_signals = []
            
            if 'free' in keyword_lower:
                opportunity_signals.append('免费增值模式')
            
            if any(term in keyword_lower for term in ['api', 'automation', 'bulk']):
                opportunity_signals.append('B2B自动化服务')
            
            if any(term in keyword_lower for term in ['professional', 'enterprise']):
                opportunity_signals.append('企业级服务')
            
            if any(term in keyword_lower for term in ['template', 'generator']):
                opportunity_signals.append('模板化产品')
            
            if opportunity_signals:
                opportunities.append({
                    'keyword': keyword,
                    'opportunity_type': opportunity_signals[0],  # 主要机会类型
                    'all_signals': opportunity_signals
                })
        
        return opportunities
    
    def _generate_market_overview(self, trends: Dict) -> Dict[str, any]:
        """生成整体市场概览"""
        # 排除元数据字段
        category_trends = {k: v for k, v in trends.items() if not k.startswith('_')}
        
        # 找到增长最快的分类
        fastest_growing = max(category_trends.items(), 
                            key=lambda x: x[1]['growth_score'], 
                            default=(None, {'growth_score': 0}))
        
        # 找到市场份额最大的分类
        largest_market = max(category_trends.items(), 
                           key=lambda x: x[1]['market_share'], 
                           default=(None, {'market_share': 0}))
        
        # 计算高优先级分类数量
        high_priority_count = sum(1 for trend in category_trends.values() 
                                if trend['investment_priority'] in ['最高优先级', '高优先级'])
        
        # 计算紧急分类数量
        urgent_categories = sum(1 for trend in category_trends.values() 
                              if trend['time_sensitivity'] == '紧急')
        
        return {
            'total_categories': len(category_trends),
            'fastest_growing_category': fastest_growing[0],
            'largest_market_category': largest_market[0],
            'high_priority_categories': high_priority_count,
            'urgent_categories': urgent_categories,
            'market_maturity': self._assess_overall_market_maturity(category_trends),
            'strategic_recommendation': self._generate_strategic_recommendation(category_trends)
        }
    
    def _assess_overall_market_maturity(self, category_trends: Dict) -> str:
        """评估整体市场成熟度"""
        avg_growth_score = sum(trend['growth_score'] for trend in category_trends.values()) / len(category_trends)
        
        if avg_growth_score >= 7:
            return '快速发展期'
        elif avg_growth_score >= 5:
            return '成长期'
        elif avg_growth_score >= 3:
            return '成熟期'
        else:
            return '稳定期'
    
    def _generate_strategic_recommendation(self, category_trends: Dict) -> str:
        """生成战略建议"""
        high_growth_categories = [name for name, trend in category_trends.items() 
                                if trend['growth_score'] >= 8]
        
        if len(high_growth_categories) >= 3:
            return f"多元化布局策略：同时投资{', '.join(high_growth_categories[:3])}等高增长领域"
        elif len(high_growth_categories) >= 1:
            return f"聚焦策略：重点投资{high_growth_categories[0]}领域，在竞争激烈前占领先机"
        else:
            return "探索策略：市场较为成熟，建议聚焦差异化创新和细分市场机会"

    def _analyze_competition_landscape(self, keywords: List[str]) -> Dict:
        """分析竞争格局"""
        competition = {'low': 0, 'medium': 0, 'high': 0}
        
        for keyword in keywords:
            # 获取基础竞争水平字符串，而不是字典
            competition_analysis = self._assess_competition_level(keyword)
            level = competition_analysis['level']  # 提取字符串值
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
    
    # === 新增的多维度评估方法 ===
    
    def _calculate_market_size_score(self, keyword_lower: str) -> int:
        """计算市场规模评分 (1-10)"""
        score = 5  # 基础分数
        
        # 大众化关键词增分
        if any(term in keyword_lower for term in ['free', 'online', 'generator', 'tool']):
            score += 2
        
        # B2B关键词增分
        if any(term in keyword_lower for term in ['business', 'enterprise', 'professional', 'commercial']):
            score += 3
        
        # 垂直领域调整
        if any(term in keyword_lower for term in ['medical', 'legal', 'finance']):
            score += 1
        
        # 新兴技术领域
        if any(term in keyword_lower for term in ['ai', 'ml', 'blockchain', 'crypto']):
            score += 1
        
        return max(1, min(10, score))
    
    def _calculate_monetization_ease_score(self, keyword_lower: str) -> int:
        """计算变现难易度评分 (1-10)"""
        score = 5
        
        # 容易变现的类型
        if any(term in keyword_lower for term in ['template', 'tool', 'generator', 'maker']):
            score += 2
        
        # API/SaaS友好
        if any(term in keyword_lower for term in ['api', 'automation', 'batch', 'bulk']):
            score += 3
        
        # 专业服务
        if any(term in keyword_lower for term in ['professional', 'custom', 'consultation']):
            score += 2
        
        # 免费产品变现较难
        if 'free' in keyword_lower:
            score -= 2
        
        return max(1, min(10, score))
    
    def _calculate_user_demand_score(self, keyword_lower: str) -> int:
        """计算用户需求强度评分 (1-10)"""
        score = 5
        
        # 高频需求关键词
        if any(term in keyword_lower for term in ['daily', 'auto', 'quick', 'instant', 'fast']):
            score += 2
        
        # 痛点解决型
        if any(term in keyword_lower for term in ['easy', 'simple', 'without', 'no code', 'drag']):
            score += 2
        
        # 专业需求
        if any(term in keyword_lower for term in ['professional', 'advanced', 'pro', 'premium']):
            score += 1
        
        # 创意类需求
        if any(term in keyword_lower for term in ['creative', 'design', 'art', 'beautiful']):
            score += 1
        
        return max(1, min(10, score))
    
    def _calculate_technical_feasibility_score(self, keyword_lower: str) -> int:
        """计算技术可行性评分 (1-10)"""
        score = 7  # 默认较高可行性
        
        # 复杂AI功能降分
        if any(term in keyword_lower for term in ['deep learning', 'neural', 'complex', 'advanced ai']):
            score -= 3
        
        # 简单工具类增分
        if any(term in keyword_lower for term in ['converter', 'formatter', 'validator', 'calculator']):
            score += 2
        
        # 需要大量数据的功能
        if any(term in keyword_lower for term in ['training', 'learning', 'personalized']):
            score -= 2
        
        # 标准化功能
        if any(term in keyword_lower for term in ['standard', 'template', 'format', 'export']):
            score += 1
        
        return max(1, min(10, score))
    
    def _get_base_competition_level(self, keyword_lower: str) -> str:
        """获取基础竞争水平"""
        # 检查高竞争指标
        for indicator in self.competition_indicators['high']:
            if indicator in keyword_lower:
                return 'high'
        
        # 检查中等竞争指标
        for indicator in self.competition_indicators['medium']:
            if indicator in keyword_lower:
                return 'medium'
        
        return 'low'
    
    def _estimate_competitor_count(self, keyword_lower: str) -> str:
        """估算竞争对手数量"""
        if any(term in keyword_lower for term in ['chatgpt', 'openai', 'google', 'microsoft']):
            return 'many (50+)'
        elif any(term in keyword_lower for term in ['generator', 'tool', 'maker', 'creator']):
            return 'moderate (10-50)'
        else:
            return 'few (<10)'
    
    def _analyze_big_tech_involvement(self, keyword_lower: str) -> Dict[str, any]:
        """分析大厂参与情况"""
        big_tech_indicators = {
            'Google': ['google', 'bard', 'gemini'],
            'Microsoft': ['microsoft', 'copilot', 'azure'],
            'OpenAI': ['openai', 'chatgpt', 'gpt'],
            'Meta': ['meta', 'facebook', 'instagram'],
            'Adobe': ['adobe', 'photoshop', 'illustrator'],
            'Amazon': ['amazon', 'aws', 'alexa']
        }
        
        involved_companies = []
        for company, indicators in big_tech_indicators.items():
            if any(indicator in keyword_lower for indicator in indicators):
                involved_companies.append(company)
        
        return {
            'companies': involved_companies,
            'threat_level': 'high' if involved_companies else 'low',
            'differentiation_needed': len(involved_companies) > 0
        }
    
    def _assess_differentiation_opportunity(self, keyword_lower: str) -> Dict[str, any]:
        """评估差异化机会"""
        opportunities = []
        
        if 'free' in keyword_lower:
            opportunities.append('premium_version')
        if 'simple' in keyword_lower:
            opportunities.append('advanced_features')
        if 'template' in keyword_lower:
            opportunities.append('custom_solutions')
        if 'online' in keyword_lower:
            opportunities.append('offline_version')
        
        return {
            'opportunities': opportunities,
            'potential_score': len(opportunities) * 2,
            'strategy': 'focus_on_unmet_needs' if opportunities else 'create_new_category'
        }
    
    def _calculate_entry_barrier(self, keyword_lower: str, competitor_count: str, big_tech_involvement: Dict) -> str:
        """计算市场进入门槛"""
        barrier_score = 0
        
        if competitor_count == 'many (50+)':
            barrier_score += 3
        elif competitor_count == 'moderate (10-50)':
            barrier_score += 2
        
        if big_tech_involvement['threat_level'] == 'high':
            barrier_score += 3
        
        if any(term in keyword_lower for term in ['enterprise', 'professional', 'advanced']):
            barrier_score += 1
        
        if barrier_score >= 5:
            return 'high'
        elif barrier_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_competitive_advantage_potential(self, keyword_lower: str) -> Dict[str, any]:
        """评估竞争优势潜力"""
        advantages = []
        
        if any(term in keyword_lower for term in ['fast', 'instant', 'quick']):
            advantages.append('speed_optimization')
        if any(term in keyword_lower for term in ['easy', 'simple', 'user-friendly']):
            advantages.append('user_experience')
        if any(term in keyword_lower for term in ['custom', 'personalized', 'tailored']):
            advantages.append('customization')
        if any(term in keyword_lower for term in ['free', 'low-cost', 'affordable']):
            advantages.append('cost_leadership')
        
        return {
            'potential_advantages': advantages,
            'strength_score': len(advantages),
            'primary_focus': advantages[0] if advantages else 'innovation'
        }
    
    def _analyze_market_potential(self, keyword: str) -> Dict[str, any]:
        """分析市场潜力"""
        keyword_lower = keyword.lower()
        
        # 市场规模分类
        if any(term in keyword_lower for term in ['enterprise', 'business', 'professional']):
            size_category = 'large_b2b'
        elif any(term in keyword_lower for term in ['personal', 'individual', 'consumer']):
            size_category = 'large_b2c'
        elif any(term in keyword_lower for term in ['niche', 'specific', 'specialized']):
            size_category = 'niche'
        else:
            size_category = 'medium'
        
        # 增长潜力评估
        growth_indicators = ['ai', 'automation', 'digital', 'online', 'cloud', 'mobile']
        growth_potential = sum(1 for indicator in growth_indicators if indicator in keyword_lower)
        growth_potential = min(10, max(1, growth_potential * 2 + 4))
        
        # 季节性趋势分析
        seasonal_keywords = {
            'high_season': ['holiday', 'christmas', 'new year', 'back to school'],
            'business_cycle': ['quarter', 'annual', 'monthly', 'weekly'],
            'event_driven': ['conference', 'presentation', 'meeting', 'report']
        }
        
        seasonality = 'none'
        for season_type, keywords in seasonal_keywords.items():
            if any(kw in keyword_lower for kw in keywords):
                seasonality = season_type
                break
        
        return {
            'size_category': size_category,
            'growth_potential': growth_potential,
            'seasonal_trends': seasonality,
            'target_segments': self._identify_target_segments(keyword_lower),
            'market_maturity': self._assess_market_maturity(keyword_lower)
        }
    
    def _identify_target_segments(self, keyword_lower: str) -> List[str]:
        """识别目标细分市场"""
        segments = []
        
        segment_indicators = {
            'developers': ['code', 'programming', 'developer', 'api', 'sdk'],
            'designers': ['design', 'ui', 'ux', 'graphic', 'visual', 'creative'],
            'marketers': ['marketing', 'ad', 'campaign', 'social media', 'seo'],
            'content_creators': ['content', 'blog', 'video', 'podcast', 'creator'],
            'entrepreneurs': ['business', 'startup', 'entrepreneur', 'small business'],
            'enterprises': ['enterprise', 'corporate', 'organization', 'team'],
            'students': ['student', 'education', 'learning', 'academic'],
            'freelancers': ['freelancer', 'consultant', 'independent', 'gig']
        }
        
        for segment, indicators in segment_indicators.items():
            if any(indicator in keyword_lower for indicator in indicators):
                segments.append(segment)
        
        return segments or ['general_users']
    
    def _assess_market_maturity(self, keyword_lower: str) -> str:
        """评估市场成熟度"""
        if any(term in keyword_lower for term in ['new', 'emerging', 'latest', 'cutting-edge']):
            return 'emerging'
        elif any(term in keyword_lower for term in ['traditional', 'standard', 'classic', 'basic']):
            return 'mature'
        else:
            return 'growing'
    
    def _analyze_user_insights(self, keyword: str) -> Dict[str, any]:
        """分析用户洞察"""
        keyword_lower = keyword.lower()
        
        # 用户画像分析
        personas = self._build_user_personas(keyword_lower)
        
        # 痛点识别
        pain_points = self._identify_pain_points(keyword_lower)
        
        # 用户旅程分析
        user_journey = self._analyze_user_journey(keyword_lower)
        
        # 付费意愿评估
        payment_willingness = self._assess_payment_willingness(keyword_lower)
        
        return {
            'personas': personas,
            'pain_points': pain_points,
            'user_journey': user_journey,
            'payment_willingness': payment_willingness,
            'engagement_level': self._assess_engagement_level(keyword_lower)
        }
    
    def _build_user_personas(self, keyword_lower: str) -> Dict[str, any]:
        """构建用户画像"""
        personas = {
            'primary': 'general_user',
            'characteristics': [],
            'skill_level': 'intermediate',
            'use_frequency': 'occasional'
        }
        
        # 技能水平判断
        if any(term in keyword_lower for term in ['professional', 'advanced', 'expert']):
            personas['skill_level'] = 'advanced'
        elif any(term in keyword_lower for term in ['beginner', 'simple', 'easy', 'basic']):
            personas['skill_level'] = 'beginner'
        
        # 使用频率判断
        if any(term in keyword_lower for term in ['daily', 'regular', 'frequent']):
            personas['use_frequency'] = 'frequent'
        elif any(term in keyword_lower for term in ['occasional', 'sometimes', 'when needed']):
            personas['use_frequency'] = 'occasional'
        
        # 用户特征
        if 'business' in keyword_lower:
            personas['characteristics'].append('business_focused')
        if 'creative' in keyword_lower:
            personas['characteristics'].append('creative_oriented')
        if 'technical' in keyword_lower:
            personas['characteristics'].append('technically_savvy')
        
        return personas
    
    def _identify_pain_points(self, keyword_lower: str) -> List[str]:
        """识别用户痛点"""
        pain_points = []
        
        pain_indicators = {
            'time_consuming': ['slow', 'time-consuming', 'manual', 'tedious'],
            'too_complex': ['complex', 'difficult', 'hard', 'complicated'],
            'expensive': ['expensive', 'costly', 'high-price', 'premium'],
            'quality_issues': ['low-quality', 'poor', 'bad', 'inadequate'],
            'limited_features': ['limited', 'basic', 'simple', 'few-options'],
            'accessibility': ['inaccessible', 'hard-to-use', 'confusing', 'unclear']
        }
        
        for pain_point, indicators in pain_indicators.items():
            if any(indicator in keyword_lower for indicator in indicators):
                pain_points.append(pain_point)
        
        # 基于关键词类型推断痛点
        if 'generator' in keyword_lower:
            pain_points.append('manual_creation_effort')
        if 'converter' in keyword_lower:
            pain_points.append('format_compatibility')
        if 'automation' in keyword_lower:
            pain_points.append('repetitive_tasks')
        
        return pain_points or ['general_efficiency']
    
    def _analyze_user_journey(self, keyword_lower: str) -> Dict[str, any]:
        """分析用户旅程"""
        journey_stages = {
            'awareness': 'search_for_solution',
            'consideration': 'compare_options',
            'decision': 'evaluate_features',
            'usage': 'regular_interaction',
            'advocacy': 'recommend_to_others'
        }
        
        # 基于关键词推断用户所处阶段
        if any(term in keyword_lower for term in ['what is', 'how to', 'best']):
            primary_stage = 'awareness'
        elif any(term in keyword_lower for term in ['vs', 'compare', 'alternative']):
            primary_stage = 'consideration'
        elif any(term in keyword_lower for term in ['review', 'pricing', 'features']):
            primary_stage = 'decision'
        else:
            primary_stage = 'usage'
        
        return {
            'primary_stage': primary_stage,
            'touchpoints': self._identify_touchpoints(keyword_lower),
            'conversion_barriers': self._identify_conversion_barriers(keyword_lower)
        }
    
    def _identify_touchpoints(self, keyword_lower: str) -> List[str]:
        """识别用户接触点"""
        touchpoints = ['search_engines']  # 默认接触点
        
        if 'social' in keyword_lower:
            touchpoints.append('social_media')
        if 'blog' in keyword_lower:
            touchpoints.append('content_marketing')
        if 'video' in keyword_lower:
            touchpoints.append('video_platforms')
        if 'review' in keyword_lower:
            touchpoints.append('review_sites')
        
        return touchpoints
    
    def _identify_conversion_barriers(self, keyword_lower: str) -> List[str]:
        """识别转化障碍"""
        barriers = []
        
        if 'free' in keyword_lower:
            barriers.append('pricing_sensitivity')
        if 'trial' in keyword_lower:
            barriers.append('commitment_hesitation')
        if 'complex' in keyword_lower:
            barriers.append('usability_concerns')
        if 'security' in keyword_lower:
            barriers.append('trust_issues')
        
        return barriers or ['general_skepticism']
    
    def _assess_payment_willingness(self, keyword_lower: str) -> Dict[str, any]:
        """评估付费意愿"""
        willingness_score = 5  # 基础分数
        
        # 提高付费意愿的因素
        if any(term in keyword_lower for term in ['professional', 'business', 'enterprise']):
            willingness_score += 3
        if any(term in keyword_lower for term in ['premium', 'pro', 'advanced']):
            willingness_score += 2
        if any(term in keyword_lower for term in ['custom', 'personalized', 'tailored']):
            willingness_score += 2
        
        # 降低付费意愿的因素
        if 'free' in keyword_lower:
            willingness_score -= 3
        if any(term in keyword_lower for term in ['basic', 'simple', 'minimal']):
            willingness_score -= 1
        
        willingness_score = max(1, min(10, willingness_score))
        
        # 价格敏感度分析
        if willingness_score >= 8:
            price_sensitivity = 'low'
            suggested_pricing = 'premium'
        elif willingness_score >= 6:
            price_sensitivity = 'medium'
            suggested_pricing = 'competitive'
        else:
            price_sensitivity = 'high'
            suggested_pricing = 'freemium'
        
        return {
            'willingness_score': willingness_score,
            'price_sensitivity': price_sensitivity,
            'suggested_pricing': suggested_pricing,
            'payment_triggers': self._identify_payment_triggers(keyword_lower)
        }
    
    def _identify_payment_triggers(self, keyword_lower: str) -> List[str]:
        """识别付费触发因素"""
        triggers = []
        
        trigger_indicators = {
            'time_savings': ['fast', 'quick', 'instant', 'automated'],
            'quality_improvement': ['professional', 'high-quality', 'premium', 'advanced'],
            'feature_access': ['unlimited', 'full-featured', 'complete', 'all-in-one'],
            'support_service': ['support', 'help', 'consultation', 'guidance'],
            'customization': ['custom', 'personalized', 'tailored', 'flexible']
        }
        
        for trigger, indicators in trigger_indicators.items():
            if any(indicator in keyword_lower for indicator in indicators):
                triggers.append(trigger)
        
        return triggers or ['basic_functionality']
    
    def _assess_engagement_level(self, keyword_lower: str) -> str:
        """评估用户参与度"""
        engagement_score = 0
        
        high_engagement_indicators = ['interactive', 'collaborative', 'social', 'sharing']
        medium_engagement_indicators = ['regular', 'frequent', 'daily', 'ongoing']
        
        if any(indicator in keyword_lower for indicator in high_engagement_indicators):
            engagement_score += 2
        if any(indicator in keyword_lower for indicator in medium_engagement_indicators):
            engagement_score += 1
        
        if engagement_score >= 2:
            return 'high'
        elif engagement_score >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_monetization_potential(self, keyword: str) -> Dict[str, any]:
        """深度分析变现潜力"""
        keyword_lower = keyword.lower()
        
        # 推荐的变现模式
        recommended_models = self._identify_monetization_models(keyword)
        
        # 收益潜力评估
        revenue_potential = self._estimate_revenue_potential(keyword_lower)
        
        # 定价策略
        pricing_strategy = self._suggest_pricing_strategy(keyword_lower)
        
        # 变现时间线
        monetization_timeline = self._estimate_monetization_timeline(keyword_lower)
        
        return {
            'recommended_models': recommended_models,
            'revenue_potential': revenue_potential,
            'pricing_strategy': pricing_strategy,
            'monetization_timeline': monetization_timeline,
            'scalability': self._assess_scalability(keyword_lower)
        }
    
    def _estimate_revenue_potential(self, keyword_lower: str) -> Dict[str, any]:
        """估算收益潜力"""
        base_score = 5
        
        # B2B市场通常收益更高
        if any(term in keyword_lower for term in ['business', 'enterprise', 'professional']):
            base_score += 3
        
        # 自动化工具收益潜力高
        if any(term in keyword_lower for term in ['automation', 'api', 'bulk', 'batch']):
            base_score += 2
        
        # 订阅模式友好
        if any(term in keyword_lower for term in ['platform', 'service', 'tool', 'software']):
            base_score += 2
        
        # 免费产品收益较低
        if 'free' in keyword_lower:
            base_score -= 2
        
        potential_score = max(1, min(10, base_score))
        
        # 收益等级分类
        if potential_score >= 8:
            revenue_category = 'high'  # $10k+/month potential
            estimated_range = '$10,000-$100,000+/month'
        elif potential_score >= 6:
            revenue_category = 'medium'  # $1k-$10k/month potential
            estimated_range = '$1,000-$10,000/month'
        else:
            revenue_category = 'low'  # <$1k/month potential
            estimated_range = '$100-$1,000/month'
        
        return {
            'potential_score': potential_score,
            'revenue_category': revenue_category,
            'estimated_range': estimated_range,
            'factors': self._identify_revenue_factors(keyword_lower)
        }
    
    def _identify_revenue_factors(self, keyword_lower: str) -> List[str]:
        """识别影响收益的因素"""
        factors = []
        
        if 'enterprise' in keyword_lower:
            factors.append('high_ticket_sales')
        if 'automation' in keyword_lower:
            factors.append('high_value_proposition')
        if 'api' in keyword_lower:
            factors.append('scalable_usage')
        if 'custom' in keyword_lower:
            factors.append('premium_pricing')
        if 'bulk' in keyword_lower:
            factors.append('volume_based_pricing')
        
        return factors or ['standard_pricing']
    
    def _suggest_pricing_strategy(self, keyword_lower: str) -> Dict[str, any]:
        """建议定价策略"""
        strategy = {
            'model': 'freemium',
            'tiers': [],
            'pricing_factors': []
        }
        
        # 基于关键词特征确定定价模式
        if any(term in keyword_lower for term in ['enterprise', 'business', 'professional']):
            strategy['model'] = 'tiered_subscription'
            strategy['tiers'] = ['basic', 'professional', 'enterprise']
        elif any(term in keyword_lower for term in ['api', 'bulk', 'batch']):
            strategy['model'] = 'usage_based'
            strategy['pricing_factors'] = ['requests_per_month', 'data_volume']
        elif any(term in keyword_lower for term in ['template', 'download', 'pack']):
            strategy['model'] = 'one_time_purchase'
        elif 'free' in keyword_lower:
            strategy['model'] = 'freemium'
            strategy['tiers'] = ['free', 'premium']
        
        return strategy
    
    def _estimate_monetization_timeline(self, keyword_lower: str) -> Dict[str, str]:
        """估算变现时间线"""
        # 基于技术复杂度和市场成熟度估算
        if any(term in keyword_lower for term in ['simple', 'basic', 'converter']):
            return {
                'mvp': '1-2 months',
                'first_revenue': '3-4 months',
                'scaling': '6-12 months'
            }
        elif any(term in keyword_lower for term in ['ai', 'ml', 'advanced']):
            return {
                'mvp': '3-6 months',
                'first_revenue': '6-9 months',
                'scaling': '12-18 months'
            }
        else:
            return {
                'mvp': '2-3 months',
                'first_revenue': '4-6 months',
                'scaling': '9-15 months'
            }
    
    def _assess_scalability(self, keyword_lower: str) -> Dict[str, any]:
        """评估可扩展性"""
        scalability_score = 5
        
        # 高可扩展性指标
        if any(term in keyword_lower for term in ['api', 'automation', 'cloud', 'saas']):
            scalability_score += 3
        
        # 中等可扩展性
        if any(term in keyword_lower for term in ['tool', 'platform', 'service']):
            scalability_score += 2
        
        # 低可扩展性
        if any(term in keyword_lower for term in ['custom', 'manual', 'consultation']):
            scalability_score -= 2
        
        scalability_score = max(1, min(10, scalability_score))
        
        return {
            'score': scalability_score,
            'level': 'high' if scalability_score >= 7 else 'medium' if scalability_score >= 4 else 'low',
            'bottlenecks': self._identify_scalability_bottlenecks(keyword_lower)
        }
    
    def _identify_scalability_bottlenecks(self, keyword_lower: str) -> List[str]:
        """识别可扩展性瓶颈"""
        bottlenecks = []
        
        if 'custom' in keyword_lower:
            bottlenecks.append('customization_overhead')
        if 'manual' in keyword_lower:
            bottlenecks.append('manual_processes')
        if 'support' in keyword_lower:
            bottlenecks.append('customer_support_scaling')
        if 'consultation' in keyword_lower:
            bottlenecks.append('human_dependency')
        
        return bottlenecks or ['none_identified']
    
    def _analyze_technical_requirements(self, keyword: str) -> Dict[str, any]:
        """分析技术需求"""
        keyword_lower = keyword.lower()
        
        # 技术难度评估
        difficulty = self._assess_technical_difficulty(keyword_lower)
        
        # 开发时间估算
        development_time = self._estimate_development_time(keyword_lower)
        
        # 所需技能
        required_skills = self._identify_required_skills(keyword_lower)
        
        # 基础设施需求
        infrastructure_needs = self._assess_infrastructure_needs(keyword_lower)
        
        return {
            'difficulty': difficulty,
            'development_time': development_time,
            'required_skills': required_skills,
            'infrastructure_needs': infrastructure_needs,
            'third_party_dependencies': self._identify_dependencies(keyword_lower)
        }
    
    def _assess_technical_difficulty(self, keyword_lower: str) -> int:
        """评估技术难度 (1-10)"""
        difficulty = 5  # 基础难度
        
        # 高难度指标
        if any(term in keyword_lower for term in ['ai', 'ml', 'neural', 'deep learning']):
            difficulty += 3
        if any(term in keyword_lower for term in ['real-time', 'streaming', 'live']):
            difficulty += 2
        if any(term in keyword_lower for term in ['3d', 'vr', 'ar', 'blockchain']):
            difficulty += 2
        
        # 中等难度
        if any(term in keyword_lower for term in ['api', 'integration', 'automation']):
            difficulty += 1
        
        # 低难度指标
        if any(term in keyword_lower for term in ['converter', 'formatter', 'validator']):
            difficulty -= 1
        if any(term in keyword_lower for term in ['template', 'static', 'simple']):
            difficulty -= 2
        
        return max(1, min(10, difficulty))
    
    def _estimate_development_time(self, keyword_lower: str) -> str:
        """估算开发时间"""
        difficulty = self._assess_technical_difficulty(keyword_lower)
        
        if difficulty >= 8:
            return '6-12 months'
        elif difficulty >= 6:
            return '3-6 months'
        elif difficulty >= 4:
            return '1-3 months'
        else:
            return '2-6 weeks'
    
    def _identify_required_skills(self, keyword_lower: str) -> List[str]:
        """识别所需技能"""
        skills = ['basic_programming']  # 基础技能
        
        skill_mapping = {
            'web_development': ['web', 'html', 'css', 'javascript', 'frontend'],
            'backend_development': ['api', 'server', 'database', 'backend'],
            'ai_ml': ['ai', 'ml', 'machine learning', 'neural', 'deep learning'],
            'data_science': ['data', 'analytics', 'statistics', 'analysis'],
            'mobile_development': ['mobile', 'app', 'ios', 'android'],
            'devops': ['cloud', 'deployment', 'scaling', 'infrastructure'],
            'ui_ux_design': ['design', 'ui', 'ux', 'interface', 'user experience'],
            'security': ['security', 'encryption', 'authentication', 'privacy']
        }
        
        for skill, indicators in skill_mapping.items():
            if any(indicator in keyword_lower for indicator in indicators):
                skills.append(skill)
        
        # 去重并返回列表
        unique_skills = []
        seen = set()
        for skill in skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        return unique_skills
    
    def _assess_infrastructure_needs(self, keyword_lower: str) -> Dict[str, any]:
        """评估基础设施需求"""
        needs = {
            'hosting': 'basic',
            'database': 'simple',
            'storage': 'minimal',
            'compute': 'low',
            'cdn': False
        }
        
        # 高性能需求
        if any(term in keyword_lower for term in ['real-time', 'high-volume', 'streaming']):
            needs['hosting'] = 'high_performance'
            needs['compute'] = 'high'
        
        # AI/ML 需求
        if any(term in keyword_lower for term in ['ai', 'ml', 'neural']):
            needs['compute'] = 'gpu_required'
            needs['hosting'] = 'specialized'
        
        # 大数据需求
        if any(term in keyword_lower for term in ['big data', 'analytics', 'massive']):
            needs['database'] = 'distributed'
            needs['storage'] = 'large_scale'
        
        # CDN 需求
        if any(term in keyword_lower for term in ['global', 'fast', 'worldwide']):
            needs['cdn'] = True
        
        return needs
    
    def _identify_dependencies(self, keyword_lower: str) -> List[str]:
        """识别第三方依赖"""
        dependencies = []
        
        dependency_mapping = {
            'payment_processing': ['payment', 'billing', 'subscription', 'checkout'],
            'ai_apis': ['ai', 'ml', 'gpt', 'openai', 'anthropic'],
            'cloud_services': ['cloud', 'aws', 'azure', 'gcp'],
            'social_apis': ['social', 'facebook', 'twitter', 'instagram'],
            'email_services': ['email', 'notification', 'smtp'],
            'analytics': ['analytics', 'tracking', 'metrics', 'stats'],
            'file_storage': ['file', 'upload', 'storage', 'download'],
            'authentication': ['auth', 'login', 'oauth', 'sso']
        }
        
        for dependency, indicators in dependency_mapping.items():
            if any(indicator in keyword_lower for indicator in indicators):
                dependencies.append(dependency)
        
        return dependencies
    
    def _assess_risks(self, keyword: str) -> Dict[str, any]:
        """评估风险"""
        keyword_lower = keyword.lower()
        
        # 市场风险
        market_risks = self._assess_market_risks(keyword_lower)
        
        # 技术风险
        technical_risks = self._assess_technical_risks(keyword_lower)
        
        # 竞争风险
        competitive_risks = self._assess_competitive_risks(keyword_lower)
        
        # 法律风险
        legal_risks = self._assess_legal_risks(keyword_lower)
        
        return {
            'market_risks': market_risks,
            'technical_risks': technical_risks,
            'competitive_risks': competitive_risks,
            'legal_risks': legal_risks,
            'overall_risk_level': self._calculate_overall_risk(market_risks, technical_risks, competitive_risks, legal_risks),
            'mitigation_strategies': self._suggest_mitigation_strategies(keyword_lower)
        }
    
    def _assess_market_risks(self, keyword_lower: str) -> Dict[str, any]:
        """评估市场风险"""
        risks = []
        risk_level = 'low'
        
        # 市场饱和风险
        if any(term in keyword_lower for term in ['generator', 'maker', 'tool']):
            risks.append('market_saturation')
            risk_level = 'medium'
        
        # 需求不确定性
        if any(term in keyword_lower for term in ['niche', 'specialized', 'specific']):
            risks.append('limited_demand')
        
        # 季节性风险
        if any(term in keyword_lower for term in ['holiday', 'seasonal', 'event']):
            risks.append('seasonal_dependency')
        
        # 趋势变化风险
        if any(term in keyword_lower for term in ['trendy', 'viral', 'popular']):
            risks.append('trend_dependency')
            risk_level = 'medium'
        
        if len(risks) >= 2:
            risk_level = 'high'
        
        return {
            'level': risk_level,
            'identified_risks': risks,
            'probability': self._estimate_risk_probability(risks)
        }
    
    def _assess_technical_risks(self, keyword_lower: str) -> Dict[str, any]:
        """评估技术风险"""
        risks = []
        risk_level = 'low'
        
        # 技术复杂性风险
        if any(term in keyword_lower for term in ['ai', 'ml', 'complex', 'advanced']):
            risks.append('technical_complexity')
            risk_level = 'high'
        
        # 性能风险
        if any(term in keyword_lower for term in ['real-time', 'high-volume', 'massive']):
            risks.append('performance_challenges')
            risk_level = 'medium'
        
        # 依赖风险
        if any(term in keyword_lower for term in ['api', 'third-party', 'integration']):
            risks.append('dependency_risks')
        
        # 可扩展性风险
        if any(term in keyword_lower for term in ['scalable', 'growing', 'expanding']):
            risks.append('scalability_challenges')
        
        return {
            'level': risk_level,
            'identified_risks': risks,
            'impact': 'high' if 'technical_complexity' in risks else 'medium'
        }
    
    def _assess_competitive_risks(self, keyword_lower: str) -> Dict[str, any]:
        """评估竞争风险"""
        risks = []
        risk_level = 'low'
        
        # 大厂进入风险
        if any(term in keyword_lower for term in ['google', 'microsoft', 'openai', 'chatgpt']):
            risks.append('big_tech_competition')
            risk_level = 'high'
        
        # 低进入门槛风险
        if any(term in keyword_lower for term in ['simple', 'basic', 'easy']):
            risks.append('low_entry_barriers')
            risk_level = 'medium'
        
        # 快速复制风险
        if any(term in keyword_lower for term in ['template', 'generator', 'converter']):
            risks.append('easy_to_replicate')
        
        return {
            'level': risk_level,
            'identified_risks': risks,
            'timeframe': 'short_term' if risk_level == 'high' else 'medium_term'
        }
    
    def _assess_legal_risks(self, keyword_lower: str) -> Dict[str, any]:
        """评估法律风险"""
        risks = []
        risk_level = 'low'
        
        # 版权风险
        if any(term in keyword_lower for term in ['content', 'image', 'video', 'music']):
            risks.append('copyright_issues')
            risk_level = 'medium'
        
        # 隐私风险
        if any(term in keyword_lower for term in ['personal', 'user data', 'private']):
            risks.append('privacy_compliance')
        
        # 行业监管风险
        if any(term in keyword_lower for term in ['medical', 'financial', 'legal']):
            risks.append('regulatory_compliance')
            risk_level = 'high'
        
        return {
            'level': risk_level,
            'identified_risks': risks,
            'compliance_required': len(risks) > 0
        }
    
    def _calculate_overall_risk(self, market_risks, technical_risks, competitive_risks, legal_risks) -> str:
        """计算总体风险等级"""
        risk_scores = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        total_score = (
            risk_scores[market_risks['level']] +
            risk_scores[technical_risks['level']] +
            risk_scores[competitive_risks['level']] +
            risk_scores[legal_risks['level']]
        )
        
        avg_score = total_score / 4
        
        if avg_score >= 2.5:
            return 'high'
        elif avg_score >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_risk_probability(self, risks: List[str]) -> str:
        """估算风险发生概率"""
        if len(risks) >= 3:
            return 'high'
        elif len(risks) >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_mitigation_strategies(self, keyword_lower: str) -> List[str]:
        """建议风险缓解策略"""
        strategies = []
        
        if any(term in keyword_lower for term in ['competitive', 'saturated']):
            strategies.append('focus_on_differentiation')
        
        if any(term in keyword_lower for term in ['technical', 'complex']):
            strategies.append('phased_development_approach')
        
        if any(term in keyword_lower for term in ['market', 'demand']):
            strategies.append('thorough_market_validation')
        
        if any(term in keyword_lower for term in ['legal', 'compliance']):
            strategies.append('early_legal_consultation')
        
        return strategies or ['continuous_monitoring']
    
    def _analyze_opportunity_window(self, keyword: str) -> Dict[str, any]:
        """分析机会窗口"""
        keyword_lower = keyword.lower()
        
        # 紧急程度评估
        urgency = self._assess_urgency(keyword_lower)
        
        # 最佳时机分析
        optimal_timing = self._analyze_optimal_timing(keyword_lower)
        
        # 市场准备度
        market_readiness = self._assess_market_readiness(keyword_lower)
        
        return {
            'urgency': urgency,
            'optimal_timing': optimal_timing,
            'market_readiness': market_readiness,
            'window_duration': self._estimate_window_duration(urgency, market_readiness)
        }
    
    def _assess_urgency(self, keyword_lower: str) -> str:
        """评估紧急程度"""
        # 高紧急性指标
        if any(term in keyword_lower for term in ['trending', 'viral', 'hot', 'emerging']):
            return 'high'
        
        # 中等紧急性
        if any(term in keyword_lower for term in ['growing', 'popular', 'increasing']):
            return 'medium'
        
        # 低紧急性
        return 'low'
    
    def _analyze_optimal_timing(self, keyword_lower: str) -> str:
        """分析最佳时机"""
        # 基于关键词特征判断时机
        if any(term in keyword_lower for term in ['new', 'latest', 'cutting-edge']):
            return 'immediate'  # 立即行动
        elif any(term in keyword_lower for term in ['mature', 'established', 'standard']):
            return 'strategic'  # 战略时机
        else:
            return 'flexible'  # 灵活时机
    
    def _assess_market_readiness(self, keyword_lower: str) -> int:
        """评估市场准备度 (1-10)"""
        readiness = 5  # 基础分数
        
        # 提高准备度的因素
        if any(term in keyword_lower for term in ['popular', 'mainstream', 'adopted']):
            readiness += 2
        
        if any(term in keyword_lower for term in ['simple', 'easy', 'user-friendly']):
            readiness += 1
        
        # 降低准备度的因素
        if any(term in keyword_lower for term in ['complex', 'advanced', 'cutting-edge']):
            readiness -= 2
        
        if any(term in keyword_lower for term in ['niche', 'specialized', 'expert']):
            readiness -= 1
        
        return max(1, min(10, readiness))
    
    def _estimate_window_duration(self, urgency: str, market_readiness: int) -> str:
        """估算机会窗口持续时间"""
        if urgency == 'high' and market_readiness >= 7:
            return '3-6 months'
        elif urgency == 'high':
            return '6-12 months'
        elif urgency == 'medium':
            return '12-24 months'
        else:
            return '24+ months'

    def _generate_business_opportunities(self, insights: Dict) -> List[Dict]:
        """生成商业机会建议"""
        opportunities = []
        
        # 基于高价值关键词生成机会 - 优化版
        for opportunity in insights.get('high_value_opportunities', [])[:10]:
            opportunities.append({
                'title': f"开发{opportunity.keyword}相关工具",
                'category': opportunity.category,
                'overall_business_value': opportunity.overall_business_value,
                'competition_analysis': opportunity.competition_analysis,
                'suggested_models': opportunity.monetization_analysis['recommended_models'],
                'priority': 'high' if opportunity.overall_business_value >= 8 else 'medium'
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
                'action': f"启动{win.keyword}项目",
                'reason': '低竞争、高价值机会',
                'timeline': '1-3个月'
            })
        
        # 中期策略
        top_categories = sorted(new_insights.get('market_trends', {}).items(), 
                               key=lambda x: x[1].get('keywords_count', 0), reverse=True)[:3]
        for category, info in top_categories:
            if not category.startswith('_'):  # 排除元数据字段
                recommendations['medium_term_strategy'].append({
                    'strategy': f"布局{category}领域",
                    'keywords_count': info.get('keywords_count', 0),
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
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 4px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        
        .metric-chip {{
            display: inline-block;
            padding: 4px 8px;
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            font-size: 0.75rem;
            margin: 2px;
            color: #4c1d95;
        }}
        
        .priority-high {{
            border-left: 4px solid #dc2626;
            background: linear-gradient(135deg, #fef2f2, #fee2e2);
        }}
        
        .priority-medium {{
            border-left: 4px solid #d97706;
            background: linear-gradient(135deg, #fffbeb, #fef3c7);
        }}
        
        .priority-low {{
            border-left: 4px solid #65a30d;
            background: linear-gradient(135deg, #f7fee7, #ecfccb);
        }}
        
        .insight-box {{
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            border: 1px solid #0ea5e9;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
        }}
        
        .prediction-box {{
            background: linear-gradient(135deg, #ecfdf5, #d1fae5);
            border: 1px solid #10b981;
            border-radius: 12px;
            padding: 12px;
            margin: 8px 0;
            font-size: 0.9em;
        }}
        
        .chart-container {{
            margin: 20px 0;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
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
                    <strong>商业价值:</strong> {opp.get('overall_business_value', opp.get('business_value', 'N/A'))}/10<br>
                    <strong>竞争程度:</strong> <span class="badge badge-{opp.get('competition_analysis', {}).get('level', opp.get('competition_level', 'unknown'))}">{opp.get('competition_analysis', {}).get('level', opp.get('competition_level', 'unknown'))}</span><br>
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
            status = info.get('status', '未知')
            status_class = "trend-up" if status in ['爆发式增长', '强劲增长', '快速增长', '稳定增长'] else "trend-down"
            trends_html += f'<div class="category-item"><span class="category-name">{category}</span><span class="trend-indicator {status_class}">{status}</span></div>'
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