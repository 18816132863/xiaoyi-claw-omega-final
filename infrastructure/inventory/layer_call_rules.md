# 层间调用约束规则

## 一、允许的调用链

### 1.1 标准调用链

```
L1 表达层
    ↓ 调用
L2 应用编排层
    ↓ 调用
L3 领域规则层
    ↓ 调用
L4 服务能力层
    ↓ 调用
L5 数据访问层
    ↓ 调用
L6 基础设施层
```

### 1.2 允许的调用关系

| 调用方 | 被调用方 | 说明 |
|-------|---------|------|
| L1 | L2, L3, L4, L5, L6 | 表达层可调用所有下层 |
| L2 | L3, L4, L5, L6 | 应用编排层可调用下层 |
| L3 | L4, L5, L6 | 领域规则层可调用下层 |
| L4 | L5, L6 | 服务能力层可调用下层 |
| L5 | L6 | 数据访问层可调用基础设施层 |
| L6 | 无 | 基础设施层不调用其他层 |

### 1.3 同层调用

| 层级 | 允许同层调用 | 说明 |
|-----|------------|------|
| L1 | ✅ 允许 | 表达层组件可互相调用 |
| L2 | ✅ 允许 | 应用编排层可互相调用 |
| L3 | ✅ 允许 | 领域规则层可互相调用 |
| L4 | ✅ 允许 | 服务能力层可互相调用 |
| L5 | ✅ 允许 | 数据访问层可互相调用 |
| L6 | ✅ 允许 | 基础设施层可互相调用 |

---

## 二、禁止的越层调用

### 2.1 禁止向上调用

| 调用方 | 禁止调用 | 原因 |
|-------|---------|------|
| L6 | L1-L5 | 基础设施层不能调用上层 |
| L5 | L1-L4 | 数据访问层不能调用上层 |
| L4 | L1-L3 | 服务能力层不能调用上层 |
| L3 | L1-L2 | 领域规则层不能调用上层 |
| L2 | L1 | 应用编排层不能调用表达层 |

### 2.2 禁止跨层调用

| 调用方 | 禁止调用 | 原因 |
|-------|---------|------|
| L1 | L3（跳过L2） | 必须通过应用编排层 |
| L1 | L5（跳过L2-L4） | 必须逐层调用 |
| L2 | L5（跳过L3-L4） | 必须逐层调用 |
| L3 | L6（跳过L4-L5） | 必须逐层调用 |

### 2.3 禁止循环调用

| 禁止模式 | 说明 |
|---------|------|
| A → B → A | 直接循环 |
| A → B → C → A | 间接循环 |
| A → B → C → D → A | 长链循环 |

---

## 三、必须通过统一服务访问的公共能力

### 3.1 数据访问（必须通过L5）

| 能力 | 统一服务 | 禁止直连 |
|-----|---------|---------|
| 文件读写 | memory_context/data/ | 禁止直接 open() |
| 缓存访问 | memory_context/memory-management/ | 禁止直接 redis |
| 数据库访问 | memory_context/data/ | 禁止直接 sqlite/mysql |
| 向量检索 | memory_context/data/ | 禁止直接 faiss/milvus |

### 3.2 日志监控（必须通过L6）

| 能力 | 统一服务 | 禁止直连 |
|-----|---------|---------|
| 日志记录 | infrastructure/monitoring/ | 禁止直接 logging |
| 指标上报 | infrastructure/monitoring/ | 禁止直接 prometheus |
| 链路追踪 | infrastructure/monitoring/ | 禁止直接 jaeger |
| 告警通知 | infrastructure/monitoring/ | 禁止直接 alert |

### 3.3 配置管理（必须通过L6）

| 能力 | 统一服务 | 禁止直连 |
|-----|---------|---------|
| 配置读取 | infrastructure/inventory/ | 禁止直接读取配置文件 |
| 配置更新 | infrastructure/inventory/ | 禁止直接写入配置文件 |
| 配置监听 | infrastructure/inventory/ | 禁止直接监听配置变化 |

### 3.4 错误处理（必须通过L6）

| 能力 | 统一服务 | 禁止直连 |
|-----|---------|---------|
| 错误上报 | governance/error-handling/ | 禁止直接 print |
| 错误恢复 | governance/failover/ | 禁止直接 retry |
| 错误审计 | governance/audit/ | 禁止直接记录 |

---

## 四、不允许私下耦合的内部模块

### 4.1 禁止私下耦合的场景

| 场景 | 禁止做法 | 正确做法 |
|-----|---------|---------|
| 技能间通信 | 直接调用其他技能内部方法 | 通过统一接口调用 |
| 数据共享 | 直接访问其他技能的数据 | 通过L5数据访问层 |
| 配置共享 | 直接读取其他技能的配置 | 通过L6配置管理 |
| 状态共享 | 直接修改其他技能的状态 | 通过统一状态管理 |

### 4.2 禁止的耦合模式

```python
# ❌ 禁止：直接调用其他技能内部方法
from execution.phone_engine.internal import helper
helper.do_something()

# ✅ 正确：通过统一接口调用
from execution.phone_engine import SkillInterface
skill = SkillInterface(config)
output = skill.execute(input)
```

```python
# ❌ 禁止：直接访问其他技能的数据
with open('execution/phone_engine/data/cache.json') as f:
    data = json.load(f)

# ✅ 正确：通过L5数据访问层
from memory_context.memory_management import DataAccessor
accessor = DataAccessor()
data = accessor.get('phone_engine', 'cache')
```

```python
# ❌ 禁止：直接读取其他技能的配置
with open('execution/phone_engine/config.json') as f:
    config = json.load(f)

# ✅ 正确：通过L6配置管理
from infrastructure.inventory import ConfigManager
config = ConfigManager.get_config('phone_engine')
```

---

## 五、调用链检查规则

### 5.1 静态检查

| 检查项 | 检查方式 | 错误级别 |
|-------|---------|---------|
| 导入语句 | 检查 import 语句 | ERROR |
| 函数调用 | 检查函数调用链 | ERROR |
| 文件访问 | 检查文件路径 | WARN |
| 配置访问 | 检查配置路径 | WARN |

### 5.2 运行时检查

| 检查项 | 检查方式 | 错误级别 |
|-------|---------|---------|
| 调用栈 | 检查调用栈深度 | WARN |
| 循环调用 | 检查调用链是否有环 | ERROR |
| 越层调用 | 检查层级跳跃 | ERROR |
| 直连访问 | 检查网络/数据库连接 | ERROR |

---

## 六、调用链检查脚本

```python
#!/usr/bin/env python3
"""
层间调用链检查脚本
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set

class CallChainChecker:
    """调用链检查器"""
    
    LAYER_MAPPING = {
        'core/': 'L1',
        'orchestration/': 'L2',
        'governance/policy/': 'L3',
        'execution/': 'L4',
        'memory_context/': 'L5',
        'infrastructure/': 'L6',
        'governance/': 'L6'
    }
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.errors = []
    
    def get_layer(self, file_path: str) -> str:
        """获取文件所属层级"""
        for path_prefix, layer in self.LAYER_MAPPING.items():
            if path_prefix in file_path:
                return layer
        return 'UNKNOWN'
    
    def check_import(self, file_path: str, import_path: str) -> bool:
        """检查导入是否合规"""
        caller_layer = self.get_layer(file_path)
        callee_layer = self.get_layer(import_path)
        
        if caller_layer == 'UNKNOWN' or callee_layer == 'UNKNOWN':
            return True
        
        # 检查是否向上调用
        if callee_layer < caller_layer:
            self.errors.append(f"[越层调用] {file_path}: {caller_layer} -> {callee_layer} ({import_path})")
            return False
        
        return True
    
    def check_file(self, file_path: Path):
        """检查单个文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.check_import(str(file_path), alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.check_import(str(file_path), node.module)
    
    def check_all(self):
        """检查所有文件"""
        for py_file in self.workspace.glob('**/*.py'):
            # 跳过 _archive 和 .git
            if '_archive' in str(py_file) or '.git' in str(py_file):
                continue
            self.check_file(py_file)
        
        return len(self.errors) == 0

if __name__ == '__main__':
    checker = CallChainChecker('/home/sandbox/.openclaw/workspace')
    passed = checker.check_all()
    
    if passed:
        print("✅ 调用链检查通过")
    else:
        print("❌ 调用链检查失败")
        for error in checker.errors:
            print(f"  - {error}")
```

---

## 版本
- V1.0.0
- 创建日期：2026-04-10
