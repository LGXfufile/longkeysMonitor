#!/usr/bin/env python3
"""
直接测试原版方法 - 确认与google_autocomplete_fetcher.py一致
"""

import requests
import json

def get_google_suggestions_original(query):
    """使用与原版完全相同的方法"""
    try:
        # Google autocomplete API endpoint
        url = f"http://suggestqueries.google.com/complete/search"
        params = {
            'client': 'firefox',
            'q': query,
            'hl': 'en'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return data[1]
        return []
    
    except Exception as e:
        print(f"Error fetching suggestions for '{query}': {e}")
        return []

if __name__ == "__main__":
    # 测试相同的查询
    test_query = "ae ai generate"
    
    print(f"🔍 测试查询: {test_query}")
    print(f"📡 使用原版方法...")
    print("=" * 50)
    
    suggestions = get_google_suggestions_original(test_query)
    
    print(f"📊 结果 ({len(suggestions)} 个):")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i:2d}. {suggestion}")
    
    print(f"\n🎯 预期关键词检查:")
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
    
    found_count = 0
    for keyword in expected_keywords:
        if any(keyword.lower() in suggestion.lower() for suggestion in suggestions):
            print(f"  ✅ 找到相关: {keyword}")
            found_count += 1
        else:
            print(f"  ❌ 未找到: {keyword}")
    
    print(f"\n📈 覆盖率: {found_count}/{len(expected_keywords)} ({found_count/len(expected_keywords)*100:.1f}%)")