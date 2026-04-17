#!/usr/bin/env python3
"""完整抓取七鲜商品数据"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def scrape_full():
    url = "https://7fresh.m.jd.com/ac/?id=31574&storeId=1017261480&tenantId=1&platformId=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 多次滚动加载更多商品
        for i in range(10):
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 1000)')
            print(f"[*] 滚动加载... {i+1}/10")
        
        await asyncio.sleep(5)
        
        # 提取所有可见的商品元素
        products_data = await page.evaluate('''() => {
            const items = [];
            const seen = new Set();
            
            // 查找所有可能包含商品信息的元素
            const elements = document.querySelectorAll('[class*="product"], [class*="sku"], [class*="goods"], [class*="item"]');
            
            elements.forEach(el => {
                const text = el.textContent || '';
                // 只保留包含【】标签和价格符号的
                if (text.includes('【') && text.includes('￥') && text.length > 20) {
                    // 简单去重
                    const key = text.slice(0, 80);
                    if (!seen.has(key)) {
                        seen.add(key);
                        items.push(text.trim());
                    }
                }
            });
            
            return items;
        }''')
        
        await browser.close()
        return products_data

def parse_products(raw_list):
    """解析原始文本为结构化数据"""
    products = []
    seen_names = set()
    
    for text in raw_list:
        # 提取【标签】商品名
        matches = re.findall(r'([【\[][^】\]]+[】\]](?:[^￥|【\]]{2,50}))', text)
        
        for match in matches:
            # 清理名称
            name = match.strip()
            name = re.sub(r'\s+', ' ', name)
            # 去除卖点后缀
            name = re.sub(r'(冷鲜|冷藏|冰鲜|限时[\d\.]+折|\d+人已回购).*', '', name).strip()
            
            # 查找该商品对应的价格
            idx = text.find(match)
            nearby = text[idx:idx+150] if idx >= 0 else ""
            prices = re.findall(r'￥([\d\.]+)', nearby)
            
            if name and len(name) > 5 and prices and name not in seen_names:
                seen_names.add(name)
                
                # 提取卖点
                sell_points = []
                if '4月' in text and '生产' in text:
                    m = re.search(r'(\d+月\d+日生产)', text)
                    if m:
                        sell_points.append(m.group(1))
                if '冷鲜' in text:
                    sell_points.append('冷鲜')
                if '冷藏' in text:
                    sell_points.append('冷藏')
                if '冰鲜' in text:
                    sell_points.append('冰鲜')
                if '有机' in text:
                    sell_points.append('有机认证')
                if '进口' in text:
                    sell_points.append('进口')
                
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
                
                products.append({
                    'name': name[:50],
                    'price': prices[0],
                    'original_price': prices[-1] if len(prices) >= 2 else None,
                    'discount': discount,
                    'sell_points': sell_points
                })
    
    return products

async def main():
    print("[*] 开始抓取七鲜商品...")
    raw_data = await scrape_full()
    
    print(f"\n[+] 抓取到 {len(raw_data)} 个原始商品数据")
    
    products = parse_products(raw_data)
    print(f"[+] 解析出 {len(products)} 个有效商品")
    
    # 显示前10个
    print("\n=== 抓取到的商品列表 ===")
    for i, p in enumerate(products[:10], 1):
        print(f"\n{i}. {p['name']}")
        print(f"   现价: ¥{p['price']}", end="")
        if p['original_price']:
            print(f" | 原价: ¥{p['original_price']}", end="")
        if p['discount']:
            print(f" | {p['discount']}", end="")
        print()
        if p['sell_points']:
            print(f"   卖点: {' | '.join(p['sell_points'])}")
    
    # 保存JSON
    with open('products_all.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n📄 已保存到 products_all.json")
    
    # 生成文案
    if products:
        copy = """🌙 七鲜晚间出清 · 4月17日限时特惠

💥 今晚不抢，明天后悔！

🔥 超值低价推荐：

"""
        
        for i, p in enumerate(products[:8], 1):
            copy += f"{i}️⃣ {p['name']}\n"
            copy += f"   💰 "
            if p['original_price']:
                copy += f"原价¥{p['original_price']} → "
            copy += f"出清价¥{p['price']}"
            if p['discount']:
                copy += f" ({p['discount']})"
            copy += "\n"
            if p['sell_points']:
                copy += f"   ✨ {' | '.join(p['sell_points'][:2])}\n"
            copy += "\n"
        
        copy += """⏰ 活动时间：今晚22:00-24:00
📱 更多商品：七鲜APP/小程序
🏠 抢购入口：https://7fresh.m.jd.com/ac/?id=31574

#七鲜晚间出清 #限时特惠 #新鲜食材"""
        
        with open('文案_final.txt', 'w', encoding='utf-8') as f:
            f.write(copy)
        
        print("\n" + "="*60)
        print(copy)
        print("="*60)
        print("\n✅ 文案已保存到: 文案_final.txt")

if __name__ == '__main__':
    asyncio.run(main())
