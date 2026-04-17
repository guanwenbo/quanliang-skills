#!/usr/bin/env python3
"""提取完整商品数据并生成文案"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def extract_products():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        print("[*] 加载页面...")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 等待加载
        for i in range(6):
            await asyncio.sleep(5)
            await page.evaluate('window.scrollBy(0, 800)')
            print(f"[*] 滚动加载... {i+1}/6")
        
        await asyncio.sleep(5)
        
        # 提取商品数据
        products = await page.evaluate('''() => {
            const items = [];
            const seen = new Set();
            
            // 查找所有包含价格信息的元素
            document.querySelectorAll('[class*="product"], [class*="sku"], [class*="goods"], [class*="item"]').forEach(el => {
                const text = el.textContent || '';
                // 只保留包含价格符号¥的元素
                if (text.includes('¥') && text.length > 20 && text.length < 500) {
                    // 去重
                    const key = text.slice(0, 50);
                    if (!seen.has(key)) {
                        seen.add(key);
                        items.push(text.trim());
                    }
                }
            });
            
            return items;
        }''')
        
        await browser.close()
        
        print(f"\n[+] 提取到 {len(products)} 个商品")
        
        # 解析商品信息
        parsed = []
        for text in products[:15]:  # 取前15个
            # 解析商品名（通常是开头的中文）
            name_match = re.match(r'([【\[\u4e00-\u9fa5\]】a-zA-Z0-9\s]+?)(?:冷鲜|冷藏|限时|\\|￥|$)', text)
            name = name_match.group(1).strip() if name_match else "未知商品"
            
            # 解析价格
            price_match = re.search(r'￥(\d+\.?\d*)', text)
            price = price_match.group(1) if price_match else "N/A"
            
            # 解析原价（如果有）
            prices = re.findall(r'￥(\d+\.?\d*)', text)
            original_price = prices[1] if len(prices) > 1 else None
            
            # 解析卖点
            sell_points = []
            if '冷鲜' in text:
                sell_points.append('冷鲜')
            if '冷藏' in text:
                sell_points.append('冷藏')
            if re.search(r'\d+月\d+日生产', text):
                date = re.search(r'(\d+月\d+日生产)', text).group(1)
                sell_points.append(date)
            
            if name and name != "未知商品" and len(name) > 3:
                parsed.append({
                    'name': name,
                    'price': price,
                    'original_price': original_price,
                    'sell_points': '|'.join(sell_points) if sell_points else '限时特惠',
                    'raw': text[:150]
                })
        
        return parsed

if __name__ == '__main__':
    products = asyncio.run(extract_products())
    
    if products:
        print("\n=== 抓取到的商品 ===")
        for i, p in enumerate(products[:8], 1):
            print(f"\n{i}. {p['name']}")
            print(f"   价格: ¥{p['price']}" + (f" (原价¥{p['original_price']})" if p['original_price'] else ''))
            print(f"   卖点: {p['sell_points']}")
        
        # 保存JSON
        with open('products_real.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"\n\n📄 已保存到 products_real.json")
    else:
        print("\n⚠️ 未解析到商品")
