---
name: 7fresh-evening-clearance-flow
description: 自动抓取七鲜晚间出清活动页商品，生成带商品详情链接的社群推广文案，并通过圈量机器人发送到微信群。支持用户点击直达商品购买页。
---

# 七鲜晚间出清 · 商品抓取与群发 Skill

## 适用场景

- 七鲜超市运营人员每日晚间出清活动推广
- 自动抓取特价商品并生成带链接的社群文案
- 批量发送促销消息到多个微信群
- **用户可直接点击商品链接直达购买页**

## 触发词

- "七鲜晚间出清"
- "抓取七鲜商品"
- "发送七鲜促销"
- "七鲜出清群发"
- "七鲜带链接发送"

## 商品详情链接格式

**URL 构造规则:**
```
https://7fresh.m.jd.com/product/{skuId}.html
```

**示例:**
- 五花肉片 (skuId: 201931): https://7fresh.m.jd.com/product/201931.html
- 猪腿肉 (skuId: 554636): https://7fresh.m.jd.com/product/554636.html

## 执行流程

### Step 1: 抓取七鲜商品数据

**活动页 URL:**
```
https://7fresh.m.jd.com/ac/?id=31574&from=&storeId={storeId}&tenantId=1&platformId=1&lat={lat}&lng={lng}
```

**参数说明:**
- `storeId`: 门店ID（如 1017261480）
- `lat`: 纬度（如 39.913541）
- `lng`: 经度（如 116.524182）

**抓取方法:**
```bash
# 使用 Playwright 浏览器自动化抓取
cd ~/Downloads && python3 scrape_7fresh_activity.py "https://7fresh.m.jd.com/ac/?id=31574..."
```

**提取字段:**
- `skuName`: 商品名称
- `skuId`: 商品ID（用于构造详情链接）
- `salePrice.value`: 出清价格
- `comparePrice.value`: 原价
- `skuImageInfo.skuImage`: 商品图片
- `sellPointList`: 卖点标签（冷鲜、生产日期等）

### Step 2: 生成带链接的社群文案

**带商品链接的标准版文案:**
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

3️⃣ 【24小时肉】新鲜猪五花350g
   💰 原价¥16.9 → 出清价¥10.1 (省40%)
   ✨ 冷鲜 | 4月15日生产
   👉 直达链接：https://7fresh.m.jd.com/product/554638.html

[继续列出Top 5商品]

⏰ 活动时间：今晚截止
📱 更多商品：七鲜APP/小程序
👇 抢购入口：https://7fresh.m.jd.com/ac/?id=31574

#七鲜晚间出清 #限时特惠 #新鲜食材
```

**用户看到的效果:**
- 点击商品链接 → 直达商品详情页
- 可立即查看商品详情、加入购物车、下单
- 无需再搜索商品，转化率更高

### Step 3: 发送消息到微信群

**前置要求:**
- 圈量平台 appKey
- 圈量平台 appSecret
- 机器人 robotId
- 目标群 groupId

**认证流程:**

1. **获取 Access Token**
```bash
curl -X POST "https://api.xunjinet.com.cn/gateway/qopen/GetAccessToken" \
  -H "Content-Type: application/json" \
  -d '{"app_key":"YOUR_APP_KEY","app_secret":"YOUR_APP_SECRET"}'
```

2. **拉取机器人群列表**
```bash
curl -X POST "https://api.xunjinet.com.cn/gateway/qopen/GetRobotGroupList" \
  -H "Content-Type: application/json" \
  -H "Token: ACCESS_TOKEN" \
  -d '{"robot_id":"ROBOT_ID","limit":100,"offset":0}'
```

3. **发送群消息（带链接文案）**
```bash
curl -X POST "https://api.xunjinet.com.cn/gateway/qopen/SendMsgToGroup" \
  -H "Content-Type: application/json" \
  -H "Token: ACCESS_TOKEN" \
  -d '{
    "robot_id":"ROBOT_ID",
    "group_id":"GROUP_ID",
    "msg_id":"msg_'$(date +%s)'",
    "msg_list":[{
      "msg_type":1,
      "msg_num":1,
      "msg_content":"文案内容（包含 https://7fresh.m.jd.com/product/{skuId}.html 链接）"
    }]
  }'
```

## API 参数说明

### SendMsgToGroup 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| robot_id | string | 是 | 机器人ID |
| group_id | string | 是 | 群ID |
| msg_id | string | 是 | 消息唯一ID（用户自定义）|
| msg_list | array | 是 | 消息列表（1-20条）|
| msg_list[].msg_type | int | 是 | 1=文字（支持链接）|
| msg_list[].msg_num | int | 是 | 消息序号，从1开始递增 |
| msg_list[].msg_content | string | 否 | 消息内容（含商品链接）|

### 响应示例

**成功:**
```json
{
  "data": {"msg_sn": "msg_1744812600"},
  "errcode": 0,
  "errmsg": "",
  "hint": "xxx"
}
```

**常见错误:**
- `1001`: 缺少必填字段（如 msg_id, msg_num, msg_content）
- `1003`: JSON格式错误
- `20105`: msg_list 格式错误

## 执行脚本

### 一键发送（带商品链接）

```bash
# 使用带链接的版本（推荐）
cd ~/.openclaw/workspace/skills/7fresh-evening-clearance-flow
./run_with_links.sh <app_key> <app_secret> <robot_id> <group_id>
```

**示例:**
```bash
./run_with_links.sh coe457d170e19f4546 rsSZb1KWrOKMR3eFNYjlSjnP7GXSLFd1sRaUTeVvZsgGm8Nawohx acceSl33GUETOcwNs6jmgou groupbucrizQmuivU7Z8gbKi9
```

### 基础版本（无商品链接）

```bash
./run.sh <app_key> <app_secret> <robot_id> <group_id>
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 完整技能文档 |
| `run_with_links.sh` | **带商品链接**的一键执行脚本 ⭐推荐 |
| `run.sh` | 基础版本（仅活动页链接）|
| `scrape.py` | 商品抓取脚本 |

## 链接点击效果

用户在微信群中看到消息后：
1. 点击 `👉 直达链接：https://7fresh.m.jd.com/product/201931.html`
2. 自动跳转到七鲜APP/小程序的商品详情页
3. 可直接查看商品详情、价格、库存
4. 一键加入购物车并下单

**优势:**
- ✅ 减少用户操作步骤（无需搜索商品）
- ✅ 提升转化率（直达购买页）
- ✅ 用户体验更好

## 注意事项

1. **Token 有效期:** 7200秒（2小时），过期需重新获取
2. **消息发送频率:** 参考圈量平台频率限制文档
3. **库存数据:** 七鲜API不返回真实库存，文案中库存信息为模拟
4. **链接有效性:** 商品链接长期有效，但商品可能下架
5. **异步回调:** SendMsgToGroup 为异步接口，发送结果通过回调返回

## 关联文档

- 圈量开放平台: http://43.156.100.243:9898/md/__01-start.html
- SendMsgToGroup API: /md/02-消息相关/2001-SendMsgToGroup__0.html
- 消息类型说明: /md/02-消息相关/2100-MessageType__0.html
- 频率限制: /md/02-消息相关/2099-MessageFreq.html

## 快速开始

```bash
# 直接进入 skill 目录
cd ~/.openclaw/workspace/skills/7fresh-evening-clearance-flow

# 使用带商品链接的版本发送
./run_with_links.sh your_app_key your_app_secret your_robot_id your_group_id
```
