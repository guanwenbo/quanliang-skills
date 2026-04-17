#!/usr/bin/env python3
"""从页面提取完整商品数据 - 最终版"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def extract_products():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 多次滚动确保加载
        for i in range(8):
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 1000)')
        
        await asyncio.sleep(5)
        
        # 从页面提取所有文本
        all_text = await page.evaluate('() => document.body.innerText')
        await browser.close()
        
        # 解析商品
        products = []
        lines = all_text.split('\n')
        
        for i, line in enumerate(lines):
            # 查找包含【】或[]的行
            if re.search(r'[【\[][^】\]]+[】\]]', line) and '¥' in line:
                # 合并多行获取完整信息
                combined = line
                if i + 1 < len(lines):
                    combined += ' ' + lines[i + 1]
                if i + 2 < len(lines):
                    combined += ' ' + lines[i + 2]
                
                # 提取商品名
                name_match = re.search(r'([【\[][^】\]]+[】\]][^￥]{2,50})', combined)
                if name_match:
                    name = name_match.group(1).strip()
                    # 清理
                    name = re.sub(r'\s+', ' ', name)
                    name = re.sub(r'(限时[\d\.]+折|\d+人已回购|超市配送).*', '', name).strip()
                    
                    # 提取价格
                    prices = re.findall(r'￥([\d\.]+)', combined)
                    if prices and len(name) > 5:
                        products.append({
                            'name': name[:50],
                            'price': prices[0],
                            'original_price': prices[1] if len(prices) > 1 else None
                        })
        
        return products

async def main():
    products = await extract_products()
    
    # 去重
    seen = set()
    unique = []
    for p in products:
        if p['name'] not in seen:
            seen.add(p['name'])
            unique.append(p)
    
    print(json.dumps(unique[:8], ensure_ascii=False, indent=2))
    
    # 生成文案
    if unique:
        copy = "🌙 七鲜晚间出清 · 限时特惠\n\n💥 今晚不抢，明天后悔！\n\n🔥 超值低价推荐：\n\n"
        
        for i, p in enumerate(unique[:5], 1):
            name = p['name']
            price = p['price']
            orig = p['original_price']
            
            discount = ""
            if orig:
                try:
                    d = int((1 - float(price)/float(orig)) * 100)
                    discount = f" (省{d}%)"
                except:
                    pass
            
            copy += f"{i}️⃣ {name}\n"
            copy += f"   💰 "
            if orig:
                copy += f"原价¥{orig} → "
            copy += f"出清价¥{price}{discount}\n\n"
        
        copy += "⏰ 活动时间：今晚截止\n"
        copy += "🏠 抢购入口：https://7fresh.m.jd.com/ac/?id=31574\n\n"
        copy += "#七鲜晚间出清 #限时特惠 #新鲜食材"
        
        print("\n" + "="*50)
        print(copy)
        print("="*50)
        
        # 保存
        with open('文案_七鲜出清.txt', 'w', encoding='utf-8') as f:
            f.write(copy)
        print("\n✅ 文案已保存到: 文案_七鲜出清.txt")

asyncio.run(main())
