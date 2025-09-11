#!/usr/bin/env python3
"""
Semantic Drift Analyzer
语义漂移分析器

专门分析关键词中的动词漂移现象，识别有价值的语义变化和噪音干扰
"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DriftPattern:
    """漂移模式数据结构"""
    original_verb: str
    new_verb: str
    frequency: int
    relevance_score: float
    value_level: str  # 'high', 'medium', 'low', 'noise'
    examples: List[str]
    context_category: str
    

@dataclass
class SemanticAnalysis:
    """语义分析结果"""
    keyword: str
    extracted_verbs: List[str]
    ai_relevance_score: float
    value_classification: str
    reasoning: str
    recommended_action: str


class SemanticDriftAnalyzer:
    """语义漂移分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.logger = logging.getLogger(__name__)
        
        # 核心动词词典
        self.core_verbs = {
            'use': {'weight': 1.0, 'context': 'usage'},
            'create': {'weight': 0.9, 'context': 'generation'},
            'generate': {'weight': 0.9, 'context': 'generation'},
            'build': {'weight': 0.8, 'context': 'construction'},
            'make': {'weight': 0.8, 'context': 'creation'}
        }
        
        # AI相关性评估词典
        self.ai_context_indicators = {
            'high_relevance': {
                'ai_core': ['ai', 'artificial intelligence', 'machine learning', 'neural', 'llm', 'gpt'],
                'ai_platforms': ['chatgpt', 'claude', 'openai', 'anthropic', 'midjourney', 'stable diffusion', 'copilot'],
                'ai_actions': ['prompt', 'fine-tune', 'train', 'inference', 'embed', 'tokenize', 'generate', 'create'],
                'ai_tools': ['ai tool', 'ai app', 'ai platform', 'ai service', 'ai api', 'ai model']
            },
            'medium_relevance': {
                'tech_ai': ['automation', 'smart', 'intelligent', 'algorithm', 'model', 'dataset'],
                'ai_access': ['access ai', 'use ai', 'learn ai', 'ai tutorial', 'ai guide', 'ai course'],
                'programming_ai': ['tensorflow', 'pytorch', 'huggingface', 'api', 'sdk', 'json']
            },
            'context_bonus': {
                'how_to_ai': ['how to use ai', 'how to access ai', 'how to learn ai', 'how i use ai'],
                'ai_learning': ['learn ai', 'ai tutorial', 'ai guide', 'ai training', 'ai course']
            }
        }
        
        # 噪音识别模式
        self.noise_patterns = {
            'hardware_devices': [
                'airpods', 'earbuds', 'headphones', 'speaker', 'tablet', 'phone',
                'iphone', 'android', 'macbook', 'laptop', 'computer'
            ],
            'physical_products': [
                'air fryer', 'air cooler', 'air conditioner', 'dyson', 'vacuum',
                'camera', 'tv', 'monitor', 'printer'
            ],
            'languages': [
                'chinese', 'english', 'spanish', 'french', 'german', 'japanese',
                'korean', 'russian', 'arabic', 'hindi', 'kazakhstan', 'lao'
            ],
            'non_ai_software': [
                'instagram', 'facebook', 'tiktok', 'spotify', 'netflix', 'youtube',
                'whatsapp', 'telegram', 'discord', 'zoom'
            ],
            'gaming': [
                'minecraft', 'fortnite', 'pubg', 'roblox', 'steam', 'epic games',
                'playstation', 'xbox', 'nintendo'
            ],
            'unrelated_domains': [
                'cooking', 'recipe', 'fitness', 'workout', 'diet', 'health',
                'travel', 'hotel', 'flight', 'car', 'driving'
            ]
        }
        
        # 价值等级权重
        self.value_weights = {
            'ai_platform_access': 0.9,
            'ai_skill_learning': 0.8,
            'ai_tool_usage': 0.7,
            'tech_integration': 0.5,
            'general_tech': 0.3,
            'unrelated': 0.1
        }
    
    def analyze_semantic_drift(self, changes_data: Dict) -> Dict:
        """
        分析语义漂移
        
        Args:
            changes_data: 关键词变化数据
            
        Returns:
            Dict: 漂移分析结果
        """
        main_keyword = changes_data.get('metadata', {}).get('main_keyword', '')
        new_keywords = changes_data.get('changes', {}).get('new_keywords', [])
        
        self.logger.info(f"开始分析语义漂移: {main_keyword}")
        
        # 提取原始动词
        original_verbs = self._extract_verbs_from_keyword(main_keyword)
        
        # 分析每个新关键词
        semantic_analyses = []
        for keyword in new_keywords:
            analysis = self._analyze_single_keyword(keyword, original_verbs)
            semantic_analyses.append(analysis)
        
        # 生成漂移模式
        drift_patterns = self._identify_drift_patterns(semantic_analyses, original_verbs)
        
        # 价值分类统计
        value_statistics = self._calculate_value_statistics(semantic_analyses)
        
        # 生成建议
        recommendations = self._generate_recommendations(drift_patterns, value_statistics)
        
        return {
            'metadata': {
                'main_keyword': main_keyword,
                'analysis_timestamp': changes_data.get('metadata', {}).get('analysis_time'),
                'total_new_keywords': len(new_keywords),
                'original_verbs': original_verbs
            },
            'semantic_analyses': [analysis.__dict__ for analysis in semantic_analyses],
            'drift_patterns': [pattern.__dict__ for pattern in drift_patterns],
            'value_statistics': value_statistics,
            'recommendations': recommendations,
            'filtered_keywords': {
                'high_value': [a.keyword for a in semantic_analyses if a.value_classification == 'high'],
                'medium_value': [a.keyword for a in semantic_analyses if a.value_classification == 'medium'],
                'low_value': [a.keyword for a in semantic_analyses if a.value_classification == 'low'],
                'noise': [a.keyword for a in semantic_analyses if a.value_classification == 'noise']
            }
        }
    
    def _extract_verbs_from_keyword(self, keyword: str) -> List[str]:
        """从关键词中提取动词"""
        keyword_lower = keyword.lower()
        
        # 常见的How to模式动词提取
        verbs = []
        
        # 直接匹配已知动词
        for verb in self.core_verbs.keys():
            if verb in keyword_lower:
                verbs.append(verb)
        
        # 使用正则表达式提取How to [verb]模式
        how_to_pattern = r'how to (\w+)'
        matches = re.findall(how_to_pattern, keyword_lower)
        verbs.extend(matches)
        
        return list(set(verbs))
    
    def _analyze_single_keyword(self, keyword: str, original_verbs: List[str]) -> SemanticAnalysis:
        """分析单个关键词的语义"""
        keyword_lower = keyword.lower()
        
        # 提取新关键词中的动词
        new_verbs = self._extract_verbs_from_keyword(keyword)
        
        # 计算AI相关性得分
        ai_relevance_score = self._calculate_ai_relevance(keyword_lower)
        
        # 检测噪音
        is_noise = self._is_noise_keyword(keyword_lower)
        
        # 价值分类
        if is_noise:
            value_classification = 'noise'
            reasoning = self._explain_noise_classification(keyword_lower)
            recommended_action = 'filter_out'
        elif ai_relevance_score >= 0.7:
            value_classification = 'high'
            reasoning = f"高AI相关性 (得分: {ai_relevance_score:.2f})"
            recommended_action = 'track_separately'
        elif ai_relevance_score >= 0.4:
            value_classification = 'medium'
            reasoning = f"中等AI相关性 (得分: {ai_relevance_score:.2f})"
            recommended_action = 'monitor'
        else:
            value_classification = 'low'
            reasoning = f"低AI相关性 (得分: {ai_relevance_score:.2f})"
            recommended_action = 'consider_filtering'
        
        return SemanticAnalysis(
            keyword=keyword,
            extracted_verbs=new_verbs,
            ai_relevance_score=ai_relevance_score,
            value_classification=value_classification,
            reasoning=reasoning,
            recommended_action=recommended_action
        )
    
    def _calculate_ai_relevance(self, keyword_lower: str) -> float:
        """计算AI相关性得分 - 优化版"""
        score = 0.0
        
        # 基础AI关键词检测 - 最重要
        if ' ai ' in keyword_lower or keyword_lower.startswith('ai ') or keyword_lower.endswith(' ai'):
            score += 0.6  # AI核心词汇基础分数
        
        # 上下文奖励 - 对于特定AI使用模式给额外分数
        for category, indicators in self.ai_context_indicators.get('context_bonus', {}).items():
            for indicator in indicators:
                if indicator in keyword_lower:
                    score += 0.3
                    break
        
        # 高相关性指标
        for category, indicators in self.ai_context_indicators['high_relevance'].items():
            for indicator in indicators:
                if indicator in keyword_lower:
                    if category == 'ai_core':
                        score += 0.4
                    elif category == 'ai_platforms':
                        score += 0.5  # AI平台特别重要
                    else:
                        score += 0.3
                    break
        
        # 中等相关性指标
        for category, indicators in self.ai_context_indicators['medium_relevance'].items():
            for indicator in indicators:
                if indicator in keyword_lower:
                    score += 0.2
                    break
        
        # 特殊处理：明确的AI访问、学习相关
        ai_action_patterns = [
            'access.*ai', 'learn.*ai', 'use.*ai', 'how.*ai', 'ai.*tutorial',
            'ai.*guide', 'ai.*course', 'ai.*training'
        ]
        
        import re
        for pattern in ai_action_patterns:
            if re.search(pattern, keyword_lower):
                score += 0.3
                break
        
        return min(1.0, score)  # 确保不超过1.0
    
    def _is_noise_keyword(self, keyword_lower: str) -> bool:
        """检测是否为噪音关键词"""
        for category, patterns in self.noise_patterns.items():
            for pattern in patterns:
                if pattern in keyword_lower:
                    return True
        return False
    
    def _explain_noise_classification(self, keyword_lower: str) -> str:
        """解释噪音分类原因"""
        for category, patterns in self.noise_patterns.items():
            for pattern in patterns:
                if pattern in keyword_lower:
                    category_names = {
                        'hardware_devices': '硬件设备相关',
                        'physical_products': '物理产品相关',
                        'languages': '语言学习相关',
                        'non_ai_software': '非AI软件相关',
                        'gaming': '游戏相关',
                        'unrelated_domains': '无关领域'
                    }
                    return f"属于{category_names.get(category, category)}，与AI使用无关"
        return "未知噪音类型"
    
    def _identify_drift_patterns(self, analyses: List[SemanticAnalysis], original_verbs: List[str]) -> List[DriftPattern]:
        """识别漂移模式"""
        patterns = []
        verb_changes = defaultdict(list)
        
        # 收集动词变化
        for analysis in analyses:
            for new_verb in analysis.extracted_verbs:
                if new_verb not in original_verbs:
                    for orig_verb in original_verbs:
                        verb_changes[(orig_verb, new_verb)].append(analysis)
        
        # 生成漂移模式
        for (orig_verb, new_verb), related_analyses in verb_changes.items():
            if len(related_analyses) >= 2:  # 至少出现2次才认为是模式
                # 计算平均相关性得分
                avg_relevance = sum(a.ai_relevance_score for a in related_analyses) / len(related_analyses)
                
                # 确定价值等级
                value_counts = Counter(a.value_classification for a in related_analyses)
                dominant_value = value_counts.most_common(1)[0][0]
                
                # 确定上下文分类
                context_category = self._determine_context_category(related_analyses)
                
                pattern = DriftPattern(
                    original_verb=orig_verb,
                    new_verb=new_verb,
                    frequency=len(related_analyses),
                    relevance_score=avg_relevance,
                    value_level=dominant_value,
                    examples=[a.keyword for a in related_analyses[:5]],  # 最多5个例子
                    context_category=context_category
                )
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: (p.relevance_score, p.frequency), reverse=True)
    
    def _determine_context_category(self, analyses: List[SemanticAnalysis]) -> str:
        """确定上下文分类"""
        keywords = [a.keyword.lower() for a in analyses]
        combined_text = ' '.join(keywords)
        
        # 检查AI平台访问
        if any(platform in combined_text for platform in ['access', 'login', 'signup', 'register']):
            return 'ai_platform_access'
        
        # 检查技能学习
        if any(learn_word in combined_text for learn_word in ['learn', 'tutorial', 'guide', 'course']):
            return 'ai_skill_learning'
        
        # 检查工具使用
        if any(tool_word in combined_text for tool_word in ['tool', 'app', 'software', 'platform']):
            return 'ai_tool_usage'
        
        # 检查技术集成
        if any(tech_word in combined_text for tech_word in ['api', 'integration', 'connect', 'setup']):
            return 'tech_integration'
        
        return 'general'
    
    def _calculate_value_statistics(self, analyses: List[SemanticAnalysis]) -> Dict:
        """计算价值统计"""
        total = len(analyses)
        if total == 0:
            return {}
        
        value_counts = Counter(a.value_classification for a in analyses)
        
        return {
            'total_keywords': total,
            'high_value': {
                'count': value_counts['high'],
                'percentage': (value_counts['high'] / total) * 100
            },
            'medium_value': {
                'count': value_counts['medium'],
                'percentage': (value_counts['medium'] / total) * 100
            },
            'low_value': {
                'count': value_counts['low'],
                'percentage': (value_counts['low'] / total) * 100
            },
            'noise': {
                'count': value_counts['noise'],
                'percentage': (value_counts['noise'] / total) * 100
            },
            'signal_to_noise_ratio': (value_counts['high'] + value_counts['medium']) / max(1, value_counts['noise']),
            'quality_score': ((value_counts['high'] * 1.0 + value_counts['medium'] * 0.6) / total) * 100
        }
    
    def _generate_recommendations(self, patterns: List[DriftPattern], statistics: Dict) -> Dict:
        """生成优化建议"""
        recommendations = {
            'summary': {},
            'actions': [],
            'filter_rules': [],
            'monitoring_suggestions': []
        }
        
        # 总体评估
        noise_percentage = statistics.get('noise', {}).get('percentage', 0)
        quality_score = statistics.get('quality_score', 0)
        
        if noise_percentage > 50:
            recommendations['summary']['data_quality'] = '差 - 噪音过多'
            recommendations['actions'].append('紧急实施噪音过滤')
        elif noise_percentage > 30:
            recommendations['summary']['data_quality'] = '中等 - 需要优化'
            recommendations['actions'].append('加强过滤规则')
        else:
            recommendations['summary']['data_quality'] = '良好'
        
        # 过滤规则建议
        high_noise_patterns = [p for p in patterns if p.value_level == 'noise' and p.frequency >= 3]
        for pattern in high_noise_patterns:
            recommendations['filter_rules'].append({
                'type': 'verb_drift_filter',
                'rule': f"过滤 '{pattern.original_verb}' → '{pattern.new_verb}' 的漂移",
                'reason': f"频繁出现噪音模式 (出现{pattern.frequency}次)",
                'examples': pattern.examples[:3]
            })
        
        # 监控建议
        valuable_patterns = [p for p in patterns if p.value_level in ['high', 'medium'] and p.frequency >= 2]
        for pattern in valuable_patterns:
            recommendations['monitoring_suggestions'].append({
                'pattern': f"'{pattern.original_verb}' → '{pattern.new_verb}'",
                'reason': f"有价值的语义漂移 - {pattern.context_category}",
                'action': '建立独立监控'
            })
        
        return recommendations


def analyze_semantic_drift_from_file(file_path: str, output_dir: str = None) -> Dict:
    """
    从文件分析语义漂移
    
    Args:
        file_path: 变化数据文件路径
        output_dir: 输出目录
        
    Returns:
        Dict: 分析结果
    """
    analyzer = SemanticDriftAnalyzer()
    
    # 读取数据
    with open(file_path, 'r', encoding='utf-8') as f:
        changes_data = json.load(f)
    
    # 分析漂移
    result = analyzer.analyze_semantic_drift(changes_data)
    
    # 保存结果
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        main_keyword = result['metadata']['main_keyword']
        safe_keyword = main_keyword.replace(' ', '_').replace('/', '_')
        timestamp = result['metadata']['analysis_timestamp'][:10] if result['metadata']['analysis_timestamp'] else 'unknown'
        
        output_file = output_path / f"semantic_drift_{safe_keyword}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"语义漂移分析结果已保存: {output_file}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='语义漂移分析器')
    parser.add_argument('file_path', help='变化数据文件路径')
    parser.add_argument('-o', '--output', help='输出目录', default='reports')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    try:
        result = analyze_semantic_drift_from_file(args.file_path, args.output)
        
        print(f"🔍 语义漂移分析完成!")
        print(f"📊 总关键词: {result['value_statistics']['total_keywords']}")
        print(f"✅ 高价值: {result['value_statistics']['high_value']['count']} ({result['value_statistics']['high_value']['percentage']:.1f}%)")
        print(f"⚠️ 噪音: {result['value_statistics']['noise']['count']} ({result['value_statistics']['noise']['percentage']:.1f}%)")
        print(f"📈 质量得分: {result['value_statistics']['quality_score']:.1f}/100")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        exit(1)