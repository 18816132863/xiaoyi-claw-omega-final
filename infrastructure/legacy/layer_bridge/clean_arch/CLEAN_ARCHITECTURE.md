# CLEAN_ARCHITECTURE.md - 整洁架构系统

## 目的
实现整洁架构的智能设计与代码生成。

## 架构层次

### 1. 实体层 (Entities)
- 企业核心业务规则
- 无外部依赖
- 最高稳定性

### 2. 用例层 (Use Cases)
- 应用业务规则
- 编排实体
- 定义输入输出端口

### 3. 接口适配层 (Interface Adapters)
- 数据转换
- 控制器
- 展示器
- 网关

### 4. 框架层 (Frameworks)
- Web框架
- 数据库
- 外部服务

## 核心原则

| 原则 | 说明 |
|------|------|
| 依赖规则 | 外层依赖内层 |
| 可测试性 | 核心层独立测试 |
| 框架无关 | 不依赖特定框架 |
| 数据库无关 | 不依赖特定数据库 |

## 使用示例

```bash
# 创建整洁架构项目
openclaw clean create --name "myapp"

# 生成实体
openclaw clean entity --name "User"

# 生成用例
openclaw clean usecase --name "CreateUser"

# 生成控制器
openclaw clean controller --name "UserController"
```

---
*V16.0 整洁架构系统*
