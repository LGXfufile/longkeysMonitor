"""
Search Executor Module
搜索执行器模块

Executes Google search queries and retrieves autocomplete suggestions.
"""

import json
import time
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from urllib.parse import quote
import asyncio
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from .anti_spider import AntiSpiderManager
from .query_generator import QueryBatch

logger = logging.getLogger(__name__)


class GoogleSuggestAPI:
    """Google搜索建议API客户端"""
    
    BASE_URL = "http://suggestqueries.google.com/complete/search"
    
    def __init__(self, anti_spider_manager: AntiSpiderManager):
        """
        初始化Google建议API客户端
        
        Args:
            anti_spider_manager: 反爬虫管理器
        """
        self.anti_spider = anti_spider_manager
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_suggestions": 0,
            "start_time": None,
            "end_time": None
        }
        
    def search_suggestions(self, query: str, language: str = "en") -> List[str]:
        """
        获取搜索建议 - 使用Chrome客户端（已验证最有效）
        
        Args:
            query: 搜索查询
            language: 语言代码 (默认en)
            
        Returns:
            List[str]: 建议词列表
        """
        self.stats["total_requests"] += 1
        
        # 使用Chrome客户端（测试证明最有效）
        suggestions = self._get_suggestions_chrome(query, language)
        
        if suggestions:
            self.stats["successful_requests"] += 1
            self.stats["total_suggestions"] += len(suggestions)
            logger.debug(f"查询 '{query}' 获得 {len(suggestions)} 个建议")
        else:
            self.stats["failed_requests"] += 1
            logger.warning(f"查询 '{query}' 未获得建议")
        
        return suggestions
    
    def _get_suggestions_chrome(self, query: str, language: str) -> List[str]:
        """使用Chrome客户端参数"""
        try:
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'chrome',
                'q': query,
                'hl': language
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and isinstance(data[1], list):
                    return [s for s in data[1] if isinstance(s, str)]
            
            return []
            
        except Exception as e:
            logger.debug(f"Chrome方法异常: {e}")
            return []
    
    def _get_suggestions_browser(self, query: str, language: str) -> List[str]:
        """使用浏览器gws-wiz客户端参数"""
        try:
            url = "https://www.google.com/complete/search"
            params = {
                'client': 'gws-wiz',
                'q': query,
                'hl': language,
                'xssi': 't',
                'gs_pcrt': '2'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # gws-wiz返回的格式可能不同，需要特殊处理
                text = response.text
                # 移除XSSI保护前缀
                if text.startswith(')]}\'\n'):
                    text = text[5:]
                
                try:
                    data = json.loads(text)
                    # gws-wiz格式可能是 [query, suggestions, ...] 或其他格式
                    if isinstance(data, list) and len(data) > 1:
                        suggestions = data[1]
                        if isinstance(suggestions, list):
                            return [s[0] if isinstance(s, list) and len(s) > 0 else str(s) 
                                   for s in suggestions if s]
                except json.JSONDecodeError:
                    pass
            
            return []
            
        except Exception as e:
            logger.debug(f"Browser方法异常: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if self.stats["total_requests"] > 0:
            stats["success_rate"] = round(
                self.stats["successful_requests"] / self.stats["total_requests"] * 100, 2
            )
            stats["avg_suggestions_per_query"] = round(
                self.stats["total_suggestions"] / self.stats["successful_requests"], 2
            ) if self.stats["successful_requests"] > 0 else 0
        
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = self.stats["end_time"] - self.stats["start_time"]
            stats["duration_seconds"] = round(duration.total_seconds(), 2)
            stats["queries_per_minute"] = round(
                self.stats["total_requests"] / (duration.total_seconds() / 60), 2
            ) if duration.total_seconds() > 0 else 0
        
        return stats


class SearchExecutor:
    """搜索执行器"""
    
    def __init__(self, anti_spider_manager: AntiSpiderManager, search_settings: Dict = None):
        """
        初始化搜索执行器
        
        Args:
            anti_spider_manager: 反爬虫管理器
            search_settings: 搜索设置
        """
        self.anti_spider = anti_spider_manager
        self.search_settings = search_settings or {}
        self.google_api = GoogleSuggestAPI(anti_spider_manager)
        
        # 支持的语言 - 与原版保持一致，默认使用英文
        self.languages = self.search_settings.get("languages", ["en"])
        
        # 执行状态
        self.is_running = False
        self.should_stop = False
        
        logger.info("搜索执行器初始化完成")
    
    def execute_single_query(self, query: str) -> Dict[str, List[str]]:
        """
        执行单个查询
        
        Args:
            query: 查询字符串
            
        Returns:
            Dict[str, List[str]]: {language: suggestions}
        """
        results = {}
        
        for language in self.languages:
            if self.should_stop:
                break
                
            suggestions = self.google_api.search_suggestions(query, language)
            if suggestions:
                results[language] = suggestions
        
        return results
    
    def execute_query_batch(self, query_batch: QueryBatch, 
                          progress_callback=None) -> Dict[str, Dict[str, List[str]]]:
        """
        执行查询批次
        
        Args:
            query_batch: 查询批次对象
            progress_callback: 进度回调函数 callback(completed, total, current_query)
            
        Returns:
            Dict[str, Dict[str, List[str]]]: 查询结果 {query: {language: suggestions}}
        """
        results = {}
        self.is_running = True
        self.should_stop = False
        
        logger.info(f"开始执行查询批次: {query_batch.batch_id}")
        
        try:
            for i, query in enumerate(query_batch.queries):
                if self.should_stop:
                    logger.info("收到停止信号，中断执行")
                    break
                
                # 执行查询
                query_results = self.execute_single_query(query)
                
                if query_results:
                    # 合并所有语言的建议
                    all_suggestions = []
                    for lang_suggestions in query_results.values():
                        all_suggestions.extend(lang_suggestions)
                    
                    # 去重并保持顺序
                    unique_suggestions = []
                    seen = set()
                    for suggestion in all_suggestions:
                        if suggestion not in seen:
                            seen.add(suggestion)
                            unique_suggestions.append(suggestion)
                    
                    results[query] = unique_suggestions
                    query_batch.mark_completed(query, unique_suggestions)
                    
                    logger.debug(f"查询完成: {query} -> {len(unique_suggestions)} 个建议")
                else:
                    query_batch.mark_failed(query)
                    logger.warning(f"查询失败: {query}")
                
                # 进度回调
                if progress_callback:
                    progress_callback(i + 1, len(query_batch.queries), query)
        
        except KeyboardInterrupt:
            logger.info("用户中断执行")
            self.should_stop = True
        
        except Exception as e:
            logger.error(f"执行查询批次异常: {e}")
        
        finally:
            self.is_running = False
        
        logger.info(f"查询批次执行完成: {len(results)} 个查询成功")
        return results
    
    def execute_queries_parallel(self, queries: List[str], 
                                max_workers: int = 3,
                                progress_callback=None) -> Dict[str, List[str]]:
        """
        并行执行查询
        
        Args:
            queries: 查询列表
            max_workers: 最大并行工作线程数
            progress_callback: 进度回调函数
            
        Returns:
            Dict[str, List[str]]: 查询结果
        """
        results = {}
        self.is_running = True
        self.should_stop = False
        completed = 0
        
        logger.info(f"开始并行执行 {len(queries)} 个查询，最大并行数: {max_workers}")
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交任务
                future_to_query = {
                    executor.submit(self.execute_single_query, query): query
                    for query in queries
                }
                
                # 收集结果
                for future in as_completed(future_to_query):
                    if self.should_stop:
                        logger.info("收到停止信号，取消剩余任务")
                        for f in future_to_query:
                            f.cancel()
                        break
                    
                    query = future_to_query[future]
                    completed += 1
                    
                    try:
                        query_results = future.result(timeout=30)
                        
                        if query_results:
                            # 合并所有语言的建议
                            all_suggestions = []
                            for lang_suggestions in query_results.values():
                                all_suggestions.extend(lang_suggestions)
                            
                            # 去重
                            unique_suggestions = list(set(all_suggestions))
                            results[query] = unique_suggestions
                            
                            logger.debug(f"并行查询完成: {query} -> {len(unique_suggestions)} 个建议")
                        
                    except Exception as e:
                        logger.error(f"并行查询 '{query}' 异常: {e}")
                    
                    # 进度回调
                    if progress_callback:
                        progress_callback(completed, len(queries), query)
        
        except KeyboardInterrupt:
            logger.info("用户中断并行执行")
            self.should_stop = True
        
        finally:
            self.is_running = False
        
        logger.info(f"并行查询执行完成: {len(results)} 个查询成功")
        return results
    
    async def execute_queries_async(self, queries: List[str],
                                   concurrent_limit: int = 5,
                                   progress_callback=None) -> Dict[str, List[str]]:
        """
        异步执行查询
        
        Args:
            queries: 查询列表
            concurrent_limit: 并发限制
            progress_callback: 进度回调函数
            
        Returns:
            Dict[str, List[str]]: 查询结果
        """
        results = {}
        completed = 0
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        logger.info(f"开始异步执行 {len(queries)} 个查询，并发限制: {concurrent_limit}")
        
        async def execute_single_async(session: aiohttp.ClientSession, query: str) -> Tuple[str, List[str]]:
            async with semaphore:
                nonlocal completed
                
                try:
                    all_suggestions = []
                    
                    for language in self.languages:
                        params = {
                            'client': 'firefox',
                            'q': query,
                            'hl': language,
                        }
                        
                        async with session.get(
                            GoogleSuggestAPI.BASE_URL,
                            params=params,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                suggestions = self.google_api._parse_suggestions(data)
                                all_suggestions.extend(suggestions)
                    
                    # 去重
                    unique_suggestions = list(set(all_suggestions))
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(queries), query)
                    
                    return query, unique_suggestions
                
                except Exception as e:
                    logger.error(f"异步查询 '{query}' 异常: {e}")
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, len(queries), query)
                    return query, []
        
        try:
            # 设置请求头
            headers = {
                'User-Agent': self.anti_spider.user_agent_rotator.get_random_user_agent()
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                tasks = [execute_single_async(session, query) for query in queries]
                query_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in query_results:
                    if isinstance(result, tuple):
                        query, suggestions = result
                        if suggestions:
                            results[query] = suggestions
        
        except Exception as e:
            logger.error(f"异步执行异常: {e}")
        
        logger.info(f"异步查询执行完成: {len(results)} 个查询成功")
        return results
    
    def stop_execution(self):
        """停止执行"""
        self.should_stop = True
        logger.info("搜索执行器收到停止信号")
    
    def get_execution_stats(self) -> Dict:
        """获取执行统计"""
        stats = self.google_api.get_stats()
        
        # 添加反爬虫统计
        anti_spider_stats = self.anti_spider.get_statistics()
        stats["anti_spider"] = anti_spider_stats
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.google_api.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_suggestions": 0,
            "start_time": None,
            "end_time": None
        }
        logger.info("执行统计已重置")


class SearchSession:
    """搜索会话管理器"""
    
    def __init__(self, executor: SearchExecutor, main_keyword: str):
        """
        初始化搜索会话
        
        Args:
            executor: 搜索执行器
            main_keyword: 主关键词
        """
        self.executor = executor
        self.main_keyword = main_keyword
        self.session_id = f"session_{main_keyword}_{int(time.time())}"
        self.start_time = None
        self.end_time = None
        self.results = {}
        
    def __enter__(self):
        """进入会话上下文"""
        self.start_time = datetime.now()
        self.executor.google_api.stats["start_time"] = self.start_time
        logger.info(f"搜索会话开始: {self.session_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出会话上下文"""
        self.end_time = datetime.now()
        self.executor.google_api.stats["end_time"] = self.end_time
        
        duration = self.end_time - self.start_time
        logger.info(f"搜索会话结束: {self.session_id}, 耗时: {duration}")
        
        if exc_type:
            logger.error(f"搜索会话异常退出: {exc_type.__name__}: {exc_val}")
    
    def execute_queries(self, queries: List[str], 
                       execution_mode: str = "sequential",
                       progress_callback=None) -> Dict[str, List[str]]:
        """
        执行查询列表
        
        Args:
            queries: 查询列表
            execution_mode: 执行模式 ("sequential", "parallel", "async")
            progress_callback: 进度回调
            
        Returns:
            Dict[str, List[str]]: 查询结果
        """
        logger.info(f"会话 {self.session_id} 开始执行 {len(queries)} 个查询，模式: {execution_mode}")
        
        if execution_mode == "parallel":
            self.results = self.executor.execute_queries_parallel(
                queries, progress_callback=progress_callback
            )
        elif execution_mode == "async":
            self.results = asyncio.run(
                self.executor.execute_queries_async(
                    queries, progress_callback=progress_callback
                )
            )
        else:  # sequential
            query_batch = QueryBatch(queries, self.session_id)
            self.results = self.executor.execute_query_batch(
                query_batch, progress_callback=progress_callback
            )
        
        return self.results
    
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        summary = {
            "session_id": self.session_id,
            "main_keyword": self.main_keyword,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_queries": len(self.results),
            "total_suggestions": sum(len(suggestions) for suggestions in self.results.values()),
            "execution_stats": self.executor.get_execution_stats()
        }
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            summary["duration_seconds"] = duration.total_seconds()
        
        return summary


def create_search_executor(anti_spider_manager: AntiSpiderManager, 
                          search_settings: Dict = None) -> SearchExecutor:
    """
    创建搜索执行器工厂函数
    
    Args:
        anti_spider_manager: 反爬虫管理器
        search_settings: 搜索设置
        
    Returns:
        SearchExecutor: 搜索执行器实例
    """
    return SearchExecutor(anti_spider_manager, search_settings)