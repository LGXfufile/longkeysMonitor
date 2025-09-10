#!/usr/bin/env python3
"""
简化的Playwright测试 - 仅对比基本功能
"""

import asyncio
from playwright.async_api import async_playwright
import requests
import json

async def test_simple_playwright(query):
    """简单的Playwright测试"""
    print(f"🎭 Playwright测试: {query}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        suggestions = []
        
        # 监听网络请求
        def handle_response(response):
            if 'complete/search' in response.url:
                try:
                    # 这里我们只记录URL，实际获取在下面
                    print(f"捕获到建议API请求: {response.url}")
                except:
                    pass
        
        page.on('response', handle_response)
        
        try:
            # 访问Google
            await page.goto('https://www.google.com')
            
            # 查找搜索框
            search_box = await page.query_selector('textarea[name="q"], input[name="q"]')
            if search_box:
                await search_box.fill(query)
                await page.wait_for_timeout(2000)
                print("✅ 成功输入查询并等待")
            else:
                print("❌ 未找到搜索框")
        
        except Exception as e:
            print(f"Playwright异常: {e}")
        
        finally:
            await browser.close()

def test_api_method(query):
    """测试API方法"""
    print(f"📡 API测试: {query}")
    
    url = "http://suggestqueries.google.com/complete/search"
    params = {'client': 'chrome', 'q': query, 'hl': 'en'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = data[1]
                print(f"✅ API获得 {len(suggestions)} 个建议:")
                for i, s in enumerate(suggestions, 1):
                    print(f"  {i}. {s}")
            else:
                print("❌ API响应格式异常")
        else:
            print(f"❌ API返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ API异常: {e}")

async def main():
    query = "ae ai generate"
    
    print("=" * 60)
    print("方法对比测试")
    print("=" * 60)
    
    # 测试API方法
    test_api_method(query)
    
    print()
    
    # 测试Playwright方法
    await test_simple_playwright(query)
    
    print("\n💭 总结:")
    print("1. API方法：直接、高效，但可能缺少个性化建议")
    print("2. Playwright方法：更接近真实用户体验，但复杂度高")
    print("3. 对于长尾监控系统，建议:")
    print("   - 如果需要高性能和稳定性：使用API方法")
    print("   - 如果需要完整建议内容：考虑结合两种方法")

if __name__ == "__main__":
    asyncio.run(main())