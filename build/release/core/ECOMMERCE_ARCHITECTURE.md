# 电商运营架构 - V2.0.0

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户请求                                  │
│   "帮我找团长" / "设计佣金" / "直播脚本" / "达人合作"            │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ L3 编排层 - orchestration/router/ECOMMERCE_ROUTER.json         │
│   意图识别 → 技能路由 → 工作流选择                               │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ L4 执行层 - execution/ecommerce/                                │
│   LeaderExecutor / LiveExecutor / InfluencerExecutor            │
│   OrderExecutor / CommissionCalculator                          │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ L2 记忆层 - memory_context/ecommerce/                           │
│   LeaderProfile / InfluencerProfile / OrderHistory              │
│   CommissionRecord / AnalyticsData                              │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ L6 基础设施层 - infrastructure/models/                          │
│   数据模型 / API接口 / 存储服务                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 技能分布

### L4 执行层技能
| 技能 | 功能 | 触发词 |
|------|------|--------|
| dealer-leader-cooperation | 团长合作 | 找团长、团长合作 |
| douyin-shop-operation | 抖音运营 | 抖音小店、抖音直播 |
| kuaishou-shop-operation | 快手运营 | 快手小店、老铁 |
| product-management | 商品管理 | 选品、定价、库存 |
| marketing-campaign | 营销活动 | 活动策划、促销 |
| customer-service | 客服售后 | 客服、售后、投诉 |

### L3 编排层技能
| 技能 | 功能 | 触发词 |
|------|------|--------|
| omni-channel-ecommerce | 全渠道运营 | 全渠道、多平台 |
| platform-comparison | 平台对比 | 平台对比、选平台 |

### L2 记忆层技能
| 技能 | 功能 | 触发词 |
|------|------|--------|
| ecommerce-analytics | 数据分析 | 数据分析、ROI |

### L6 基础设施层技能
| 技能 | 功能 | 触发词 |
|------|------|--------|
| supply-chain-management | 供应链 | 供应商、采购、物流 |

## 工作流分布

| 工作流 | 层级 | 功能 |
|--------|------|------|
| leader_selection | L4 | 团长筛选 |
| commission_design | L4 | 佣金设计 |
| cooperation_negotiation | L4 | 合作洽谈 |
| live_stream_operation | L4 | 直播带货 |
| influencer_cooperation | L4 | 达人合作 |
| ecommerce_operation | L3 | 电商运营主流程 |

## 数据流向

```
用户请求
    ↓
路由识别 (ECOMMERCE_ROUTER.json)
    ↓
工作流执行 (orchestration/workflows/)
    ↓
执行器处理 (execution/ecommerce/)
    ↓
数据存储 (memory_context/ecommerce/)
    ↓
结果返回
```

## 扩展点

1. **新增平台** → 添加平台运营技能 + 更新路由
2. **新增工作流** → 创建工作流文件 + 注册到路由
3. **新增数据模型** → 添加到 memory_context/ecommerce/
4. **新增执行器** → 添加到 execution/ecommerce/
