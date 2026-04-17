#!/usr/bin/env python3
"""抓取七鲜首页商品数据"""
import asyncio
from playwright.async_api import async_playwright
import re
import json

async def scrape_homepage():
    url = "https://7fresh.m.jd.com/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
            viewport={"width": 390, "height": 844}
        )
        page = await context.new_page()
        
        print(f"[*] 访问七鲜首页: {url}")
        await page.goto(url, wait_until='networkidle', timeout=90000)
        
        # 等待页面加载
        for i in range(8):
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 1000)')
            print(f"[*] 滚动加载... {i+1}/8")
        
        await asyncio.sleep(5)
        
        # 提取页面所有文本
        all_text = await page.evaluate('() => document.body.innerText')
        
        # 提取商品元素
        products_data = await page.evaluate('''() => {
            const items = [];
            const seen = new Set();
            
            // 查找所有可能包含商品信息的元素
            const elements = document.querySelectorAll('[class*="product"], [class*="sku"], [class*="goods"], [class*="item"], [class*="card"]');
            
            elements.forEach(el => {
                const text = el.textContent || '';
                // 只保留包含价格符号的
                if (text.includes('¥') && text.length > 20 && text.length < 500) {
                    const key = text.slice(0, 100);
                    if (!seen.has(key)) {
                        seen.add(key);
                        items.push(text.trim());
                    }
                }
            });
            
            return items;
        }''')
        
        await browser.close()
        
        print(f"\n[+] 抓取到 {len(products_data)} 个原始商品数据")
        
        # 解析商品
        products = []
        seen_names = set()
        
        for text in products_data:
            # 尝试提取商品名
            # 模式1: 【标签】+ 商品名
            name_match = re.search(r'([【\[][^】\]]+[】\]](?:[^￥【\]]{2,50}))', text)
            if not name_match:
                # 模式2: 纯中文商品名
                name_match = re.search(r'([^￥【\]\n]{5,50}?(?:肉|鸡|牛|鱼|虾|蛋|菜|果|米|油|奶|水|酒|茶|零食|饮料|面包))', text)
            
            if name_match:
                name = name_match.group(1).strip()
                name = re.sub(r'\s+', ' ', name)
                name = re.sub(r'(限时[\d\.]+折|\d+人已回购|超市配送|加入购物车).*', '', name).strip()
                
                # 提取价格
                prices = re.findall(r'￥([\d\.]+)', text)
                
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
                        sell_points.append('有机')
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
                        'name': name[:60],
                        'price': prices[0],
                        'original_price': prices[-1] if len(prices) >= 2 else None,
                        'discount': discount,
                        'sell_points': sell_points,
                        'raw': text[:150]
                    })
        
        return products, all_text[:3000]  # 返回前3000字符用于调试

async def main():
    products, debug_text = await scrape_homepage()
    
    print(f"[+] 解析出 {len(products)} 个有效商品")
    
    # 显示前15个
    print("\n=== 抓取到的商品列表 ===")
    for i, p in enumerate(products[:15], 1):
        print(f"\n{i}. {p['name']}")
        print(f"   现价: ¥{p['price']}", end="")
        if p['original_price']:
            print(f" | 原价: ¥{p['original_price']}", end="")
        if p['discount']:
            print(f" | {p['discount']}", end="")
        print()
        if p['sell_points']:
            print(f"   卖点: {' | '.join(p['sell_points'][:3])}")
    
    # 保存JSON
    with open('homepage_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n📄 已保存到 homepage_products.json")
    
    # 生成文案
    if products:
        # 筛选有折扣的商品
        deals = [p for p in products if p['original_price'] and float(p['original_price']) > float(p['price'])]
        deals.sort(key=lambda x: int(x['discount'].replace('省', '').replace('%', '')) if x['discount'] else 0, reverse=True)
        
        copy = """🌙 七鲜首页精选 · 今日特惠

💥 限时低价，新鲜直达！

🔥 热门推荐：

"""
        
        display_products = deals[:8] if deals else products[:8]
        
        for i, p in enumerate(display_products, 1):
            copy += f"{i}️⃣ {p['name']}\n"
            copy += f"   💰 "
            if p['original_price'] and float(p['original_price']) > float(p['price']):
                copy += f"原价¥{p['original_price']} → 现价¥{p['price']}"
                if p['discount']:
                    copy += f" ({p['discount']})"
            else:
                copy += f"¥{p['price']}"
            copy += "\n"
            if p['sell_points']:
                copy += f"   ✨ {' | '.join(p['sell_points'][:2])}\n"
            copy += "\n"
        
        copy += """📱 更多优惠：七鲜APP/小程序
🏠 首页入口：https://7fresh.m.jd.com/

#七鲜超市 #今日特惠 #生鲜直达"""
        
        with open('文案_七鲜首页.txt', 'w', encoding='utf-8') as f:
            f.write(copy)
        
        print("\n" + "="*60)
        print(copy)
        print("="*60)
        print("\n✅ 文案已保存到: 文案_七鲜首页.txt")
    else:
        print("\n⚠️ 未抓取到商品，页面调试信息：")
        print(debug_text)

if __name__ == '__main__':
    asyncio.run(main())
