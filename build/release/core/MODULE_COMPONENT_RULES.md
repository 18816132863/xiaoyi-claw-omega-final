# 模块与组件接入规则

## V2.7.0 - 2026-04-10

将技能要求扩展到模块和组件，确保架构一致性。

---

## 一、总原则

1. **模块必须归属层级**，不允许游离模块
2. **组件必须注册入表**，未注册组件不可用
3. **接口必须标准化**，禁止自定义接口格式
4. **性能必须达标**，延迟/QPS需满足要求
5. **监控必须接入**，所有组件可观测

---

## 二、模块分类与归属

| 模块类型 | 归属层 | 示例 | 性能要求 |
|---------|--------|------|----------|
| **核心模块** | L1 Core | FastBridge, Identity | 延迟 <0.01ms |
| **记忆模块** | L2 Memory | LayerCache, ZeroCopy | 延迟 <0.01ms |
| **编排模块** | L3 Orchestration | AsyncQueue, SmartRouter | 延迟 <0.1ms |
| **执行模块** | L4 Execution | UnifiedOptimizer | 延迟 <1ms |
| **治理模块** | L5 Governance | PerformanceMonitor | 延迟 <10ms |
| **基建模块** | L6 Infrastructure | Logger, Config | 延迟 <5ms |

---

## 三、组件接入标准

### 3.1 必须实现

```python
class Component:
    """组件基类"""
    
    @property
    def name(self) -> str:
        """组件名称"""
        pass
    
    @property
    def version(self) -> str:
        """组件版本"""
        pass
    
    @property
    def layer(self) -> int:
        """归属层级 (1-6)"""
        pass
    
    def init(self) -> bool:
        """初始化"""
        pass
    
    def health_check(self) -> dict:
        """健康检查"""
        pass
    
    def get_stats(self) -> dict:
        """获取统计"""
        pass
    
    def shutdown(self) -> bool:
        """关闭"""
        pass
```

### 3.2 必须提供

| 项目 | 说明 | 格式 |
|------|------|------|
| `__init__.py` | 模块入口 | 导出所有公共接口 |
| `README.md` | 使用文档 | 包含示例代码 |
| `config.json` | 配置文件 | JSON Schema |
| `benchmark.py` | 性能测试 | 可独立运行 |

---

## 四、性能要求

### 4.1 延迟分级

| 级别 | 延迟范围 | 适用场景 |
|------|----------|----------|
| **P0 极速** | <0.01ms | 层间调用、缓存读取 |
| **P1 快速** | <0.1ms | 路由、数据共享 |
| **P2 标准** | <1ms | 优化、转换 |
| **P3 普通** | <10ms | 监控、审计 |
| **P4 宽松** | <100ms | 日志、备份 |

### 4.2 QPS 要求

| 层级 | 最低 QPS | 推荐 QPS |
|------|----------|----------|
| L1 Core | 100,000 | 200,000+ |
| L2 Memory | 100,000 | 200,000+ |
| L3 Orchestration | 50,000 | 100,000+ |
| L4 Execution | 10,000 | 50,000+ |
| L5 Governance | 1,000 | 10,000+ |
| L6 Infrastructure | 10,000 | 50,000+ |

### 4.3 资源限制

| 资源 | 限制 | 说明 |
|------|------|------|
| 内存 | <100MB | 单组件最大占用 |
| CPU | <10% | 空闲时占用 |
| 文件描述符 | <100 | 单组件最大打开数 |
| 线程数 | <10 | 单组件最大线程数 |

---

## 五、接口规范

### 5.1 命名规范

```python
# 模块命名: snake_case
# 例: fast_bridge, layer_cache

# 类命名: PascalCase
# 例: FastBridge, LayerCache

# 函数命名: snake_case
# 例: get_bridge(), cache_get()

# 常量命名: UPPER_SNAKE_CASE
# 例: MAX_CACHE_SIZE, DEFAULT_TTL
```

### 5.2 返回格式

```python
# 成功返回
{
    "success": True,
    "data": {...},
    "latency_ms": 0.005
}

# 失败返回
{
    "success": False,
    "error": {
        "code": "ERR_001",
        "message": "描述",
        "details": {...}
    }
}
```

### 5.3 错误码规范

| 范围 | 类型 |
|------|------|
| 1xxx | 参数错误 |
| 2xxx | 状态错误 |
| 3xxx | 资源错误 |
| 4xxx | 超时错误 |
| 5xxx | 系统错误 |

---

## 六、注册流程

### 6.1 注册表结构

```json
{
  "name": "fast_bridge",
  "version": "2.7.0",
  "layer": 1,
  "type": "core",
  "entry": "core/layer_bridge/fast_bridge.py",
  "config": "core/layer_bridge/LAYER_BRIDGE_CONFIG.json",
  "performance": {
    "avg_latency_ms": 0.005,
    "qps": 217523
  },
  "dependencies": [],
  "status": "active"
}
```

### 6.2 注册步骤

1. **创建组件** - 实现必须接口
2. **编写文档** - README + 配置
3. **性能测试** - 运行 benchmark
4. **提交注册** - 更新注册表
5. **集成测试** - 验证层间调用
6. **上线发布** - 更新版本号

---

## 七、监控要求

### 7.1 必须暴露指标

| 指标 | 类型 | 说明 |
|------|------|------|
| `calls_total` | Counter | 总调用次数 |
| `calls_success` | Counter | 成功次数 |
| `calls_failed` | Counter | 失败次数 |
| `latency_ms` | Histogram | 延迟分布 |
| `memory_mb` | Gauge | 内存占用 |
| `cpu_percent` | Gauge | CPU占用 |

### 7.2 健康检查

```python
def health_check(self) -> dict:
    return {
        "healthy": True,
        "checks": {
            "memory": {"status": "ok", "value": 50},
            "latency": {"status": "ok", "value": 0.005},
            "errors": {"status": "ok", "value": 0}
        }
    }
```

---

## 八、测试要求

### 8.1 单元测试

- 覆盖率 > 80%
- 所有公共接口有测试
- 边界条件有测试

### 8.2 性能测试

- 基准测试 (benchmark)
- 压力测试 (stress)
- 稳定性测试 (stability)

### 8.3 集成测试

- 层间调用测试
- 依赖组件测试
- 故障恢复测试

---

## 九、文档要求

### 9.1 README 必须包含

1. 组件概述
2. 快速开始
3. API 文档
4. 配置说明
5. 性能指标
6. 示例代码
7. 故障排查

### 9.2 代码注释

```python
def fast_call(from_layer: Layer, to_layer: Layer, action: str, data: Any = None) -> Any:
    """
    快速层间调用
    
    Args:
        from_layer: 源层级
        to_layer: 目标层级
        action: 动作名称
        data: 传递数据
    
    Returns:
        调用结果
    
    Raises:
        ValueError: 参数错误
        TimeoutError: 调用超时
    
    Example:
        >>> result = fast_call(Layer.L1_CORE, Layer.L2_MEMORY, "recall", "query")
    """
```

---

## 十、版本管理

### 10.1 版本号规则

```
主版本.次版本.修订号
例: 2.7.0

- 主版本: 架构变更
- 次版本: 功能新增
- 修订号: Bug修复
```

### 10.2 变更日志

```markdown
## [2.7.0] - 2026-04-10

### Added
- 新增统一性能模块
- 新增智能路由器

### Changed
- 优化缓存性能

### Fixed
- 修复内存泄漏
```

---

**版本**: V2.7.0
**作者**: @18816132863
