#!/usr/bin/env python3
"""调试七鲜页面"""
import asyncio
from playwright.async_api import async_playwright
import re

async def debug():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(15)
        
        html = await page.content()
        await browser.close()
        
        # 查找商品相关关键词
        keywords = ['skuId', 'skuName', 'salePrice', 'productId', '商品', '出清', '活动']
        
        for kw in keywords:
            matches = re.findall(kw + r'["\']?\s*[:=]\s*["\']?([^"\'<>,}\s]+)', html)
            if matches:
                print(f"{kw}: {matches[:3]}")
        
        # 检查页面是否加载了商品
        if '暂无商品' in html:
            print("\n⚠️ 页面显示: 暂无商品")
        if '活动已结束' in html:
            print("\n⚠️ 页面显示: 活动已结束")
        
        # 输出页面标题
        title_match = re.search(r'<title>([^<]+)</title>', html)
        if title_match:
            print(f"\n页面标题: {title_match.group(1)}")
        
        # 查找可能的活动ID
        id_matches = re.findall(r'id["\']?\s*:\s*(\d{4,})', html)
        if id_matches:
            print(f"\n找到活动ID: {set(id_matches[:10])}")

asyncio.run(debug())
