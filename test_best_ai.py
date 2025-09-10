#!/usr/bin/env python3
"""
使用"best ai"进行单次执行测试
"""

import requests
import json
import time

def get_suggestions_chrome(query, language="en"):
    """使用Chrome客户端参数"""
    try:
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            'client': 'chrome',
            'q': query,
            'hl': language
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return [s for s in data[1] if isinstance(s, str)]
        
        return []
        
    except Exception as e:
        print(f"Chrome方法异常: {e}")
        return []

def test_best_ai():
    test_query = "best ai"
    
    print(f"🔍 单次执行测试: {test_query}")
    print("=" * 60)
    
    # 获取建议
    suggestions = get_suggestions_chrome(test_query)
    
    print(f"📊 获得 {len(suggestions)} 个建议:")
    print("-" * 40)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i:2d}. {suggestion}")
    
    # 分析建议内容
    print(f"\n📈 建议分析:")
    print("-" * 40)
    
    # 按类别分析
    categories = {
        "AI工具": ["tool", "generator", "software", "app", "platform"],
        "AI模型": ["model", "chatgpt", "gpt", "claude", "gemini"],
        "AI服务": ["free", "online", "website", "service"],
        "具体用途": ["writing", "image", "video", "code", "art", "music"]
    }
    
    for category, keywords in categories.items():
        matching = []
        for suggestion in suggestions:
            if any(keyword in suggestion.lower() for keyword in keywords):
                matching.append(suggestion)
        
        if matching:
            print(f"\n  📂 {category} ({len(matching)} 个):")
            for match in matching:
                print(f"    • {match}")
    
    # 热门AI工具检查
    popular_ai_tools = [
        "chatgpt", "claude", "gemini", "copilot", "midjourney", 
        "dall-e", "stable diffusion", "runway", "leonardo",
        "jasper", "copy.ai", "notion ai"
    ]
    
    print(f"\n🎯 热门AI工具覆盖检查:")
    print("-" * 40)
    found_tools = []
    for tool in popular_ai_tools:
        if any(tool.lower() in suggestion.lower() for suggestion in suggestions):
            found_tools.append(tool)
            print(f"  ✅ 找到: {tool}")
    
    missing_tools = set(popular_ai_tools) - set(found_tools)
    for tool in missing_tools:
        print(f"  ❌ 未找到: {tool}")
    
    print(f"\n📊 覆盖率: {len(found_tools)}/{len(popular_ai_tools)} ({len(found_tools)/len(popular_ai_tools)*100:.1f}%)")
    
    # 显示原始JSON响应（用于调试）
    print(f"\n🔧 技术信息:")
    print("-" * 40)
    print(f"  查询: {test_query}")
    print(f"  建议总数: {len(suggestions)}")
    print(f"  最长建议: {max(len(s) for s in suggestions) if suggestions else 0} 字符")
    print(f"  最短建议: {min(len(s) for s in suggestions) if suggestions else 0} 字符")

if __name__ == "__main__":
    test_best_ai()