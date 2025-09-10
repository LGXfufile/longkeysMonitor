"""
Query Generator Module
查询生成器模块

Generates all possible query combinations for keyword monitoring.
"""

import string
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)


class QueryGenerator:
    """查询生成器"""
    
    def __init__(self, search_settings: Dict = None):
        """
        初始化查询生成器
        
        Args:
            search_settings: 搜索设置配置
        """
        self.search_settings = search_settings or {
            "include_single_letters": True,
            "include_double_letters": True,
            "include_prefix": True,
            "include_suffix": True,
            "languages": ["zh", "en"]
        }
        
    def generate_all_queries(self, main_keyword: str) -> List[str]:
        """
        生成主关键词的所有查询组合
        
        Args:
            main_keyword: 主关键词
            
        Returns:
            List[str]: 所有查询组合列表
        """
        queries = []
        
        # 基础查询（主关键词本身）
        queries.append(main_keyword)
        
        # 生成字母组合
        if self.search_settings.get("include_single_letters", True):
            queries.extend(self._generate_single_letter_queries(main_keyword))
        
        if self.search_settings.get("include_double_letters", True):
            queries.extend(self._generate_double_letter_queries(main_keyword))
        
        # 去重并排序
        unique_queries = list(set(queries))
        unique_queries.sort()
        
        logger.info(f"为关键词 '{main_keyword}' 生成了 {len(unique_queries)} 个查询")
        
        return unique_queries
    
    def _generate_single_letter_queries(self, main_keyword: str) -> List[str]:
        """生成单字母组合查询"""
        queries = []
        
        # a-z 26个字母
        for letter in string.ascii_lowercase:
            # 后缀: "AI写作 a"
            if self.search_settings.get("include_suffix", True):
                queries.append(f"{main_keyword} {letter}")
            
            # 前缀: "a AI写作"  
            if self.search_settings.get("include_prefix", True):
                queries.append(f"{letter} {main_keyword}")
        
        logger.debug(f"单字母组合生成了 {len(queries)} 个查询")
        return queries
    
    def _generate_double_letter_queries(self, main_keyword: str) -> List[str]:
        """生成双字母组合查询"""
        queries = []
        
        # aa-zz 676个双字母组合
        for first_letter in string.ascii_lowercase:
            for second_letter in string.ascii_lowercase:
                double_letter = first_letter + second_letter
                
                # 后缀: "AI写作 aa"
                if self.search_settings.get("include_suffix", True):
                    queries.append(f"{main_keyword} {double_letter}")
                
                # 前缀: "aa AI写作"
                if self.search_settings.get("include_prefix", True):
                    queries.append(f"{double_letter} {main_keyword}")
        
        logger.debug(f"双字母组合生成了 {len(queries)} 个查询")
        return queries
    
    def get_query_statistics(self, main_keyword: str) -> Dict[str, int]:
        """
        获取查询统计信息
        
        Args:
            main_keyword: 主关键词
            
        Returns:
            Dict[str, int]: 统计信息
        """
        stats = {
            "base_query": 1,  # 基础查询
            "single_letter_suffix": 0,
            "single_letter_prefix": 0, 
            "double_letter_suffix": 0,
            "double_letter_prefix": 0,
            "total": 1
        }
        
        if self.search_settings.get("include_single_letters", True):
            if self.search_settings.get("include_suffix", True):
                stats["single_letter_suffix"] = 26
            if self.search_settings.get("include_prefix", True):
                stats["single_letter_prefix"] = 26
        
        if self.search_settings.get("include_double_letters", True):
            if self.search_settings.get("include_suffix", True):
                stats["double_letter_suffix"] = 676
            if self.search_settings.get("include_prefix", True):
                stats["double_letter_prefix"] = 676
        
        stats["total"] = sum(stats.values()) - stats["total"]  # 减去重复计算的total
        stats["total"] += 1  # 加回基础查询
        
        return stats
    
    def validate_keyword(self, main_keyword: str) -> tuple[bool, str]:
        """
        验证主关键词格式
        
        Args:
            main_keyword: 主关键词
            
        Returns:
            tuple[bool, str]: (是否有效, 错误信息)
        """
        if not main_keyword or not main_keyword.strip():
            return False, "关键词不能为空"
        
        # 去除前后空格
        main_keyword = main_keyword.strip()
        
        # 检查长度
        if len(main_keyword) > 100:
            return False, "关键词长度不能超过100个字符"
        
        # 检查是否包含特殊字符（可能影响搜索）
        invalid_chars = ['<', '>', '"', "'", '&', '%']
        for char in invalid_chars:
            if char in main_keyword:
                return False, f"关键词包含无效字符: {char}"
        
        return True, ""
    
    def optimize_query_list(self, queries: List[str]) -> List[str]:
        """
        优化查询列表，移除可能无效的查询
        
        Args:
            queries: 原始查询列表
            
        Returns:
            List[str]: 优化后的查询列表
        """
        optimized_queries = []
        
        for query in queries:
            # 基本清理
            query = query.strip()
            if not query:
                continue
            
            # 移除重复的空格
            query = ' '.join(query.split())
            
            # 检查查询长度
            if len(query) > 150:
                logger.debug(f"跳过过长的查询: {query[:50]}...")
                continue
            
            optimized_queries.append(query)
        
        # 去重并保持顺序
        seen = set()
        final_queries = []
        for query in optimized_queries:
            if query not in seen:
                seen.add(query)
                final_queries.append(query)
        
        logger.info(f"查询优化完成: {len(queries)} -> {len(final_queries)}")
        
        return final_queries
    
    def generate_batch_queries(self, keywords: List[str], batch_size: int = 100) -> List[List[str]]:
        """
        批量生成查询，用于分批处理
        
        Args:
            keywords: 主关键词列表
            batch_size: 每批查询数量
            
        Returns:
            List[List[str]]: 分批的查询列表
        """
        all_queries = []
        
        for keyword in keywords:
            is_valid, error_msg = self.validate_keyword(keyword)
            if not is_valid:
                logger.error(f"关键词 '{keyword}' 无效: {error_msg}")
                continue
            
            keyword_queries = self.generate_all_queries(keyword)
            all_queries.extend(keyword_queries)
        
        # 分批处理
        batches = []
        for i in range(0, len(all_queries), batch_size):
            batch = all_queries[i:i + batch_size]
            batches.append(batch)
        
        logger.info(f"查询分批完成: {len(all_queries)} 个查询分为 {len(batches)} 批")
        
        return batches
    
    def get_query_priority(self, query: str, main_keyword: str) -> int:
        """
        获取查询优先级，用于排序
        优先级越高，数字越小
        
        Args:
            query: 查询字符串
            main_keyword: 主关键词
            
        Returns:
            int: 优先级数值
        """
        if query == main_keyword:
            return 1  # 最高优先级：基础查询
        
        if query.startswith(main_keyword + " "):
            suffix = query[len(main_keyword) + 1:]
            if len(suffix) == 1:
                return 2  # 高优先级：单字母后缀
            elif len(suffix) == 2:
                return 4  # 中等优先级：双字母后缀
        
        if query.endswith(" " + main_keyword):
            prefix = query[:-(len(main_keyword) + 1)]
            if len(prefix) == 1:
                return 3  # 高优先级：单字母前缀
            elif len(prefix) == 2:
                return 5  # 中等优先级：双字母前缀
        
        return 6  # 最低优先级：其他查询
    
    def sort_queries_by_priority(self, queries: List[str], main_keyword: str) -> List[str]:
        """
        按优先级排序查询列表
        
        Args:
            queries: 查询列表
            main_keyword: 主关键词
            
        Returns:
            List[str]: 排序后的查询列表
        """
        sorted_queries = sorted(
            queries,
            key=lambda q: (
                self.get_query_priority(q, main_keyword),
                q  # 同优先级按字母序排序
            )
        )
        
        logger.debug(f"查询按优先级排序完成，共 {len(sorted_queries)} 个查询")
        
        return sorted_queries


class QueryBatch:
    """查询批次管理器"""
    
    def __init__(self, queries: List[str], batch_id: str = None):
        """
        初始化查询批次
        
        Args:
            queries: 查询列表
            batch_id: 批次ID
        """
        self.queries = queries
        self.batch_id = batch_id or f"batch_{len(queries)}"
        self.completed_queries = set()
        self.failed_queries = set()
        self.results = {}
        
    def mark_completed(self, query: str, result: List[str]):
        """标记查询完成"""
        self.completed_queries.add(query)
        self.results[query] = result
        
    def mark_failed(self, query: str):
        """标记查询失败"""
        self.failed_queries.add(query)
        
    def get_remaining_queries(self) -> List[str]:
        """获取剩余查询"""
        processed = self.completed_queries | self.failed_queries
        remaining = [q for q in self.queries if q not in processed]
        return remaining
    
    def get_progress(self) -> Dict[str, int]:
        """获取执行进度"""
        total = len(self.queries)
        completed = len(self.completed_queries)
        failed = len(self.failed_queries)
        remaining = total - completed - failed
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "remaining": remaining,
            "progress_percent": round((completed + failed) / total * 100, 2) if total > 0 else 0
        }
    
    def get_batch_summary(self) -> str:
        """获取批次摘要信息"""
        progress = self.get_progress()
        return (f"批次 {self.batch_id}: "
                f"{progress['completed']}/{progress['total']} 完成, "
                f"{progress['failed']} 失败, "
                f"{progress['progress_percent']}% 进度")


def create_query_generator(search_settings: Dict = None) -> QueryGenerator:
    """
    创建查询生成器工厂函数
    
    Args:
        search_settings: 搜索设置
        
    Returns:
        QueryGenerator: 查询生成器实例
    """
    return QueryGenerator(search_settings)