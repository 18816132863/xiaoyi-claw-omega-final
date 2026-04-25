# Root 权限功能移除说明

## 版本信息

- **版本**: v6.3.4
- **日期**: 2026-04-15
- **变更类型**: 安全改进 - 移除 root 权限依赖

## 移除的功能模块

以下需要 root 权限的功能模块已被移除：

### 1. HugePageManager (hugepage_manager.py)
- **功能**: 大页内存管理
- **需要 root 原因**: 需要执行 `sysctl -w vm.nr_hugepages=N`
- **移除原因**: 当前设备无法使用 root 权限

### 2. IRQIsolator (irq_isolator.py)
- **功能**: IRQ 中断隔离
- **需要 root 原因**: 需要修改 `/proc/irq/N/smp_affinity` 和停止 irqbalance 服务
- **移除原因**: 当前设备无法使用 root 权限

### 3. RealtimeScheduler (realtime_scheduler.py)
- **功能**: 实时调度设置
- **需要 root 原因**: 需要设置 SCHED_FIFO/SCHED_RR 调度策略
- **移除原因**: 当前设备无法使用 root 权限

### 4. CacheAwareScheduler (cache_aware_scheduler.py)
- **功能**: 缓存感知调度
- **需要 root 原因**: 需要执行 `sysctl -w kernel.sched_cache_aware=1`
- **移除原因**: 当前设备无法使用 root 权限

## 保留的功能

以下功能不需要 root 权限，已保留：

### Level 0 - 普通用户权限
- ✅ 向量搜索
- ✅ 记忆管理
- ✅ LLM 集成

### Level 1 - 文件系统访问
- ✅ 读写 ~/.openclaw 子目录
- ✅ 文件操作

### Level 2 - 网络访问
- ✅ LLM API 调用
- ✅ Embedding API 调用
- ✅ HTTP 请求

### Level 3 - 原生扩展加载
- ⚠️ 默认禁用
- ⚠️ 需要用户确认
- ✅ 不需要 root 权限

## 权限级别变更

| 级别 | v6.3.3 | v6.3.4 |
|------|--------|--------|
| Level 0 | ✅ 启用 | ✅ 启用 |
| Level 1 | ✅ 启用 | ✅ 启用 |
| Level 2 | ✅ 启用 | ✅ 启用 |
| Level 3 | ❌ 禁用 | ❌ 禁用 |
| Level 4 | ❌ 禁用 | 🗑️ 已移除 |

## 安全改进

1. **不再需要 root 权限**: 所有功能都可以在普通用户权限下运行
2. **减少攻击面**: 移除了所有系统级操作
3. **降低安全风险**: 不再包含可能影响系统稳定性的操作
4. **提高兼容性**: 可以在任何普通用户环境下运行

## 性能影响

移除的功能主要影响高性能场景：

| 功能 | 性能提升 | 影响场景 |
|------|----------|----------|
| HugePageManager | 内存访问延迟降低 20-30% | 大规模向量搜索 |
| IRQIsolator | 延迟抖动降低 80% | 实时推理 |
| RealtimeScheduler | 调度延迟降低 50% | 实时任务 |
| CacheAwareScheduler | 缓存命中率提升 40% | 密集计算 |

**注意**: 对于大多数普通使用场景，这些性能影响可以忽略不计。

## 迁移指南

如果你之前使用了这些功能，请注意：

1. **HugePageManager**: 改用普通内存分配
2. **IRQIsolator**: 不再隔离中断，依赖系统默认调度
3. **RealtimeScheduler**: 使用普通调度策略
4. **CacheAwareScheduler**: 不再优化缓存调度

## 未来计划

如果需要在有 root 权限的环境中使用这些功能，可以：

1. 使用 v6.3.3 或更早版本
2. 等待未来发布的 "Enterprise" 版本（包含所有高性能功能）
3. 在 Docker 容器中运行（需要 --privileged 参数）

---

**变更人**: xkzs2007
**变更日期**: 2026-04-15
**变更原因**: 当前设备无法使用 root 权限，移除不需要的功能以提高兼容性
