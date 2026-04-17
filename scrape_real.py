#!/usr/bin/env python3
"""
七鲜商品抓取 - 深度版
尝试从页面脚本和网络请求中提取商品数据
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_deep():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1&lat=39.913541&lng=116.524182"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38(0x18002628) NetType/WIFI Language/zh_CN",
            viewport={"width": 390, "height": 844},
            device_scale_factor=3
        )
        
        all_products = []
        all_responses = []
        
        page = await context.new_page()
        
        async def handle_response(response):
            url = response.url
            try:
                if any(k in url for k in ['sku', 'activity', 'product', 'list', 'search', 'promotion']):
                    text = await response.text()
                    if len(text) > 100 and len(text) < 500000:  # 合理范围
                        all_responses.append({'url': url, 'text': text[:5000]})
            except:
                pass
        
        page.on('response', handle_response)
        
        print(f"[*] 访问页面: {url}")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 等待并点击可能的加载更多按钮
        for attempt in range(3):
            await asyncio.sleep(5)
            
            # 尝试点击"查看更多"或类似按钮
            try:
                buttons = await page.query_selector_all('text=/查看更多|更多商品|加载更多|显示更多/')
                for btn in buttons[:3]:
                    await btn.click()
                    await asyncio.sleep(2)
            except:
                pass
            
            # 滚动加载
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(3)
        
        await asyncio.sleep(5)
        
        # 从页面HTML提取
        html = await page.content()
        
        # 从脚本标签提取
        scripts = await page.query_selector_all('script')
        script_contents = []
        for script in scripts:
            text = await script.text_content()
            if text and len(text) > 50:
                script_contents.append(text)
        
        await browser.close()
        
        # 分析收集到的数据
        print(f"\n[+] 捕获 {len(all_responses)} 个相关响应")
        print(f"[+] 页面HTML长度: {len(html)}")
        print(f"[+] 脚本标签数量: {len(script_contents)}")
        
        # 尝试解析响应中的JSON
        products = []
        for resp in all_responses:
            try:
                data = json.loads(resp['text'])
                if isinstance(data, dict):
                    # 查找包含sku数据的字段
                    for key in ['data', 'result', 'list', 'skus', 'products', 'items']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list):
                                products.extend(items)
                            elif isinstance(items, dict):
                                for k, v in items.items():
                                    if isinstance(v, list):
                                        products.extend(v)
            except:
                pass
        
        # 从脚本内容中提取
        for script in script_contents:
            # 查找初始状态数据
            matches = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.+?});<', script)
            for m in matches:
                try:
                    data = json.loads(m)
                    print(f"\n[+] 从 __INITIAL_STATE__ 提取数据")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                except:
                    pass
            
            # 查找包含skuId的JSON
            sku_matches = re.findall(r'"skuId":\s*(\d+)', script)
            if sku_matches:
                print(f"\n[+] 找到skuId: {sku_matches[:10]}")
        
        # 去重
        seen = set()
        unique = []
        for p in products:
            sku = p.get('skuId') or p.get('sku_id') or p.get('id')
            if sku and sku not in seen:
                seen.add(sku)
                unique.append(p)
        
        return unique

if __name__ == '__main__':
    products = asyncio.run(scrape_deep())
    
    if products:
        print(f"\n✅ 成功抓取 {len(products)} 个商品")
        # 提取关键字段
        formatted = []
        for p in products[:10]:
            item = {
                'skuId': p.get('skuId') or p.get('sku_id'),
                'skuName': p.get('skuName') or p.get('name') or p.get('title'),
                'price': p.get('salePrice', {}).get('value') if isinstance(p.get('salePrice'), dict) else p.get('price'),
                'originalPrice': p.get('comparePrice', {}).get('value') if isinstance(p.get('comparePrice'), dict) else p.get('originalPrice'),
                'image': p.get('skuImageInfo', {}).get('skuImage') if isinstance(p.get('skuImageInfo'), dict) else p.get('image')
            }
            formatted.append(item)
        
        print(json.dumps(formatted, indent=2, ensure_ascii=False))
        
        # 保存到文件
        with open('products_7fresh.json', 'w', encoding='utf-8') as f:
            json.dump(formatted, f, ensure_ascii=False, indent=2)
        print(f"\n📄 已保存到 products_7fresh.json")
    else:
        print("\n⚠️ 未抓取到商品数据")
        print("可能原因：页面结构变化、需要登录、或活动已结束")
