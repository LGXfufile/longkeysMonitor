"""
Compare Analyzer Module
对比分析器模块

Analyzes differences between current and previous keyword data.
"""

from typing import Set, List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from collections import Counter

from .data_processor import KeywordData, DataProcessor

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """对比结果数据结构"""
    main_keyword: str
    current_date: str
    previous_date: str
    new_keywords: List[str]
    disappeared_keywords: List[str]
    stable_keywords: List[str]
    total_current: int
    total_previous: int
    new_count: int
    disappeared_count: int
    stable_count: int
    change_rate: float
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "main_keyword": self.main_keyword,
            "current_date": self.current_date,
            "previous_date": self.previous_date,
            "new_keywords": self.new_keywords,
            "disappeared_keywords": self.disappeared_keywords,
            "stable_keywords": self.stable_keywords,
            "statistics": {
                "total_current": self.total_current,
                "total_previous": self.total_previous,
                "new_count": self.new_count,
                "disappeared_count": self.disappeared_count,
                "stable_count": self.stable_count,
                "change_rate": self.change_rate
            }
        }


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    keyword: str
    trend_direction: str  # "rising", "falling", "stable"
    frequency_change: int
    first_appearance: str
    last_appearance: str
    appearance_count: int
    stability_score: float
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "keyword": self.keyword,
            "trend_direction": self.trend_direction,
            "frequency_change": self.frequency_change,
            "first_appearance": self.first_appearance,
            "last_appearance": self.last_appearance,
            "appearance_count": self.appearance_count,
            "stability_score": self.stability_score
        }


class CompareAnalyzer:
    """对比分析器"""
    
    def __init__(self, data_processor: DataProcessor):
        """
        初始化对比分析器
        
        Args:
            data_processor: 数据处理器实例
        """
        self.data_processor = data_processor
        logger.info("对比分析器初始化完成")
    
    def compare_with_previous_day(self, current_data: KeywordData) -> Optional[ComparisonResult]:
        """
        与前一天数据对比
        
        Args:
            current_data: 当前数据
            
        Returns:
            Optional[ComparisonResult]: 对比结果
        """
        # 获取前一天数据
        previous_data = self.data_processor.get_previous_day_data(
            current_data.main_keyword, 
            current_data.execution_date
        )
        
        if not previous_data:
            logger.warning(f"未找到 {current_data.main_keyword} 的前一天数据，跳过对比")
            return None
        
        return self.compare_keyword_data(current_data, previous_data)
    
    def compare_keyword_data(self, current_data: KeywordData, 
                           previous_data: KeywordData) -> ComparisonResult:
        """
        对比两个关键词数据
        
        Args:
            current_data: 当前数据
            previous_data: 前一天数据
            
        Returns:
            ComparisonResult: 对比结果
        """
        # 提取关键词集合
        current_keywords = self.data_processor.extract_all_keywords(current_data)
        previous_keywords = self.data_processor.extract_all_keywords(previous_data)
        
        # 计算差异
        new_keywords = list(current_keywords - previous_keywords)
        disappeared_keywords = list(previous_keywords - current_keywords)
        stable_keywords = list(current_keywords & previous_keywords)
        
        # 排序（按字母顺序）
        new_keywords.sort()
        disappeared_keywords.sort()
        stable_keywords.sort()
        
        # 计算变化率
        total_previous = len(previous_keywords)
        change_rate = 0.0
        if total_previous > 0:
            change_rate = round(
                (len(new_keywords) - len(disappeared_keywords)) / total_previous * 100, 2
            )
        
        result = ComparisonResult(
            main_keyword=current_data.main_keyword,
            current_date=current_data.execution_date,
            previous_date=previous_data.execution_date,
            new_keywords=new_keywords,
            disappeared_keywords=disappeared_keywords,
            stable_keywords=stable_keywords,
            total_current=len(current_keywords),
            total_previous=total_previous,
            new_count=len(new_keywords),
            disappeared_count=len(disappeared_keywords),
            stable_count=len(stable_keywords),
            change_rate=change_rate
        )
        
        logger.info(f"对比分析完成: {result.new_count} 新增, {result.disappeared_count} 消失")
        
        return result
    
    def analyze_keyword_trends(self, main_keyword: str, days: int = 7) -> List[TrendAnalysis]:
        """
        分析关键词趋势
        
        Args:
            main_keyword: 主关键词
            days: 分析天数
            
        Returns:
            List[TrendAnalysis]: 趋势分析结果
        """
        # 获取历史数据
        historical_data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            data = self.data_processor.get_previous_day_data(main_keyword, date)
            if data:
                historical_data.append(data)
        
        if len(historical_data) < 2:
            logger.warning(f"历史数据不足，无法分析趋势")
            return []
        
        # 统计关键词出现频率
        keyword_frequency = Counter()
        keyword_dates = {}
        
        for data in historical_data:
            keywords = self.data_processor.extract_all_keywords(data)
            for keyword in keywords:
                keyword_frequency[keyword] += 1
                if keyword not in keyword_dates:
                    keyword_dates[keyword] = []
                keyword_dates[keyword].append(data.execution_date)
        
        # 分析趋势
        trends = []
        for keyword, frequency in keyword_frequency.items():
            dates = sorted(keyword_dates[keyword])
            first_appearance = dates[0]
            last_appearance = dates[-1]
            
            # 计算稳定性得分 (出现频率 / 总天数)
            stability_score = frequency / len(historical_data)
            
            # 判断趋势方向
            recent_appearances = len([d for d in dates if d >= (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')])
            early_appearances = len([d for d in dates if d <= (datetime.now() - timedelta(days=days-3)).strftime('%Y-%m-%d')])
            
            if recent_appearances > early_appearances:
                trend_direction = "rising"
            elif recent_appearances < early_appearances:
                trend_direction = "falling"
            else:
                trend_direction = "stable"
            
            trend = TrendAnalysis(
                keyword=keyword,
                trend_direction=trend_direction,
                frequency_change=recent_appearances - early_appearances,
                first_appearance=first_appearance,
                last_appearance=last_appearance,
                appearance_count=frequency,
                stability_score=round(stability_score, 3)
            )
            
            trends.append(trend)
        
        # 按稳定性得分排序
        trends.sort(key=lambda x: x.stability_score, reverse=True)
        
        logger.info(f"趋势分析完成，共分析 {len(trends)} 个关键词")
        
        return trends
    
    def get_trending_keywords(self, main_keyword: str, limit: int = 10) -> Dict[str, List[str]]:
        """
        获取热门趋势关键词
        
        Args:
            main_keyword: 主关键词
            limit: 返回数量限制
            
        Returns:
            Dict[str, List[str]]: 分类的热门关键词
        """
        trends = self.analyze_keyword_trends(main_keyword, days=7)
        
        rising_keywords = [t.keyword for t in trends if t.trend_direction == "rising"][:limit]
        stable_keywords = [t.keyword for t in trends if t.trend_direction == "stable" and t.stability_score > 0.5][:limit]
        falling_keywords = [t.keyword for t in trends if t.trend_direction == "falling"][:limit]
        
        return {
            "rising": rising_keywords,
            "stable": stable_keywords,
            "falling": falling_keywords
        }
    
    def analyze_query_performance(self, keyword_data: KeywordData) -> Dict[str, any]:
        """
        分析查询性能
        
        Args:
            keyword_data: 关键词数据
            
        Returns:
            Dict: 性能分析结果
        """
        query_stats = []
        
        for query, suggestions in keyword_data.query_results.items():
            suggestion_count = len(suggestions) if suggestions else 0
            
            # 分析查询类型
            query_type = self._classify_query(query, keyword_data.main_keyword)
            
            query_stats.append({
                "query": query,
                "suggestion_count": suggestion_count,
                "query_type": query_type,
                "has_results": suggestion_count > 0
            })
        
        # 统计分析
        total_queries = len(query_stats)
        successful_queries = len([q for q in query_stats if q["has_results"]])
        empty_queries = total_queries - successful_queries
        
        # 按查询类型统计
        type_stats = Counter(q["query_type"] for q in query_stats)
        
        # 找出效果最好的查询
        top_queries = sorted(query_stats, key=lambda x: x["suggestion_count"], reverse=True)[:10]
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "empty_queries": empty_queries,
            "success_rate": round(successful_queries / total_queries * 100, 2) if total_queries > 0 else 0,
            "query_type_distribution": dict(type_stats),
            "top_performing_queries": top_queries,
            "avg_suggestions_per_query": round(
                sum(q["suggestion_count"] for q in query_stats) / total_queries, 2
            ) if total_queries > 0 else 0
        }
    
    def _classify_query(self, query: str, main_keyword: str) -> str:
        """
        分类查询类型
        
        Args:
            query: 查询字符串
            main_keyword: 主关键词
            
        Returns:
            str: 查询类型
        """
        if query == main_keyword:
            return "base"
        elif query.startswith(main_keyword + " "):
            suffix = query[len(main_keyword) + 1:]
            if len(suffix) == 1:
                return "single_suffix"
            elif len(suffix) == 2:
                return "double_suffix"
            else:
                return "other_suffix"
        elif query.endswith(" " + main_keyword):
            prefix = query[:-(len(main_keyword) + 1)]
            if len(prefix) == 1:
                return "single_prefix"
            elif len(prefix) == 2:
                return "double_prefix"
            else:
                return "other_prefix"
        else:
            return "other"
    
    def generate_insights(self, comparison_result: ComparisonResult) -> List[str]:
        """
        生成分析洞察
        
        Args:
            comparison_result: 对比结果
            
        Returns:
            List[str]: 洞察列表
        """
        insights = []
        
        # 变化幅度洞察
        if comparison_result.change_rate > 20:
            insights.append(f"关键词数量大幅增长 {comparison_result.change_rate:.1f}%，搜索趋势活跃")
        elif comparison_result.change_rate < -20:
            insights.append(f"关键词数量大幅下降 {abs(comparison_result.change_rate):.1f}%，关注度可能降低")
        elif abs(comparison_result.change_rate) < 5:
            insights.append("关键词数量相对稳定，搜索趋势平稳")
        
        # 新增关键词洞察
        if comparison_result.new_count > 50:
            insights.append(f"发现大量新关键词 ({comparison_result.new_count}个)，可能出现新热点")
        elif comparison_result.new_count > 20:
            insights.append(f"有较多新关键词出现 ({comparison_result.new_count}个)，值得关注")
        
        # 消失关键词洞察
        if comparison_result.disappeared_count > 30:
            insights.append(f"较多关键词消失 ({comparison_result.disappeared_count}个)，可能热度下降")
        
        # 稳定性洞察
        stability_rate = comparison_result.stable_count / comparison_result.total_previous * 100 if comparison_result.total_previous > 0 else 0
        if stability_rate > 80:
            insights.append(f"关键词稳定性高 ({stability_rate:.1f}%)，核心搜索词相对固定")
        elif stability_rate < 50:
            insights.append(f"关键词变化较大 ({stability_rate:.1f}%)，搜索行为波动明显")
        
        return insights
    
    def export_comparison_report(self, comparison_result: ComparisonResult, 
                               file_path: str = None) -> str:
        """
        导出对比报告
        
        Args:
            comparison_result: 对比结果
            file_path: 导出文件路径
            
        Returns:
            str: 导出文件路径
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_keyword = self.data_processor._sanitize_filename(comparison_result.main_keyword)
            filename = f"comparison_report_{safe_keyword}_{timestamp}.json"
            file_path = self.data_processor.data_dir / filename
        
        # 生成报告数据
        report_data = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "keyword_comparison",
                "version": "1.0"
            },
            "comparison_result": comparison_result.to_dict(),
            "insights": self.generate_insights(comparison_result),
            "performance_analysis": self.analyze_query_performance(
                # 这里需要当前数据，暂时跳过
            ) if hasattr(self, '_current_data') else None
        }
        
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"对比报告已导出: {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"导出对比报告失败: {e}")
            raise


def create_compare_analyzer(data_processor: DataProcessor) -> CompareAnalyzer:
    """
    创建对比分析器工厂函数
    
    Args:
        data_processor: 数据处理器
        
    Returns:
        CompareAnalyzer: 对比分析器实例
    """
    return CompareAnalyzer(data_processor)