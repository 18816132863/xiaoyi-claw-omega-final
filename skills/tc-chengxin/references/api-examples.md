# API 调用示例

_同程程心 API 调用参考_

---

## 📋 通用查询 API（query.js）

### 基础调用

```bash
node scripts/query.js "<用户查询>" <意图类型> <channel> <surface>
```

### 意图类型

| planning 值 | 适用场景 |
|------------|---------|
| `Flight` | 机票、航班查询 |
| `Train` | 火车票、高铁、动车查询 |
| `Hotel` | 酒店、住宿查询 |
| `Scenery` | 景区、景点、门票查询 |
| `Travel` | 度假产品、旅游攻略、行程规划 |

### 渠道参数

| channel | 说明 | 输出格式 |
|---------|------|---------|
| `webchat` | Web 聊天 | 表格 + Markdown 链接 |
| `wechat` | 微信 | 卡片 + 纯文本链接 |
| `weixin` | 微信 | 卡片 + 纯文本链接 |
| `qq` | QQ | 卡片 + Markdown 链接 |
| `dingtalk` | 钉钉 | 卡片 + Markdown 链接 |

### 调用示例

```bash
# 机票查询（webchat）
node scripts/query.js "明天上海到北京的航班" Flight webchat webchat

# 火车票查询（微信）
node scripts/query.js "苏州到上海的高铁" Train wechat ""

# 酒店查询（移动端）
node scripts/query.js "上海外滩附近的酒店" Hotel "" mobile

# 景区查询
node scripts/query.js "苏州有哪些景区" Scenery webchat webchat

# 旅游攻略
node scripts/query.js "帮我规划北京三日游" Travel webchat webchat
```

---

## 🚂 火车票专用 API（train-query.js）

### 基础调用

```bash
node scripts/train-query.js [参数] --channel <渠道> --surface <界面>
```

### 合法参数组合

| 组合 | 参数示例 | 说明 |
|------|---------|------|
| 出发地 + 目的地 | `--departure "北京" --destination "上海"` | 按城市查询 |
| 车次号 | `--train-number "G1234"` | 精确查车次 |
| 出发站 + 到达站 | `--departure-station "北京南站" --arrival-station "上海虹桥站"` | 精确站点查询 |

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--departure <城市>` | 视情况 | 出发地城市 |
| `--destination <城市>` | 视情况 | 目的地城市 |
| `--departure-station <站>` | 视情况 | 出发站（精确） |
| `--arrival-station <站>` | 视情况 | 到达站（精确） |
| `--train-number <车次>` | 视情况 | 车次号（如 G1234） |
| `--extra <补充信息>` | 可选 | 额外信息（日期、偏好等） |
| `--channel <渠道>` | 可选 | 通信渠道 |
| `--surface <界面>` | 可选 | 交互界面 |

### extra 参数示例

| extra 值 | 说明 |
|---------|------|
| `"明天"` | 明天的车次 |
| `"高铁"` | 只查高铁 |
| `"动车"` | 只查动车 |
| `"一等座"` | 优先一等座 |
| `"明天 高铁 赏花专线"` | 多条件组合 |

### 调用示例

```bash
# 北京到上海，明天的高铁
node scripts/train-query.js \
  --departure "北京" \
  --destination "上海" \
  --extra "明天 高铁" \
  --channel webchat \
  --surface webchat

# 查询特定车次
node scripts/train-query.js \
  --train-number "G1234" \
  --channel webchat \
  --surface webchat

# 站到站精确查询
node scripts/train-query.js \
  --departure-station "北京南站" \
  --arrival-station "上海虹桥站" \
  --channel webchat \
  --surface webchat
```

---

## 🔍 意图自动识别

query.js 会自动识别用户查询中的意图关键词：

| 关键词 | 识别为 |
|--------|-------|
| 机票、航班、飞机 | `Flight` |
| 火车、高铁、动车、车票 | `Train` |
| 酒店、住宿、宾馆 | `Hotel` |
| 景区、景点、门票 | `Scenery` |
| 度假、旅游 | `Travel` |

**注意**：火车票专用查询（train-query.js）不自动识别意图，需要明确提供参数。

---

## 📤 响应结构

### 成功响应

```json
{
  "code": "0",
  "data": {
    "data": {
      "trainData": { ... },
      "flightData": { ... },
      "hotelData": { ... },
      "sceneryData": { ... },
      "tripData": { ... }
    }
  }
}
```

### 无结果

```json
{
  "code": "1",
  "message": "无结果"
}
```

### 错误响应

```json
{
  "code": "3",
  "message": "鉴权失败"
}
```

---

_同程旅行 · 让旅行更简单，更快乐_
