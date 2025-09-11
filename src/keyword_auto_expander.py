#!/usr/bin/env python3
"""
Keyword Auto Expander
智能关键词自动扩展器

基于语义漂移分析结果，自动发现并添加高价值关键词到配置中
"""

import json
import re
import logging
from typing import List, Dict, Set, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KeywordCandidate:
    """关键词候选数据结构"""
    keyword: str
    source_keyword: str
    discovery_pattern: str
    relevance_score: float
    business_value: int
    frequency: int
    discovery_time: str
    confidence_score: float


class KeywordAutoExpander:
    """智能关键词自动扩展器"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化关键词扩展器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器
        """
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # 扩展配置
        self.expansion_settings = {
            'min_relevance_score': 0.7,        # 最低AI相关性得分
            'min_business_value': 7,            # 最低商业价值
            'min_frequency': 5,                 # 最低出现频次
            'max_auto_additions': 3,            # 单次最大自动添加数量
            'similarity_threshold': 0.8,        # 相似度阈值（避免重复）
            'min_confidence_score': 0.75,      # 最低置信度
            'enable_auto_expansion': True,      # 是否启用自动扩展
            'exclude_patterns': [               # 排除模式
                r'.*\d{4}.*',                  # 包含年份的
                r'.*version.*',                # 版本相关
                r'.*test.*',                   # 测试相关
                r'.*demo.*',                   # 演示相关
            ]
        }
        
        # 高价值动词模式
        self.valuable_verbs = {
            'access': {'weight': 0.9, 'context': 'platform_access'},
            'learn': {'weight': 0.8, 'context': 'skill_acquisition'},
            'create': {'weight': 0.9, 'context': 'content_generation'},
            'build': {'weight': 0.8, 'context': 'development'},
            'integrate': {'weight': 0.7, 'context': 'technical_integration'},
            'optimize': {'weight': 0.7, 'context': 'improvement'},
            'automate': {'weight': 0.8, 'context': 'automation'},
            'analyze': {'weight': 0.6, 'context': 'analysis'}
        }
    
    def analyze_and_expand(self, analysis_json_file: str, source_keyword: str) -> List[str]:
        """
        分析并执行关键词扩展
        
        Args:
            analysis_json_file: 增强分析结果JSON文件
            source_keyword: 源关键词
            
        Returns:
            List[str]: 新添加的关键词列表
        """
        if not self.expansion_settings['enable_auto_expansion']:
            self.logger.debug("关键词自动扩展已禁用")
            return []
        
        try:
            # 读取分析结果
            with open(analysis_json_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # 提取候选关键词
            candidates = self._extract_keyword_candidates(analysis_data, source_keyword)
            
            # 过滤和评分
            qualified_candidates = self._filter_and_score_candidates(candidates)
            
            # 检查重复和相似度
            unique_candidates = self._deduplicate_candidates(qualified_candidates)
            
            # 选择最佳候选
            selected_candidates = self._select_best_candidates(unique_candidates)
            
            # 添加到配置
            added_keywords = self._add_to_config(selected_candidates)
            
            return added_keywords
            
        except Exception as e:
            self.logger.error(f"关键词扩展分析失败: {e}")
            return []
    
    def _extract_keyword_candidates(self, analysis_data: Dict, source_keyword: str) -> List[KeywordCandidate]:
        """提取关键词候选"""
        candidates = []
        
        # 从语义漂移分析中提取
        drift_analysis = analysis_data.get('semantic_drift_analysis', {})
        drift_patterns = drift_analysis.get('drift_patterns', [])
        
        for pattern in drift_patterns:
            if pattern.get('value_level') in ['high', 'medium']:
                # 基于漂移模式生成候选关键词
                candidates.extend(self._generate_candidates_from_pattern(pattern, source_keyword))
        
        # 从高价值关键词中提取
        filtered_keywords = drift_analysis.get('filtered_keywords', {})
        high_value_keywords = filtered_keywords.get('high_value', [])
        
        for keyword in high_value_keywords:
            candidate = self._create_candidate_from_keyword(keyword, source_keyword)
            if candidate:
                candidates.append(candidate)
        
        return candidates
    
    def _generate_candidates_from_pattern(self, pattern: Dict, source_keyword: str) -> List[KeywordCandidate]:
        """基于漂移模式生成候选关键词"""
        candidates = []
        
        original_verb = pattern.get('original_verb', '')
        new_verb = pattern.get('new_verb', '')
        examples = pattern.get('examples', [])
        frequency = pattern.get('frequency', 0)
        relevance_score = pattern.get('relevance_score', 0.0)
        
        # 检查是否为有价值的动词
        if new_verb in self.valuable_verbs:
            verb_info = self.valuable_verbs[new_verb]
            
            # 生成新的关键词组合
            base_parts = source_keyword.split()
            if len(base_parts) >= 3:  # 例如 "how to use ai"
                new_keyword = f"{base_parts[0]} {base_parts[1]} {new_verb} {' '.join(base_parts[3:])}"
                
                candidate = KeywordCandidate(
                    keyword=new_keyword,
                    source_keyword=source_keyword,
                    discovery_pattern=f"{original_verb} → {new_verb}",
                    relevance_score=relevance_score,
                    business_value=self._estimate_business_value(new_keyword, verb_info),
                    frequency=frequency,
                    discovery_time=datetime.now().isoformat(),
                    confidence_score=self._calculate_confidence(pattern, verb_info)
                )
                
                candidates.append(candidate)
        
        return candidates
    
    def _create_candidate_from_keyword(self, keyword: str, source_keyword: str) -> Optional[KeywordCandidate]:
        """从关键词创建候选"""
        
        # 检查关键词是否符合扩展条件
        if not self._is_expandable_keyword(keyword, source_keyword):
            return None
        
        # 计算相关性和商业价值
        relevance_score = self._calculate_keyword_relevance(keyword)
        business_value = self._estimate_business_value_from_keyword(keyword)
        
        return KeywordCandidate(
            keyword=keyword,
            source_keyword=source_keyword,
            discovery_pattern="high_value_keyword",
            relevance_score=relevance_score,
            business_value=business_value,
            frequency=1,  # 默认频次
            discovery_time=datetime.now().isoformat(),
            confidence_score=relevance_score * 0.8  # 保守估计
        )
    
    def _is_expandable_keyword(self, keyword: str, source_keyword: str) -> bool:
        """判断关键词是否可扩展"""
        
        # 长度检查
        if len(keyword.split()) < 3 or len(keyword.split()) > 6:
            return False
        
        # 排除模式检查
        for pattern in self.expansion_settings['exclude_patterns']:
            if re.match(pattern, keyword.lower()):
                return False
        
        # 与源关键词的相似度检查
        similarity = SequenceMatcher(None, keyword.lower(), source_keyword.lower()).ratio()
        if similarity > 0.9:  # 太相似，可能是重复
            return False
        
        # 检查是否包含有价值的动词
        for verb in self.valuable_verbs:
            if verb in keyword.lower():
                return True
        
        return False
    
    def _calculate_keyword_relevance(self, keyword: str) -> float:
        """计算关键词的AI相关性"""
        keyword_lower = keyword.lower()
        score = 0.0
        
        # AI核心词汇
        if ' ai ' in keyword_lower or keyword_lower.startswith('ai ') or keyword_lower.endswith(' ai'):
            score += 0.6
        
        # 高价值动词
        for verb, info in self.valuable_verbs.items():
            if verb in keyword_lower:
                score += info['weight'] * 0.3
                break
        
        # 技术相关词汇
        tech_terms = ['api', 'platform', 'tool', 'service', 'app', 'software']
        for term in tech_terms:
            if term in keyword_lower:
                score += 0.2
                break
        
        return min(1.0, score)
    
    def _estimate_business_value(self, keyword: str, verb_info: Dict) -> int:
        """估算商业价值"""
        base_score = 5
        
        # 基于动词上下文调整
        context = verb_info.get('context', '')
        context_scores = {
            'platform_access': 8,
            'content_generation': 9,
            'skill_acquisition': 7,
            'development': 8,
            'automation': 8,
            'technical_integration': 7
        }
        
        base_score = context_scores.get(context, base_score)
        
        # 基于关键词内容调整
        keyword_lower = keyword.lower()
        
        if any(term in keyword_lower for term in ['professional', 'enterprise', 'business']):
            base_score += 1
        
        if any(term in keyword_lower for term in ['free', 'open source']):
            base_score -= 1
        
        if any(term in keyword_lower for term in ['api', 'platform', 'service']):
            base_score += 1
        
        return max(1, min(10, base_score))
    
    def _estimate_business_value_from_keyword(self, keyword: str) -> int:
        """从关键词估算商业价值"""
        keyword_lower = keyword.lower()
        score = 5
        
        # 商业相关词汇
        if any(term in keyword_lower for term in ['business', 'enterprise', 'professional', 'commercial']):
            score += 2
        
        # 技术相关词汇
        if any(term in keyword_lower for term in ['api', 'platform', 'service', 'tool', 'app']):
            score += 1
        
        # 创作相关词汇
        if any(term in keyword_lower for term in ['create', 'generate', 'build', 'make']):
            score += 1
        
        # 免费相关（降低商业价值）
        if any(term in keyword_lower for term in ['free', 'gratis', 'no cost']):
            score -= 1
        
        return max(1, min(10, score))
    
    def _calculate_confidence(self, pattern: Dict, verb_info: Dict) -> float:
        """计算置信度"""
        relevance_score = pattern.get('relevance_score', 0.0)
        frequency = pattern.get('frequency', 0)
        verb_weight = verb_info.get('weight', 0.5)
        
        # 综合计算置信度
        frequency_score = min(1.0, frequency / 10.0)  # 频次贡献
        confidence = (relevance_score * 0.4 + frequency_score * 0.3 + verb_weight * 0.3)
        
        return confidence
    
    def _filter_and_score_candidates(self, candidates: List[KeywordCandidate]) -> List[KeywordCandidate]:
        """过滤和评分候选关键词"""
        qualified = []
        
        for candidate in candidates:
            # 应用过滤条件
            if (candidate.relevance_score >= self.expansion_settings['min_relevance_score'] and
                candidate.business_value >= self.expansion_settings['min_business_value'] and
                candidate.frequency >= self.expansion_settings['min_frequency'] and
                candidate.confidence_score >= self.expansion_settings['min_confidence_score']):
                
                qualified.append(candidate)
        
        # 按综合得分排序
        qualified.sort(key=lambda c: (c.confidence_score, c.business_value, c.frequency), reverse=True)
        
        return qualified
    
    def _deduplicate_candidates(self, candidates: List[KeywordCandidate]) -> List[KeywordCandidate]:
        """去重候选关键词 - 增强版本"""
        unique_candidates = []
        existing_keywords = set()
        
        # 获取现有配置中的关键词
        try:
            config = self.config_manager.load_config()
            for keyword_config in config.get('keywords', []):
                existing_keywords.add(keyword_config['main_keyword'].lower())
        except Exception as e:
            self.logger.warning(f"读取现有配置失败: {e}")
        
        # 高级去重算法
        seen_patterns = set()
        seen_roots = set()
        
        for candidate in candidates:
            keyword_lower = candidate.keyword.lower()
            
            # 1. 基本重复检查
            if keyword_lower in existing_keywords:
                self.logger.debug(f"跳过已存在关键词: {candidate.keyword}")
                continue
            
            # 2. 语义模式去重 - 防止相同模式的重复添加
            pattern_key = f"{candidate.source_keyword}:{candidate.discovery_pattern}"
            if pattern_key in seen_patterns:
                self.logger.debug(f"跳过重复模式: {pattern_key}")
                continue
            
            # 3. 词根相似性检查 - 提取核心概念
            keyword_root = self._extract_keyword_root(candidate.keyword)
            if keyword_root in seen_roots:
                self.logger.debug(f"跳过相似词根: {keyword_root}")
                continue
            
            # 4. 与已选择候选词的相似度检查
            is_too_similar = False
            for existing in unique_candidates:
                # 使用多种相似度算法
                similarity_scores = [
                    SequenceMatcher(None, keyword_lower, existing.keyword.lower()).ratio(),
                    self._calculate_semantic_similarity(candidate.keyword, existing.keyword),
                    self._calculate_structural_similarity(candidate.keyword, existing.keyword)
                ]
                
                max_similarity = max(similarity_scores)
                if max_similarity >= self.expansion_settings['similarity_threshold']:
                    self.logger.debug(f"跳过相似关键词: {candidate.keyword} vs {existing.keyword} (相似度: {max_similarity:.3f})")
                    is_too_similar = True
                    break
            
            if not is_too_similar:
                # 5. 质量验证通过，添加到结果
                unique_candidates.append(candidate)
                existing_keywords.add(keyword_lower)
                seen_patterns.add(pattern_key)
                seen_roots.add(keyword_root)
                
                self.logger.debug(f"接受候选关键词: {candidate.keyword} (置信度: {candidate.confidence_score:.3f})")
        
        self.logger.info(f"去重完成: {len(candidates)} -> {len(unique_candidates)} 个候选关键词")
        return unique_candidates
    
    def _extract_keyword_root(self, keyword: str) -> str:
        """提取关键词的核心概念"""
        # 移除常见的前缀和后缀
        keyword_lower = keyword.lower().strip()
        
        # 移除常见的引导词
        prefixes_to_remove = ['how to ', 'what is ', 'where to ', 'when to ', 'why ', 'best way to ']
        for prefix in prefixes_to_remove:
            if keyword_lower.startswith(prefix):
                keyword_lower = keyword_lower[len(prefix):]
                break
        
        # 移除常见的后缀
        suffixes_to_remove = [' online', ' free', ' tool', ' app', ' software', ' platform']
        for suffix in suffixes_to_remove:
            if keyword_lower.endswith(suffix):
                keyword_lower = keyword_lower[:-len(suffix)]
                break
        
        # 提取核心动词和名词
        words = keyword_lower.split()
        if len(words) >= 2:
            # 保留主要的动作词和对象词
            core_words = [word for word in words if len(word) >= 3 and word not in ['the', 'and', 'for', 'with']]
            if len(core_words) >= 2:
                return ' '.join(core_words[:2])  # 取前两个核心词
        
        return keyword_lower
    
    def _calculate_semantic_similarity(self, keyword1: str, keyword2: str) -> float:
        """计算语义相似度"""
        # 简化版语义相似度计算
        words1 = set(keyword1.lower().split())
        words2 = set(keyword2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard相似度
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_structural_similarity(self, keyword1: str, keyword2: str) -> float:
        """计算结构相似度 - 基于词序和语法结构"""
        words1 = keyword1.lower().split()
        words2 = keyword2.lower().split()
        
        if len(words1) != len(words2):
            return 0.0
        
        # 位置匹配得分
        position_matches = sum(1 for w1, w2 in zip(words1, words2) if w1 == w2)
        return position_matches / len(words1) if words1 else 0.0
    
    def _select_best_candidates(self, candidates: List[KeywordCandidate]) -> List[KeywordCandidate]:
        """选择最佳候选关键词"""
        max_additions = self.expansion_settings['max_auto_additions']
        return candidates[:max_additions]
    
    def _add_to_config(self, candidates: List[KeywordCandidate]) -> List[str]:
        """添加关键词到配置文件"""
        if not candidates:
            return []
        
        try:
            # 读取当前配置
            config = self.config_manager.load_config()
            
            # 准备新的关键词配置
            new_keywords = []
            default_schedule = "0 12 * * *"  # 默认调度时间
            
            for candidate in candidates:
                keyword_config = {
                    "main_keyword": candidate.keyword,
                    "enabled": True,
                    "schedule": default_schedule,
                    "auto_added": True,
                    "source_keyword": candidate.source_keyword,
                    "discovery_pattern": candidate.discovery_pattern,
                    "discovery_time": candidate.discovery_time,
                    "confidence_score": candidate.confidence_score,
                    "business_value": candidate.business_value
                }
                
                config['keywords'].append(keyword_config)
                new_keywords.append(candidate.keyword)
            
            # 保存更新后的配置
            self.config_manager.save_config(config)
            
            self.logger.info(f"成功添加 {len(new_keywords)} 个关键词到配置: {new_keywords}")
            return new_keywords
            
        except Exception as e:
            self.logger.error(f"添加关键词到配置失败: {e}")
            return []
    
    def get_auto_added_keywords(self) -> List[Dict]:
        """获取所有自动添加的关键词"""
        try:
            config = self.config_manager.load_config()
            auto_added = []
            
            for keyword_config in config.get('keywords', []):
                if keyword_config.get('auto_added', False):
                    auto_added.append(keyword_config)
            
            return auto_added
            
        except Exception as e:
            self.logger.error(f"获取自动添加关键词失败: {e}")
            return []
    
    def cleanup_low_performance_keywords(self, days: int = 30) -> List[str]:
        """清理低效的自动添加关键词 - 完整实现"""
        try:
            # 获取自动添加的关键词统计
            auto_keywords_stats = self.config_manager.get_auto_added_keywords_stats()
            auto_keywords = auto_keywords_stats.get('auto_keywords', [])
            
            if not auto_keywords:
                self.logger.info("没有自动添加的关键词需要清理")
                return []
            
            # 分析关键词性能
            low_performance_keywords = []
            current_time = datetime.now()
            
            for kw_info in auto_keywords:
                keyword = kw_info['keyword']
                discovery_time_str = kw_info.get('discovery_time', '')
                confidence = kw_info.get('confidence', 0.0)
                business_value = kw_info.get('business_value', 5)
                
                # 解析添加时间
                try:
                    if discovery_time_str:
                        discovery_time = datetime.fromisoformat(discovery_time_str.replace('Z', '+00:00'))
                        days_since_added = (current_time - discovery_time.replace(tzinfo=None)).days
                    else:
                        days_since_added = days  # 默认为满足清理条件的天数
                except:
                    days_since_added = days
                
                # 清理条件
                should_cleanup = False
                cleanup_reason = ""
                
                # 1. 时间条件 - 添加超过指定天数
                if days_since_added >= days:
                    # 2. 性能条件
                    if confidence < 0.6:
                        should_cleanup = True
                        cleanup_reason = f"置信度过低 ({confidence:.3f} < 0.6)"
                    elif business_value < 4:
                        should_cleanup = True
                        cleanup_reason = f"商业价值过低 ({business_value} < 4)"
                    # 3. 检查是否有实际搜索数据（未来可以集成）
                    # TODO: 检查该关键词的搜索结果质量和数据量
                
                if should_cleanup:
                    low_performance_keywords.append({
                        'keyword': keyword,
                        'reason': cleanup_reason,
                        'days_since_added': days_since_added,
                        'confidence': confidence,
                        'business_value': business_value
                    })
            
            # 执行清理
            cleaned_keywords = []
            if low_performance_keywords:
                config = self.config_manager.load_config()
                keywords_to_remove = [kw['keyword'] for kw in low_performance_keywords]
                
                # 过滤掉低效关键词
                original_count = len(config['keywords'])
                config['keywords'] = [
                    kw for kw in config['keywords'] 
                    if kw['main_keyword'] not in keywords_to_remove
                ]
                
                # 保存更新后的配置
                if len(config['keywords']) < original_count:
                    self.config_manager.save_config(config)
                    cleaned_keywords = keywords_to_remove
                    
                    self.logger.info(f"清理完成: 删除了 {len(cleaned_keywords)} 个低效关键词")
                    for kw_info in low_performance_keywords:
                        self.logger.info(f"  - {kw_info['keyword']}: {kw_info['reason']}")
                else:
                    self.logger.info("没有关键词需要清理")
            else:
                self.logger.info("所有自动添加的关键词性能良好，无需清理")
            
            return cleaned_keywords
            
        except Exception as e:
            self.logger.error(f"清理低效关键词失败: {e}")
            return []
    
    def get_expansion_performance_report(self) -> Dict[str, Any]:
        """获取扩展性能报告"""
        try:
            stats = self.config_manager.get_auto_added_keywords_stats()
            
            # 分析扩展效果
            auto_keywords = stats.get('auto_keywords', [])
            performance_analysis = {
                'high_confidence': len([kw for kw in auto_keywords if kw.get('confidence', 0) >= 0.8]),
                'medium_confidence': len([kw for kw in auto_keywords if 0.6 <= kw.get('confidence', 0) < 0.8]),
                'low_confidence': len([kw for kw in auto_keywords if kw.get('confidence', 0) < 0.6]),
                'high_business_value': len([kw for kw in auto_keywords if kw.get('business_value', 0) >= 8]),
                'medium_business_value': len([kw for kw in auto_keywords if 5 <= kw.get('business_value', 0) < 8]),
                'low_business_value': len([kw for kw in auto_keywords if kw.get('business_value', 0) < 5])
            }
            
            # 模式分析
            pattern_analysis = {}
            for kw in auto_keywords:
                pattern = kw.get('pattern', 'unknown')
                if pattern not in pattern_analysis:
                    pattern_analysis[pattern] = 0
                pattern_analysis[pattern] += 1
            
            return {
                'basic_stats': stats,
                'performance_analysis': performance_analysis,
                'pattern_analysis': pattern_analysis,
                'effectiveness_score': self._calculate_expansion_effectiveness(auto_keywords),
                'recommendations': self._generate_expansion_recommendations(performance_analysis, pattern_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"生成扩展性能报告失败: {e}")
            return {}
    
    def _calculate_expansion_effectiveness(self, auto_keywords: List[Dict]) -> float:
        """计算扩展效果评分"""
        if not auto_keywords:
            return 0.0
        
        total_score = 0.0
        for kw in auto_keywords:
            confidence = kw.get('confidence', 0.0)
            business_value = kw.get('business_value', 0) / 10.0  # 归一化到0-1
            
            # 综合评分
            keyword_score = (confidence * 0.6) + (business_value * 0.4)
            total_score += keyword_score
        
        return total_score / len(auto_keywords)
    
    def _generate_expansion_recommendations(self, performance_analysis: Dict, pattern_analysis: Dict) -> List[str]:
        """生成扩展建议"""
        recommendations = []
        
        total_keywords = sum(performance_analysis.values())
        if total_keywords == 0:
            return ["暂无自动添加的关键词，建议启用关键词扩展功能"]
        
        # 置信度分析
        low_confidence_ratio = performance_analysis.get('low_confidence', 0) / total_keywords
        if low_confidence_ratio > 0.3:
            recommendations.append("建议提高最低置信度阈值，当前有超过30%的关键词置信度较低")
        
        # 商业价值分析
        low_value_ratio = performance_analysis.get('low_business_value', 0) / total_keywords
        if low_value_ratio > 0.25:
            recommendations.append("建议调整商业价值评分算法，当前有超过25%的关键词商业价值较低")
        
        # 模式多样性分析
        if len(pattern_analysis) < 3:
            recommendations.append("建议增加语义漂移模式的多样性，当前模式过于单一")
        
        # 最优模式推荐
        if pattern_analysis:
            best_pattern = max(pattern_analysis.items(), key=lambda x: x[1])
            if best_pattern[1] >= 3:
                recommendations.append(f"模式 '{best_pattern[0]}' 表现优秀，建议优化相关规则")
        
        return recommendations if recommendations else ["当前扩展策略运行良好，继续保持"]
    
    def update_expansion_settings(self, settings: Dict):
        """更新扩展设置"""
        self.expansion_settings.update(settings)
        self.logger.info(f"扩展设置已更新: {settings}")


def create_keyword_auto_expander(config_manager, logger=None) -> KeywordAutoExpander:
    """
    创建关键词自动扩展器工厂函数
    
    Args:
        config_manager: 配置管理器
        logger: 日志记录器
        
    Returns:
        KeywordAutoExpander: 扩展器实例
    """
    return KeywordAutoExpander(config_manager, logger)