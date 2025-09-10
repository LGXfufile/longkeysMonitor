"""
Data Processor Module
数据处理器模块

Handles data storage, processing, and management.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import logging
import re
from pathlib import Path
import glob
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class KeywordData:
    """关键词数据结构"""
    main_keyword: str
    execution_date: str
    execution_time: str
    total_queries: int
    successful_queries: int
    failed_queries: int
    execution_duration: str
    total_keywords_found: int
    unique_keywords: int
    average_suggestions_per_query: float
    query_results: Dict[str, List[str]]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'KeywordData':
        """从字典创建实例"""
        return cls(**data)


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, data_dir: str = None):
        """
        初始化数据处理器
        
        Args:
            data_dir: 数据存储目录
        """
        if data_dir is None:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            data_dir = os.path.join(project_root, "data")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据处理器初始化，数据目录: {self.data_dir}")
    
    def save_keyword_data(self, keyword_data: KeywordData) -> str:
        """
        保存关键词数据
        
        Args:
            keyword_data: 关键词数据
            
        Returns:
            str: 保存的文件路径
        """
        # 生成文件名：YYYY-MM-DD_主关键词.json
        safe_keyword = self._sanitize_filename(keyword_data.main_keyword)
        filename = f"{keyword_data.execution_date}_{safe_keyword}.json"
        file_path = self.data_dir / filename
        
        try:
            # 准备保存数据
            save_data = {
                "metadata": {
                    "main_keyword": keyword_data.main_keyword,
                    "execution_date": keyword_data.execution_date,
                    "execution_time": keyword_data.execution_time,
                    "total_queries": keyword_data.total_queries,
                    "successful_queries": keyword_data.successful_queries,
                    "failed_queries": keyword_data.failed_queries,
                    "execution_duration": keyword_data.execution_duration,
                    "file_version": "1.0",
                    "created_at": datetime.now().isoformat()
                },
                "query_results": keyword_data.query_results,
                "statistics": {
                    "total_keywords_found": keyword_data.total_keywords_found,
                    "unique_keywords": keyword_data.unique_keywords,
                    "average_suggestions_per_query": keyword_data.average_suggestions_per_query,
                    "queries_with_results": len([q for q, r in keyword_data.query_results.items() if r]),
                    "empty_queries": len([q for q, r in keyword_data.query_results.items() if not r])
                }
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"关键词数据已保存: {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"保存关键词数据失败: {e}")
            raise
    
    def load_keyword_data(self, file_path: str) -> Optional[KeywordData]:
        """
        加载关键词数据
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            Optional[KeywordData]: 关键词数据，加载失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析数据结构
            metadata = data.get("metadata", {})
            query_results = data.get("query_results", {})
            statistics = data.get("statistics", {})
            
            keyword_data = KeywordData(
                main_keyword=metadata.get("main_keyword", ""),
                execution_date=metadata.get("execution_date", ""),
                execution_time=metadata.get("execution_time", ""),
                total_queries=metadata.get("total_queries", 0),
                successful_queries=metadata.get("successful_queries", 0),
                failed_queries=metadata.get("failed_queries", 0),
                execution_duration=metadata.get("execution_duration", ""),
                total_keywords_found=statistics.get("total_keywords_found", 0),
                unique_keywords=statistics.get("unique_keywords", 0),
                average_suggestions_per_query=statistics.get("average_suggestions_per_query", 0.0),
                query_results=query_results
            )
            
            logger.debug(f"关键词数据加载成功: {file_path}")
            return keyword_data
        
        except Exception as e:
            logger.error(f"加载关键词数据失败: {file_path}, 错误: {e}")
            return None
    
    def get_latest_data(self, main_keyword: str, days_back: int = 7) -> Optional[KeywordData]:
        """
        获取指定关键词的最新数据
        
        Args:
            main_keyword: 主关键词
            days_back: 向前查找的天数
            
        Returns:
            Optional[KeywordData]: 最新的关键词数据
        """
        safe_keyword = self._sanitize_filename(main_keyword)
        
        # 查找最近几天的数据文件
        for i in range(days_back):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            pattern = f"{date}_{safe_keyword}.json"
            file_path = self.data_dir / pattern
            
            if file_path.exists():
                data = self.load_keyword_data(str(file_path))
                if data:
                    return data
        
        logger.warning(f"未找到关键词 '{main_keyword}' 在最近 {days_back} 天的数据")
        return None
    
    def get_previous_day_data(self, main_keyword: str, current_date: str = None) -> Optional[KeywordData]:
        """
        获取前一天的数据
        
        Args:
            main_keyword: 主关键词
            current_date: 当前日期，格式 YYYY-MM-DD
            
        Returns:
            Optional[KeywordData]: 前一天的数据
        """
        if current_date is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            current = datetime.strptime(current_date, '%Y-%m-%d')
            previous_date = (current - timedelta(days=1)).strftime('%Y-%m-%d')
            
            safe_keyword = self._sanitize_filename(main_keyword)
            file_path = self.data_dir / f"{previous_date}_{safe_keyword}.json"
            
            if file_path.exists():
                return self.load_keyword_data(str(file_path))
        
        except Exception as e:
            logger.error(f"获取前一天数据失败: {e}")
        
        return None
    
    def list_data_files(self, main_keyword: str = None, limit: int = None) -> List[Dict]:
        """
        列出数据文件
        
        Args:
            main_keyword: 过滤特定关键词，None表示所有关键词
            limit: 限制返回数量
            
        Returns:
            List[Dict]: 文件信息列表
        """
        files = []
        
        if main_keyword:
            safe_keyword = self._sanitize_filename(main_keyword)
            pattern = f"*_{safe_keyword}.json"
        else:
            pattern = "*.json"
        
        for file_path in self.data_dir.glob(pattern):
            try:
                stat = file_path.stat()
                file_info = {
                    "file_path": str(file_path),
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created_time": datetime.fromtimestamp(stat.st_ctime),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime)
                }
                
                # 解析文件名获取关键词和日期
                name_parts = file_path.stem.split('_', 1)
                if len(name_parts) >= 2:
                    file_info["date"] = name_parts[0]
                    file_info["keyword"] = name_parts[1]
                
                files.append(file_info)
            
            except Exception as e:
                logger.warning(f"读取文件信息失败: {file_path}, 错误: {e}")
        
        # 按修改时间倒序排序
        files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        if limit:
            files = files[:limit]
        
        return files
    
    def extract_all_keywords(self, keyword_data: KeywordData) -> Set[str]:
        """
        提取所有关键词建议
        
        Args:
            keyword_data: 关键词数据
            
        Returns:
            Set[str]: 所有关键词集合
        """
        all_keywords = set()
        
        for query, suggestions in keyword_data.query_results.items():
            if isinstance(suggestions, list):
                for suggestion in suggestions:
                    if isinstance(suggestion, str) and suggestion.strip():
                        all_keywords.add(suggestion.strip())
        
        return all_keywords
    
    def clean_and_deduplicate_keywords(self, keywords: List[str]) -> List[str]:
        """
        清理和去重关键词
        
        Args:
            keywords: 原始关键词列表
            
        Returns:
            List[str]: 清理后的关键词列表
        """
        cleaned = set()
        
        for keyword in keywords:
            if not isinstance(keyword, str):
                continue
            
            # 基础清理
            keyword = keyword.strip()
            if not keyword:
                continue
            
            # 移除过长的关键词
            if len(keyword) > 200:
                continue
            
            # 移除包含特殊字符的关键词
            if re.search(r'[<>&"\']', keyword):
                continue
            
            # 转换为小写进行去重
            keyword_lower = keyword.lower()
            if keyword_lower not in cleaned:
                cleaned.add(keyword)
        
        return list(cleaned)
    
    def calculate_statistics(self, query_results: Dict[str, List[str]]) -> Dict:
        """
        计算统计信息
        
        Args:
            query_results: 查询结果
            
        Returns:
            Dict: 统计信息
        """
        # 统计查询数量
        total_queries = len(query_results)
        successful_queries = len([q for q, r in query_results.items() if r])
        failed_queries = total_queries - successful_queries
        
        # 统计关键词
        all_keywords = []
        for suggestions in query_results.values():
            if suggestions:
                all_keywords.extend(suggestions)
        
        unique_keywords = len(set(all_keywords))
        total_keywords_found = len(all_keywords)
        
        # 计算平均值
        avg_suggestions_per_query = (
            total_keywords_found / successful_queries 
            if successful_queries > 0 else 0
        )
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "total_keywords_found": total_keywords_found,
            "unique_keywords": unique_keywords,
            "average_suggestions_per_query": round(avg_suggestions_per_query, 2),
            "success_rate": round(successful_queries / total_queries * 100, 2) if total_queries > 0 else 0
        }
    
    def create_keyword_data(self, main_keyword: str, query_results: Dict[str, List[str]], 
                           execution_stats: Dict = None) -> KeywordData:
        """
        创建关键词数据对象
        
        Args:
            main_keyword: 主关键词
            query_results: 查询结果
            execution_stats: 执行统计
            
        Returns:
            KeywordData: 关键词数据对象
        """
        now = datetime.now()
        execution_date = now.strftime('%Y-%m-%d')
        execution_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算统计信息
        stats = self.calculate_statistics(query_results)
        
        # 计算执行时长
        execution_duration = "00:00:00"
        if execution_stats and "duration_seconds" in execution_stats:
            seconds = int(execution_stats["duration_seconds"])
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            execution_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        keyword_data = KeywordData(
            main_keyword=main_keyword,
            execution_date=execution_date,
            execution_time=execution_time,
            total_queries=stats["total_queries"],
            successful_queries=stats["successful_queries"],
            failed_queries=stats["failed_queries"],
            execution_duration=execution_duration,
            total_keywords_found=stats["total_keywords_found"],
            unique_keywords=stats["unique_keywords"],
            average_suggestions_per_query=stats["average_suggestions_per_query"],
            query_results=query_results
        )
        
        return keyword_data
    
    def cleanup_old_files(self, retention_days: int = 30):
        """
        清理旧的数据文件
        
        Args:
            retention_days: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        for file_path in self.data_dir.glob("*.json"):
            try:
                # 从文件名解析日期
                date_str = file_path.stem.split('_')[0]
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"已删除过期文件: {file_path.name}")
            
            except Exception as e:
                logger.warning(f"处理文件 {file_path.name} 时出错: {e}")
        
        logger.info(f"清理完成，删除了 {deleted_count} 个过期文件")
    
    def export_data(self, main_keyword: str, start_date: str = None, 
                   end_date: str = None, format_type: str = "json") -> Optional[str]:
        """
        导出数据
        
        Args:
            main_keyword: 主关键词
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            format_type: 导出格式 ("json", "csv")
            
        Returns:
            Optional[str]: 导出文件路径
        """
        try:
            safe_keyword = self._sanitize_filename(main_keyword)
            
            # 获取文件列表
            files = self.list_data_files(main_keyword)
            
            # 按日期过滤
            if start_date or end_date:
                filtered_files = []
                for file_info in files:
                    file_date = file_info.get("date")
                    if file_date:
                        if start_date and file_date < start_date:
                            continue
                        if end_date and file_date > end_date:
                            continue
                    filtered_files.append(file_info)
                files = filtered_files
            
            if not files:
                logger.warning(f"没有找到符合条件的数据文件")
                return None
            
            # 导出文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"export_{safe_keyword}_{timestamp}.{format_type}"
            export_path = self.data_dir / export_filename
            
            if format_type == "json":
                export_data = []
                for file_info in files:
                    data = self.load_keyword_data(file_info["file_path"])
                    if data:
                        export_data.append(data.to_dict())
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            elif format_type == "csv":
                # CSV导出需要pandas库
                try:
                    import pandas as pd
                    
                    rows = []
                    for file_info in files:
                        data = self.load_keyword_data(file_info["file_path"])
                        if data:
                            for query, suggestions in data.query_results.items():
                                for suggestion in suggestions:
                                    rows.append({
                                        "date": data.execution_date,
                                        "main_keyword": data.main_keyword,
                                        "query": query,
                                        "suggestion": suggestion
                                    })
                    
                    df = pd.DataFrame(rows)
                    df.to_csv(export_path, index=False, encoding='utf-8-sig')
                    
                except ImportError:
                    logger.error("CSV导出需要安装pandas库")
                    return None
            
            logger.info(f"数据导出完成: {export_path}")
            return str(export_path)
        
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return None
    
    def save_comparison_result(self, comparison_result) -> str:
        """
        保存对比结果
        
        Args:
            comparison_result: ComparisonResult对象
            
        Returns:
            str: 保存的文件路径
        """
        # 生成文件名：YYYY-MM-DD_主关键词_changes.json
        safe_keyword = self._sanitize_filename(comparison_result.main_keyword)
        filename = f"{comparison_result.current_date}_{safe_keyword}_changes.json"
        file_path = self.data_dir / filename
        
        try:
            # 准备保存数据
            save_data = {
                "metadata": {
                    "main_keyword": comparison_result.main_keyword,
                    "current_date": comparison_result.current_date,
                    "previous_date": comparison_result.previous_date,
                    "analysis_time": datetime.now().isoformat(),
                    "file_version": "1.0"
                },
                "statistics": {
                    "total_current": comparison_result.total_current,
                    "total_previous": comparison_result.total_previous,
                    "new_count": comparison_result.new_count,
                    "disappeared_count": comparison_result.disappeared_count,
                    "stable_count": comparison_result.stable_count,
                    "change_rate": comparison_result.change_rate
                },
                "changes": {
                    "new_keywords": comparison_result.new_keywords,
                    "disappeared_keywords": comparison_result.disappeared_keywords,
                    "stable_keywords": comparison_result.stable_keywords
                }
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"对比结果已保存: {file_path}")
            logger.info(f"新增关键词: {comparison_result.new_count} 个")
            logger.info(f"消失关键词: {comparison_result.disappeared_count} 个")
            
            return str(file_path)
        
        except Exception as e:
            logger.error(f"保存对比结果失败: {e}")
            raise
    
    def load_comparison_result(self, file_path: str) -> Optional[Dict]:
        """
        加载对比结果
        
        Args:
            file_path: 对比结果文件路径
            
        Returns:
            Optional[Dict]: 对比结果数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"对比结果加载成功: {file_path}")
            return data
        
        except Exception as e:
            logger.error(f"加载对比结果失败: {file_path}, 错误: {e}")
            return None
    
    def list_comparison_files(self, main_keyword: str = None, limit: int = None) -> List[Dict]:
        """
        列出对比结果文件
        
        Args:
            main_keyword: 过滤特定关键词，None表示所有关键词
            limit: 限制返回数量
            
        Returns:
            List[Dict]: 文件信息列表
        """
        files = []
        
        if main_keyword:
            safe_keyword = self._sanitize_filename(main_keyword)
            pattern = f"*_{safe_keyword}_changes.json"
        else:
            pattern = "*_changes.json"
        
        for file_path in self.data_dir.glob(pattern):
            try:
                stat = file_path.stat()
                file_info = {
                    "file_path": str(file_path),
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created_time": datetime.fromtimestamp(stat.st_ctime),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime)
                }
                
                # 解析文件名获取关键词和日期
                name_parts = file_path.stem.split('_')
                if len(name_parts) >= 3 and name_parts[-1] == 'changes':
                    file_info["date"] = name_parts[0]
                    file_info["keyword"] = '_'.join(name_parts[1:-1])
                
                files.append(file_info)
            
            except Exception as e:
                logger.warning(f"读取对比文件信息失败: {file_path}, 错误: {e}")
        
        # 按修改时间倒序排序
        files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        if limit:
            files = files[:limit]
        
        return files
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        # 替换非法字符为下划线
        sanitized = re.sub(r'[<>:"/\\|?*\s]', '_', filename)
        # 移除多个连续下划线
        sanitized = re.sub(r'_+', '_', sanitized)
        # 移除开头结尾的下划线
        sanitized = sanitized.strip('_')
        # 限制长度
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized


def create_data_processor(data_dir: str = None) -> DataProcessor:
    """
    创建数据处理器工厂函数
    
    Args:
        data_dir: 数据目录
        
    Returns:
        DataProcessor: 数据处理器实例
    """
    return DataProcessor(data_dir)