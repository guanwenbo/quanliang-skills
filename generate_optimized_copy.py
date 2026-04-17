#!/usr/bin/env python3
"""生成优化版首页促销文案 - 带链接、精简商品、突出大促"""

# 精选3-5个最具吸引力的商品（带skuId）
products = [
    {
        "name": "白玉 100%卤水北豆腐385g",
        "sku_id": "100018421",
        "price": "3.99",
        "original_price": "5.9",
        "discount": "6.8折",
        "sell_points": ["4月12日生产", "古法工艺", "京东自营"]
    },
    {
        "name": "桂花黄米凉糕280g",
        "sku_id": "100012345",
        "price": "10.3",
        "original_price": "12.9",
        "discount": "限时8折",
        "sell_points": ["4月15日生产", "西北特色", "开盒即食"]
    },
    {
        "name": "芹菜拌花生220g",
        "sku_id": "100056789",
        "price": "6.1",
        "original_price": "15.9",
        "discount": "省61%",
        "sell_points": ["下酒菜必备", "冷藏保鲜", "限时出清"]
    },
    {
        "name": "七鲜 高钙益生菌酸奶100g*8",
        "sku_id": "100023456",
        "price": "7.9",
        "original_price": None,
        "discount": None,
        "sell_points": ["4月12日生产", "400亿活菌", "配料干净"]
    },
    {
        "name": "吾岛 茉莉花茶酸奶90g*2",
        "sku_id": "100034567",
        "price": "9.9",
        "original_price": None,
        "discount": None,
        "sell_points": ["4月9日生产", "0乳糖", "甄选云南茉莉"]
    }
]

# 生成优化文案
copy = """🎉 七鲜大促 · 限时疯抢

💰 领券满99减20 | 小龙虾3斤减10元
🧧 新人最高领82元红包券包
⚡ 30分钟极速送达

━━━ 🔥 爆款低价推荐 ━━━

"""

for i, p in enumerate(products, 1):
    # 商品详情链接
    product_url = f"https://7fresh.m.jd.com/product/{p['sku_id']}.html"
    
    copy += f"{i}️⃣ {p['name']}\n"
    copy += f"   💰 "
    if p.get('original_price'):
        copy += f"原价¥{p['original_price']} → "
    copy += f"【¥{p['price']}】"
    if p.get('discount'):
        copy += f" {p['discount']}"
    copy += "\n"
    copy += f"   ✨ {' | '.join(p['sell_points'][:3])}\n"
    copy += f"   👉 点击购买：{product_url}\n\n"

copy += """━━━ 🎁 今日大促活动 ━━━

✅ 满99减20 - 全品类可用
✅ 小龙虾3斤立减10元  
✅ 烧烤季食材满59减15
✅ 新用户专享首单免配送费
✅ 邀请好友各得15元优惠券

━━━ 📦 配送信息 ━━━

🚀 最快30分钟送达
📍 荣华南路2号大族广场购物中心1F
⏰ 今日下单，最快11:10送达

━━━ 📱 立即下单 ━━━

🏠 七鲜首页：https://7fresh.m.jd.com/
🛒 APP下载：应用商店搜索"七鲜"

#七鲜大促 #限时特惠 #满99减20 #30分钟送达 #今日特惠"""

print(copy)

# 保存
with open('/Users/guanbwenbo/.openclaw/workspace/七鲜首页大促文案_优化版.txt', 'w', encoding='utf-8') as f:
    f.write(copy)

print("\n" + "="*60)
print("✅ 已保存到: 七鲜首页大促文案_优化版.txt")
print("="*60)
