"""
Main Entry Point
主入口文件

Google Long-tail Keyword Monitor main application.
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from src.config_manager import ConfigManager
from src.query_generator import QueryGenerator
from src.anti_spider import AntiSpiderManager
from src.search_executor import SearchExecutor, SearchSession
from src.data_processor import DataProcessor
from src.compare_analyzer import CompareAnalyzer
from src.feishu_notifier import FeishuNotifier

# 配置日志
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """设置日志配置"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 创建logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)


class KeywordMonitor:
    """关键词监控主类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化关键词监控器
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        
        # 初始化数据处理器
        self.data_processor = DataProcessor()
        
        # 初始化对比分析器
        self.compare_analyzer = CompareAnalyzer(self.data_processor)
        
        # 初始化飞书通知器
        self.feishu_notifier = FeishuNotifier(
            self.config_manager.get_feishu_webhook(),
            self.config.get("notification_settings", {})
        )
        
        self.logger.info("关键词监控器初始化完成")
    
    def run_single_keyword(self, main_keyword: str, execution_mode: str = "sequential") -> bool:
        """
        执行单个关键词监控
        
        Args:
            main_keyword: 主关键词
            execution_mode: 执行模式
            
        Returns:
            bool: 执行是否成功
        """
        self.logger.info(f"开始监控关键词: {main_keyword}")
        
        try:
            # 初始化反爬虫管理器
            anti_spider = AntiSpiderManager(
                self.config_manager.get_proxy_settings(),
                self.config_manager.get_request_settings()
            )
            
            # 初始化搜索执行器
            search_executor = SearchExecutor(
                anti_spider,
                self.config_manager.get_search_settings()
            )
            
            # 初始化查询生成器
            query_generator = QueryGenerator(
                self.config_manager.get_search_settings()
            )
            
            # 生成查询列表
            queries = query_generator.generate_all_queries(main_keyword)
            self.logger.info(f"生成了 {len(queries)} 个查询")
            
            # 进度回调函数
            def progress_callback(completed: int, total: int, current_query: str):
                progress = completed / total * 100
                self.logger.info(f"执行进度: {completed}/{total} ({progress:.1f}%) - 当前查询: {current_query}")
            
            # 使用搜索会话执行查询
            with SearchSession(search_executor, main_keyword) as session:
                results = session.execute_queries(
                    queries,
                    execution_mode=execution_mode,
                    progress_callback=progress_callback
                )
                
                execution_stats = session.get_session_summary()
            
            if not results:
                self.logger.error(f"未获取到任何结果: {main_keyword}")
                self.feishu_notifier.send_error_notification(
                    main_keyword,
                    "未获取到任何搜索结果，请检查网络连接和配置",
                    execution_stats.get("execution_stats", {})
                )
                return False
            
            self.logger.info(f"查询完成，获得 {len(results)} 个结果")
            
            # 创建关键词数据
            keyword_data = self.data_processor.create_keyword_data(
                main_keyword,
                results,
                execution_stats.get("execution_stats", {})
            )
            
            # 保存数据
            file_path = self.data_processor.save_keyword_data(keyword_data)
            
            # 对比分析
            comparison_result = self.compare_analyzer.compare_with_previous_day(keyword_data)
            
            # 保存对比结果（如果存在对比数据）
            comparison_file = None
            business_report_file = None
            if comparison_result:
                comparison_file = self.data_processor.save_comparison_result(comparison_result)
                
                # 自动执行商业价值分析
                self.logger.info(f"检测到关键词变化，开始商业价值分析...")
                business_report_file = self._run_business_analysis(comparison_file)
            
            # 发送成功通知
            self.feishu_notifier.send_success_notification(
                keyword_data,
                comparison_result,
                file_path,
                comparison_file,
                business_report_file
            )
            
            self.logger.info(f"关键词监控完成: {main_keyword}")
            return True
        
        except KeyboardInterrupt:
            self.logger.info("用户中断执行")
            search_executor.stop_execution()
            return False
        
        except Exception as e:
            self.logger.error(f"执行关键词监控异常: {e}")
            self.feishu_notifier.send_error_notification(
                main_keyword,
                f"执行异常: {str(e)}",
                {}
            )
            return False
    
    def run_all_keywords(self, execution_mode: str = "sequential") -> Dict[str, bool]:
        """
        执行所有启用的关键词监控
        
        Args:
            execution_mode: 执行模式
            
        Returns:
            Dict[str, bool]: 每个关键词的执行结果
        """
        enabled_keywords = self.config_manager.get_enabled_keywords()
        
        if not enabled_keywords:
            self.logger.warning("没有启用的关键词")
            return {}
        
        self.logger.info(f"开始批量监控 {len(enabled_keywords)} 个关键词")
        
        results = {}
        successful_count = 0
        
        for keyword_config in enabled_keywords:
            main_keyword = keyword_config["main_keyword"]
            
            try:
                success = self.run_single_keyword(main_keyword, execution_mode)
                results[main_keyword] = success
                
                if success:
                    successful_count += 1
            
            except Exception as e:
                self.logger.error(f"关键词 {main_keyword} 执行异常: {e}")
                results[main_keyword] = False
        
        # 发送每日摘要
        daily_stats = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "total_keywords": len(enabled_keywords),
            "successful_executions": successful_count,
            "failed_executions": len(enabled_keywords) - successful_count,
            "data_files_created": successful_count
        }
        
        self.feishu_notifier.send_daily_summary(daily_stats)
        
        self.logger.info(f"批量监控完成: {successful_count}/{len(enabled_keywords)} 成功")
        
        return results
    
    def test_configuration(self) -> bool:
        """测试配置"""
        self.logger.info("开始测试配置...")
        
        success = True
        
        # 测试飞书webhook
        if not self.feishu_notifier.test_webhook():
            self.logger.error("飞书webhook测试失败")
            success = False
        
        # 测试数据目录
        try:
            test_data = self.data_processor.create_keyword_data(
                "test",
                {"test query": ["test suggestion"]},
                {}
            )
            test_file = self.data_processor.save_keyword_data(test_data)
            
            # 删除测试文件
            os.unlink(test_file)
            self.logger.info("数据存储测试通过")
        
        except Exception as e:
            self.logger.error(f"数据存储测试失败: {e}")
            success = False
        
        # 测试反爬虫设置
        try:
            anti_spider = AntiSpiderManager(
                self.config_manager.get_proxy_settings(),
                self.config_manager.get_request_settings()
            )
            
            stats = anti_spider.get_statistics()
            self.logger.info(f"反爬虫设置测试通过: {stats}")
        
        except Exception as e:
            self.logger.error(f"反爬虫设置测试失败: {e}")
            success = False
        
        if success:
            self.logger.info("所有配置测试通过")
        else:
            self.logger.error("配置测试失败，请检查配置")
        
        return success
    
    def cleanup_old_data(self, retention_days: int = None):
        """清理旧数据"""
        if retention_days is None:
            retention_days = self.config.get("storage_settings", {}).get("data_retention_days", 30)
        
        self.logger.info(f"清理 {retention_days} 天前的数据...")
        self.data_processor.cleanup_old_files(retention_days)
    
    def export_keyword_data(self, main_keyword: str, start_date: str = None, 
                          end_date: str = None, format_type: str = "json") -> str:
        """导出关键词数据"""
        self.logger.info(f"导出关键词数据: {main_keyword}")
        
        export_file = self.data_processor.export_data(
            main_keyword, start_date, end_date, format_type
        )
        
        if export_file:
            self.logger.info(f"数据导出完成: {export_file}")
        else:
            self.logger.error("数据导出失败")
        
        return export_file
    
    def _run_business_analysis(self, comparison_file: str) -> Optional[str]:
        """
        执行商业价值分析
        
        Args:
            comparison_file: 对比结果文件路径
            
        Returns:
            Optional[str]: 生成的HTML报告文件路径，失败返回None
        """
        try:
            import subprocess
            import os
            
            # 确保comparison_file存在
            if not os.path.exists(comparison_file):
                self.logger.error(f"对比文件不存在: {comparison_file}")
                return None
            
            # 构建项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # 构建商业分析脚本路径
            business_analyzer_path = os.path.join(current_dir, "business_analyzer.py")
            reports_dir = os.path.join(project_root, "reports")
            
            # 确保reports目录存在
            os.makedirs(reports_dir, exist_ok=True)
            
            self.logger.info(f"启动商业价值分析: {comparison_file}")
            
            # 执行商业分析脚本
            cmd = [
                "python3", 
                business_analyzer_path, 
                comparison_file, 
                "-o", reports_dir,
                "-v"
            ]
            
            # 在项目根目录执行
            result = subprocess.run(
                cmd, 
                cwd=project_root,
                capture_output=True, 
                text=True, 
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                # 解析输出，查找生成的HTML文件路径
                output_lines = result.stdout.split('\n')
                html_file = None
                
                for line in output_lines:
                    if "报告已保存:" in line or "HTML报告已生成:" in line:
                        # 提取文件路径
                        html_file = line.split(":")[1].strip() if ":" in line else None
                        break
                
                # 如果没有从输出中找到，尝试查找最新的HTML文件
                if not html_file:
                    import glob
                    pattern = os.path.join(reports_dir, "business_analysis_*.html")
                    html_files = glob.glob(pattern)
                    if html_files:
                        # 按修改时间排序，取最新的
                        html_files.sort(key=os.path.getmtime, reverse=True)
                        html_file = html_files[0]
                
                if html_file and os.path.exists(html_file):
                    self.logger.info(f"商业价值分析完成: {html_file}")
                    return html_file
                else:
                    self.logger.warning("商业价值分析完成，但未找到生成的HTML文件")
                    return None
            else:
                self.logger.error(f"商业价值分析失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("商业价值分析超时")
            return None
        except Exception as e:
            self.logger.error(f"执行商业价值分析异常: {e}")
            return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Google Long-tail Keyword Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py run                    # 执行所有关键词监控
  python main.py run -k "AI写作"        # 执行单个关键词监控
  python main.py test                   # 测试配置
  python main.py cleanup                # 清理旧数据
  python main.py export -k "AI写作"     # 导出数据
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # run命令
    run_parser = subparsers.add_parser("run", help="执行关键词监控")
    run_parser.add_argument("-k", "--keyword", help="指定单个关键词")
    run_parser.add_argument("-m", "--mode", choices=["sequential", "parallel", "async"], 
                           default="sequential", help="执行模式")
    
    # test命令
    test_parser = subparsers.add_parser("test", help="测试配置")
    
    # cleanup命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理旧数据")
    cleanup_parser.add_argument("-d", "--days", type=int, default=30, 
                               help="保留天数，默认30天")
    
    # export命令
    export_parser = subparsers.add_parser("export", help="导出数据")
    export_parser.add_argument("-k", "--keyword", required=True, help="关键词")
    export_parser.add_argument("-s", "--start", help="开始日期 YYYY-MM-DD")
    export_parser.add_argument("-e", "--end", help="结束日期 YYYY-MM-DD")
    export_parser.add_argument("-f", "--format", choices=["json", "csv"], 
                              default="json", help="导出格式")
    
    # 全局参数
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--log-file", help="日志文件路径")
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = "DEBUG" if args.verbose else "INFO"
    log_file = args.log_file
    
    if not log_file and args.command:
        # 自动生成日志文件名
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(project_root, "logs")
        timestamp = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(logs_dir, f"monitor_{timestamp}.log")
    
    setup_logging(log_level, log_file)
    
    logger = logging.getLogger(__name__)
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # 初始化监控器
        monitor = KeywordMonitor(args.config)
        
        if args.command == "run":
            if args.keyword:
                # 执行单个关键词
                success = monitor.run_single_keyword(args.keyword, args.mode)
                sys.exit(0 if success else 1)
            else:
                # 执行所有关键词
                results = monitor.run_all_keywords(args.mode)
                failed_count = sum(1 for success in results.values() if not success)
                sys.exit(0 if failed_count == 0 else 1)
        
        elif args.command == "test":
            success = monitor.test_configuration()
            sys.exit(0 if success else 1)
        
        elif args.command == "cleanup":
            monitor.cleanup_old_data(args.days)
        
        elif args.command == "export":
            export_file = monitor.export_keyword_data(
                args.keyword, args.start, args.end, args.format
            )
            sys.exit(0 if export_file else 1)
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"程序执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()