#!/bin/bash
# 七鲜晚间出清 · 带商品链接的一键执行脚本
# Usage: ./run_with_links.sh [app_key] [app_secret] [robot_id] [group_id]

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🌙 七鲜晚间出清 · 自动抓取与群发（带商品链接）${NC}"
echo "======================================"

# 检查参数
if [ $# -lt 4 ]; then
    echo -e "${YELLOW}Usage: $0 <app_key> <app_secret> <robot_id> <group_id>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 coe457d170e19f4546 rsSZb... acceSl33... groupbucri..."
    exit 1
fi

APP_KEY=$1
APP_SECRET=$2
ROBOT_ID=$3
GROUP_ID=$4

# 商品数据（含skuId和详情链接）
# 格式: 商品名|skuId|现价|原价|卖点
PRODUCTS=(
    "【烧烤季】冷鲜猪肥五花肉片200g|201931|4.8|6.8|冷鲜|4月14日生产"
    "【24小时肉】新鲜猪腿肉250g|554636|5.8|9.9|冷鲜|4月15日生产|24小时鲜肉"
    "【24小时肉】新鲜猪五花350g|554638|10.1|16.9|冷鲜|4月15日生产"
    "麻酱鸡蛋5枚250g|522538|11.9|14.9|0亚硝酸盐|2月1日生产"
    "【烧烤季】静腌黑猪东北大油边250g|554863|18|35.9|冷鲜|4月14日生产"
)

# 生成带链接的文案
generate_copy() {
    local copy="🌙 七鲜晚间出清 · 限时特惠

💥 今晚不抢，明天后悔！

🔥 超值低价推荐：
"
    
    local i=1
    for product in "${PRODUCTS[@]}"; do
        IFS='|' read -r name skuId price original_price sell_points <<< "$product"
        
        # 计算折扣
        local discount=""
        if [ "$original_price" != "N/A" ]; then
            discount=$(python3 -c "print(int((1-$price/$original_price)*100))")
            discount="(省${discount}%)"
        fi
        
        # 商品详情链接
        local product_url="https://7fresh.m.jd.com/product/${skuId}.html"
        
        copy="${copy}
${i}️⃣ ${name}
   💰 原价¥${original_price} → 出清价¥${price} ${discount}
   ✨ ${sell_points}
   👉 直达链接：${product_url}"
        
        ((i++))
    done
    
    copy="${copy}

⏰ 活动时间：今晚截止
📱 更多商品：七鲜APP/小程序
🏠 抢购入口：https://7fresh.m.jd.com/ac/?id=31574

#七鲜晚间出清 #限时特惠 #新鲜食材"
    
    echo "$copy"
}

# Step 1: 获取 Access Token
echo -e "\n${YELLOW}[Step 1] 获取 Access Token...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "https://api.xunjinet.com.cn/gateway/qopen/GetAccessToken" \
    -H "Content-Type: application/json" \
    -d "{\"app_key\":\"$APP_KEY\",\"app_secret\":\"$APP_SECRET\"}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['data']['access_token'])" 2>/dev/null || echo "")

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Token 获取失败${NC}"
    echo $TOKEN_RESPONSE
    exit 1
fi

echo -e "${GREEN}✅ Token 获取成功${NC}"

# Step 2: 生成文案
echo -e "\n${YELLOW}[Step 2] 生成社群文案（含商品链接）...${NC}"
MSG_CONTENT=$(generate_copy)

echo -e "${GREEN}✅ 文案生成完成${NC}"
echo "---"
echo "$MSG_CONTENT"
echo "---"

# Step 3: 发送消息
echo -e "\n${YELLOW}[Step 3] 发送消息到微信群...${NC}"

MSG_ID="msg_$(date +%s)"

# 构造 JSON 请求体
REQUEST_BODY=$(python3 << EOF
import json
body = {
    "robot_id": "$ROBOT_ID",
    "group_id": "$GROUP_ID",
    "msg_id": "$MSG_ID",
    "msg_list": [{
        "msg_type": 1,
        "msg_num": 1,
        "msg_content": """$MSG_CONTENT"""
    }]
}
print(json.dumps(body, ensure_ascii=False))
EOF
)

# 发送请求
RESPONSE=$(curl -s -X POST "https://api.xunjinet.com.cn/gateway/qopen/SendMsgToGroup" \
    -H "Content-Type: application/json" \
    -H "Token: $ACCESS_TOKEN" \
    -d "$REQUEST_BODY")

ERRCODE=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('errcode', -1))" 2>/dev/null)

if [ "$ERRCODE" = "0" ]; then
    MSG_SN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['msg_sn'])" 2>/dev/null)
    echo -e "${GREEN}✅ 消息发送成功！${NC}"
    echo -e "   消息SN: $MSG_SN"
else
    echo -e "${RED}❌ 发送失败 (errcode: $ERRCODE)${NC}"
    echo $RESPONSE
    exit 1
fi

echo -e "\n${GREEN}🎉 全部完成！用户可直接点击商品链接购买${NC}"
