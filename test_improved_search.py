#!/usr/bin/env python3
"""
测试改进后的搜索方法 - 直接实现版本
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

def get_suggestions_browser(query, language="en"):
    """使用浏览器gws-wiz客户端参数"""
    try:
        url = "https://www.google.com/complete/search"
        params = {
            'client': 'gws-wiz',
            'q': query,
            'hl': language,
            'xssi': 't',
            'gs_pcrt': '2'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # gws-wiz返回的格式可能不同，需要特殊处理
            text = response.text
            # 移除XSSI保护前缀
            if text.startswith(')]}\'\n'):
                text = text[5:]
            
            try:
                data = json.loads(text)
                # gws-wiz格式可能是 [query, suggestions, ...] 或其他格式
                if isinstance(data, list) and len(data) > 1:
                    suggestions = data[1]
                    if isinstance(suggestions, list):
                        return [s[0] if isinstance(s, list) and len(s) > 0 else str(s) 
                               for s in suggestions if s]
            except json.JSONDecodeError as e:
                print(f"gws-wiz JSON解析失败: {e}")
        
        return []
        
    except Exception as e:
        print(f"Browser方法异常: {e}")
        return []

def test_improved_search():
    test_query = "ae ai generate"
    
    print(f"🔍 测试改进的搜索方法: {test_query}")
    print("=" * 60)
    
    # 方法1: Chrome客户端
    print("📡 方法1: Chrome客户端")
    print("-" * 30)
    chrome_suggestions = get_suggestions_chrome(test_query)
    print(f"Chrome建议数量: {len(chrome_suggestions)}")
    for i, suggestion in enumerate(chrome_suggestions, 1):
        print(f"  {i:2d}. {suggestion}")
    
    time.sleep(1)  # 避免请求过快
    
    # 方法2: 浏览器gws-wiz客户端
    print(f"\n📡 方法2: 浏览器gws-wiz客户端")
    print("-" * 30)
    browser_suggestions = get_suggestions_browser(test_query)
    print(f"Browser建议数量: {len(browser_suggestions)}")
    for i, suggestion in enumerate(browser_suggestions, 1):
        print(f"  {i:2d}. {suggestion}")
    
    # 合并去重
    all_suggestions = set(chrome_suggestions + browser_suggestions)
    print(f"\n🔥 合并后的唯一建议 ({len(all_suggestions)} 个):")
    print("-" * 30)
    for i, suggestion in enumerate(sorted(all_suggestions), 1):
        print(f"  {i:2d}. {suggestion}")
    
    # 检查预期关键词
    expected_keywords = [
        "ai image generator", 
        "ai video generator",
        "adobe firefly",
        "leonardo ai",
        "midjourney",
        "after effects"
    ]
    
    print(f"\n🎯 预期关键词检查:")
    found_count = 0
    for keyword in expected_keywords:
        if any(keyword.lower() in suggestion.lower() for suggestion in all_suggestions):
            print(f"  ✅ 找到相关: {keyword}")
            found_count += 1
        else:
            print(f"  ❌ 未找到: {keyword}")
    
    print(f"\n📈 覆盖率: {found_count}/{len(expected_keywords)} ({found_count/len(expected_keywords)*100:.1f}%)")

if __name__ == "__main__":
    test_improved_search()