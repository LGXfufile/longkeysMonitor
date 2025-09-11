#!/usr/bin/env python3
"""
Enhanced HTML Report Generator
增强版HTML报告生成器

生成专业的商机挖掘分析HTML报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EnhancedHTMLReportGenerator:
    """增强版HTML报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.logger = logging.getLogger(__name__)
        
    def generate_html_report(self, analysis_data: Dict, output_path: str) -> str:
        """
        生成完整的HTML分析报告
        
        Args:
            analysis_data: 分析数据
            output_path: 输出文件路径
            
        Returns:
            str: 生成的HTML文件路径
        """
        try:
            # 构建HTML内容
            html_content = self._build_html_structure(analysis_data)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML报告已生成: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"生成HTML报告失败: {e}")
            raise
    
    def _build_html_structure(self, data: Dict) -> str:
        """构建HTML结构"""
        metadata = data.get('metadata', {})
        drift_analysis = data.get('semantic_drift_analysis', {})
        business_opportunities = data.get('enhanced_business_opportunities', {})
        quality_assessment = data.get('data_quality_assessment', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>商机挖掘分析报告 - {metadata.get('main_keyword', 'Unknown')}</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        {self._build_header(metadata)}
        {self._build_executive_summary(quality_assessment, drift_analysis)}
        {self._build_data_quality_section(quality_assessment)}
        {self._build_semantic_drift_analysis(drift_analysis)}
        {self._build_business_opportunities(business_opportunities)}
        {self._build_market_trends(data)}
        {self._build_strategic_recommendations(data)}
        {self._build_appendix(drift_analysis)}
        {self._build_footer()}
    </div>
    {self._get_javascript()}
</body>
</html>"""
        return html
    
    def _get_css_styles(self) -> str:
        """获取CSS样式"""
        return """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
        line-height: 1.6;
        color: #2c3e50;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-radius: 12px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    .header {
        text-align: center;
        padding: 40px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 30px;
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .header .subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .section {
        margin-bottom: 40px;
        padding: 25px;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-title .icon {
        font-size: 1.5rem;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e9ecef;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    .quality-indicator {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin: 5px;
    }
    
    .quality-excellent { background: #d4edda; color: #155724; }
    .quality-good { background: #d1ecf1; color: #0c5460; }
    .quality-average { background: #fff3cd; color: #856404; }
    .quality-poor { background: #f8d7da; color: #721c24; }
    
    .drift-pattern {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .drift-pattern:hover {
        background: #e9ecef;
        transform: translateX(5px);
    }
    
    .pattern-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .pattern-verb {
        font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
        background: #667eea;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    
    .pattern-frequency {
        background: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    
    .pattern-examples {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 8px;
    }
    
    .opportunity-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border: 1px solid #feb2b2;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        position: relative;
        overflow: hidden;
    }
    
    .opportunity-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .opportunity-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 10px;
    }
    
    .opportunity-desc {
        color: #4a5568;
        margin-bottom: 15px;
    }
    
    .keyword-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
    }
    
    .keyword-tag {
        background: #667eea;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .recommendation-list {
        list-style: none;
        padding: 0;
    }
    
    .recommendation-list li {
        background: #f8f9fa;
        margin: 10px 0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        position: relative;
    }
    
    .recommendation-list li::before {
        content: '✓';
        position: absolute;
        left: -12px;
        top: 15px;
        background: #28a745;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .chart-container {
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .progress-bar {
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
        margin: 10px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .footer {
        text-align: center;
        padding: 30px;
        background: #f8f9fa;
        border-radius: 8px;
        margin-top: 40px;
        color: #6c757d;
    }
    
    .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 20px 0;
    }
    
    .tag {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        transition: transform 0.2s ease;
    }
    
    .tag:hover {
        transform: scale(1.05);
    }
    
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
        margin: 30px 0;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .summary-card h3 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.2rem;
    }
    
    @media (max-width: 768px) {
        .container {
            margin: 10px;
            padding: 15px;
        }
        
        .header h1 {
            font-size: 2rem;
        }
        
        .metric-grid {
            grid-template-columns: 1fr;
        }
        
        .summary-grid {
            grid-template-columns: 1fr;
        }
    }
</style>"""
    
    def _build_header(self, metadata: Dict) -> str:
        """构建页面头部"""
        main_keyword = metadata.get('main_keyword', 'Unknown')
        analysis_time = metadata.get('analysis_time', datetime.now().isoformat())
        
        try:
            formatted_time = datetime.fromisoformat(analysis_time.replace('Z', '+00:00')).strftime('%Y年%m月%d日 %H:%M')
        except:
            formatted_time = analysis_time
        
        return f"""
<div class="header">
    <h1>🚀 商机挖掘分析报告</h1>
    <div class="subtitle">
        关键词: <strong>{main_keyword}</strong> | 
        分析时间: {formatted_time} |
        智能语义漂移检测
    </div>
</div>"""
    
    def _build_executive_summary(self, quality_assessment: Dict, drift_analysis: Dict) -> str:
        """构建执行摘要"""
        stats = drift_analysis.get('value_statistics', {})
        
        return f"""
<div class="section">
    <h2 class="section-title">
        <span class="icon">📊</span>
        执行摘要
    </h2>
    
    <div class="summary-grid">
        <div class="summary-card">
            <h3>🎯 核心发现</h3>
            <p>本次分析发现 <strong>{stats.get('total_keywords', 0):,}</strong> 个新增关键词，其中 <strong>{stats.get('high_value', {}).get('count', 0)}</strong> 个具有高商业价值，质量得分为 <strong>{quality_assessment.get('quality_score', 0):.1f}分</strong>。</p>
            <div class="quality-indicator quality-{self._get_quality_class(quality_assessment.get('data_health', ''))}">
                数据健康度: {quality_assessment.get('data_health', 'unknown')}
            </div>
        </div>
        
        <div class="summary-card">
            <h3>💡 商业机会</h3>
            <p>识别出多个高价值的语义漂移模式，特别是用户对AI平台访问和技能学习的强烈需求，为相关产品和服务提供了明确的市场方向。</p>
        </div>
        
        <div class="summary-card">
            <h3>⚡ 立即行动</h3>
            <p>建议优先关注AI平台准入教育市场，同时实施智能过滤机制减少数据噪音，提高分析精度。</p>
        </div>
    </div>
</div>"""
    
    def _build_data_quality_section(self, quality_assessment: Dict) -> str:
        """构建数据质量分析部分"""
        return f"""
<div class="section">
    <h2 class="section-title">
        <span class="icon">🔍</span>
        数据质量分析
    </h2>
    
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-value">{quality_assessment.get('actionable_insights', 0)}</div>
            <div class="metric-label">高价值关键词</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{quality_assessment.get('filtered_noise', 0)}</div>
            <div class="metric-label">过滤噪音</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{quality_assessment.get('signal_to_noise_ratio', 0):.1f}:1</div>
            <div class="metric-label">信噪比</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{quality_assessment.get('quality_score', 0):.1f}%</div>
            <div class="metric-label">质量得分</div>
        </div>
    </div>
    
    <div class="chart-container">
        <h3>数据分布概览</h3>
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>高价值</span>
                <span>{quality_assessment.get('high_value_percentage', 0):.1f}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {quality_assessment.get('high_value_percentage', 0)}%">
                    {quality_assessment.get('high_value_percentage', 0):.1f}%
                </div>
            </div>
        </div>
        
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>噪音</span>
                <span>{quality_assessment.get('noise_percentage', 0):.1f}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {quality_assessment.get('noise_percentage', 0)}%; background: #dc3545;">
                    {quality_assessment.get('noise_percentage', 0):.1f}%
                </div>
            </div>
        </div>
    </div>
</div>"""
    
    def _build_semantic_drift_analysis(self, drift_analysis: Dict) -> str:
        """构建语义漂移分析部分"""
        patterns = drift_analysis.get('drift_patterns', [])
        
        patterns_html = ""
        for pattern in patterns[:10]:  # 显示前10个模式
            examples = pattern.get('examples', [])[:3]
            examples_text = " | ".join(examples)
            
            patterns_html += f"""
            <div class="drift-pattern">
                <div class="pattern-header">
                    <div>
                        <span class="pattern-verb">{pattern.get('original_verb', '')} → {pattern.get('new_verb', '')}</span>
                        <span style="margin-left: 10px; color: #6c757d;">价值等级: {pattern.get('value_level', 'unknown')}</span>
                    </div>
                    <span class="pattern-frequency">出现 {pattern.get('frequency', 0)} 次</span>
                </div>
                <div style="margin: 10px 0;">
                    <strong>上下文:</strong> {pattern.get('context_category', 'general')}
                </div>
                <div class="pattern-examples">
                    <strong>示例:</strong> {examples_text}
                </div>
            </div>"""
        
        return f"""
<div class="section">
    <h2 class="section-title">
        <span class="icon">🔄</span>
        语义漂移分析
    </h2>
    
    <p>语义漂移检测识别出用户搜索行为中的动词变化模式，这些变化揭示了用户需求的演进和新兴市场机会。</p>
    
    <h3 style="margin: 25px 0 15px 0; color: #2c3e50;">🎯 关键漂移模式</h3>
    {patterns_html}
</div>"""
    
    def _build_business_opportunities(self, opportunities: Dict) -> str:
        """构建商业机会分析部分"""
        opportunities_html = ""
        
        # AI平台访问机会
        platform_opps = opportunities.get('ai_platform_access_opportunities', [])
        if platform_opps:
            opportunities_html += """
            <div class="opportunity-card">
                <div class="opportunity-title">🚪 AI平台访问市场机会</div>
                <div class="opportunity-desc">
                    用户在寻找各种AI平台的访问方法，表明存在平台导航、教育内容和技术支持的巨大需求。
                </div>"""
            
            for opp in platform_opps[:3]:
                examples = opp.get('examples', [])[:3]
                opportunities_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.8); border-radius: 6px;">
                    <strong>模式:</strong> {opp.get('pattern', '')} (频次: {opp.get('frequency', 0)})
                    <div class="keyword-list">
                        {' '.join([f'<span class="keyword-tag">{ex}</span>' for ex in examples])}
                    </div>
                </div>"""
            
            opportunities_html += "</div>"
        
        # AI工具使用机会
        tool_opps = opportunities.get('emerging_ai_tools_opportunities', [])
        if tool_opps:
            opportunities_html += """
            <div class="opportunity-card">
                <div class="opportunity-title">🛠️ 新兴AI工具市场机会</div>
                <div class="opportunity-desc">
                    用户对AI工具的创作和生成能力有强烈需求，SaaS产品和API服务存在巨大市场空间。
                </div>"""
            
            for opp in tool_opps[:3]:
                examples = opp.get('examples', [])[:3]
                opportunities_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.8); border-radius: 6px;">
                    <strong>模式:</strong> {opp.get('pattern', '')} (频次: {opp.get('frequency', 0)})
                    <div class="keyword-list">
                        {' '.join([f'<span class="keyword-tag">{ex}</span>' for ex in examples])}
                    </div>
                </div>"""
            
            opportunities_html += "</div>"
        
        # 学习市场机会
        learning_opps = opportunities.get('ai_learning_market_opportunities', [])
        if learning_opps:
            opportunities_html += """
            <div class="opportunity-card">
                <div class="opportunity-title">📚 AI技能学习市场机会</div>
                <div class="opportunity-desc">
                    在线教育和技能培训需求旺盛，课程开发和培训服务具有很大潜力。
                </div>"""
            
            for opp in learning_opps[:3]:
                examples = opp.get('examples', [])[:3]
                opportunities_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.8); border-radius: 6px;">
                    <strong>模式:</strong> {opp.get('pattern', '')} (频次: {opp.get('frequency', 0)})
                    <div class="keyword-list">
                        {' '.join([f'<span class="keyword-tag">{ex}</span>' for ex in examples])}
                    </div>
                </div>"""
            
            opportunities_html += "</div>"
        
        if not opportunities_html:
            opportunities_html = "<p>暂未发现显著的商业机会模式。</p>"
        
        return f"""
<div class="section">
    <h2 class="section-title">
        <span class="icon">💡</span>
        商业机会分析
    </h2>
    
    <p>基于语义漂移分析，我们识别出以下具有商业价值的市场机会：</p>
    
    {opportunities_html}
</div>"""
    
    def _build_market_trends(self, data: Dict) -> str:
        """构建市场趋势分析"""
        return """
<div class="section">
    <h2 class="section-title">
        <span class="icon">📈</span>
        市场趋势洞察
    </h2>
    
    <div class="summary-grid">
        <div class="summary-card">
            <h3>🔥 热门趋势</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 8px 0;">📱 移动端AI工具需求增长</li>
                <li style="margin: 8px 0;">🎯 平台整合与一站式服务</li>
                <li style="margin: 8px 0;">🎓 AI技能教育市场爆发</li>
                <li style="margin: 8px 0;">🔗 API集成和自动化需求</li>
            </ul>
        </div>
        
        <div class="summary-card">
            <h3>⚠️ 风险提示</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 8px 0;">🚫 硬件相关搜索干扰严重</li>
                <li style="margin: 8px 0;">📉 部分传统工具热度下降</li>
                <li style="margin: 8px 0;">🔄 用户需求变化速度加快</li>
                <li style="margin: 8px 0;">💸 免费工具竞争激烈</li>
            </ul>
        </div>
        
        <div class="summary-card">
            <h3>🎯 目标用户</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 8px 0;">👨‍💻 开发者和技术人员</li>
                <li style="margin: 8px 0;">🎨 创意工作者和设计师</li>
                <li style="margin: 8px 0;">📊 商业分析师和营销人员</li>
                <li style="margin: 8px 0;">🎓 学生和自学者</li>
            </ul>
        </div>
    </div>
</div>"""
    
    def _build_strategic_recommendations(self, data: Dict) -> str:
        """构建战略建议"""
        return """
<div class="section">
    <h2 class="section-title">
        <span class="icon">🎯</span>
        战略建议
    </h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
        <div>
            <h3 style="color: #28a745; margin-bottom: 15px;">✅ 立即行动</h3>
            <ul class="recommendation-list">
                <li>开发AI平台导航和比较工具</li>
                <li>创建AI技能学习课程和认证体系</li>
                <li>实施智能过滤系统减少数据噪音</li>
                <li>建立用户需求变化监控机制</li>
            </ul>
        </div>
        
        <div>
            <h3 style="color: #667eea; margin-bottom: 15px;">🚀 中长期规划</h3>
            <ul class="recommendation-list">
                <li>构建AI工具生态系统和API市场</li>
                <li>开发智能化的个人AI助手</li>
                <li>创建行业垂直的AI解决方案</li>
                <li>建立AI技术社区和知识库</li>
            </ul>
        </div>
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #ffc107;">
        <h3 style="color: #856404; margin-bottom: 10px;">⚡ 关键成功因素</h3>
        <p style="margin-bottom: 15px;">基于数据分析，以下因素对商业成功至关重要：</p>
        <div class="tag-cloud">
            <span class="tag">用户体验优先</span>
            <span class="tag">数据驱动决策</span>
            <span class="tag">快速迭代优化</span>
            <span class="tag">社区生态建设</span>
            <span class="tag">技术创新领先</span>
            <span class="tag">教育内容质量</span>
        </div>
    </div>
</div>"""
    
    def _build_appendix(self, drift_analysis: Dict) -> str:
        """构建附录"""
        filter_rules = drift_analysis.get('recommendations', {}).get('filter_rules', [])
        
        filter_rules_html = ""
        for rule in filter_rules[:5]:
            examples = rule.get('examples', [])[:3]
            filter_rules_html += f"""
            <li style="margin: 10px 0; padding: 10px; background: #fff5f5; border-radius: 6px;">
                <strong>规则:</strong> {rule.get('rule', '')}<br>
                <strong>原因:</strong> {rule.get('reason', '')}<br>
                <strong>示例:</strong> {' | '.join(examples)}
            </li>"""
        
        return f"""
<div class="section">
    <h2 class="section-title">
        <span class="icon">📋</span>
        技术附录
    </h2>
    
    <h3 style="margin: 20px 0 10px 0;">🛡️ 推荐过滤规则</h3>
    <ul style="list-style: none; padding: 0;">
        {filter_rules_html}
    </ul>
    
    <h3 style="margin: 20px 0 10px 0;">📊 分析方法说明</h3>
    <p>本报告采用先进的语义漂移检测技术，结合AI相关性评分算法，对关键词变化进行多维度分析：</p>
    <ul style="margin: 10px 0; padding-left: 20px;">
        <li>动词漂移模式识别</li>
        <li>语义相关性评估 (0-1.0分制)</li>
        <li>噪音检测和过滤</li>
        <li>商业价值评分计算</li>
        <li>市场机会挖掘</li>
    </ul>
</div>"""
    
    def _build_footer(self) -> str:
        """构建页面底部"""
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        return f"""
<div class="footer">
    <p>
        🤖 本报告由智能语义分析系统自动生成<br>
        生成时间: {current_time}<br>
        <strong>Claude Code 商机挖掘分析系统 v2.0</strong>
    </p>
</div>"""
    
    def _get_javascript(self) -> str:
        """获取JavaScript代码"""
        return """
<script>
    // 添加交互效果
    document.addEventListener('DOMContentLoaded', function() {
        // 为卡片添加点击效果
        const cards = document.querySelectorAll('.metric-card, .opportunity-card, .drift-pattern');
        cards.forEach(card => {
            card.addEventListener('click', function() {
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 100);
            });
        });
        
        // 添加滚动动画
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        });
        
        const sections = document.querySelectorAll('.section');
        sections.forEach(section => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(20px)';
            section.style.transition = 'all 0.6s ease';
            observer.observe(section);
        });
    });
</script>"""
    
    def _get_quality_class(self, quality: str) -> str:
        """获取质量等级的CSS类名"""
        quality_map = {
            '优秀': 'excellent',
            '良好': 'good', 
            '一般': 'average',
            '需要改进': 'poor'
        }
        return quality_map.get(quality, 'average')


def generate_html_from_json(json_file_path: str, output_dir: str = "reports") -> str:
    """
    从JSON文件生成HTML报告
    
    Args:
        json_file_path: JSON文件路径
        output_dir: 输出目录
        
    Returns:
        str: 生成的HTML文件路径
    """
    try:
        # 读取JSON数据
        with open(json_file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # 生成输出文件名
        input_path = Path(json_file_path)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        html_filename = input_path.stem.replace('enhanced_business_analysis_', 'business_report_') + '.html'
        html_file_path = output_path / html_filename
        
        # 生成HTML报告
        generator = EnhancedHTMLReportGenerator()
        result_path = generator.generate_html_report(analysis_data, str(html_file_path))
        
        return result_path
        
    except Exception as e:
        logger.error(f"生成HTML报告失败: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='生成HTML商机分析报告')
    parser.add_argument('json_file', help='JSON分析数据文件路径')
    parser.add_argument('-o', '--output', help='输出目录', default='reports')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    try:
        html_file = generate_html_from_json(args.json_file, args.output)
        print(f"🎉 HTML报告生成成功!")
        print(f"📊 文件路径: {html_file}")
        print(f"🌐 请在浏览器中打开查看详细报告")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        exit(1)