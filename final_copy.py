#!/usr/bin/env python3
"""基于真实抓取数据生成正确文案"""
import json

# 读取抓取的数据
with open('/Users/guanbwenbo/.openclaw/workspace/skills/7fresh-evening-clearance-flow/products_all.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# 筛选真正打折的商品（现价 < 原价）
valid_deals = []
for p in products:
    try:
        price = float(p['price'])
        orig = float(p['original_price']) if p['original_price'] else 0
        if orig > price and orig > 0:
            discount_pct = int((1 - price/orig) * 100)
            valid_deals.append({
                'name': p['name'],
                'price': p['price'],
                'original_price': p['original_price'],
                'discount': f"省{discount_pct}%",
                'sell_points': [s for s in p['sell_points'] if s not in ['冷鲜', '冰鲜', '有机认证']][:2]
            })
    except:
        pass

# 按折扣力度排序
valid_deals.sort(key=lambda x: int(x['discount'].replace('省', '').replace('%', '')), reverse=True)

print(f"✅ 筛选出 {len(valid_deals)} 个真实优惠商品\n")

# 生成文案
copy = """🌙 七鲜晚间出清 · 4月17日限时特惠

💥 今晚不抢，明天后悔！

🔥 超值低价推荐：

"""

for i, p in enumerate(valid_deals[:8], 1):
    copy += f"{i}️⃣ {p['name']}\n"
    copy += f"   💰 原价¥{p['original_price']} → 出清价¥{p['price']} ({p['discount']})\n"
    if p['sell_points']:
        copy += f"   ✨ {' | '.join(p['sell_points'])}\n"
    copy += "\n"

copy += """⏰ 活动时间：今晚22:00-24:00
📱 更多商品：七鲜APP/小程序
🏠 抢购入口：https://7fresh.m.jd.com/ac/?id=31574

#七鲜晚间出清 #限时特惠 #新鲜食材"""

print(copy)

# 保存
output_path = '/Users/guanbwenbo/.openclaw/workspace/七鲜晚间出清文案_真实抓取.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(copy)

print(f"\n{'='*60}")
print(f"✅ 文案已保存到: {output_path}")
print(f"{'='*60}")
