#!/usr/bin/env python3
"""从页面文本直接提取商品和链接"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def scrape_deep():
    url = "https://7fresh.m.jd.com/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"[*] 访问七鲜首页...")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        for i in range(8):
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 1000)')
            print(f"[*] 滚动... {i+1}/8")
        
        await asyncio.sleep(5)
        
        # 获取完整页面内容
        html = await page.content()
        text = await page.evaluate('() => document.body.innerText')
        
        await browser.close()
        
        print(f"\n[+] HTML长度: {len(html)}")
        print(f"[+] 文本长度: {len(text)}")
        
        # 从HTML中提取skuId
        sku_ids = re.findall(r'/product/(\d+)\.html', html)
        sku_ids += re.findall(r'"skuId":\s*(\d+)', html)
        sku_ids += re.findall(r'skuId[=":\s]+(\d{5,})', html)
        unique_skus = list(set(sku_ids))
        print(f"\n[+] 提取到 {len(unique_skus)} 个skuId")
        if unique_skus:
            print(f"   skuIds: {unique_skus[:10]}")
        
        return text, html, unique_skus

def extract_products_from_text(text, sku_ids):
    """从页面文本提取商品"""
    products = []
    
    # 查找包含【】或价格的行
    lines = text.split('\n')
    sku_index = 0
    
    for i, line in enumerate(lines):
        # 查找包含价格的行
        if '¥' in line and len(line) > 10 and len(line) < 200:
            # 向前查找商品名
            name = ""
            for j in range(max(0, i-5), i):
                prev_line = lines[j].strip()
                if len(prev_line) > 5 and len(prev_line) < 60 and not ('¥' in prev_line and len(prev_line) < 15):
                    # 排除纯价格行
                    if not re.match(r'^￥?[\d\.]+$', prev_line):
                        name = prev_line
                        break
            
            # 提取价格
            prices = re.findall(r'￥?\s*([\d\.]+)', line)
            
            # 分配skuId
            sku_id = sku_ids[sku_index] if sku_index < len(sku_ids) else None
            
            if name and prices and len(name) > 5:
                sku_index += 1
                
                # 清理名称
                name = re.sub(r'(京东自营|近期[\d万]+人购买|仅剩[\d]+[盒瓶个份]|加入购物车).*', '', name).strip()
                
                # 提取卖点 - 向后查找
                sell_points = []
                for j in range(i+1, min(len(lines), i+4)):
                    next_line = lines[j].strip()
                    if '|' in next_line or '生产' in next_line or '冷藏' in next_line:
                        parts = next_line.split('|')
                        for part in parts[:3]:
                            part = part.strip()
                            if len(part) > 2 and len(part) < 20:
                                sell_points.append(part)
                        break
                
                # 计算折扣
                discount = ""
                if len(prices) >= 2:
                    try:
                        curr = float(prices[0])
                        orig = float(prices[1])
                        if orig > curr:
                            d = int((1 - curr/orig) * 100)
                            discount = f"省{d}%"
                    except:
                        pass
                
                products.append({
                    'name': name[:50],
                    'sku_id': sku_id,
                    'price': prices[0],
                    'original_price': prices[1] if len(prices) >= 2 else None,
                    'discount': discount,
                    'sell_points': sell_points[:3]
                })
    
    return products

async def main():
    text, html, sku_ids = await scrape_deep()
    
    products = extract_products_from_text(text, sku_ids)
    
    print(f"\n[+] 解析出 {len(products)} 个商品")
    
    # 去重
    seen = set()
    unique = []
    for p in products:
        key = p['name']
        if key not in seen:
            seen.add(key)
            unique.append(p)
    
    print(f"[+] 去重后 {len(unique)} 个商品")
    
    # 显示
    print("\n=== 商品列表 ===")
    for i, p in enumerate(unique[:15], 1):
        print(f"\n{i}. {p['name']}")
        if p['sku_id']:
            print(f"   skuId: {p['sku_id']}")
        print(f"   价格: ¥{p['price']}", end="")
        if p['original_price']:
            print(f" (原价¥{p['original_price']})", end="")
        print()
        if p['discount']:
            print(f"   折扣: {p['discount']}")
        if p['sell_points']:
            print(f"   卖点: {' | '.join(p['sell_points'])}")
    
    # 保存
    with open('/Users/guanbwenbo/.openclaw/workspace/七鲜首页商品_真实抓取.json', 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"\n📄 已保存到 七鲜首页商品_真实抓取.json")
    
    return unique

if __name__ == '__main__':
    asyncio.run(main())
