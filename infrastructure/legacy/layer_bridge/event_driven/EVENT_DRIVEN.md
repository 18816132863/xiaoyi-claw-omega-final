# EVENT_DRIVEN.md - 事件驱动架构

## 目的
实现高性能事件驱动架构。

## 支持的消息中间件

| 中间件 | 版本 | 状态 |
|--------|------|------|
| Kafka | 3.6 | ✅ |
| RabbitMQ | 3.12 | ✅ |
| Pulsar | 3.0 | ✅ |
| NATS | 2.10 | ✅ |

## 核心能力

### 1. 事件总线
- 发布订阅
- 事件过滤
- 死信队列

### 2. 事件溯源
- 完整事件历史
- 自动快照
- 事件重放

### 3. CQRS
- 读写分离
- 独立扩展
- 最终一致性

### 4. Saga模式
- 编排式
- 协同式
- 补偿事务

## 使用示例

```bash
# 创建事件总线
openclaw event bus create --name "order-events"

# 发布事件
openclaw event publish --bus "order-events" --type "OrderCreated"

# 订阅事件
openclaw event subscribe --bus "order-events" --handler "processOrder"

# 事件溯源
openclaw event replay --aggregate "order-123"
```

## 性能指标

| 指标 | 值 |
|------|-----|
| 吞吐量 | 100万事件/秒 |
| 延迟 | 1ms |
| 保留期 | 30天 |

---
*V16.0 事件驱动架构*
