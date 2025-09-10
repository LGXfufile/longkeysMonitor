"""
Configuration Manager Module
配置管理模块

Handles loading, validation and management of configuration files.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class KeywordConfig:
    """单个关键词配置"""
    main_keyword: str
    enabled: bool = True
    schedule: str = "0 12 * * *"
    
    def __post_init__(self):
        if not self.main_keyword.strip():
            raise ValueError("主关键词不能为空")


@dataclass
class RequestSettings:
    """请求设置配置"""
    base_delay: List[int] = None
    max_retries: int = 3
    timeout: int = 10
    dynamic_delay: bool = True
    
    def __post_init__(self):
        if self.base_delay is None:
            self.base_delay = [1, 3]
        if len(self.base_delay) != 2:
            raise ValueError("base_delay 必须包含两个数字 [min, max]")


@dataclass
class ProxySettings:
    """代理设置配置"""
    enabled: bool = False
    proxy_list: List[str] = None
    rotation: bool = True
    
    def __post_init__(self):
        if self.proxy_list is None:
            self.proxy_list = []


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 config/config.json
        """
        if config_path is None:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "config", "config.json")
        
        self.config_path = config_path
        self.config_dir = os.path.dirname(config_path)
        self._config = None
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            logger.warning(f"配置文件不存在: {self.config_path}")
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._config = self._validate_config(config)
            logger.info(f"配置文件加载成功: {self.config_path}")
            return self._config
        
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式错误: {e}")
            raise ValueError(f"配置文件JSON格式错误: {e}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default_config = {
            "keywords": [
                {
                    "main_keyword": "AI写作",
                    "enabled": True,
                    "schedule": "0 12 * * *"
                }
            ],
            "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/fd8c7806-5aca-4dbf-b621-8b3f1c271bbd",
            "request_settings": {
                "base_delay": [1, 3],
                "max_retries": 3,
                "timeout": 10,
                "dynamic_delay": True
            },
            "proxy_settings": {
                "enabled": False,
                "proxy_list": [],
                "rotation": True
            },
            "search_settings": {
                "include_single_letters": True,
                "include_double_letters": True,
                "include_prefix": True,
                "include_suffix": True,
                "languages": ["zh", "en"]
            },
            "storage_settings": {
                "data_retention_days": 30,
                "auto_cleanup": True,
                "backup_enabled": False
            },
            "notification_settings": {
                "notify_on_success": True,
                "notify_on_error": True,
                "include_statistics": True,
                "max_keywords_display": 20
            }
        }
        
        # 保存默认配置
        self.save_config(default_config)
        logger.info(f"默认配置文件已创建: {self.config_path}")
        
        return default_config
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置文件格式"""
        # 验证必需字段
        required_fields = ["keywords", "feishu_webhook"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"配置文件缺少必需字段: {field}")
        
        # 验证关键词配置
        if not isinstance(config["keywords"], list) or len(config["keywords"]) == 0:
            raise ValueError("keywords 必须是非空数组")
        
        validated_keywords = []
        for i, kw_config in enumerate(config["keywords"]):
            try:
                kw = KeywordConfig(**kw_config)
                validated_keywords.append(kw.__dict__)
            except Exception as e:
                raise ValueError(f"关键词配置 {i} 格式错误: {e}")
        
        config["keywords"] = validated_keywords
        
        # 验证飞书webhook
        if not config["feishu_webhook"].startswith("https://open.feishu.cn/"):
            logger.warning("飞书webhook格式可能不正确")
        
        # 验证请求设置
        if "request_settings" in config:
            try:
                req_settings = RequestSettings(**config["request_settings"])
                config["request_settings"] = req_settings.__dict__
            except Exception as e:
                logger.warning(f"请求设置格式错误，使用默认值: {e}")
                config["request_settings"] = RequestSettings().__dict__
        else:
            config["request_settings"] = RequestSettings().__dict__
        
        # 验证代理设置
        if "proxy_settings" in config:
            try:
                proxy_settings = ProxySettings(**config["proxy_settings"])
                config["proxy_settings"] = proxy_settings.__dict__
            except Exception as e:
                logger.warning(f"代理设置格式错误，使用默认值: {e}")
                config["proxy_settings"] = ProxySettings().__dict__
        else:
            config["proxy_settings"] = ProxySettings().__dict__
        
        return config
    
    def save_config(self, config: Dict[str, Any]):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置文件保存成功: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def get_enabled_keywords(self) -> List[Dict[str, Any]]:
        """获取启用的关键词配置"""
        if self._config is None:
            self.load_config()
        
        enabled_keywords = [kw for kw in self._config["keywords"] if kw["enabled"]]
        return enabled_keywords
    
    def get_feishu_webhook(self) -> str:
        """获取飞书webhook地址"""
        if self._config is None:
            self.load_config()
        
        return self._config["feishu_webhook"]
    
    def get_request_settings(self) -> Dict[str, Any]:
        """获取请求设置"""
        if self._config is None:
            self.load_config()
        
        return self._config["request_settings"]
    
    def get_proxy_settings(self) -> Dict[str, Any]:
        """获取代理设置"""
        if self._config is None:
            self.load_config()
        
        return self._config["proxy_settings"]
    
    def get_search_settings(self) -> Dict[str, Any]:
        """获取搜索设置"""
        if self._config is None:
            self.load_config()
        
        return self._config.get("search_settings", {
            "include_single_letters": True,
            "include_double_letters": True,
            "include_prefix": True,
            "include_suffix": True,
            "languages": ["zh", "en"]
        })
    
    def add_keyword(self, keyword_config: Dict[str, Any]):
        """添加新的关键词配置"""
        if self._config is None:
            self.load_config()
        
        # 验证新关键词配置
        try:
            kw = KeywordConfig(**keyword_config)
            self._config["keywords"].append(kw.__dict__)
            self.save_config(self._config)
            logger.info(f"新关键词已添加: {kw.main_keyword}")
        except Exception as e:
            raise ValueError(f"添加关键词失败: {e}")
    
    def remove_keyword(self, main_keyword: str):
        """删除关键词配置"""
        if self._config is None:
            self.load_config()
        
        original_count = len(self._config["keywords"])
        self._config["keywords"] = [
            kw for kw in self._config["keywords"] 
            if kw["main_keyword"] != main_keyword
        ]
        
        if len(self._config["keywords"]) < original_count:
            self.save_config(self._config)
            logger.info(f"关键词已删除: {main_keyword}")
        else:
            logger.warning(f"未找到要删除的关键词: {main_keyword}")
    
    def update_feishu_webhook(self, webhook_url: str):
        """更新飞书webhook地址"""
        if self._config is None:
            self.load_config()
        
        self._config["feishu_webhook"] = webhook_url
        self.save_config(self._config)
        logger.info("飞书webhook已更新")


def load_proxy_list(proxy_file: str) -> List[str]:
    """从文件加载代理列表"""
    if not os.path.exists(proxy_file):
        logger.warning(f"代理文件不存在: {proxy_file}")
        return []
    
    try:
        with open(proxy_file, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"代理列表加载成功，共 {len(proxies)} 个代理")
        return proxies
    except Exception as e:
        logger.error(f"加载代理文件失败: {e}")
        return []


def load_user_agents(ua_file: str) -> List[str]:
    """从文件加载User-Agent列表"""
    if not os.path.exists(ua_file):
        # 返回默认User-Agent列表
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    try:
        with open(ua_file, 'r', encoding='utf-8') as f:
            user_agents = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"User-Agent列表加载成功，共 {len(user_agents)} 个")
        return user_agents
    except Exception as e:
        logger.error(f"加载User-Agent文件失败: {e}")
        # 返回默认列表
        return load_user_agents("")