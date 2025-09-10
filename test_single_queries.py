#!/usr/bin/env python3
"""
快速测试系统的单个查询功能
"""

import sys
sys.path.insert(0, 'src')

import requests

def test_single_query(query):
    """测试单个查询"""
    print(f"🔍 测试查询: '{query}'")
    
    try:
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            'client': 'chrome',
            'q': query,
            'hl': 'en'
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
                suggestions = [s for s in data[1] if isinstance(s, str)]
                print(f"✅ 获得 {len(suggestions)} 个建议:")
                for i, s in enumerate(suggestions, 1):
                    print(f"  {i:2d}. {s}")
                return suggestions
        
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return []
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return []

if __name__ == "__main__":
    # 测试一些常见的查询
    test_queries = [
        "best ai",          # 基础查询
        "a best ai",        # 前缀查询
        "best ai a",        # 后缀查询
        "ai generate",      # 之前成功的查询
    ]
    
    for query in test_queries:
        test_single_query(query)
        print("-" * 50)