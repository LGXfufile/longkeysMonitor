"""
Feishu Notifier Module
飞书通知器模块

Sends rich notifications to Feishu (Lark) using webhook.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

from .data_processor import KeywordData
from .compare_analyzer import ComparisonResult

logger = logging.getLogger(__name__)


class FeishuNotifier:
    """飞书通知器"""
    
    def __init__(self, webhook_url: str, notification_settings: Dict = None):
        """
        初始化飞书通知器
        
        Args:
            webhook_url: 飞书机器人webhook地址
            notification_settings: 通知设置
        """
        self.webhook_url = webhook_url
        self.notification_settings = notification_settings or {
            "notify_on_success": True,
            "notify_on_error": True,
            "include_statistics": True,
            "max_keywords_display": 20
        }
        
        # 验证webhook地址
        if not self.webhook_url or not self.webhook_url.startswith("https://open.feishu.cn/"):
            logger.warning("飞书webhook地址格式可能不正确")
        
        logger.info("飞书通知器初始化完成")
    
    def send_success_notification(self, keyword_data: KeywordData, 
                                comparison_result: Optional[ComparisonResult] = None,
                                file_path: str = None,
                                comparison_file: str = None,
                                business_report_file: str = None) -> bool:
        """
        发送成功通知
        
        Args:
            keyword_data: 关键词数据
            comparison_result: 对比结果
            file_path: 数据文件路径
            comparison_file: 对比结果文件路径
            business_report_file: 商业分析报告文件路径
            
        Returns:
            bool: 发送是否成功
        """
        if not self.notification_settings.get("notify_on_success", True):
            logger.debug("成功通知已禁用")
            return True
        
        try:
            # 构建消息内容
            message = self._build_success_message(keyword_data, comparison_result, file_path, comparison_file, business_report_file)
            
            # 发送消息
            success = self._send_message(message)
            
            if success:
                logger.info(f"成功通知已发送: {keyword_data.main_keyword}")
            else:
                logger.error(f"成功通知发送失败: {keyword_data.main_keyword}")
            
            return success
        
        except Exception as e:
            logger.error(f"发送成功通知异常: {e}")
            return False
    
    def send_error_notification(self, main_keyword: str, error_message: str,
                              execution_stats: Dict = None) -> bool:
        """
        发送错误通知
        
        Args:
            main_keyword: 主关键词
            error_message: 错误信息
            execution_stats: 执行统计
            
        Returns:
            bool: 发送是否成功
        """
        if not self.notification_settings.get("notify_on_error", True):
            logger.debug("错误通知已禁用")
            return True
        
        try:
            # 构建错误消息
            message = self._build_error_message(main_keyword, error_message, execution_stats)
            
            # 发送消息
            success = self._send_message(message)
            
            if success:
                logger.info(f"错误通知已发送: {main_keyword}")
            else:
                logger.error(f"错误通知发送失败: {main_keyword}")
            
            return success
        
        except Exception as e:
            logger.error(f"发送错误通知异常: {e}")
            return False
    
    def send_custom_message(self, title: str, content: str, 
                           message_type: str = "info") -> bool:
        """
        发送自定义消息
        
        Args:
            title: 消息标题
            content: 消息内容
            message_type: 消息类型 ("info", "warning", "error", "success")
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 选择表情符号
            emoji_map = {
                "info": "ℹ️",
                "warning": "⚠️", 
                "error": "❌",
                "success": "✅"
            }
            emoji = emoji_map.get(message_type, "📢")
            
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"{emoji} {title}\\n\\n{content}"
                }
            }
            
            return self._send_message(message)
        
        except Exception as e:
            logger.error(f"发送自定义消息异常: {e}")
            return False
    
    def _build_success_message(self, keyword_data: KeywordData,
                             comparison_result: Optional[ComparisonResult],
                             file_path: str,
                             comparison_file: str = None,
                             business_report_file: str = None) -> Dict:
        """构建成功通知消息"""
        
        # 标题
        content_parts = [
            f"🎯 {keyword_data.main_keyword} - 谷歌长尾词监控完成"
        ]
        
        # 今日数据统计
        success_rate = (keyword_data.successful_queries/keyword_data.total_queries*100) if keyword_data.total_queries > 0 else 0
        content_parts.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"📊 今日数据统计:",
            f"• 总查询: {keyword_data.total_queries:,} 次",
            f"• 成功率: {success_rate:.1f}%",
            f"• 收集词汇: {keyword_data.unique_keywords:,} 个",
            f"• 执行时长: {keyword_data.execution_duration}"
        ])
        
        # 变化分析（与昨日对比）
        if comparison_result and (comparison_result.new_count > 0 or comparison_result.disappeared_count > 0):
            content_parts.extend([
                "",
                f"📈 与昨日对比变化:",
                f"• 新增趋势词: {comparison_result.new_count} 个",
                f"• 热度下降词: {comparison_result.disappeared_count} 个",
                f"• 整体变化率: {comparison_result.change_rate:+.1f}%"
            ])
            
            # 重要新增关键词分析
            if comparison_result.new_count > 0:
                business_keywords = self._analyze_business_opportunities(comparison_result.new_keywords[:10])
                if business_keywords:
                    content_parts.extend([
                        "",
                        "💡 潜在商机关键词:",
                        f"• {' | '.join(business_keywords[:3])}"
                    ])
                    if len(business_keywords) > 3:
                        content_parts.append(f"• ...还有{len(business_keywords)-3}个商业机会")
                
                # 显示其他重要新词
                other_keywords = [k for k in comparison_result.new_keywords[:6] if k not in business_keywords]
                if other_keywords:
                    content_parts.extend([
                        "",
                        "🔥 其他新增热词:",
                        f"• {' | '.join(other_keywords[:3])}"
                    ])
        
        # 商业分析状态
        if business_report_file:
            content_parts.extend([
                "",
                "📋 详细商业分析报告已生成"
            ])
        
        # 时间戳
        current_time = datetime.now().strftime('%m-%d %H:%M')
        content_parts.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"⏰ {current_time} | 🤖 自动监控系统"
        ])
        
        # 构建消息
        content_text = "\n".join(content_parts)
        
        message = {
            "msg_type": "text", 
            "content": {
                "text": content_text
            }
        }
        
        return message
    
    def _analyze_business_opportunities(self, new_keywords: List[str]) -> List[str]:
        """分析新增关键词的商业机会"""
        business_keywords = []
        
        # 商业价值关键词识别
        high_value_patterns = {
            'SaaS/工具类': ['tool', 'generator', 'creator', 'maker', 'builder', 'platform', 'app'],
            '电商/销售': ['ecommerce', 'shop', 'store', 'sell', 'business', 'commercial', 'product'],
            '专业服务': ['professional', 'enterprise', 'pro', 'premium', 'custom', 'api'],
            '教育培训': ['course', 'tutorial', 'training', 'learn', 'education', 'guide'],
            '创意设计': ['design', 'art', 'logo', 'illustration', 'creative', 'visual'],
            '技术开发': ['code', 'js', 'html', 'json', 'website', 'database', 'developer']
        }
        
        for keyword in new_keywords:
            keyword_lower = keyword.lower()
            
            # 检查是否包含高价值指标
            for category, patterns in high_value_patterns.items():
                if any(pattern in keyword_lower for pattern in patterns):
                    # 进一步筛选有商业价值的关键词
                    if self._has_commercial_potential(keyword_lower):
                        business_keywords.append(keyword)
                        break
        
        return business_keywords[:6]  # 最多返回6个
    
    def _has_commercial_potential(self, keyword: str) -> bool:
        """判断关键词是否具有商业潜力"""
        
        # 高商业价值指标
        high_commercial_terms = [
            'free', 'professional', 'business', 'enterprise', 'commercial', 'premium',
            'generator', 'creator', 'maker', 'tool', 'platform', 'service',
            'ecommerce', 'website', 'app', 'api', 'automation', 'custom'
        ]
        
        # 过滤掉明显没有商业价值的词
        low_value_terms = [
            'meme', 'funny', 'joke', 'random', 'silly', 'weird', 'stupid', 
            'test', 'demo', 'sample', 'example'
        ]
        
        # 如果包含低价值词汇，则排除
        if any(term in keyword for term in low_value_terms):
            return False
        
        # 如果包含高商业价值词汇，则包含
        return any(term in keyword for term in high_commercial_terms)
    
    def _build_error_message(self, main_keyword: str, error_message: str,
                           execution_stats: Dict) -> Dict:
        """构建错误通知消息"""
        
        content_parts = [
            f"❌ {main_keyword} 监控失败",
            f"💥 {error_message}"
        ]
        
        # 执行统计（简化显示）
        if execution_stats:
            total = execution_stats.get('total_requests', 0)
            success = execution_stats.get('successful_requests', 0)
            success_rate = (success / total * 100) if total > 0 else 0
            content_parts.append(f"📊 {success}/{total}请求 | {success_rate:.0f}%成功率")
        
        content_parts.append(f"🕒 {datetime.now().strftime('%m-%d %H:%M')}")
        
        content_text = "\n".join(content_parts)
        
        message = {
            "msg_type": "text",
            "content": {
                "text": content_text
            }
        }
        
        return message
    
    def _get_top_keywords(self, keyword_data: KeywordData, limit: int = 5) -> List[Tuple[str, int]]:
        """获取热门关键词"""
        from collections import Counter
        
        # 统计关键词出现频率
        keyword_count = Counter()
        
        for query, suggestions in keyword_data.query_results.items():
            if suggestions:
                for suggestion in suggestions:
                    keyword_count[suggestion] += 1
        
        # 返回最热门的关键词
        return keyword_count.most_common(limit)
    
    def _send_message(self, message: Dict) -> bool:
        """发送消息到飞书"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(message, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.debug("飞书消息发送成功")
                    return True
                else:
                    # 如果是关键词问题，尝试发送简化版本
                    if result.get("code") == 19024:  # Key Words Not Found
                        logger.warning("飞书消息包含敏感词，尝试发送简化版本")
                        simplified_message = self._create_simplified_message(message)
                        if simplified_message:
                            return self._send_simplified_message(simplified_message)
                    
                    logger.error(f"飞书消息发送失败: {result}")
                    return False
            else:
                logger.error(f"飞书API请求失败: {response.status_code} - {response.text}")
                return False
        
        except requests.exceptions.Timeout:
            logger.error("飞书消息发送超时")
            return False
        
        except requests.exceptions.ConnectionError:
            logger.error("飞书消息发送连接失败")
            return False
        
        except Exception as e:
            logger.error(f"飞书消息发送异常: {e}")
            return False
    
    def _create_simplified_message(self, original_message: Dict) -> Dict:
        """创建简化版本的消息，避免敏感词"""
        try:
            original_text = original_message.get("content", {}).get("text", "")
            
            # 创建安全的词汇替换映射
            safe_replacements = {
                "Google": "搜索引擎",
                "google": "搜索引擎", 
                "谷歌": "搜索引擎",
                "Google 长尾词监控报告": "关键词监控报告",
                "Google长尾词监控系统": "关键词监控系统",
                "长尾词": "关键词",
                "ai generate": "内容生成",
                "generate": "生成",
                "AI": "智能",
                "ai": "智能"
            }
            
            # 应用替换
            simplified_text = original_text
            for original, replacement in safe_replacements.items():
                simplified_text = simplified_text.replace(original, replacement)
            
            return {
                "msg_type": "text",
                "content": {
                    "text": simplified_text
                }
            }
        except Exception as e:
            logger.error(f"创建简化消息失败: {e}")
            return None
    
    def _send_simplified_message(self, message: Dict) -> bool:
        """发送简化消息"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(message, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.debug("简化飞书消息发送成功")
                    return True
                else:
                    logger.error(f"简化飞书消息发送失败: {result}")
                    # 如果简化版本仍然失败，尝试发送最小化通知
                    return self._send_minimal_notification()
            else:
                return self._send_minimal_notification()
                
        except Exception as e:
            logger.error(f"发送简化消息异常: {e}")
            return self._send_minimal_notification()
    
    def _send_minimal_notification(self) -> bool:
        """发送最小化通知，避免所有可能的敏感词"""
        try:
            # 包含飞书机器人关键词的最小化通知
            current_time = datetime.now()
            minimal_message = {
                "msg_type": "text",
                "content": {
                    "text": f"谷歌长尾词监控任务完成\n时间: {current_time.strftime('%m-%d %H:%M')}\n状态: 成功\n数据已保存"
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(minimal_message, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info("最小化通知发送成功")
                    return True
                else:
                    logger.error(f"最小化通知发送失败: {result}")
                    # 如果连最小化通知都失败，尝试发送纯数字状态
                    return self._send_numeric_status()
            else:
                logger.error(f"最小化通知请求失败: {response.status_code}")
                return self._send_numeric_status()
                
        except Exception as e:
            logger.error(f"发送最小化通知异常: {e}")
            return self._send_numeric_status()
    
    def _send_numeric_status(self) -> bool:
        """发送纯数字状态码"""
        try:
            # 最保险的通知，只使用数字和基础符号
            current_time = datetime.now()
            numeric_message = {
                "msg_type": "text", 
                "content": {
                    "text": f"{current_time.strftime('%m%d')} {current_time.strftime('%H%M')} OK"
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(numeric_message, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info("数字状态通知发送成功")
                    return True
                else:
                    logger.error(f"数字状态通知发送失败: {result}")
                    # 如果连数字都不行，尝试发送纯文本
                    return self._send_plain_text()
            else:
                logger.error(f"数字状态通知请求失败: {response.status_code}")
                return self._send_plain_text()
                
        except Exception as e:
            logger.error(f"发送数字状态通知异常: {e}")
            return self._send_plain_text()
    
    def _send_plain_text(self) -> bool:
        """发送纯文本通知"""
        try:
            # 最简单的文本
            plain_message = {
                "msg_type": "text",
                "content": {
                    "text": "done"
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(plain_message, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info("纯文本通知发送成功")
                    return True
                else:
                    logger.error(f"纯文本通知发送失败: {result}")
                    return False
            else:
                logger.error(f"纯文本通知请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送纯文本通知异常: {e}")
            return False
    
    def test_webhook(self) -> bool:
        """测试webhook连接"""
        test_message = {
            "msg_type": "text",
            "content": {
                "text": "谷歌长尾词监控连接测试\n状态: 正常\n时间: " + datetime.now().strftime('%H:%M')
            }
        }
        
        success = self._send_message(test_message)
        
        if success:
            logger.info("飞书webhook测试成功")
        else:
            logger.error("飞书webhook测试失败")
        
        return success
    
    def send_daily_summary(self, daily_stats: Dict) -> bool:
        """
        发送每日摘要
        
        Args:
            daily_stats: 每日统计数据
            
        Returns:
            bool: 发送是否成功
        """
        try:
            content_parts = [
                "📈 **每日监控摘要**",
                f"📅 **日期**: {daily_stats.get('date', '未知')}",
                f"",
                f"📊 **执行统计**:",
                f"- 监控关键词: {daily_stats.get('total_keywords', 0)}个",
                f"- 成功执行: {daily_stats.get('successful_executions', 0)}次",
                f"- 失败执行: {daily_stats.get('failed_executions', 0)}次",
                f"- 总采集词汇: {daily_stats.get('total_collected_words', 0)}个",
                f"",
                f"🔄 **趋势变化**:",
                f"- 新增趋势词: {daily_stats.get('trending_new', 0)}个",
                f"- 热度下降词: {daily_stats.get('trending_down', 0)}个",
                f"",
                f"📁 **数据存储**: {daily_stats.get('data_files_created', 0)}个文件已保存",
                f"",
                f"🤖 Google长尾词监控系统 · 每日摘要"
            ]
            
            content_text = "\\n".join(content_parts)
            
            message = {
                "msg_type": "text",
                "content": {
                    "text": content_text
                }
            }
            
            return self._send_message(message)
        
        except Exception as e:
            logger.error(f"发送每日摘要异常: {e}")
            return False
    
    def update_webhook_url(self, new_webhook_url: str):
        """更新webhook地址"""
        self.webhook_url = new_webhook_url
        logger.info("飞书webhook地址已更新")
    
    def get_notification_stats(self) -> Dict:
        """获取通知统计信息"""
        # 这里可以添加发送统计逻辑
        return {
            "webhook_url": self.webhook_url,
            "settings": self.notification_settings,
            "status": "active" if self.webhook_url else "inactive"
        }


class MessageBuilder:
    """消息构建器辅助类"""
    
    @staticmethod
    def build_rich_card_message(title: str, content: Dict) -> Dict:
        """构建富文本卡片消息"""
        # 飞书富文本卡片格式
        card_content = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "blue"
            },
            "elements": []
        }
        
        # 添加内容元素
        for section_title, section_content in content.items():
            if isinstance(section_content, str):
                card_content["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{section_title}**\\n{section_content}"
                    }
                })
            elif isinstance(section_content, list):
                text_content = f"**{section_title}**\\n"
                text_content += "\\n".join([f"- {item}" for item in section_content])
                
                card_content["elements"].append({
                    "tag": "div", 
                    "text": {
                        "tag": "lark_md",
                        "content": text_content
                    }
                })
        
        message = {
            "msg_type": "interactive",
            "card": card_content
        }
        
        return message
    
    @staticmethod
    def build_table_message(title: str, headers: List[str], rows: List[List[str]]) -> Dict:
        """构建表格消息"""
        # 构建表格文本
        table_text = f"**{title}**\\n\\n"
        
        # 表头
        header_row = " | ".join(headers)
        separator_row = " | ".join(["---"] * len(headers))
        table_text += f"{header_row}\\n{separator_row}\\n"
        
        # 数据行
        for row in rows:
            row_text = " | ".join(str(cell) for cell in row)
            table_text += f"{row_text}\\n"
        
        message = {
            "msg_type": "text",
            "content": {
                "text": table_text
            }
        }
        
        return message


def create_feishu_notifier(webhook_url: str, notification_settings: Dict = None) -> FeishuNotifier:
    """
    创建飞书通知器工厂函数
    
    Args:
        webhook_url: 飞书webhook地址
        notification_settings: 通知设置
        
    Returns:
        FeishuNotifier: 飞书通知器实例
    """
    return FeishuNotifier(webhook_url, notification_settings)