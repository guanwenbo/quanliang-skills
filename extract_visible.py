#!/usr/bin/env python3
"""完整渲染页面并提取可见商品"""
import asyncio
from playwright.async_api import async_playwright
import re

async def extract_visible_products():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        print("[*] 加载页面...")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 等待更长时间让商品加载
        for i in range(6):
            await asyncio.sleep(5)
            await page.evaluate('window.scrollBy(0, 600)')
            print(f"[*] 等待加载... {i+1}/6")
        
        await asyncio.sleep(5)
        
        # 提取页面上可见的商品信息
        products = await page.evaluate('''() => {
            const items = [];
            // 尝试多种可能的选择器
            const selectors = [
                '[class*="product"]', '[class*="sku"]', '[class*="goods"]', 
                '[class*="item"]', '.card', '.cell'
            ];
            
            for (const sel of selectors) {
                const elements = document.querySelectorAll(sel);
                elements.forEach(el => {
                    const text = el.textContent || '';
                    if (text.includes('¥') || text.includes('元') || /\d+g/.test(text)) {
                        items.push({
                            selector: sel,
                            text: text.slice(0, 200),
                            html: el.outerHTML.slice(0, 500)
                        });
                    }
                });
            }
            return items;
        }''')
        
        # 获取页面HTML
        html = await page.content()
        
        await browser.close()
        
        print(f"\n[+] 找到 {len(products)} 个可能的商品元素")
        
        if products:
            for i, p in enumerate(products[:5]):
                print(f"\n--- 商品 {i+1} ---")
                print(f"选择器: {p['selector']}")
                print(f"文本: {p['text'][:100]}")
        else:
            # 尝试从HTML直接提取中文商品名称
            chinese_names = re.findall(r'[\u4e00-\u9fa5]{4,20}(?:肉|蛋|菜|果|鱼|虾|米|油|奶|水)', html)
            if chinese_names:
                print(f"\n[+] 从HTML提取到商品名: {list(set(chinese_names))[:10]}")
        
        # 检查页面是否有特定状态
        if '活动已结束' in html:
            print("\n⚠️ 活动已结束")
        elif '已抢光' in html:
            print("\n⚠️ 商品已抢光")
        elif '补货中' in html:
            print("\n⚠️ 商品补货中")
        else:
            print("\n页面正常，但可能无商品或商品未加载")

asyncio.run(extract_visible_products())
