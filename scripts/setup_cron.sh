#!/bin/bash
# 设置定时任务脚本

echo "⏰ 设置Google长尾词监控定时任务"

# 检查是否为root用户或sudo权限
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  检测到root权限，将为系统设置定时任务"
else
    echo "📝 为当前用户设置定时任务"
fi

# 获取项目绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 检查Python虚拟环境
if [ -d "$PROJECT_DIR/venv" ]; then
    PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
    echo "✅ 找到虚拟环境: $PYTHON_PATH"
else
    PYTHON_PATH="python3"
    echo "⚠️  未找到虚拟环境，使用系统Python: $PYTHON_PATH"
fi

# 创建定时任务内容
CRON_CONTENT="# Google Long-tail Keyword Monitor 定时任务
# 每天中午12点执行所有关键词监控
0 12 * * * cd $PROJECT_DIR && $PYTHON_PATH src/main.py run >> $PROJECT_DIR/logs/cron.log 2>&1

# 每周日凌晨2点清理30天前的旧数据
0 2 * * 0 cd $PROJECT_DIR && $PYTHON_PATH src/main.py cleanup >> $PROJECT_DIR/logs/cron.log 2>&1

# 每月1号凌晨3点备份数据 (可选，取消注释启用)
# 0 3 1 * * cd $PROJECT_DIR && tar -czf $PROJECT_DIR/data/backup_\$(date +\\%Y\\%m\\%d).tar.gz $PROJECT_DIR/data/*.json >> $PROJECT_DIR/logs/cron.log 2>&1
"

# 写入临时文件
TEMP_CRON_FILE="/tmp/keyword_monitor_cron"
echo "$CRON_CONTENT" > "$TEMP_CRON_FILE"

# 显示将要添加的定时任务
echo "📋 将要添加的定时任务:"
echo "----------------------------------------"
cat "$TEMP_CRON_FILE"
echo "----------------------------------------"

# 询问确认
read -p "❓ 是否添加这些定时任务? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消设置定时任务"
    rm "$TEMP_CRON_FILE"
    exit 0
fi

# 备份现有crontab
echo "💾 备份现有crontab..."
crontab -l > "$PROJECT_DIR/crontab.backup" 2>/dev/null || echo "# No existing crontab" > "$PROJECT_DIR/crontab.backup"

# 添加新的定时任务
echo "➕ 添加定时任务..."
(crontab -l 2>/dev/null; echo ""; cat "$TEMP_CRON_FILE") | crontab -

# 验证定时任务
echo "✅ 定时任务设置完成!"
echo ""
echo "📋 当前的定时任务:"
crontab -l | grep -A 10 -B 2 "Google Long-tail Keyword Monitor"

# 清理临时文件
rm "$TEMP_CRON_FILE"

echo ""
echo "💡 提示:"
echo "- 日志文件位置: $PROJECT_DIR/logs/cron.log"
echo "- 查看定时任务: crontab -l"
echo "- 删除定时任务: crontab -e (手动编辑删除)"
echo "- 恢复备份: crontab $PROJECT_DIR/crontab.backup"