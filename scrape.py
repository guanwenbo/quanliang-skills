#!/usr/bin/env python3
"""
七鲜晚间出清商品抓取脚本
Skill: 7fresh-evening-clearance-flow
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_7fresh_activity(url=None):
    """抓取七鲜晚间出清活动页商品"""
    
    if not url:
        # 默认URL - 北京姚家园万象汇店
        url = "https://7fresh.m.jd.com/ac/?id=31574&from=&storeId=1017261480&tenantId=1&platformId=1&lat=39.913541&lng=116.524182"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1 MicroMessenger/8.0.38",
            viewport={"width": 375, "height": 812},
            device_scale_factor=3
        )
        page = await context.new_page()
        
        print(f"[*] 正在访问七鲜晚间出清活动页...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(5)
        
        # 滚动加载所有商品
        for i in range(5):
            await page.evaluate("window.scrollBy(0, 600)")
            await asyncio.sleep(2)
        
        # 从页面提取商品数据
        page_data = await page.evaluate("""
            () => {
                const products = [];
                const selectors = ['.product-item', '.goods-item', '.item-card', '.sku-item', '.product-card'];
                
                for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    elements.forEach(el => {
                        const nameEl = el.querySelector('.name, .title, .product-name, .sku-name');
                        const name = nameEl ? nameEl.textContent.trim() : null;
                        
                        if (name) {
                            products.push({name});
                        }
                    });
                }
                return {products};
            }
        """)
        
        # 从API响应中提取完整数据
        html = await page.content()
        
        await browser.close()
        return page_data.get("products", [])

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else None
    products = asyncio.run(scrape_7fresh_activity(url))
    print(f"[+] 找到 {len(products)} 个商品")
