# DDD_ENGINE.md - 领域驱动设计引擎

## 目的
实现领域驱动设计的智能建模。

## 核心能力

### 1. 限界上下文
- 自动识别业务边界
- 上下文映射
- 防腐层设计

### 2. 聚合设计
- 聚合根识别
- 实体设计
- 值对象设计
- 领域事件

### 3. 战略设计
- 上下文映射图
- 合作关系
- 共享内核
- 客户供应商

### 4. 战术设计
- 仓储模式
- 工厂模式
- 领域服务
- 规格模式

## 设计模式

| 模式 | 层级 | 用途 |
|------|------|------|
| Aggregate | 战术 | 一致性边界 |
| Entity | 战术 | 唯一标识 |
| Value Object | 战术 | 无标识对象 |
| Domain Event | 战术 | 领域事件 |
| Repository | 战术 | 持久化抽象 |

## 使用示例

```bash
# 分析业务领域
openclaw ddd analyze --domain "电商系统"

# 生成限界上下文
openclaw ddd contexts --domain "电商系统"

# 设计聚合
openclaw ddd aggregate --context "订单" --name "Order"

# 生成代码
openclaw ddd generate --context "订单"
```

---
*V16.0 领域驱动设计引擎*
