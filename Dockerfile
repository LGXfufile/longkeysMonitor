# Google Long-tail Keyword Monitor Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# 创建必要目录
RUN mkdir -p /app/data /app/logs

# 设置脚本执行权限
RUN chmod +x scripts/*.sh

# 复制定时任务配置
COPY scripts/crontab /etc/cron.d/keyword-monitor-cron

# 设置定时任务权限
RUN chmod 0644 /etc/cron.d/keyword-monitor-cron

# 创建定时任务
RUN crontab /etc/cron.d/keyword-monitor-cron

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置Python环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); from src.config_manager import ConfigManager; ConfigManager().load_config()" || exit 1

# 暴露端口 (如果需要)
# EXPOSE 8080

# 启动命令
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]