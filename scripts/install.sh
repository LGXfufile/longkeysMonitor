#!/bin/bash
# Google Long-tail Keyword Monitor 安装脚本

set -e

echo "🚀 Google Long-tail Keyword Monitor 安装脚本"
echo "=============================================="

# 检查Python版本
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到pip3，请先安装pip"
    exit 1
fi

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装Python依赖包..."
pip install -r requirements.txt

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p data logs config

# 复制配置模板
echo "📋 设置配置文件..."
if [ ! -f "config/config.json" ]; then
    cp config/config.template.json config/config.json
    echo "✅ 配置文件已创建: config/config.json"
    echo "⚠️  请编辑config/config.json填入您的配置"
else
    echo "✅ 配置文件已存在: config/config.json"
fi

# 复制环境变量模板
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "✅ 环境变量文件已创建: .env"
    echo "⚠️  请编辑.env文件填入您的配置"
else
    echo "✅ 环境变量文件已存在: .env"
fi

# 设置脚本权限
echo "🔧 设置脚本权限..."
chmod +x scripts/*.sh

# 测试安装
echo "🧪 测试安装..."
if python src/main.py test; then
    echo "✅ 安装测试通过"
else
    echo "⚠️  安装测试失败，请检查配置"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📖 下一步操作："
echo "1. 编辑配置文件: config/config.json"
echo "2. 设置飞书webhook地址"
echo "3. 运行测试: python src/main.py test"
echo "4. 执行监控: python src/main.py run"
echo ""
echo "💡 更多使用说明请参考 README.md"