#!/usr/bin/env python3
"""基于抓取的真实数据生成文案"""
import re

# 从抓取结果中提取的真实商品数据
raw_texts = [
    "【无抗】冷鲜鸡里脊300g冷鲜|4月14日生产|活禽鲜宰|白羽鸡|谷物喂养限时8.9折9184人已回购￥8.8/盒￥9.9",
    "【烧烤季】蒜香牛肉粒240g冷藏|4月14日生产|全程溯源|可口美味限时8.9折￥17.7￥19.9",
    "【烧烤季】冷鲜五花肉片200g冷鲜|4月14日生产|肥而不腻限时6.9折￥6.8￥9.9",
    "【烧烤季】炙子烤肉300g冷藏|4月14日生产|腌制入味限时6.9折￥13.9￥19.9",
    "【烧烤季】冰鲜三文鱼刺身100g冰鲜|4月14日生产|挪威进口限时7.9折￥31.5￥39.9",
]

products = []

for text in raw_texts:
    # 提取商品名: 【标签】+ 名称
    name_match = re.match(r'([【\[][^】\]]+[】\]][^￥|]+)', text)
    if name_match:
        name = name_match.group(1).strip()
        
        # 提取价格
        prices = re.findall(r'￥([\d\.]+)', text)
        
        # 提取卖点 (|分隔的部分)
        sell_points = []
        if '|' in text:
            parts = text.split('|')
            for p in parts[1:]:
                if '￥' in p:
                    break
                if '折' in p or '生产' in p or '冷' in p or '鲜' in p or '回购' in p:
                    sell_points.append(p.strip())
        
        # 计算折扣
        discount = ""
        if len(prices) >= 2:
            try:
                orig = float(prices[-1])  # 最后一个通常是原价
                curr = float(prices[0])   # 第一个通常是现价
                d = int((1 - curr/orig) * 100)
                discount = f"省{d}%"
            except:
                pass
        
        products.append({
            'name': name,
            'price': prices[0] if prices else '?',
            'original_price': prices[-1] if len(prices) >= 2 else None,
            'discount': discount,
            'sell_points': sell_points[:3]
        })

# 生成文案
copy = """🌙 七鲜晚间出清 · 4月17日限时特惠

💥 今晚不抢，明天后悔！

🔥 超值低价推荐：

"""

for i, p in enumerate(products, 1):
    copy += f"{i}️⃣ {p['name']}\n"
    copy += f"   💰 "
    if p['original_price']:
        copy += f"原价¥{p['original_price']} → "
    copy += f"出清价¥{p['price']}"
    if p['discount']:
        copy += f" ({p['discount']})"
    copy += "\n"
    
    if p['sell_points']:
        points = ' | '.join(p['sell_points'][:2])
        copy += f"   ✨ {points}\n"
    
    copy += "\n"

copy += """⏰ 活动时间：今晚22:00-24:00
📱 更多商品：七鲜APP/小程序
🏠 抢购入口：https://7fresh.m.jd.com/ac/?id=31574

#七鲜晚间出清 #限时特惠 #新鲜食材"""

print(copy)

# 保存
with open('/Users/guanbwenbo/.openclaw/workspace/七鲜出清文案_真实数据.txt', 'w', encoding='utf-8') as f:
    f.write(copy)

print("\n" + "="*50)
print("✅ 文案已保存到: 七鲜出清文案_真实数据.txt")
