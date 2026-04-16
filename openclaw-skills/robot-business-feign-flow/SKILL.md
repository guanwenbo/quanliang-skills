---
name: robot-business-feign-flow
description: 通过 openclaw 直连圈量接口，完成机器人绑定、拉取机器人群列表、向指定群发送指定消息。适用于基于 hishop-switch 字段语义的自动化编排场景，包含 token 获取、绑定前置、群列表分页与群消息发送。
---

# 文档基准（最新）

- 文档站点：`http://43.156.100.243:9898/md/__01-start.html`
- 基础域名（文档声明）：`api.xunjinet.com.cn`
- 统一网关前缀：`https://$basehost/gateway/qopen/`
- 协议与格式：`HTTPS` + `POST` + `JSON`

# 目标

参考 `hishop-switch` 的请求/响应模型与业务语义，但执行时不调用本工程 RPC 或 Application Service，直接请求圈量网关：

- 基础地址（最新）：`https://api.xunjinet.com.cn/gateway/qopen/`

主流程目标（openclaw）：

1. 绑定机器人（登录二维码 -> 人工扫码 -> 机器人可用）
2. 拉取机器人群列表（分页）
3. 按指定 `groupId` 发送指定消息

补充能力（可选）：

1. `RobotBusinessFeignClient#getRobotAccountList`
2. `RobotBusinessFeignClient#getRobotAccountByIds`
3. `RobotBusinessFeignClient#sendMessageToAccount`

# 适用触发词

- 通过 openclaw 绑定机器人
- 拉取机器人群列表
- 给指定群发送指定消息
- 机器人扫码登录后自动执行群发
- 需要绕过本工程服务直连圈量

# 执行前置

1. 准备圈量平台凭证：`appKey`、`appSecret`。
2. 准备业务维度标识：`wwCorpId`（店铺绑定企微公司标识）。
3. 准备 HTTP 客户端（curl/postman/openclaw http action）。
4. 所有请求均设置：
   - `Content-Type: application/json`
   - `Token: <token>`

# 核心鉴权机制

执行顺序必须固定：

1. 获取服务商 token
   - `POST /GetAccessToken`
   - body: `{"appKey":"...","appSecret":"..."}`
2. 获取子租户 token  
   - `POST /GetSubCorpToken`
   - Header: `Token=<服务商token>`
   - body: `{"wwCorpId":"..."}`
3. 调用业务接口
   - Header: `Token=<子租户token>`
   - body: 各业务接口对应请求体

说明：`RobotBusinessFeignClient` 在工程里通过拦截器自动做这件事；本 skill 要求在 openclaw 中显式分步完成。

# 主流程（绑定 -> 拉群 -> 发群消息）

## Step 0 输入参数

最小输入：

- `appKey`
- `appSecret`
- `wwCorpId`
- `robotId`
- `targetGroupId`
- `messageText`（或完整 `msgList`）

## Step 1 绑定机器人（前置）

推荐流程：

1. 调 `POST /GenHostAccountLoginQRCode` 生成扫码登录二维码。
2. 人工扫码完成登录绑定。
3. 通过状态接口确认机器人已可用（例如轮询状态查询接口，直到在线/可发消息）。

说明：若机器人已绑定且在线，可跳过本步骤。

## Step 2 拉取群列表

1. 调 `POST /GetRobotWatchGroupChatList`
2. 入参：`robotId + limit + offset`
3. 按 `hasMore` 翻页拉全量 `groupList`
4. 校验 `targetGroupId` 是否存在于群列表

## Step 3 向指定群发消息

1. 组装 `POST /SendMsgToGroup` 请求体：
   - `robotId`
   - `groupId = targetGroupId`
   - `msgList`（建议先发 `TEXT`）
2. 调用后检查 `errcode == 0`
3. 记录 `msgSn` 用于后续异步回执对账

## Step 4 失败回滚/补偿

1. 群不存在：终止并返回“目标群不在机器人关注列表”
2. 发送失败：记录 `errcode/errmsg`，可按策略重试一次
3. 高频限流：进入退避重试（建议指数退避）

# 关键接口剧本

## 1) getRobotWatchGroupChatList（主流程必需）

### 接口信息
- 最新文档页面：`/md/03-群相关/02-群列表/3201-GetWatchGroupChatList.html`
- 路径：`POST /GetRobotWatchGroupChatList`
- 入参：`RobotIdPageSendRequest`
- 出参：`BaseRobotResponse<RobotGroupPageResponse>`

### 操作步骤
1. 校验 `robotId`。
2. 初始分页参数建议：`limit=100, offset=0`。
3. 直连调用 `POST /GetRobotWatchGroupChatList`。
4. 判断：
   - `errCode == 0` 且 `data != null`
   - 读取 `data.groupList`
5. 若 `hasMore=true`，递增 `offset` 继续拉取。

## 2) sendMsgToGroup（主流程必需）

### 接口信息
- 最新文档页面：`/md/02-消息相关/2001-SendMsgToGroup__0.html`
- 路径：`POST /SendMsgToGroup`
- 入参：`RobotGroupMsgSendRequest`
- 出参：`BaseRobotResponse<RobotMsgSnResponse>`

### 操作步骤
1. 校验 `robotId/groupId/msgList`。
2. 若 `msgType` 为 `FILE/VIDEO`，对 `href` 文件名 URL 编码。
3. 调 `POST /SendMsgToGroup`。
4. 读取 `data.msgSn`。

## 3) getRobotAccountList（可选）

### 接口信息
- 最新文档页面：`/md/01-机器人相关/04-机器人客户/1405-GetRobotAccountListV2.html`
- 路径：`POST /GetRobotAccountListV2`
- 用途：补充客户信息或校验客户关系

### 特殊处理
- 参考工程逻辑，发送前对 `msgList` 执行文件名编码：
  - 当 `msgType` 为 `FILE` 或 `VIDEO` 时
  - 对 `href` 的文件名做 URL 编码

### 操作步骤
1. 校验 `robotId/groupId/msgList`。
2. 若有文件或视频消息，确保文件 URL 可编码。
3. 直连调用 `POST /SendMsgToGroup`。
4. 读取 `data.msgSn`（或映射后的消息 sn）。
4. 记录消息发送事件与 sn，便于异步回执对账。

## 4) getRobotAccountByIds（可选）

### 接口信息
- 最新文档页面：`/md/01-机器人相关/04-机器人客户/1406-GetRobotAccountByIdsV2.html`
- 路径：`POST /GetRobotAccountByIdsV2`
- 用途：按客户ID精确查询

### 特殊处理
- 与群发一致，文件/视频消息 URL 文件名会预编码。

### 操作步骤
1. 校验 `robotId/accountId/msgList`。
2. 处理文件 URL 编码。
3. 直连调用 `POST /SendMessageToAccount` 并提取 `msgSn`。
4. 入库或日志记录 message sn。

## 5) sendMessageToAccount（可选）

### 接口信息
- 最新文档页面：`/md/02-消息相关/2002-SendMessageToAccount__0.html`
- 路径：`POST /SendMessageToAccount`
- 用途：当目标不是群而是单聊时使用

# 错误处理规则

1. 直连模式下不依赖 `RobotFastjsonDecoder`，统一按响应体判断：
   - `errcode != 0` 视为失败
   - 记录 `errcode/errmsg/hint`
2. 若 `data == null`，按“响应为空”处理，禁止盲目取字段。
3. 消息发送接口需重点记录：
   - 入参摘要（脱敏）
   - `errCode/errMsg/hint`
   - 业务唯一标识（如 msgSn）

# 建议输出格式（给调用方/排障）

每次调用固定输出：

1. 接口名 + 路径
2. 入参摘要（关键字段）
3. 鉴权来源（服务商 token / 子租户 token）
4. 分页信息（若有）
5. `errCode/errMsg`
6. 关键结果（客户数、群数、msgSn）

# 快速排障清单

1. `GetAccessToken` 是否成功返回服务商 token。
2. `GetSubCorpToken` 是否成功返回子租户 token。
3. `wwCorpId` 是否与业务目标店铺一致。
4. 目标对象是否存在（robotId/groupId/accountId）。
5. 文件/视频消息 URL 是否可访问且文件名可编码。

# openclaw 编排建议

按 5 段 action 编排：

1. `http_get_access_token`
2. `http_get_subcorp_token`
3. `http_bind_robot`（`GenHostAccountLoginQRCode` + 人工扫码等待）
4. `http_get_watch_group_list`（分页循环）
5. `http_send_msg_to_group`

变量传递：

- action1.token -> action2.header.Token
- action2.subCorpToken -> action3/4/5.header.Token
- action4.groupList -> action5.groupId 选择逻辑

# 字段策略（重要）

最新文档中，两个客户接口已升级为 `V2`。若页面参数表因权限不可见，按以下策略执行：

1. 优先使用官方页面可见字段。
2. 不可见字段使用工程现有 DTO 字段作为兼容兜底（`RobotIdPageSendRequest`、`RobotAccountListSendRequest`）。
3. 首次联调打开请求/响应全量日志，确认 V2 字段差异后再收敛。
