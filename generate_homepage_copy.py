#!/usr/bin/env python3
"""基于首页抓取的真实数据生成文案"""

# 从调试输出中提取的真实商品数据
products = [
    {"name": "吾岛 茉莉花茶酸奶 90g*2", "price": "9.9", "original_price": None, "sell_points": ["4月9日生产", "0乳糖", "甄选云南茉莉"]},
    {"name": "七鲜 高钙益生菌酸奶100g*8", "price": "7.9", "original_price": None, "sell_points": ["4月12日生产", "400亿活菌", "配料干净"]},
    {"name": "欣和 葱伴侣原酿豆瓣酱300g", "price": "6.9", "original_price": None, "sell_points": ["90天原酿", "浓郁酱香"]},
    {"name": "上海青约500g(油菜)", "price": "1.85", "original_price": None, "sell_points": ["全程溯源", "家常鲜蔬"]},
    {"name": "白玉 100%卤水北豆腐385g", "price": "3.99", "original_price": "5.9", "sell_points": ["4月12日生产", "古法工艺", "豆香醇厚"], "discount": "6.8折"},
    {"name": "超级奶牛乳蛋糕220g", "price": "14.9", "original_price": None, "sell_points": ["4月16日生产", "无抗鸡蛋", "鲜奶打面"]},
    {"name": "七鲜 美式鲜萃无糖黑咖啡1L", "price": "8.9", "original_price": None, "sell_points": ["阿拉比卡豆", "零糖零脂", "解腻搭档"]},
    {"name": "桂花黄米凉糕280g", "price": "10.3", "original_price": "12.9", "sell_points": ["4月15日生产", "西北特色", "开盒即食"], "discount": "限时8折"},
    {"name": "草莓米露750ml", "price": "15.9", "original_price": None, "sell_points": ["产地限定", "草莓味", "独饮小酌"]},
    {"name": "芹菜拌花生220g", "price": "6.1", "original_price": "15.9", "sell_points": ["下酒菜", "冷藏"]},
    {"name": "胡麻油花卷240g", "price": "5.5", "original_price": "12.9", "sell_points": ["新中式面点", "冷藏"]},
    {"name": "一手店 干豆腐卷180g", "price": "8.8", "original_price": "19.9", "sell_points": ["下酒菜", "冷藏"]},
]

# 生成文案
copy = """🌙 七鲜首页精选 · 4月17日特惠

💥 30分钟极速送达，新鲜直达！

🔥 今日低价好物：

"""

for i, p in enumerate(products[:10], 1):
    copy += f"{i}️⃣ {p['name']}\n"
    copy += f"   💰 "
    if p.get('original_price') and float(p['original_price']) > float(p['price']):
        # 计算折扣
        try:
            d = int((1 - float(p['price'])/float(p['original_price'])) * 100)
            copy += f"原价¥{p['original_price']} → 现价¥{p['price']} (省{d}%)"
        except:
            copy += f"¥{p['price']}"
    else:
        copy += f"¥{p['price']}"
    
    if p.get('discount'):
        copy += f" | {p['discount']}"
    copy += "\n"
    
    if p.get('sell_points'):
        copy += f"   ✨ {' | '.join(p['sell_points'][:3])}\n"
    copy += "\n"

copy += """🎁 限时活动：
• 新用户注册享新人优惠
• 领券满99减20
• 小龙虾3斤减10元
• 最高领82元红包券包

⏰ 配送时间：最快30分钟送达
📱 立即下单：七鲜APP/小程序
🏠 首页入口：https://7fresh.m.jd.com/

#七鲜超市 #今日特惠 #生鲜直达"""

print(copy)

# 保存
with open('/Users/guanbwenbo/.openclaw/workspace/七鲜首页文案_0417.txt', 'w', encoding='utf-8') as f:
    f.write(copy)

print("\n" + "="*60)
print("✅ 文案已保存到: 七鲜首页文案_0417.txt")
print("="*60)
