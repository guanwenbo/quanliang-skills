#!/bin/bash
# 七鲜晚间出清 · 一键执行脚本（基础版本）
# 注意：此版本仅包含活动页链接，不包含单个商品链接
# 如需带商品详情链接的版本，请使用: ./run_with_links.sh
#
# Usage: ./run.sh [app_key] [app_secret] [robot_id] [group_id]

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌙 七鲜晚间出清 · 自动抓取与群发${NC}"
echo "======================================"
echo "提示: 此版本不包含单个商品链接"
echo "使用 ./run_with_links.sh 可发送带商品直达链接的版本 ⭐"
echo ""

# 检查参数
if [ $# -lt 4 ]; then
    echo -e "${YELLOW}Usage: $0 <app_key> <app_secret> <robot_id> <group_id>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 coe457d170e19f4546 rsSZb... acceSl33... groupbucri..."
    echo ""
    echo "推荐使用（带商品链接）:"
    echo "  ./run_with_links.sh coe457d170e19f4546 rsSZb... acceSl33... groupbucri..."
    exit 1
fi

APP_KEY=$1
APP_SECRET=$2
ROBOT_ID=$3
GROUP_ID=$4

# Step 1: 获取 Access Token
echo -e "\n${YELLOW}[Step 1] 获取 Access Token...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "https://api.xunjinet.com.cn/gateway/qopen/GetAccessToken" \
    -H "Content-Type: application/json" \
    -d "{\"app_key\":\"$APP_KEY\",\"app_secret\":\"$APP_SECRET\"}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['data']['access_token'])")

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Token 获取失败${NC}"
    echo $TOKEN_RESPONSE
    exit 1
fi

echo -e "${GREEN}✅ Token 获取成功${NC}"

# Step 2: 发送消息
echo -e "\n${YELLOW}[Step 2] 发送消息到微信群...${NC}"
echo "（此版本不含商品详情链接，如需直达链接请使用 run_with_links.sh）"

# 生成文案内容（基础版本，不含商品链接）
MSG_CONTENT=$(cat << 'EOF'
🌙 七鲜晚间出清 · 限时特惠

💥 今晚不抢，明天后悔！

🔥 超值低价推荐：

1️⃣ 【烧烤季】冷鲜猪肥五花肉片200g
   💰 原价¥6.8 → 出清价¥4.8 (省29%)
   ✨ 冷鲜 | 4月14日生产

2️⃣ 【24小时肉】新鲜猪腿肉250g
   💰 原价¥9.9 → 出清价¥5.8 (省41%)
   ✨ 冷鲜 | 4月15日生产

3️⃣ 【24小时肉】新鲜猪五花350g
   💰 原价¥16.9 → 出清价¥10.1 (省40%)
   ✨ 冷鲜 | 4月15日生产

⏰ 活动时间：今晚截止
📱 下单方式：七鲜APP/小程序
👇 抢购链接：https://7fresh.m.jd.com/ac/?id=31574

#七鲜晚间出清 #限时特惠 #新鲜食材
EOF
)

# 构造 JSON 请求体
MSG_ID="msg_$(date +%s)"
REQUEST_BODY=$(python3 -c "
import json
import sys
body = {
    'robot_id': '$ROBOT_ID',
    'group_id': '$GROUP_ID',
    'msg_id': '$MSG_ID',
    'msg_list': [{
        'msg_type': 1,
        'msg_num': 1,
        'msg_content': '''$MSG_CONTENT'''
    }]
}
print(json.dumps(body, ensure_ascii=False))
")

# 发送请求
RESPONSE=$(curl -s -X POST "https://api.xunjinet.com.cn/gateway/qopen/SendMsgToGroup" \
    -H "Content-Type: application/json" \
    -H "Token: $ACCESS_TOKEN" \
    -d "$REQUEST_BODY")

ERRCODE=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('errcode', -1))")

if [ "$ERRCODE" = "0" ]; then
    MSG_SN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['msg_sn'])")
    echo -e "${GREEN}✅ 消息发送成功！${NC}"
    echo -e "   消息SN: $MSG_SN"
    echo ""
    echo -e "${YELLOW}💡 提示: 如需发送带商品直达链接的版本，请使用:${NC}"
    echo "   ./run_with_links.sh $APP_KEY $APP_SECRET $ROBOT_ID $GROUP_ID"
else
    echo -e "${RED}❌ 发送失败 (errcode: $ERRCODE)${NC}"
    echo $RESPONSE
    exit 1
fi

echo -e "\n${GREEN}🎉 全部完成！${NC}"
