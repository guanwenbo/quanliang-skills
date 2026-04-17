#!/usr/bin/env python3
"""从七鲜活动页抓取真实skuId和商品链接"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def scrape_with_skuid():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        print(f"[*] 访问七鲜活动页...")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 监听网络请求获取API数据
        api_responses = []
        
        async def handle_response(response):
            url = response.url
            try:
                if any(k in url for k in ['sku', 'product', 'goods', 'list', 'activity']):
                    text = await response.text()
                    if len(text) > 100 and 'skuId' in text:
                        api_responses.append({'url': url, 'text': text[:3000]})
            except:
                pass
        
        page.on('response', handle_response)
        
        # 滚动加载
        for i in range(10):
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 1000)')
            print(f"[*] 滚动... {i+1}/10")
        
        await asyncio.sleep(5)
        
        # 获取页面内容
        html = await page.content()
        text = await page.evaluate('() => document.body.innerText')
        
        await browser.close()
        
        print(f"\n[+] 捕获 {len(api_responses)} 个API响应")
        print(f"[+] HTML长度: {len(html)}")
        
        return html, text, api_responses

def extract_skuid_from_html(html):
    """从HTML中提取skuId"""
    sku_ids = []
    
    # 多种模式匹配
    patterns = [
        r'/product/(\d+)\.html',
        r'"skuId":\s*(\d+)',
        r'"sku_id":\s*(\d+)',
        r'skuId[=":\s]+["\']?(\d{5,})',
        r'data-sku-id[=":\s]+["\']?(\d+)',
        r'id[=":\s]+["\']?(\d{8,})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        sku_ids.extend(matches)
    
    # 去重并过滤合理长度
    unique = []
    for s in set(sku_ids):
        if len(s) >= 5 and len(s) <= 15 and s.isdigit():
            unique.append(s)
    
    return unique

def extract_products_from_text(text):
    """从页面文本提取商品信息"""
    products = []
    
    # 查找商品块 - 包含【】标签和价格
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if '【' in line and '】' in line and '¥' in line and len(line) > 20:
            # 提取商品名
            name_match = re.search(r'([【\[][^】\]]+[】\]][^￥【\]]{2,50})', line)
            if name_match:
                name = name_match.group(1).strip()
                name = re.sub(r'\s+', ' ', name)
                name = re.sub(r'(限时[\d\.]+折|\d+人已回购|冷鲜|冷藏|冰鲜).*$', '', name).strip()
                
                # 提取价格
                prices = re.findall(r'￥([\d\.]+)', line)
                
                if name and len(name) > 5 and prices:
                    # 提取卖点
                    sell_points = []
                    nearby = ' '.join(lines[i:i+3])
                    if re.search(r'\d+月\d+日生产', nearby):
                        m = re.search(r'(\d+月\d+日生产)', nearby)
                        if m:
                            sell_points.append(m.group(1))
                    if '冷鲜' in nearby:
                        sell_points.append('冷鲜')
                    if '限时' in nearby:
                        m = re.search(r'(限时[\d\.]+折)', nearby)
                        if m:
                            sell_points.append(m.group(1))
                    
                    products.append({
                        'name': name[:50],
                        'price': prices[0],
                        'original_price': prices[1] if len(prices) > 1 else None,
                        'sell_points': sell_points
                    })
    
    return products

async def main():
    html, text, api_responses = await scrape_with_skuid()
    
    # 提取skuId
    sku_ids = extract_skuid_from_html(html)
    print(f"\n[+] 提取到 {len(sku_ids)} 个skuId")
    print(f"   前10个: {sku_ids[:10]}")
    
    # 提取商品
    products = extract_products_from_text(text)
    print(f"\n[+] 提取到 {len(products)} 个商品")
    
    # 合并skuId和商品
    for i, p in enumerate(products):
        if i < len(sku_ids):
            p['sku_id'] = sku_ids[i]
            p['url'] = f"https://7fresh.m.jd.com/product/{sku_ids[i]}.html"
    
    # 显示结果
    print("\n=== 商品列表（带链接）===")
    valid_count = 0
    for i, p in enumerate(products[:15], 1):
        print(f"\n{i}. {p['name']}")
        print(f"   价格: ¥{p['price']}", end="")
        if p.get('original_price'):
            print(f" (原价¥{p['original_price']})", end="")
        print()
        if p.get('sku_id'):
            print(f"   skuId: {p['sku_id']}")
            print(f"   链接: {p['url']}")
            valid_count += 1
        if p.get('sell_points'):
            print(f"   卖点: {' | '.join(p['sell_points'])}")
    
    # 保存
    with open('/Users/guanbwenbo/.openclaw/workspace/七鲜商品_带真实链接.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ 共 {len(products)} 个商品，{valid_count} 个带真实链接")
    print("📄 已保存到: 七鲜商品_带真实链接.json")
    
    return products

if __name__ == '__main__':
    asyncio.run(main())
