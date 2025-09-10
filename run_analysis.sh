#!/bin/bash
# 商业价值分析脚本运行器
# Business Value Analysis Script Runner

echo "🚀 AI关键词商业价值分析器"
echo "=============================="
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "使用方法："
    echo "  ./run_analysis.sh <关键词变化文件路径> [输出目录]"
    echo ""
    echo "示例："
    echo "  ./run_analysis.sh data/2025-09-11_ai_generate_changes.json"
    echo "  ./run_analysis.sh data/2025-09-11_ai_generate_changes.json reports/"
    echo ""
    echo "可用的变化文件："
    find data/ -name "*_changes.json" -type f | head -5
    echo ""
    exit 1
fi

CHANGES_FILE=$1
OUTPUT_DIR=${2:-"reports/"}

# 检查文件是否存在
if [ ! -f "$CHANGES_FILE" ]; then
    echo "❌ 错误: 文件不存在 '$CHANGES_FILE'"
    echo ""
    echo "可用的变化文件："
    find data/ -name "*_changes.json" -type f | head -10
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "📂 输入文件: $CHANGES_FILE"
echo "📁 输出目录: $OUTPUT_DIR"
echo ""

# 运行分析
echo "🔍 开始商业价值分析..."
python3 src/business_analyzer.py "$CHANGES_FILE" -o "$OUTPUT_DIR" -v

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 分析完成！"
    echo ""
    echo "📊 报告文件已生成在: $OUTPUT_DIR"
    echo "🌐 请用浏览器打开 HTML 文件查看完整报告"
    echo ""
    
    # 尝试在macOS上自动打开报告
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LATEST_REPORT=$(find "$OUTPUT_DIR" -name "business_analysis_*.html" -type f | sort -r | head -1)
        if [ -n "$LATEST_REPORT" ]; then
            echo "🖥️  正在打开报告..."
            open "$LATEST_REPORT"
        fi
    fi
else
    echo ""
    echo "❌ 分析失败，请检查错误信息"
    exit 1
fi