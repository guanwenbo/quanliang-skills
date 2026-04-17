#!/usr/bin/env python3
"""提取完整商品数据"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def extract():
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
        
        # 清理HTML标签
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        
        # 查找商品模式: 【标签】商品名 ... 价格
        # 商品名通常包含中文、数字、g、规格等
        products = []
        
        # 模式: 【xxx】+ 商品名(含中文、规格) + 卖点 + 价格
        pattern = r'([【\[][^(]+?[】\])([^【\]]{3,50}?(?:肉|鸡|牛|鱼|虾|蛋|菜|果|米|油|奶|饮料|零食)[^【\]]{0,30})'
        matches = re.findall(pattern, text)
        
        for tag, name in matches[:15]:
            # 在附近查找价格
            idx = text.find(tag + name)
            nearby = text[idx:idx+200] if idx >= 0 else ""
            
            prices = re.findall(r'￥([\d\.]+)', nearby)
            if prices:
                # 清理商品名
                clean_name = re.sub(r'\s+', ' ', name).strip()
                clean_name = re.sub(r'(冷鲜|冷藏|限时|\d+\.\d+折|\d+人已回购).*', '', clean_name).strip()
                
                if len(clean_name) > 3:
                    products.append({
                        'tag': tag.strip('【】[]'),
                        'name': clean_name[:40],
                        'price': prices[0],
                        'original_price': prices[1] if len(prices) > 1 else None
                    })
        
        # 去重
        seen = set()
        unique = []
        for p in products:
            key = p['name']
            if key not in seen:
                seen.add(key)
                unique.append(p)
        
        return unique

asyncio.run(extract())
