# 新增技能接入流程（唯一入口）

## 一、接入流程总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     新增技能接入流程                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 能力归类 → 判断归属层（L1-L6）                                       │
│       ↓                                                                 │
│  2. 创建目录 → 按标准目录结构创建                                        │
│       ↓                                                                 │
│  3. 填写注册表 → 在 skill_registry.json 中注册                          │
│       ↓                                                                 │
│  4. 编写代码 → 按标准接口编写                                            │
│       ↓                                                                 │
│  5. 编写测试 → 按标准测试编写                                            │
│       ↓                                                                 │
│  6. 运行检查 → 运行 skill_access_checker.py                             │
│       ↓                                                                 │
│  7. 灰度接入 → 测试链路验证                                              │
│       ↓                                                                 │
│  8. 正式放量 → 验收后并入主流程                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、详细步骤

### 步骤1：能力归类

**目标**：判断新技能属于哪一层

**判断规则**：

| 新增内容类型 | 首选层 | 说明 |
|------------|-------|------|
| 纯业务判断/新规则 | L3 领域规则层 | 例如新增判定标准、过滤逻辑、策略切换 |
| 可复用工具/新技能接口 | L4 服务能力层 | 例如OCR、检索、总结、翻译、外部系统调用 |
| 流程串联/自动执行链路 | L2 应用编排层 | 例如多技能顺序执行、回退、重试、审批 |
| 新数据源/新库存取 | L5 数据访问层 | 例如新增表、缓存、文件、向量库 |
| 日志监控/权限鉴权/配置 | L6 基础设施层 | 只做底座能力，不承载业务含义 |
| 新页面/新交互入口 | L1 表达层 | 只负责展示与交互，不写业务决策 |

**输出**：确定 `entry_layer` 和 `layer_path`

---

### 步骤2：创建目录

**目标**：按标准目录结构创建技能目录

**标准目录结构**：

```
{layer_path}/{skill_name}/
├── SKILL.md                    # 技能说明文档（必需）
├── config.json                 # 技能配置（必需）
├── main.py                     # 主入口文件（必需）
├── interface.py                # 标准接口定义（必需）
├── test/
│   ├── test_main.py            # 单元测试（必需）
│   └── test_integration.py     # 集成测试（可选）
├── docs/
│   ├── API.md                  # API文档（可选）
│   └── EXAMPLES.md             # 使用示例（可选）
└── README.md                   # 快速入门（必需）
```

**命令**：

```bash
# 创建目录
mkdir -p {layer_path}/{skill_name}/test
mkdir -p {layer_path}/{skill_name}/docs

# 创建必需文件
touch {layer_path}/{skill_name}/SKILL.md
touch {layer_path}/{skill_name}/config.json
touch {layer_path}/{skill_name}/main.py
touch {layer_path}/{skill_name}/interface.py
touch {layer_path}/{skill_name}/test/test_main.py
touch {layer_path}/{skill_name}/README.md
```

---

### 步骤3：填写注册表

**目标**：在 `skill_registry.json` 中注册新技能

**注册位置**：`infrastructure/inventory/skill_registry.json`

**必填字段**：

```json
{
  "skill_id": "skill_{name}_v{version}",
  "skill_name": "{中文名称}",
  "version": "{version}",
  "entry_layer": "{L1-L6}",
  "layer_name": "{层名}",
  "layer_path": "{路径}",
  "input_schema": "{输入参数定义}",
  "output_schema": "{返回结构定义}",
  "dependencies": "{依赖的服务或库}",
  "owner": "{负责人}",
  "timeout_ms": {超时毫秒},
  "fallback_strategy": "{回退策略}",
  "status": "draft",
  "call_scope": "{internal/external}",
  "created_at": "{创建时间}",
  "updated_at": "{更新时间}"
}
```

**示例**：

```json
{
  "skill_id": "skill_ocr_v1",
  "skill_name": "OCR识别",
  "version": "1.0.0",
  "entry_layer": "L4",
  "layer_name": "服务能力层",
  "layer_path": "execution/ocr/",
  "input_schema": "file_url, lang",
  "output_schema": "text, confidence",
  "dependencies": "storage, model_api",
  "owner": "系统管理员",
  "timeout_ms": 15000,
  "fallback_strategy": "retry->degrade",
  "status": "draft",
  "call_scope": "internal",
  "created_at": "2026-04-10T00:00:00Z",
  "updated_at": "2026-04-10T00:00:00Z"
}
```

---

### 步骤4：编写代码

**目标**：按标准接口编写技能代码

**标准接口**：

```python
# interface.py
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SkillStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    DEGRADED = "degraded"

@dataclass
class SkillInput:
    request_id: str
    skill_id: str
    params: Dict[str, Any]
    context: Optional[Dict]
    timeout_ms: Optional[int]
    fallback: Optional[bool]

@dataclass
class SkillOutput:
    request_id: str
    skill_id: str
    status: SkillStatus
    data: Optional[Dict]
    error: Optional[str]
    latency_ms: int
    cached: bool
    timestamp: str

class SkillInterface:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.skill_id = config.get('skill_id')
        self.timeout_ms = config.get('timeout_ms', 30000)
    
    def execute(self, input: SkillInput) -> SkillOutput:
        raise NotImplementedError
    
    def validate_input(self, input: SkillInput) -> bool:
        raise NotImplementedError
    
    def fallback(self, input: SkillInput, error: Exception) -> SkillOutput:
        raise NotImplementedError
```

---

### 步骤5：编写测试

**目标**：按标准测试编写技能测试

**标准测试**：

```python
# test/test_main.py
import pytest
from main import SkillInterface, SkillInput, SkillOutput

class TestSkill:
    @pytest.fixture
    def skill(self):
        config = {"skill_id": "skill_test_v1", "timeout_ms": 5000}
        return SkillInterface(config)
    
    def test_execute_success(self, skill):
        input = SkillInput(
            request_id="test_001",
            skill_id="skill_test_v1",
            params={"key": "value"},
            context=None,
            timeout_ms=5000,
            fallback=True
        )
        output = skill.execute(input)
        assert output.status == SkillStatus.SUCCESS
```

---

### 步骤6：运行检查

**目标**：运行自动检查脚本验证技能合规

**检查脚本**：`infrastructure/inventory/skill_access_checker.py`

**检查项**：

| 检查项 | 说明 |
|-------|------|
| 层级归属 | 是否进入正确层级 |
| 统一注册 | 是否完成统一注册 |
| 字段完整 | 是否字段完整 |
| 配置唯一 | 是否配置唯一 |
| 接口合规 | 是否接口合规 |
| 测试覆盖 | 是否具备测试 |
| 日志错误处理 | 是否具备日志和错误处理 |
| 无绕过调用 | 是否存在绕过主架构的直连调用 |

**命令**：

```bash
python3 infrastructure/inventory/skill_access_checker.py
```

**输出**：

```
============================================================
技能接入检查报告
============================================================

总计: 10 个技能
通过: 10 个
失败: 0 个
警告: 2 个

------------------------------------------------------------

✅ 通过 OCR识别 (skill_ocr_v1)
  警告:
    - [测试警告] skill_ocr_v1: 缺少集成测试

============================================================

✅ 所有技能检查通过！
============================================================
```

---

### 步骤7：灰度接入

**目标**：在测试链路或灰度流量里接入

**灰度流程**：

1. **配置灰度** → 在 config.json 中设置 `status: "gray"`
2. **测试链路** → 在测试环境验证
3. **监控指标** → 观察耗时、成功率、错误率
4. **问题修复** → 修复发现的问题
5. **灰度放量** → 逐步放量到生产环境

---

### 步骤8：正式放量

**目标**：验收后并入主流程

**放量条件**：

| 条件 | 要求 |
|-----|------|
| 检查通过 | 所有检查项通过 |
| 测试通过 | 单元测试和集成测试通过 |
| 灰度验证 | 灰度环境验证通过 |
| 监控正常 | 无异常错误和性能问题 |
| 文档完整 | SKILL.md 和 README.md 完整 |

**放量操作**：

1. **更新状态** → 在 skill_registry.json 中设置 `status: "prod"`
2. **更新文档** → 更新 SKILL.md 和 README.md
3. **通知相关方** → 通知使用方和运维方
4. **监控观察** → 持续观察监控指标

---

## 三、唯一接入位置

| 项目 | 路径 |
|-----|------|
| **注册表** | `infrastructure/inventory/skill_registry.json` |
| **检查脚本** | `infrastructure/inventory/skill_access_checker.py` |
| **模板文档** | `infrastructure/inventory/skill_template.md` |
| **调用规则** | `infrastructure/inventory/layer_call_rules.md` |
| **架构真源** | `core/ARCHITECTURE.md` |
| **接入规则** | `core/SKILL_ACCESS_RULES.md` |

---

## 四、禁止事项

| 禁止事项 | 说明 |
|---------|------|
| 禁止游离模块 | 所有技能必须注册到 skill_registry.json |
| 禁止重复注册 | 每个 skill_id 只能注册一次 |
| 禁止越层调用 | 必须按层级逐层调用 |
| 禁止直连访问 | 必须通过统一服务访问公共能力 |
| 禁止私下耦合 | 禁止技能间私下耦合 |
| 禁止绕过检查 | 必须通过 skill_access_checker.py 检查 |

---

## 版本
- V1.0.0
- 创建日期：2026-04-10
