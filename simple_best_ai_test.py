#!/usr/bin/env python3
"""
简单测试有意义的"best ai"查询组合
"""

import requests
import time

def get_suggestions(query):
    """获取建议"""
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
                return [s for s in data[1] if isinstance(s, str)]
        
        return []
        
    except Exception as e:
        print(f"    ❌ 异常: {e}")
        return []

def test_best_ai_combinations():
    """测试best ai的有意义组合"""
    
    # 有意义的查询组合
    meaningful_queries = [
        "best ai",           # 基础查询
        "best ai apps",      # 具体应用
        "best ai tools",     # AI工具
        "best ai chatbot",   # 聊天机器人
        "best ai image",     # 图像相关
        "best ai video",     # 视频相关
        "best ai writing",   # 写作相关
        "best ai code",      # 编程相关
        "best ai free",      # 免费AI
        "best ai 2025",      # 最新的
    ]
    
    print(f"🔍 测试 'best ai' 相关的 {len(meaningful_queries)} 个有意义查询")
    print("=" * 70)
    
    all_suggestions = set()
    successful_queries = 0
    
    for i, query in enumerate(meaningful_queries, 1):
        print(f"\n📡 {i:2d}/{len(meaningful_queries)}: {query}")
        print("-" * 50)
        
        suggestions = get_suggestions(query)
        
        if suggestions:
            successful_queries += 1
            print(f"    ✅ 获得 {len(suggestions)} 个建议:")
            for j, suggestion in enumerate(suggestions[:8], 1):  # 显示前8个
                print(f"      {j:2d}. {suggestion}")
                all_suggestions.add(suggestion)
            
            if len(suggestions) > 8:
                print(f"      ... 还有 {len(suggestions) - 8} 个建议")
        else:
            print("    ❌ 无建议")
        
        time.sleep(0.5)  # 避免请求过快
    
    # 汇总分析
    print(f"\n🎯 汇总分析:")
    print("=" * 70)
    print(f"成功查询: {successful_queries}/{len(meaningful_queries)} ({successful_queries/len(meaningful_queries)*100:.1f}%)")
    print(f"唯一建议总数: {len(all_suggestions)}")
    
    # AI工具分类分析
    tool_categories = {
        "图像生成": ["image", "photo", "picture", "art", "visual"],
        "视频生成": ["video", "movie", "animation", "film"],
        "文本写作": ["writing", "text", "content", "copy", "essay"],
        "编程助手": ["coding", "code", "programming", "developer"],
        "聊天机器人": ["chatbot", "chat", "assistant", "conversation"],
        "创意设计": ["design", "creative", "logo", "graphic"],
        "语音音频": ["voice", "audio", "music", "sound", "speech"],
        "数据分析": ["data", "analysis", "analytics", "insights"]
    }
    
    print(f"\n📊 AI工具分类分析:")
    print("-" * 50)
    
    for category, keywords in tool_categories.items():
        matching = []
        for suggestion in all_suggestions:
            if any(keyword in suggestion.lower() for keyword in keywords):
                matching.append(suggestion)
        
        if matching:
            print(f"  📂 {category} ({len(matching)} 个):")
            for match in matching[:5]:  # 只显示前5个
                print(f"    • {match}")
            if len(matching) > 5:
                print(f"    ... 还有 {len(matching) - 5} 个")
    
    # 显示热门建议
    print(f"\n🔥 所有唯一建议（按字母排序）:")
    print("-" * 50)
    for i, suggestion in enumerate(sorted(all_suggestions), 1):
        print(f"  {i:2d}. {suggestion}")

if __name__ == "__main__":
    test_best_ai_combinations()