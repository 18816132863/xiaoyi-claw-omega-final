# 渐进式启用架构

**版本**: 1.0.0
**来源**: llm-memory-integration (改进版)
**集成时间**: 2026-04-07 00:12 UTC

---

## 🎯 架构概述

渐进式启用是一种分阶段激活功能的策略，确保系统稳定性和可控性。

### 核心思想
```
功能按优先级分阶段启用
每个阶段独立测试验证
问题可快速定位和回滚
系统逐步达到完整能力
```

---

## 📊 阶段划分

### P0 - 核心阶段
| 模块 | 说明 | 状态 |
|------|------|------|
| router | 智能路由 | ✅ 必须启用 |
| weights | 动态权重 | ✅ 必须启用 |
| rrf | 结果融合 | ✅ 必须启用 |
| dedup | 结果去重 | ✅ 必须启用 |

### P1 - 增强阶段
| 模块 | 说明 | 状态 |
|------|------|------|
| understand | 查询理解 | 🟡 可选启用 |
| rewriter | 查询改写 | 🟡 可选启用 |

### P2 - 优化阶段
| 模块 | 说明 | 状态 |
|------|------|------|
| feedback | 反馈学习 | 🟡 可选启用 |
| history | 历史缓存 | 🟡 可选启用 |

### P3 - 扩展阶段
| 模块 | 说明 | 状态 |
|------|------|------|
| explainer | 结果解释 | 🟢 可选启用 |
| summarizer | 结果摘要 | 🟢 可选启用 |

---

## 🏗️ 架构设计

### 配置结构
```json
{
  "progressive": {
    "version": "1.0.0",
    "stages": {
      "P0": {
        "name": "核心阶段",
        "modules": ["router", "weights", "rrf", "dedup"],
        "enabled": true,
        "required": true
      },
      "P1": {
        "name": "增强阶段",
        "modules": ["understand", "rewriter"],
        "enabled": true,
        "required": false
      },
      "P2": {
        "name": "优化阶段",
        "modules": ["feedback", "history"],
        "enabled": false,
        "required": false
      },
      "P3": {
        "name": "扩展阶段",
        "modules": ["explainer", "summarizer"],
        "enabled": false,
        "required": false
      }
    }
  }
}
```

### 状态管理
```python
class ProgressiveManager:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.stage_status = {}

    def is_enabled(self, module: str) -> bool:
        """检查模块是否启用"""
        for stage_name, stage in self.config["stages"].items():
            if module in stage["modules"]:
                return stage["enabled"]
        return False

    def enable_stage(self, stage_name: str) -> bool:
        """启用阶段"""
        if stage_name not in self.config["stages"]:
            return False

        # 检查前置阶段
        prerequisites = self.get_prerequisites(stage_name)
        for prereq in prerequisites:
            if not self.config["stages"][prereq]["enabled"]:
                raise Exception(f"前置阶段 {prereq} 未启用")

        self.config["stages"][stage_name]["enabled"] = True
        self.save_config()
        return True

    def disable_stage(self, stage_name: str) -> bool:
        """禁用阶段"""
        if stage_name not in self.config["stages"]:
            return False

        # 核心阶段不可禁用
        if self.config["stages"][stage_name]["required"]:
            raise Exception(f"核心阶段 {stage_name} 不可禁用")

        self.config["stages"][stage_name]["enabled"] = False
        self.save_config()
        return True
```

---

## 🔄 启用流程

### 标准流程
```
1. 检查前置阶段状态
2. 验证模块依赖
3. 启用阶段
4. 运行验证测试
5. 监控运行状态
6. 确认或回滚
```

### 依赖关系
```
P0 (核心) ← 必须先启用
    ↓
P1 (增强) ← 依赖 P0
    ↓
P2 (优化) ← 依赖 P1
    ↓
P3 (扩展) ← 依赖 P2
```

---

## 📋 管理命令

### 查看状态
```bash
progressive status

# 输出:
# P0: ✅ 已启用 (核心阶段)
# P1: ✅ 已启用 (增强阶段)
# P2: ⬜ 未启用 (优化阶段)
# P3: ⬜ 未启用 (扩展阶段)
```

### 启用阶段
```bash
progressive enable P1

# 输出:
# 检查前置阶段 P0... ✅
# 启用 P1 阶段... ✅
# 验证模块... ✅
# P1 阶段已启用
```

### 禁用阶段
```bash
progressive disable P3

# 输出:
# P3 阶段已禁用
```

---

## ⚠️ 安全规则

### 强制规则
| 规则 | 说明 |
|------|------|
| 核心不可禁用 | P0 阶段标记为 required |
| 顺序启用 | 必须按 P0→P1→P2→P3 顺序 |
| 验证后启用 | 启用前必须通过验证 |
| 回滚保护 | 禁用时自动保存状态 |

### 异常处理
```python
def safe_enable(manager: ProgressiveManager, stage: str):
    """安全启用阶段"""
    try:
        # 备份当前状态
        backup = manager.backup()

        # 启用阶段
        manager.enable_stage(stage)

        # 验证
        if not manager.validate(stage):
            # 回滚
            manager.restore(backup)
            return False

        return True
    except Exception as e:
        manager.restore(backup)
        raise e
```

---

## 📊 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| 阶段可用性 | 阶段模块正常运行 | >99% |
| 启用成功率 | 启用操作成功比例 | >95% |
| 回滚次数 | 需要回滚的次数 | <5% |
| 依赖检查 | 依赖验证通过率 | 100% |

---

## 🔗 集成点

### 功能模块
```
每个功能模块检查:
if progressive_manager.is_enabled("module_name"):
    # 执行模块功能
else:
    # 跳过或降级
```

### 配置加载
```
系统启动时:
1. 加载渐进式配置
2. 检查各阶段状态
3. 初始化已启用模块
4. 跳过未启用模块
```

---

## 💡 最佳实践

1. **从核心开始** - 先启用 P0，确保基础功能正常
2. **逐步验证** - 每启用一个阶段，验证后再继续
3. **监控指标** - 关注性能和错误率变化
4. **保留回滚** - 随时可以禁用非核心阶段
5. **文档记录** - 记录每次启用/禁用的原因和效果

---

*渐进式启用架构 - 稳步前进，可控演进*
