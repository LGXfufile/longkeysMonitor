# Google Long-tail Keyword Monitor

<div align="center">

🔍 **谷歌长尾词监控系统**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

*一个自动化监控Google搜索建议变化的专业SEO工具*

[功能特性](#-功能特性) • 
[快速开始](#-快速开始) • 
[配置说明](#-配置说明) • 
[部署方案](#-部署方案) • 
[API文档](#-api文档)

</div>

---

## 📋 项目概述

Google Long-tail Keyword Monitor 是一个专业的SEO关键词研究工具，通过自动化监控Google搜索建议的变化，帮助用户发现新兴长尾关键词趋势，提升内容策略和搜索引擎优化效果。

### 🎯 核心价值

- **🚀 效率提升**: 自动化执行1400+个查询组合，覆盖全面
- **📈 趋势发现**: 智能识别新增/消失关键词，把握搜索热点
- **⏰ 定时监控**: 每日自动执行，无需人工干预
- **📱 即时通知**: 飞书机器人推送，第一时间获取结果
- **📊 数据分析**: 对比分析、趋势统计、数据可视化

## ✨ 功能特性

### 🔍 全面搜索覆盖
- **查询策略**: 主关键词 + [a-z, aa-zz] 前后缀组合
- **查询规模**: 单个关键词生成1,404个查询组合
- **多语言支持**: 中文、英文搜索建议并行获取
- **智能去重**: 自动清理重复和无效建议词

### 🛡️ 反爬虫保护
- **代理池轮换**: 支持HTTP/SOCKS5代理自动切换
- **动态延时**: 智能调整请求间隔，避免触发限制
- **请求头随机化**: User-Agent、Accept等字段轮换
- **失败重试**: 指数退避重试策略，提高成功率

### 📊 智能分析
- **增量对比**: 自动与前一天数据对比，识别变化趋势
- **热门统计**: 关键词频率分析，发现热点词汇
- **性能评估**: 查询效果统计，优化搜索策略
- **趋势洞察**: 7天历史数据分析，预测发展方向

### 📱 实时通知
- **飞书集成**: 富文本消息推送，美观易读
- **成功通知**: 详细执行报告，包含统计和对比结果
- **异常告警**: 执行失败自动通知，快速响应问题
- **每日摘要**: 汇总当日监控情况，全局掌控

### 🗄️ 数据管理
- **持久化存储**: JSON格式保存，结构化数据管理
- **历史追溯**: 完整保留历史数据，支持长期分析
- **数据导出**: 支持JSON/CSV格式导出，便于进一步处理
- **自动清理**: 定期清理过期数据，节省存储空间

## 🚀 快速开始

### 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python版本**: Python 3.8或更高版本
- **内存要求**: 至少1GB可用内存
- **存储空间**: 至少5GB可用空间（用于数据存储）
- **网络要求**: 稳定的互联网连接

### 方法一: 自动安装 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/your-username/google-longtail-monitor.git
cd google-longtail-monitor

# 2. 运行安装脚本
chmod +x scripts/install.sh
./scripts/install.sh

# 3. 编辑配置文件
nano config/config.json

# 4. 测试配置
python src/main.py test

# 5. 执行监控
python src/main.py run
```

### 方法二: 手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 创建配置文件
cp config/config.template.json config/config.json
cp .env.template .env

# 4. 编辑配置 (必需)
nano config/config.json
```

### 方法三: Docker部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 编辑配置
nano config/config.json

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f keyword-monitor
```

## ⚙️ 配置说明

### 主配置文件 (config/config.json)

```json
{
  "keywords": [
    {
      "main_keyword": "AI写作",
      "enabled": true,
      "schedule": "0 12 * * *"
    }
  ],
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-id",
  "request_settings": {
    "base_delay": [1, 3],
    "max_retries": 3,
    "timeout": 10,
    "dynamic_delay": true
  },
  "proxy_settings": {
    "enabled": false,
    "proxy_list": [
      "http://proxy1.example.com:8080"
    ]
  }
}
```

#### 关键参数说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `keywords` | Array | 监控关键词列表 | - |
| `feishu_webhook` | String | 飞书机器人Webhook地址 | - |
| `base_delay` | Array | 请求延时范围[最小,最大]秒 | [1, 3] |
| `max_retries` | Integer | 最大重试次数 | 3 |
| `proxy_enabled` | Boolean | 是否启用代理 | false |

### 飞书机器人配置

1. **创建飞书机器人**
   - 进入飞书群聊 → 设置 → 机器人 → 添加机器人
   - 选择"自定义机器人" → 填写机器人名称
   - 复制生成的Webhook地址

2. **配置Webhook**
   ```json
   {
     "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-id"
   }
   ```

3. **测试连接**
   ```bash
   python src/main.py test
   ```

### 代理配置 (可选)

如需使用代理，编辑`config/proxies.txt`:

```text
# HTTP代理
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:3128

# SOCKS5代理  
socks5://proxy3.example.com:1080
```

然后在配置文件中启用:

```json
{
  "proxy_settings": {
    "enabled": true,
    "proxy_list": [], // 会自动从proxies.txt加载
    "rotation": true
  }
}
```

## 📖 使用指南

### 命令行接口

```bash
# 执行所有关键词监控
python src/main.py run

# 执行单个关键词监控
python src/main.py run -k "AI写作"

# 并行执行模式 (更快)
python src/main.py run --mode parallel

# 测试配置
python src/main.py test

# 清理30天前的数据
python src/main.py cleanup --days 30

# 导出数据
python src/main.py export -k "AI写作" --format json
python src/main.py export -k "AI写作" --format csv --start 2025-01-01
```

### 定时任务设置

#### Linux/macOS

```bash
# 使用脚本自动设置
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh

# 或手动编辑crontab
crontab -e

# 添加以下内容 (每天中午12点执行)
0 12 * * * cd /path/to/project && python src/main.py run
```

#### Windows

使用任务计划程序:

1. 打开"任务计划程序"
2. 创建基本任务 → 填写名称和描述
3. 设置触发器为"每天"，时间为"12:00"
4. 操作选择"启动程序"
5. 程序路径: `C:\path\to\python.exe`
6. 参数: `C:\path\to\project\src\main.py run`
7. 起始位置: `C:\path\to\project`

## 🚢 部署方案

### 本地部署 (推荐新手)

**优势**: 
- 配置简单，易于调试
- 直接访问本地文件系统
- 适合开发测试环境

**步骤**:
1. 按照"快速开始"安装配置
2. 设置定时任务
3. 运行测试确认正常

### Docker部署 (推荐生产)

**优势**:
- 环境隔离，依赖统一
- 易于迁移和扩展
- 支持容器编排

**步骤**:

```bash
# 1. 构建和启动
docker-compose up -d

# 2. 查看运行状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

**配置文件挂载**:
```yaml
volumes:
  - ./config:/app/config:ro    # 配置文件只读
  - ./data:/app/data          # 数据目录读写
  - ./logs:/app/logs          # 日志目录读写
```

### 云服务器部署

**推荐配置**:
- **CPU**: 1核心或更高
- **内存**: 1GB或更高  
- **存储**: 20GB或更高
- **带宽**: 1Mbps或更高

**部署脚本**:

```bash
#!/bin/bash
# 云服务器一键部署脚本

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 克隆项目
git clone https://github.com/your-username/google-longtail-monitor.git
cd google-longtail-monitor

# 配置并启动
cp config/config.template.json config/config.json
# 编辑配置文件...
docker-compose up -d
```

## 📊 数据格式说明

### 输出数据结构

```json
{
  "metadata": {
    "main_keyword": "AI写作",
    "execution_date": "2025-01-10",
    "execution_time": "2025-01-10 12:00:00",
    "total_queries": 1404,
    "successful_queries": 1398,
    "execution_duration": "01:45:32"
  },
  "query_results": {
    "AI写作": ["AI写作工具", "AI写作软件", "AI写作教程"],
    "AI写作 a": ["AI写作app", "AI写作api", "AI写作algorithm"],
    "a AI写作": ["app AI写作", "api AI写作"]
  },
  "statistics": {
    "total_keywords_found": 2841,
    "unique_keywords": 2156,
    "average_suggestions_per_query": 2.1
  }
}
```

### 文件命名规范

- **数据文件**: `YYYY-MM-DD_关键词.json`
- **日志文件**: `monitor_YYYY-MM-DD.log`
- **备份文件**: `backup_YYYYMMDD.tar.gz`

## 🔧 高级配置

### 性能优化

```json
{
  "search_settings": {
    "include_single_letters": true,    // 包含单字母组合
    "include_double_letters": false,   // 禁用双字母以减少查询数量
    "languages": ["zh"]                // 只监控中文，提高速度
  },
  "request_settings": {
    "base_delay": [0.5, 1.5],         // 减少延时，提高速度
    "timeout": 5                       // 缩短超时时间
  }
}
```

### 大规模部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  keyword-monitor-1:
    build: .
    environment:
      - KEYWORDS_BATCH=1  # 处理第一批关键词
  
  keyword-monitor-2:
    build: .
    environment:
      - KEYWORDS_BATCH=2  # 处理第二批关键词
```

### 监控和告警

```json
{
  "notification_settings": {
    "notify_on_success": true,
    "notify_on_error": true,
    "error_threshold": 5,              // 失败次数阈值
    "performance_alert": true,         // 性能异常告警
    "daily_summary": true              // 每日摘要报告
  }
}
```

## 🐛 故障排除

### 常见问题

#### Q: 执行失败，提示网络连接错误？

**A**: 检查网络连接和防火墙设置
```bash
# 测试网络连接
curl -I "http://suggestqueries.google.com/complete/search"

# 检查DNS解析
nslookup suggestqueries.google.com
```

#### Q: 飞书通知发送失败？

**A**: 验证webhook地址和网络连接
```bash
# 测试webhook
python src/main.py test

# 手动测试
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-id" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试消息"}}'
```

#### Q: 查询结果为空或很少？

**A**: 可能触发了反爬虫限制
```json
{
  "request_settings": {
    "base_delay": [3, 8],      // 增加延时
    "dynamic_delay": true      // 启用动态延时
  },
  "proxy_settings": {
    "enabled": true            // 启用代理轮换
  }
}
```

#### Q: Docker容器启动失败？

**A**: 检查配置文件和权限
```bash
# 检查配置文件
docker-compose config

# 查看详细日志
docker-compose logs keyword-monitor

# 检查文件权限
ls -la config/
```

### 日志分析

```bash
# 查看实时日志
tail -f logs/monitor_$(date +%Y-%m-%d).log

# 搜索错误日志
grep -i error logs/*.log

# 统计成功率
grep -c "查询完成" logs/monitor_$(date +%Y-%m-%d).log
```

### 性能监控

```bash
# 监控资源使用
docker stats keyword-monitor

# 查看进程状态
ps aux | grep python

# 磁盘使用情况
du -sh data/ logs/
```

## 🤝 开发贡献

### 开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/google-longtail-monitor.git
cd google-longtail-monitor

# 2. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. 安装pre-commit hooks
pre-commit install

# 4. 运行测试
pytest tests/ -v
```

### 代码规范

- 遵循PEP 8编码规范
- 使用Black进行代码格式化
- 使用MyPy进行类型检查
- 编写完整的文档字符串

### 提交代码

```bash
# 1. 创建新分支
git checkout -b feature/your-feature-name

# 2. 提交更改
git add .
git commit -m "feat: add new feature description"

# 3. 推送并创建PR
git push origin feature/your-feature-name
```

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋 支持和反馈

### 获取帮助

- **文档**: [完整文档](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/google-longtail-monitor/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-username/google-longtail-monitor/discussions)

### 反馈渠道

- 🐛 **Bug报告**: 请使用GitHub Issues
- 💡 **功能建议**: 请使用GitHub Discussions
- 📧 **技术咨询**: your-email@example.com

## 🗺️ 发展规划

### v1.1 (计划中)
- [ ] 支持Bing、百度等搜索引擎
- [ ] Web管理界面
- [ ] 数据可视化图表
- [ ] 关键词聚类分析

### v1.2 (计划中)
- [ ] 机器学习趋势预测
- [ ] 多租户支持
- [ ] API接口开放
- [ ] 移动端App

### v2.0 (计划中)
- [ ] 分布式架构
- [ ] 实时监控
- [ ] 高级数据分析
- [ ] 商业智能报告

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请不要忘记给我们一个Star！**

[📝 报告问题](https://github.com/your-username/google-longtail-monitor/issues) • 
[💡 功能建议](https://github.com/your-username/google-longtail-monitor/discussions) • 
[🤝 贡献代码](https://github.com/your-username/google-longtail-monitor/pulls)

</div># longkeysMonitor
