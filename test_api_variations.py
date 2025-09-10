#!/usr/bin/env python3
"""
测试各种API参数组合，寻找能获取到浏览器级别建议的方法
"""

import requests
import json
import time

def test_api_variations(query):
    """测试不同的API参数组合"""
    print(f"🔍 测试查询: {query}")
    print("=" * 80)
    
    # 测试配置列表
    test_configs = [
        {
            "name": "原版方法 (firefox + en)",
            "params": {'client': 'firefox', 'q': query, 'hl': 'en'}
        },
        {
            "name": "Chrome客户端",
            "params": {'client': 'chrome', 'q': query, 'hl': 'en'}
        },
        {
            "name": "Chrome omni",
            "params": {'client': 'chrome-omni', 'q': query, 'hl': 'en'}
        },
        {
            "name": "Firefox + US地区",
            "params": {'client': 'firefox', 'q': query, 'hl': 'en', 'gl': 'us'}
        },
        {
            "name": "Chrome + US地区",
            "params": {'client': 'chrome', 'q': query, 'hl': 'en', 'gl': 'us'}
        },
        {
            "name": "无客户端参数",
            "params": {'q': query, 'hl': 'en'}
        },
        {
            "name": "gws客户端 (Google Web Search)",
            "params": {'client': 'gws', 'q': query, 'hl': 'en'}
        },
        {
            "name": "YouTube客户端",
            "params": {'client': 'youtube', 'q': query, 'hl': 'en'}
        }
    ]
    
    all_unique_suggestions = set()
    
    for config in test_configs:
        print(f"\n📡 测试: {config['name']}")
        print("-" * 40)
        
        suggestions = get_suggestions_with_params(config['params'])
        
        print(f"结果数量: {len(suggestions)}")
        if suggestions:
            for i, suggestion in enumerate(suggestions[:10], 1):  # 显示前10个
                print(f"  {i:2d}. {suggestion}")
                all_unique_suggestions.add(suggestion)
        else:
            print("  (无结果)")
        
        time.sleep(0.5)  # 避免请求过快
    
    print(f"\n🔥 汇总所有唯一建议 ({len(all_unique_suggestions)} 个):")
    print("=" * 80)
    for i, suggestion in enumerate(sorted(all_unique_suggestions), 1):
        print(f"  {i:2d}. {suggestion}")
    
    # 检查预期关键词
    expected_keywords = [
        "ai after effects online",
        "ai image generator", 
        "ai video generator",
        "adobe firefly",
        "heliumx ai",
        "image to video ai",
        "image after effects",
        "leonardo ai",
        "aescripts ai",
        "midjourney"
    ]
    
    print(f"\n🎯 预期关键词检查:")
    found_count = 0
    for keyword in expected_keywords:
        if any(keyword.lower() in suggestion.lower() for suggestion in all_unique_suggestions):
            print(f"  ✅ 找到相关: {keyword}")
            found_count += 1
        else:
            print(f"  ❌ 未找到: {keyword}")
    
    print(f"\n📈 覆盖率: {found_count}/{len(expected_keywords)} ({found_count/len(expected_keywords)*100:.1f}%)")

def get_suggestions_with_params(params):
    """使用指定参数获取建议"""
    try:
        url = "http://suggestqueries.google.com/complete/search"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return [s for s in data[1] if isinstance(s, str) and s.strip()]
        
        return []
    
    except Exception as e:
        print(f"    错误: {e}")
        return []

if __name__ == "__main__":
    test_api_variations("ae ai generate")