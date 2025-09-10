#!/usr/bin/env python3
"""
Playwright方案测试 - 获取真实浏览器中的Google自动完成建议
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time

async def get_google_suggestions_playwright(query):
    """使用Playwright获取Google自动完成建议"""
    suggestions = []
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,  # 改为可见模式，方便调试
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
        )
        
        try:
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # 监听网络请求，直接获取API响应
            async def handle_response(response):
                if 'complete/search' in response.url:
                    try:
                        text = await response.text()
                        # 解析JSON响应
                        data = json.loads(text)
                        if len(data) > 1 and isinstance(data[1], list):
                            nonlocal suggestions
                            suggestions.extend([s for s in data[1] if isinstance(s, str) and s not in suggestions])
                    except Exception as e:
                        print(f"解析响应失败: {e}")
            
            page.on('response', handle_response)
            
            # 访问Google首页
            await page.goto('https://www.google.com', wait_until='networkidle')
            
            # 查找搜索框的多种可能选择器
            search_selectors = [
                'input[name="q"]',
                'textarea[name="q"]', 
                '.gLFyf',
                'input[title="Search"]',
                '#searchboxinput'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = await page.wait_for_selector(selector, timeout=3000)
                    if search_box:
                        print(f"找到搜索框: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                print("未找到搜索框，尝试截图调试")
                await page.screenshot(path="debug_google.png")
                return suggestions
            
            # 输入查询
            await search_box.click()
            await search_box.fill(query)
            
            # 等待自动完成
            await page.wait_for_timeout(2000)
            
            print(f"网络监听获得 {len(suggestions)} 个建议")
            
        except Exception as e:
            print(f"Playwright执行异常: {e}")
            
        finally:
            await browser.close()
    
    return suggestions

async def compare_methods(query):
    """对比API和Playwright两种方法"""
    print(f"🔍 对比测试查询: {query}")
    print("=" * 80)
    
    # 方法1: API方式
    print("📡 方法1: Google Suggest API")
    print("-" * 40)
    start_time = time.time()
    
    import requests
    try:
        url = "http://suggestqueries.google.com/complete/search"
        params = {'client': 'chrome', 'q': query, 'hl': 'en'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        api_suggestions = []
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                api_suggestions = data[1]
    except Exception as e:
        api_suggestions = []
        print(f"API请求失败: {e}")
    
    api_time = time.time() - start_time
    print(f"⏱️  API方式耗时: {api_time:.2f}秒")
    print(f"📊 API建议数量: {len(api_suggestions)}")
    for i, suggestion in enumerate(api_suggestions, 1):
        print(f"  {i:2d}. {suggestion}")
    
    # 方法2: Playwright方式
    print(f"\n🎭 方法2: Playwright浏览器")
    print("-" * 40)
    start_time = time.time()
    
    playwright_suggestions = await get_google_suggestions_playwright(query)
    
    playwright_time = time.time() - start_time
    print(f"⏱️  Playwright方式耗时: {playwright_time:.2f}秒")
    print(f"📊 Playwright建议数量: {len(playwright_suggestions)}")
    for i, suggestion in enumerate(playwright_suggestions, 1):
        print(f"  {i:2d}. {suggestion}")
    
    # 对比分析
    print(f"\n📈 对比分析:")
    print("-" * 40)
    print(f"速度对比: API({api_time:.2f}s) vs Playwright({playwright_time:.2f}s)")
    print(f"建议数量: API({len(api_suggestions)}) vs Playwright({len(playwright_suggestions)})")
    
    # 找出Playwright独有的建议
    api_set = set(api_suggestions)
    playwright_set = set(playwright_suggestions)
    
    unique_to_playwright = playwright_set - api_set
    unique_to_api = api_set - playwright_set
    common = api_set & playwright_set
    
    print(f"共同建议: {len(common)} 个")
    print(f"Playwright独有: {len(unique_to_playwright)} 个")
    print(f"API独有: {len(unique_to_api)} 个")
    
    if unique_to_playwright:
        print(f"\n✨ Playwright独有建议:")
        for suggestion in unique_to_playwright:
            print(f"  - {suggestion}")
    
    if unique_to_api:
        print(f"\n🔧 API独有建议:")
        for suggestion in unique_to_api:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    asyncio.run(compare_methods("ae ai generate"))