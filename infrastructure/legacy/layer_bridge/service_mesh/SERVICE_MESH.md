# SERVICE_MESH.md - 服务网格系统

## 目的
提供服务网格的完整管理能力。

## 支持平台

| 平台 | 版本 | 状态 |
|------|------|------|
| Istio | 1.20 | ✅ |
| Linkerd | 2.14 | ✅ |
| Consul Connect | 1.16 | ✅ |

## 核心能力

### 1. 流量管理
- 智能路由
- 流量分割
- 金丝雀发布
- A/B测试

### 2. 安全通信
- mTLS加密
- 访问控制
- 证书管理

### 3. 可观测性
- 分布式追踪
- 指标监控
- 日志聚合
- 可视化仪表盘

## 使用示例

```bash
# 启用服务网格
openclaw mesh enable --type istio

# 配置金丝雀发布
openclaw mesh canary --service user --percent 10

# 查看服务拓扑
openclaw mesh topology

# 查看追踪
openclaw mesh trace --service user
```

## 性能指标

| 指标 | 值 |
|------|-----|
| 代理延迟 | 0.5ms |
| 吞吐量 | 100000 RPS |
| Sidecar内存 | 50MB |

---
*V16.0 服务网格系统*
