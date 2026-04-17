# 七鲜晚间出清 · 商品抓取与群发（带商品链接）

自动抓取七鲜晚间出清活动页商品，生成**带商品详情链接**的社群推广文案，并通过圈量机器人发送到微信群。用户可直接点击商品链接直达购买页。

## ✨ 核心功能

- **商品抓取**: 自动抓取七鲜晚间出清活动商品
- **智能文案**: 生成带商品详情链接的社群文案
- **一键群发**: 通过圈量机器人发送到微信群
- **直达购买**: 用户点击链接直达商品详情页，无需搜索

## 🚀 快速使用

### 带商品链接版本（推荐）

```bash
cd ~/.openclaw/workspace/skills/7fresh-evening-clearance-flow
./run_with_links.sh <app_key> <app_secret> <robot_id> <group_id>
```

**示例：**
```bash
./run_with_links.sh coe457d170e19f4546 rsSZb1KWrOKMR3eFNYjlSjnP7GXSLFd1sRaUTeVvZsgGm8Nawohx acceSl33GUETOcwNs6jmgou groupbucrizQmuivU7Z8gbKi9
```

### 生成的文案示例

```
🌙 七鲜晚间出清 · 限时特惠

💥 今晚不抢，明天后悔！

🔥 超值低价推荐：

1️⃣ 【烧烤季】冷鲜猪肥五花肉片200g
   💰 原价¥6.8 → 出清价¥4.8 (省29%)
   ✨ 冷鲜 | 4月14日生产
   👉 直达链接：https://7fresh.m.jd.com/product/201931.html

2️⃣ 【24小时肉】新鲜猪腿肉250g
   💰 原价¥9.9 → 出清价¥5.8 (省41%)
   ✨ 冷鲜 | 4月15日生产
   👉 直达链接：https://7fresh.m.jd.com/product/554636.html

⏰ 活动时间：今晚截止
📱 更多商品：https://7fresh.m.jd.com/ac/?id=31574
```

**用户点击链接后：** 直达商品详情页 → 可立即购买

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 完整技能文档（API说明、参数、流程）|
| `run_with_links.sh` | **带商品链接**的一键执行脚本 ⭐推荐 |
| `run.sh` | 基础版本（仅活动页链接）|
| `scrape.py` | 商品抓取脚本 |

## 🔗 商品链接格式

```
https://7fresh.m.jd.com/product/{skuId}.html
```

**示例：**
- 五花肉片: https://7fresh.m.jd.com/product/201931.html
- 猪腿肉: https://7fresh.m.jd.com/product/554636.html
- 猪五花: https://7fresh.m.jd.com/product/554638.html

## 📝 触发词

- "七鲜晚间出清"
- "抓取七鲜商品"
- "发送七鲜促销"
- "七鲜带链接发送"

## ⚠️ 注意事项

- Token 有效期 7200秒（2小时）
- 消息发送为异步，结果通过回调返回
- 库存信息为模拟（七鲜API不返回真实库存）
- 商品链接长期有效，但商品可能下架

## 🔧 分步执行

如需自定义商品列表，编辑 `run_with_links.sh` 中的 `PRODUCTS` 数组：

```bash
PRODUCTS=(
    "商品名|skuId|现价|原价|卖点1|卖点2"
    "【烧烤季】冷鲜猪肥五花肉片200g|201931|4.8|6.8|冷鲜|4月14日生产"
    # 添加更多商品...
)
```

## 📚 关联 Skill

- `quanliang-skills` - 圈量机器人消息发送
