# 平台增强型技能架构

## 架构理念

**核心理念**：技能自洽 + 平台增强 + 优雅降级

```
┌────────────────────────────────────────────┐
│              技能内核 (自洽)                 │
│  ┌──────────────────────────────────────┐  │
│  │  SQLite + 单进程 + Request-driven    │  │
│  │  完整功能，零配置可用                  │  │
│  └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤
│           平台适配层 (增强)                  │
│  ┌──────────────────────────────────────┐  │
│  │  Xiaoyi / HarmonyOS / 其他平台        │  │
│  │  借用平台能力，增强体验                │  │
│  └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤
│           降级策略 (兜底)                    │
│  ┌──────────────────────────────────────┐  │
│  │  平台不可用 → 回退到技能内核           │  │
│  │  保证基本功能始终可用                  │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

## 平台适配器

### 适配器接口

```python
class PlatformAdapter(ABC):
    @abstractmethod
    async def probe(self) -> Dict[str, Any]:
        """探测平台能力"""
        pass
    
    @abstractmethod
    async def invoke(self, capability: str, params: Dict) -> Dict:
        """调用平台能力"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """检查平台是否可用"""
        pass
```

### 内置适配器

| 适配器 | 用途 |
|--------|------|
| NullAdapter | 默认适配器，所有能力不可用 |
| XiaoyiAdapter | 小艺平台适配器 |
| HarmonyOSAdapter | 鸿蒙平台适配器 |

### 适配器选择

```python
from platform_adapter.runtime_probe import RuntimeProbe

adapter_name = RuntimeProbe.get_recommended_adapter()
# 返回: "xiaoyi" / "harmonyos" / "null"
```

## 能力映射

| 技能能力 | 平台能力 | 降级方案 |
|----------|----------|----------|
| 发送消息 | 小艺消息 | 本地记录 |
| 调度任务 | 小艺调度 | 本地调度 |
| 通知 | 小艺通知 | 本地日志 |

## 扩展新平台

1. 继承 `PlatformAdapter`
2. 实现必要方法
3. 注册到 `RuntimeProbe`
4. 添加能力映射
