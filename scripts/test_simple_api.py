#!/usr/bin/env python3
"""
修复版Google搜索执行器 - 基于成功的旧版本
"""

import requests
import json
import time
from typing import List, Dict

def get_google_suggestions_simple(query: str, language: str = "zh") -> List[str]:
    """简化版Google建议获取 - 基于成功的旧版本"""
    try:
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            'client': 'firefox',
            'q': query,
            'hl': language
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if len(data) > 1 and isinstance(data[1], list):
                    return data[1]
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始响应: {response.text[:200]}")
                return []
        else:
            print(f"HTTP错误: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"请求异常: {e}")
        return []
    
    return []

def test_simple_api():
    """测试简化版API"""
    print("🔍 测试简化版Google Suggest API")
    print("=" * 40)
    
    # 测试不同查询
    test_queries = [
        ("ai generate", "en"),
        ("AI写作", "zh"),
        ("SEO工具", "zh"),
        ("python", "en")
    ]
    
    for query, lang in test_queries:
        print(f"\n测试查询: '{query}' (语言: {lang})")
        suggestions = get_google_suggestions_simple(query, lang)
        print(f"结果数量: {len(suggestions)}")
        
        if suggestions:
            print("前5个建议:")
            for i, s in enumerate(suggestions[:5]):
                print(f"  {i+1}. {s}")
        else:
            print("⚠️  未获取到建议")
        
        time.sleep(1)  # 避免请求过快

if __name__ == "__main__":
    test_simple_api()