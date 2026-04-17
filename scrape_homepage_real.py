#!/usr/bin/env python3
"""从七鲜首页真实抓取商品链接和skuId"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def scrape_homepage_with_skuid():
    url = "https://7fresh.m.jd.com/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        print(f"[*] 访问七鲜首页...")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 等待并滚动加载
        for i in range(10):
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 1000)')
            print(f"[*] 滚动加载... {i+1}/10")
        
        await asyncio.sleep(5)
        
        # 提取页面HTML
        html = await page.content()
        
        # 提取所有商品链接中的skuId
        # 模式: /product/xxxxx.html 或 skuId=xxxxx
        sku_patterns = [
            r'/product/(\d+)\.html',
            r'skuId[=":\s]+(\d+)',
            r'"skuId":\s*(\d+)',
            r'data-sku[=":\s]+["\']?(\d+)',
        ]
        
        all_sku_ids = []
        for pattern in sku_patterns:
            matches = re.findall(pattern, html)
            all_sku_ids.extend(matches)
        
        # 去重
        unique_skus = list(set(all_sku_ids))
        print(f"\n[+] 找到 {len(unique_skus)} 个skuId: {unique_skus[:15]}")
        
        # 提取商品文本和关联
        products_data = await page.evaluate('''() => {
            const items = [];
            const seen = new Set();
            
            // 查找所有商品卡片
            const elements = document.querySelectorAll('[class*="product"], [class*="sku"], [class*="goods"], [class*="item"], [class*="card"]');
            
            elements.forEach(el => {
                const text = el.textContent || '';
                if (text.includes('¥') && text.length > 20 && text.length < 600) {
                    const key = text.slice(0, 80);
                    if (!seen.has(key)) {
                        seen.add(key);
                        // 尝试找到链接
                        const link = el.querySelector('a');
                        const href = link ? link.getAttribute('href') : '';
                        items.push({
                            text: text.trim(),
                            href: href
                        });
                    }
                }
            });
            
            return items;
        }''')
        
        await browser.close()
        
        print(f"[+] 抓取到 {len(products_data)} 个商品元素")
        
        return products_data, unique_skus, html[:5000]

def parse_products(products_data, sku_ids):
    """解析商品数据并关联skuId"""
    products = []
    seen_names = set()
    sku_index = 0
    
    for item in products_data:
        text = item['text']
        href = item.get('href', '')
        
        # 从href提取skuId
        sku_match = re.search(r'/product/(\d+)\.html', href)
        if sku_match:
            sku_id = sku_match.group(1)
        elif sku_index < len(sku_ids):
            sku_id = sku_ids[sku_index]
            sku_index += 1
        else:
            sku_id = None
        
        # 提取商品名
        name_match = re.search(r'([^￥【\]\n]{3,60}?(?:酸奶|蛋糕|豆腐|凉糕|芹菜|花生|牛肉|鸡|鱼|虾|蛋|菜|米|油|奶|咖啡|饮料|面包|青团|烧麦))', text)
        if not name_match:
            # 尝试其他模式
            name_match = re.search(r'([【\[]?[^】\]]+[】\]]?[^￥【\]]{3,50})', text)
        
        if name_match:
            name = name_match.group(1).strip()
            name = re.sub(r'\s+', ' ', name)
            name = re.sub(r'(限时[\d\.]+折|\d+人已回购|京东自营|近期[\d万]+人购买|仅剩[\d]+[盒瓶个]).*', '', name).strip()
            name = re.sub(r'加入购物车', '', name).strip()
            
            # 提取价格
            prices = re.findall(r'￥\s*([\d\.]+)', text)
            
            if name and len(name) > 5 and prices and name not in seen_names:
                seen_names.add(name)
                
                # 提取卖点
                sell_points = []
                if re.search(r'\d+月\d+日生产', text):
                    m = re.search(r'(\d+月\d+日生产)', text)
                    if m:
                        sell_points.append(m.group(1))
                if '冷鲜' in text:
                    sell_points.append('冷鲜')
                if '冷藏' in text:
                    sell_points.append('冷藏')
                if '0乳糖' in text:
                    sell_points.append('0乳糖')
                if '活菌' in text or '益生菌' in text:
                    sell_points.append('益生菌')
                if '古法' in text:
                    sell_points.append('古法工艺')
                if '西北特色' in text:
                    sell_points.append('西北特色')
                
                # 计算折扣
                discount = ""
                if len(prices) >= 2:
                    try:
                        curr = float(prices[0])
                        orig = float(prices[-1])
                        if orig > curr:
                            d = int((1 - curr/orig) * 100)
                            discount = f"省{d}%"
                    except:
                        pass
                # 从文本中提取折扣信息
                if re.search(r'(\d+\.?\d*)折', text):
                    m = re.search(r'(\d+\.?\d*折)', text)
                    if m:
                        discount = m.group(1)
                
                products.append({
                    'name': name[:60],
                    'sku_id': sku_id,
                    'price': prices[0],
                    'original_price': prices[-1] if len(prices) >= 2 else None,
                    'discount': discount,
                    'sell_points': sell_points[:3],
                    'href': href
                })
    
    return products

async def main():
    products_data, sku_ids, debug_html = await scrape_homepage_with_skuid()
    
    products = parse_products(products_data, sku_ids)
    
    print(f"\n[+] 解析出 {len(products)} 个有效商品")
    
    # 显示前10个
    print("\n=== 抓取到的商品（带skuId）===")
    for i, p in enumerate(products[:10], 1):
        print(f"\n{i}. {p['name']}")
        print(f"   skuId: {p['sku_id']}")
        print(f"   现价: ¥{p['price']}", end="")
        if p['original_price']:
            print(f" | 原价: ¥{p['original_price']}", end="")
        if p['discount']:
            print(f" | {p['discount']}", end="")
        print()
        if p['sell_points']:
            print(f"   卖点: {' | '.join(p['sell_points'])}")
        if p['sku_id']:
            print(f"   链接: https://7fresh.m.jd.com/product/{p['sku_id']}.html")
    
    # 保存JSON
    with open('homepage_products_real.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n📄 已保存到 homepage_products_real.json")
    
    return products

if __name__ == '__main__':
    products = asyncio.run(main())
    
    # 筛选有折扣的商品
    deals = [p for p in products if p.get('original_price') and p.get('sku_id')]
    
    if deals:
        print(f"\n\n✅ 找到 {len(deals)} 个带折扣和链接的商品")
    else:
        print("\n\n⚠️ 需要检查抓取结果")
