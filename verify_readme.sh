#!/bin/bash
# README 功能验证脚本
echo "🔍 验证 README.md 中提到的所有功能..."
echo "=================================="

# 检查核心文件是否存在
echo ""
echo "📁 检查核心文件:"
files=(
    "src/business_analyzer.py"
    "run_analysis.sh" 
    "BUSINESS_ANALYSIS_GUIDE.md"
    "src/main.py"
    "config/config.json"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
    fi
done

# 检查目录结构
echo ""
echo "📂 检查目录结构:"
dirs=("src" "data" "reports" "config" "logs")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ (缺失)"
    fi
done

# 检查脚本可执行性
echo ""
echo "🔧 检查脚本权限:"
if [ -x "run_analysis.sh" ]; then
    echo "✅ run_analysis.sh 可执行"
else
    echo "❌ run_analysis.sh 不可执行，运行: chmod +x run_analysis.sh"
fi

# 检查Python依赖
echo ""
echo "🐍 检查Python脚本语法:"
python3 -m py_compile src/business_analyzer.py && echo "✅ business_analyzer.py 语法正确" || echo "❌ business_analyzer.py 语法错误"

# 检查示例数据文件
echo ""
echo "📊 检查示例数据:"
if ls data/*_changes.json 1> /dev/null 2>&1; then
    echo "✅ 找到变化文件:"
    ls data/*_changes.json | head -3
else
    echo "⚠️  未找到变化文件，请先运行监控生成数据"
fi

# 检查生成的报告
echo ""
echo "📋 检查分析报告:"
if ls reports/business_analysis_*.html 1> /dev/null 2>&1; then
    echo "✅ 找到分析报告:"
    ls reports/business_analysis_*.html | head -3
else
    echo "⚠️  未找到分析报告，请运行商业分析脚本生成"
fi

echo ""
echo "🎉 README功能验证完成！"
echo "📖 完整文档请查看: README.md"
echo "📚 商业分析使用说明: BUSINESS_ANALYSIS_GUIDE.md"