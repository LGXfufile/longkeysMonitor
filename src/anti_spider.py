"""
Anti-Spider Module
反爬虫模块

Handles proxy rotation, request delays, and other anti-detection measures.
"""

import random
import time
import requests
from typing import List, Dict, Optional, Tuple
import logging
from urllib.parse import urlparse
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ProxyInfo:
    """代理信息"""
    url: str
    protocol: str
    host: str
    port: int
    is_working: bool = True
    last_used: datetime = None
    failure_count: int = 0
    response_time: float = 0.0
    
    def __post_init__(self):
        if self.last_used is None:
            self.last_used = datetime.now()


class ProxyPool:
    """代理池管理器"""
    
    def __init__(self, proxy_list: List[str]):
        """
        初始化代理池
        
        Args:
            proxy_list: 代理地址列表
        """
        self.proxies = self._parse_proxy_list(proxy_list)
        self.current_index = 0
        self.lock = threading.Lock()
        self.max_failures = 3
        self.cooldown_minutes = 10
        
        logger.info(f"代理池初始化完成，共 {len(self.proxies)} 个代理")
    
    def _parse_proxy_list(self, proxy_list: List[str]) -> List[ProxyInfo]:
        """解析代理列表"""
        proxies = []
        
        for proxy_str in proxy_list:
            try:
                if not proxy_str.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
                    proxy_str = 'http://' + proxy_str
                
                parsed = urlparse(proxy_str)
                
                proxy_info = ProxyInfo(
                    url=proxy_str,
                    protocol=parsed.scheme,
                    host=parsed.hostname,
                    port=parsed.port or (80 if parsed.scheme == 'http' else 443)
                )
                
                proxies.append(proxy_info)
                
            except Exception as e:
                logger.warning(f"解析代理地址失败: {proxy_str}, 错误: {e}")
        
        return proxies
    
    def get_working_proxy(self) -> Optional[ProxyInfo]:
        """获取可用的代理"""
        with self.lock:
            if not self.proxies:
                return None
            
            # 查找可用代理
            for _ in range(len(self.proxies)):
                proxy = self.proxies[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.proxies)
                
                if self._is_proxy_available(proxy):
                    proxy.last_used = datetime.now()
                    return proxy
            
            logger.warning("没有可用的代理")
            return None
    
    def _is_proxy_available(self, proxy: ProxyInfo) -> bool:
        """检查代理是否可用"""
        # 失败次数过多
        if proxy.failure_count >= self.max_failures:
            # 检查是否已经过了冷却时间
            if datetime.now() - proxy.last_used < timedelta(minutes=self.cooldown_minutes):
                return False
            else:
                # 重置失败计数，给代理一次机会
                proxy.failure_count = 0
        
        return proxy.is_working
    
    def mark_proxy_failed(self, proxy: ProxyInfo):
        """标记代理失败"""
        with self.lock:
            proxy.failure_count += 1
            proxy.is_working = proxy.failure_count < self.max_failures
            
            if not proxy.is_working:
                logger.warning(f"代理 {proxy.host}:{proxy.port} 被标记为不可用")
    
    def mark_proxy_success(self, proxy: ProxyInfo, response_time: float):
        """标记代理成功"""
        with self.lock:
            proxy.failure_count = 0
            proxy.is_working = True
            proxy.response_time = response_time
            proxy.last_used = datetime.now()
    
    def get_stats(self) -> Dict:
        """获取代理池统计信息"""
        working_count = sum(1 for p in self.proxies if p.is_working)
        failed_count = len(self.proxies) - working_count
        avg_response_time = sum(p.response_time for p in self.proxies if p.response_time > 0) / max(1, working_count)
        
        return {
            "total": len(self.proxies),
            "working": working_count,
            "failed": failed_count,
            "avg_response_time": round(avg_response_time, 3)
        }


class UserAgentRotator:
    """User-Agent轮换器"""
    
    DEFAULT_USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        
        # Chrome on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
        
        # Firefox on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
        
        # Safari on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        
        # Chrome on Linux
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
    ]
    
    def __init__(self, user_agents: List[str] = None):
        """
        初始化User-Agent轮换器
        
        Args:
            user_agents: 自定义User-Agent列表
        """
        self.user_agents = user_agents or self.DEFAULT_USER_AGENTS
        self.current_index = 0
        
        logger.info(f"User-Agent轮换器初始化，共 {len(self.user_agents)} 个UA")
    
    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.user_agents)
    
    def get_next_user_agent(self) -> str:
        """获取下一个User-Agent（轮换）"""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua


class RequestDelayManager:
    """请求延时管理器"""
    
    def __init__(self, base_delay: Tuple[int, int] = (1, 3), dynamic_delay: bool = True):
        """
        初始化延时管理器
        
        Args:
            base_delay: 基础延时范围 (最小, 最大) 秒
            dynamic_delay: 是否启用动态延时调整
        """
        self.base_delay = base_delay
        self.dynamic_delay = dynamic_delay
        self.current_delay = base_delay
        self.consecutive_failures = 0
        self.last_request_time = 0
        
    def wait(self):
        """执行延时等待"""
        # 计算延时时间
        delay = random.uniform(self.current_delay[0], self.current_delay[1])
        
        # 确保与上次请求的间隔
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self.last_request_time = time.time()
        
        logger.debug(f"请求延时: {delay:.2f}秒")
    
    def on_success(self):
        """请求成功回调"""
        self.consecutive_failures = 0
        
        # 动态调整：成功时逐渐减少延时
        if self.dynamic_delay and self.current_delay[0] > self.base_delay[0]:
            new_min = max(self.base_delay[0], self.current_delay[0] - 0.5)
            new_max = max(self.base_delay[1], self.current_delay[1] - 0.5)
            self.current_delay = (new_min, new_max)
            
            logger.debug(f"延时调整（减少）: {self.current_delay}")
    
    def on_failure(self, status_code: int = None):
        """请求失败回调"""
        self.consecutive_failures += 1
        
        # 动态调整：失败时增加延时
        if self.dynamic_delay:
            # 根据HTTP状态码和连续失败次数调整
            multiplier = 1.5
            if status_code in [429, 503]:  # 限流或服务不可用
                multiplier = 2.0
            
            new_min = self.current_delay[0] * multiplier
            new_max = self.current_delay[1] * multiplier
            
            # 设置最大延时上限（避免等待过久）
            max_delay = 30
            self.current_delay = (
                min(new_min, max_delay),
                min(new_max, max_delay)
            )
            
            logger.warning(f"延时调整（增加）: {self.current_delay}, 连续失败: {self.consecutive_failures}")


class AntiSpiderManager:
    """反爬虫管理器"""
    
    def __init__(self, proxy_settings: Dict, request_settings: Dict):
        """
        初始化反爬虫管理器
        
        Args:
            proxy_settings: 代理设置
            request_settings: 请求设置
        """
        self.proxy_settings = proxy_settings
        self.request_settings = request_settings
        
        # 初始化组件
        self.proxy_pool = None
        if proxy_settings.get("enabled", False) and proxy_settings.get("proxy_list"):
            self.proxy_pool = ProxyPool(proxy_settings["proxy_list"])
        
        self.user_agent_rotator = UserAgentRotator()
        
        self.delay_manager = RequestDelayManager(
            base_delay=tuple(request_settings.get("base_delay", [1, 3])),
            dynamic_delay=request_settings.get("dynamic_delay", True)
        )
        
        self.session = requests.Session()
        self._setup_session()
        
        logger.info("反爬虫管理器初始化完成")
    
    def _setup_session(self):
        """设置session默认参数"""
        # 设置超时
        self.session.timeout = self.request_settings.get("timeout", 10)
        
        # 设置重试策略
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.request_settings.get("max_retries", 3),
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def prepare_request(self) -> Dict[str, any]:
        """准备请求参数"""
        # 获取随机User-Agent
        user_agent = self.user_agent_rotator.get_random_user_agent()
        
        # 构建请求头
        headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        
        # 获取代理
        proxy = None
        proxies = None
        if self.proxy_pool:
            proxy = self.proxy_pool.get_working_proxy()
            if proxy:
                proxies = {
                    'http': proxy.url,
                    'https': proxy.url
                }
        
        return {
            'headers': headers,
            'proxies': proxies,
            'proxy_info': proxy,
            'timeout': self.request_settings.get("timeout", 10)
        }
    
    def make_request(self, url: str, params: Dict = None) -> Tuple[bool, any, ProxyInfo]:
        """
        发起请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            Tuple[bool, response_data, proxy_info]: (是否成功, 响应数据, 使用的代理)
        """
        # 执行延时
        self.delay_manager.wait()
        
        # 准备请求参数
        request_params = self.prepare_request()
        
        proxy_info = request_params['proxy_info']
        
        try:
            start_time = time.time()
            
            response = self.session.get(
                url,
                params=params,
                headers=request_params['headers'],
                proxies=request_params['proxies'],
                timeout=request_params['timeout']
            )
            
            response_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code == 200:
                self.delay_manager.on_success()
                if proxy_info:
                    self.proxy_pool.mark_proxy_success(proxy_info, response_time)
                
                return True, response.json(), proxy_info
            
            else:
                logger.warning(f"请求失败，状态码: {response.status_code}")
                self.delay_manager.on_failure(response.status_code)
                if proxy_info:
                    self.proxy_pool.mark_proxy_failed(proxy_info)
                
                return False, None, proxy_info
        
        except requests.exceptions.Timeout:
            logger.warning(f"请求超时: {url}")
            self.delay_manager.on_failure()
            if proxy_info:
                self.proxy_pool.mark_proxy_failed(proxy_info)
            return False, None, proxy_info
        
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"连接错误: {e}")
            self.delay_manager.on_failure()
            if proxy_info:
                self.proxy_pool.mark_proxy_failed(proxy_info)
            return False, None, proxy_info
        
        except Exception as e:
            logger.error(f"请求异常: {e}")
            self.delay_manager.on_failure()
            if proxy_info:
                self.proxy_pool.mark_proxy_failed(proxy_info)
            return False, None, proxy_info
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            "delay_settings": {
                "current_delay": self.delay_manager.current_delay,
                "consecutive_failures": self.delay_manager.consecutive_failures
            }
        }
        
        if self.proxy_pool:
            stats["proxy_pool"] = self.proxy_pool.get_stats()
        
        return stats
    
    def reset_delay(self):
        """重置延时设置"""
        self.delay_manager = RequestDelayManager(
            base_delay=tuple(self.request_settings.get("base_delay", [1, 3])),
            dynamic_delay=self.request_settings.get("dynamic_delay", True)
        )
        logger.info("延时设置已重置")


def create_anti_spider_manager(proxy_settings: Dict, request_settings: Dict) -> AntiSpiderManager:
    """
    创建反爬虫管理器工厂函数
    
    Args:
        proxy_settings: 代理设置
        request_settings: 请求设置
        
    Returns:
        AntiSpiderManager: 反爬虫管理器实例
    """
    return AntiSpiderManager(proxy_settings, request_settings)