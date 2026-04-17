#!/usr/bin/env python3
"""
七鲜晚间出清商品抓取脚本 - 增强版
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_7fresh_activity():
    """抓取七鲜晚间出清活动页商品"""
    
    # 北京姚家园万象汇店
    url = "https://7fresh.m.jd.com/ac/?id=31574&from=&storeId=1017261480&tenantId=1&platformId=1&lat=39.913541&lng=116.524182"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 375, "height": 812}
        )
        page = await context.new_page()
        
        print("[*] 正在访问七鲜晚间出清活动页...")
        
        # 监听 API 响应
        products = []
        
        async def handle_response(response):
            try:
                url = response.url
                if 'api' in url or 'ac' in url:
                    text = await response.text()
                    if 'skuId' in text or 'skuName' in text:
                        try:
                            data = json.loads(text)
                            if isinstance(data, dict) and 'data' in data:
                                items = data.get('data', {}).get('skus', []) or data.get('data', {}).get('list', [])
                                if items:
                                    products.extend(items)
                        except:
                            pass
            except:
                pass
        
        page.on('response', handle_response)
        
        await page.goto(url, wait_until='networkidle', timeout=90000)
        await asyncio.sleep(8)  # 等待页面加载
        
        # 滚动加载更多
        for i in range(10):
            await page.evaluate('window.scrollBy(0, 800)')
            await asyncio.sleep(3)
        
        await asyncio.sleep(5)
        await browser.close()
        
        return products

if __name__ == '__main__':
    products = asyncio.run(scrape_7fresh_activity())
    print(f"[+] 找到 {len(products)} 个商品")
    
    if products:
        # 去重
        seen = set()
        unique = []
        for p in products:
            sku_id = p.get('skuId') or p.get('sku_id')
            if sku_id and sku_id not in seen:
                seen.add(sku_id)
                unique.append(p)
        
        print(f"[+] 去重后 {len(unique)} 个商品")
        print(json.dumps(unique[:10], indent=2, ensure_ascii=False))
