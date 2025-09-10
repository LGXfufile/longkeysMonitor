#!/usr/bin/env python3
"""
简单的Google Suggest API测试脚本
用于调试API连接问题
"""

import requests
import json

def test_google_suggest_api():
    """测试Google建议API的多种方法"""
    
    query = "ai generate"  # 使用日志中的查询
    
    print(f"🔍 测试查询: '{query}'")
    print("=" * 50)
    
    # 方法1: Chrome客户端 (原代码使用的方法)
    print("\n1. Chrome客户端方法:")
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
        
        print(f"URL: {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON解析成功，数据结构: {type(data)}")
                if isinstance(data, list) and len(data) > 1:
                    suggestions = data[1]
                    print(f"建议数量: {len(suggestions) if isinstance(suggestions, list) else 'N/A'}")
                    if isinstance(suggestions, list):
                        print(f"前5个建议: {suggestions[:5]}")
                    else:
                        print(f"建议类型: {type(suggestions)}")
                else:
                    print("响应格式不符合预期")
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"Chrome方法异常: {e}")
    
    # 方法2: Firefox客户端
    print("\n2. Firefox客户端方法:")
    try:
        params = {
            'client': 'firefox',
            'q': query,
            'hl': 'en'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Firefox响应: {data[:2] if isinstance(data, list) else str(data)[:100]}")
            if isinstance(data, list) and len(data) > 1:
                suggestions = data[1]
                print(f"建议数量: {len(suggestions) if isinstance(suggestions, list) else 'N/A'}")
        
    except Exception as e:
        print(f"Firefox方法异常: {e}")
    
    # 方法3: 工具客户端
    print("\n3. 工具客户端方法:")
    try:
        params = {
            'client': 'toolbar',
            'q': query,
            'hl': 'en'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"响应内容: {response.text[:200]}...")
        
    except Exception as e:
        print(f"工具方法异常: {e}")
    
    # 方法4: 直接测试网络连接
    print("\n4. 网络连接测试:")
    try:
        response = requests.get("http://suggestqueries.google.com/complete/search?client=chrome&q=test", timeout=10)
        print(f"基础连接状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
    except Exception as e:
        print(f"网络连接异常: {e}")

if __name__ == "__main__":
    test_google_suggest_api()