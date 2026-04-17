#!/usr/bin/env python3
"""从页面HTML直接提取商品"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def extract_from_html():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        for i in range(5):
            await asyncio.sleep(5)
            await page.evaluate('window.scrollBy(0, 800)')
        
        await asyncio.sleep(5)
        html = await page.content()
        await browser.close()
        
        # 从HTML中提取商品块
        # 寻找包含价格和商品名的模式
        products = []
        
        # 模式1: 【xxx】商品名 + 价格
        pattern1 = r'([【\[][^】\]]+[】\]][^￥]{2,30}?)(?:[\s\|]*)(.*?￥[\d\.]+.*?)(?=【|$)'
        matches1 = re.findall(pattern1, html)
        
        for m in matches1[:10]:
            name = re.sub(r'<[^>]+>', '', m[0]).strip()
            price_text = re.sub(r'<[^>]+>', '', m[1]).strip()
            
            prices = re.findall(r'￥([\d\.]+)', price_text)
            if prices and len(name) > 3:
                products.append({
                    'name': name[:50],
                    'price': prices[0],
                    'original_price': prices[1] if len(prices) > 1 else None,
                    'raw': price_text[:100]
                })
        
        # 模式2: 直接查找所有包含【】和价格的文本
        if not products:
            # 找到所有商品块
            blocks = re.findall(r'[【\[][^【\]]{2,50}[】\]][^【\]]{0,100}￥[\d\.]+', html)
            for block in set(blocks[:15]):
                clean = re.sub(r'<[^>]+>', ' ', block)
                name_match = re.search(r'([【\[][^】\]]+[】\]][^￥]{2,40})', clean)
                prices = re.findall(r'￥([\d\.]+)', clean)
                
                if name_match and prices:
                    products.append({
                        'name': name_match.group(1).strip()[:50],
                        'price': prices[0],
                        'original_price': prices[1] if len(prices) > 1 else None,
                        'raw': clean[:100]
                    })
        
        return products

if __name__ == '__main__':
    products = asyncio.run(extract_from_html())
    
    print(f"[+] 提取到 {len(products)} 个商品")
    
    for i, p in enumerate(products[:10], 1):
        print(f"\n{i}. {p['name']}")
        print(f"   现价: ¥{p['price']}" + (f" | 原价: ¥{p['original_price']}" if p['original_price'] else ''))
    
    if products:
        with open('products_final.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
