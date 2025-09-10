#!/usr/bin/env python3
"""
改进版搜索测试 - 多种方法获取更全面的建议
"""

import requests
import json
import time
from typing import List, Set

def get_comprehensive_suggestions(query: str) -> List[str]:
    """使用多种方法获取更全面的建议"""
    all_suggestions = set()
    
    # 方法1: 不同client参数
    clients = ['firefox', 'chrome', 'chrome-omni']
    for client in clients:
        suggestions = get_suggestions_with_client(query, client)
        all_suggestions.update(suggestions)
        time.sleep(0.5)
    
    # 方法2: 不同地区参数
    regions = ['us', 'uk', 'ca']
    for region in regions:
        suggestions = get_suggestions_with_region(query, region)
        all_suggestions.update(suggestions)
        time.sleep(0.5)
    
    # 方法3: 不同语言参数
    languages = ['en', 'en-US', 'en-GB']
    for lang in languages:
        suggestions = get_suggestions_with_lang(query, lang)
        all_suggestions.update(suggestions)
        time.sleep(0.5)
    
    return list(all_suggestions)

def get_suggestions_with_client(query: str, client: str) -> List[str]:
    """使用指定client获取建议"""
    url = 'http://suggestqueries.google.com/complete/search'
    params = {
        'client': client,
        'q': query,
        'hl': 'en'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return [s for s in data[1] if isinstance(s, str) and s.strip()]
    except:
        pass
    
    return []

def get_suggestions_with_region(query: str, region: str) -> List[str]:
    """使用指定地区获取建议"""
    url = 'http://suggestqueries.google.com/complete/search'
    params = {
        'client': 'firefox',
        'q': query,
        'hl': 'en',
        'gl': region
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return [s for s in data[1] if isinstance(s, str) and s.strip()]
    except:
        pass
    
    return []

def get_suggestions_with_lang(query: str, lang: str) -> List[str]:
    """使用指定语言获取建议"""
    url = 'http://suggestqueries.google.com/complete/search'
    params = {
        'client': 'firefox',
        'q': query,
        'hl': lang
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return [s for s in data[1] if isinstance(s, str) and s.strip()]
    except:
        pass
    
    return []

def test_comprehensive_search():
    """测试综合搜索"""
    test_query = "ae ai generate"
    
    print(f"🔍 综合测试查询: {test_query}")
    print("=" * 50)
    
    # 获取综合结果
    all_suggestions = get_comprehensive_suggestions(test_query)
    
    print(f"📊 综合结果 ({len(all_suggestions)} 个):")
    for i, suggestion in enumerate(sorted(all_suggestions), 1):
        print(f"  {i:2d}. {suggestion}")
    
    print(f"\n🎯 预期包含的关键词检查:")
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
        if any(keyword.lower() in suggestion.lower() for suggestion in all_suggestions):
            print(f"  ✅ 找到相关: {keyword}")
            found_count += 1
        else:
            print(f"  ❌ 未找到: {keyword}")
    
    print(f"\n📈 覆盖率: {found_count}/{len(expected_keywords)} ({found_count/len(expected_keywords)*100:.1f}%)")

if __name__ == "__main__":
    test_comprehensive_search()