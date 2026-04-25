# 新增技能标准模板

## 一、标准目录结构

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

---

## 二、标准注册方式

### 2.1 注册到技能注册表

**文件位置**：`infrastructure/inventory/skill_registry.json`

**注册模板**：
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
  "status": "{draft/gray/prod/offline}",
  "call_scope": "{internal/external}",
  "created_at": "{创建时间}",
  "updated_at": "{更新时间}"
}
```

### 2.2 注册流程

1. **填写注册表** → 在 `skill_registry.json` 中添加新技能
2. **验证字段** → 运行自动检查脚本
3. **创建目录** → 按标准目录结构创建
4. **编写代码** → 按标准接口编写
5. **编写测试** → 按标准测试编写
6. **提交审核** → 运行完整检查

---

## 三、标准输入输出接口

### 3.1 标准输入接口

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
    """标准输入结构"""
    request_id: str              # 请求唯一标识
    skill_id: str                # 技能ID
    params: Dict[str, Any]       # 业务参数
    context: Optional[Dict]      # 上下文信息
    timeout_ms: Optional[int]    # 超时时间
    fallback: Optional[bool]     # 是否允许降级

@dataclass
class SkillOutput:
    """标准输出结构"""
    request_id: str              # 请求唯一标识
    skill_id: str                # 技能ID
    status: SkillStatus          # 执行状态
    data: Optional[Dict]         # 返回数据
    error: Optional[str]         # 错误信息
    latency_ms: int              # 耗时（毫秒）
    cached: bool                 # 是否来自缓存
    timestamp: str               # 时间戳
```

### 3.2 标准接口方法

```python
# interface.py
class SkillInterface:
    """技能标准接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化技能"""
        self.config = config
        self.skill_id = config.get('skill_id')
        self.timeout_ms = config.get('timeout_ms', 30000)
    
    def execute(self, input: SkillInput) -> SkillOutput:
        """执行技能（必需实现）"""
        raise NotImplementedError
    
    def validate_input(self, input: SkillInput) -> bool:
        """验证输入（必需实现）"""
        raise NotImplementedError
    
    def fallback(self, input: SkillInput, error: Exception) -> SkillOutput:
        """降级处理（必需实现）"""
        raise NotImplementedError
    
    def health_check(self) -> bool:
        """健康检查（可选实现）"""
        return True
```

---

## 四、标准元数据字段

### 4.1 必填字段

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| skill_id | string | 唯一标识 | skill_ocr_v1 |
| skill_name | string | 中文名称 | OCR识别 |
| version | string | 版本号 | 1.0.0 |
| entry_layer | string | 所属层级 | L4 |
| input_schema | string | 输入定义 | file_url, lang |
| output_schema | string | 输出定义 | text, confidence |
| dependencies | string | 依赖项 | storage, model_api |
| owner | string | 负责人 | 系统管理员 |
| timeout_ms | number | 超时时间 | 15000 |
| fallback_strategy | string | 回退策略 | retry->degrade |
| status | string | 状态 | draft/gray/prod/offline |

### 4.2 可选字段

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| call_scope | string | 调用范围 | internal/external |
| description | string | 详细描述 | OCR文字识别服务 |
| tags | array | 标签 | ["vision", "ocr"] |
| created_at | string | 创建时间 | 2026-04-10T00:00:00Z |
| updated_at | string | 更新时间 | 2026-04-10T00:00:00Z |

---

## 五、标准配置字段

### 5.1 config.json 模板

```json
{
  "skill_id": "skill_{name}_v{version}",
  "version": "{version}",
  "entry_layer": "{L1-L6}",
  "timeout_ms": {超时毫秒},
  "retry": {
    "max_attempts": 3,
    "backoff_ms": 1000
  },
  "cache": {
    "enabled": true,
    "ttl_seconds": 3600
  },
  "logging": {
    "level": "INFO",
    "format": "json"
  },
  "monitoring": {
    "enabled": true,
    "metrics": ["latency", "success_rate", "error_count"]
  },
  "fallback": {
    "strategy": "retry->degrade->abort",
    "degrade_output": {}
  }
}
```

---

## 六、标准日志格式

### 6.1 日志结构

```json
{
  "timestamp": "2026-04-10T00:00:00.000Z",
  "level": "INFO",
  "skill_id": "skill_ocr_v1",
  "request_id": "req_123456",
  "message": "Skill execution started",
  "context": {
    "input_params": {"file_url": "https://example.com/image.jpg"},
    "layer": "L4",
    "version": "1.0.0"
  },
  "latency_ms": 1234,
  "status": "success"
}
```

### 6.2 日志级别

| 级别 | 说明 | 使用场景 |
|-----|------|---------|
| DEBUG | 调试信息 | 开发调试 |
| INFO | 正常信息 | 正常执行 |
| WARN | 警告信息 | 降级、重试 |
| ERROR | 错误信息 | 执行失败 |
| FATAL | 致命错误 | 系统崩溃 |

---

## 七、标准错误处理

### 7.1 错误码定义

| 错误码 | 说明 | 处理方式 |
|-------|------|---------|
| E001 | 输入参数错误 | 返回错误信息 |
| E002 | 依赖服务不可用 | 重试或降级 |
| E003 | 执行超时 | 重试或降级 |
| E004 | 资源不足 | 排队或拒绝 |
| E005 | 权限不足 | 返回错误信息 |
| E006 | 配置错误 | 返回错误信息 |
| E007 | 内部错误 | 记录日志并降级 |
| E008 | 缓存错误 | 忽略缓存继续执行 |

### 7.2 错误处理模板

```python
# main.py
from enum import Enum
from typing import Optional

class ErrorCode(Enum):
    INPUT_ERROR = "E001"
    DEPENDENCY_ERROR = "E002"
    TIMEOUT_ERROR = "E003"
    RESOURCE_ERROR = "E004"
    PERMISSION_ERROR = "E005"
    CONFIG_ERROR = "E006"
    INTERNAL_ERROR = "E007"
    CACHE_ERROR = "E008"

class SkillError(Exception):
    """技能错误基类"""
    def __init__(self, code: ErrorCode, message: str, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

def handle_error(error: Exception, input: SkillInput) -> SkillOutput:
    """统一错误处理"""
    if isinstance(error, SkillError):
        return SkillOutput(
            request_id=input.request_id,
            skill_id=input.skill_id,
            status=SkillStatus.FAILURE,
            data=None,
            error=f"[{error.code.value}] {error.message}",
            latency_ms=0,
            cached=False,
            timestamp=datetime.now().isoformat()
        )
    else:
        return SkillOutput(
            request_id=input.request_id,
            skill_id=input.skill_id,
            status=SkillStatus.FAILURE,
            data=None,
            error=f"[E007] Internal error: {str(error)}",
            latency_ms=0,
            cached=False,
            timestamp=datetime.now().isoformat()
        )
```

---

## 八、标准超时与回退

### 8.1 超时策略

```python
# main.py
import signal
from contextlib import contextmanager

class TimeoutError(Exception):
    pass

@contextmanager
def timeout_handler(seconds: int):
    """超时处理器"""
    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def execute_with_timeout(input: SkillInput, skill: SkillInterface) -> SkillOutput:
    """带超时的执行"""
    timeout_seconds = input.timeout_ms or skill.timeout_ms // 1000
    try:
        with timeout_handler(timeout_seconds):
            return skill.execute(input)
    except TimeoutError:
        return skill.fallback(input, TimeoutError())
```

### 8.2 回退策略

| 策略 | 说明 | 适用场景 |
|-----|------|---------|
| retry | 重试 | 临时故障 |
| degrade | 降级 | 服务不可用 |
| cache | 使用缓存 | 数据获取失败 |
| abort | 中止 | 严重错误 |
| retry->degrade | 重试后降级 | 一般故障 |
| retry->cache->degrade | 重试后缓存后降级 | 数据服务 |

---

## 九、标准测试文件

### 9.1 单元测试模板

```python
# test/test_main.py
import pytest
from main import SkillInterface, SkillInput, SkillOutput

class TestSkill:
    """技能单元测试"""
    
    @pytest.fixture
    def skill(self):
        """初始化技能"""
        config = {
            "skill_id": "skill_test_v1",
            "timeout_ms": 5000
        }
        return SkillInterface(config)
    
    def test_execute_success(self, skill):
        """测试成功执行"""
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
        assert output.data is not None
    
    def test_execute_timeout(self, skill):
        """测试超时处理"""
        input = SkillInput(
            request_id="test_002",
            skill_id="skill_test_v1",
            params={"delay": 10},
            context=None,
            timeout_ms=100,
            fallback=True
        )
        output = skill.execute(input)
        assert output.status in [SkillStatus.TIMEOUT, SkillStatus.DEGRADED]
    
    def test_fallback(self, skill):
        """测试降级处理"""
        input = SkillInput(
            request_id="test_003",
            skill_id="skill_test_v1",
            params={"error": True},
            context=None,
            timeout_ms=5000,
            fallback=True
        )
        error = Exception("Test error")
        output = skill.fallback(input, error)
        assert output.status == SkillStatus.DEGRADED
```

### 9.2 集成测试模板

```python
# test/test_integration.py
import pytest
from main import SkillInterface, SkillInput

class TestIntegration:
    """集成测试"""
    
    def test_end_to_end(self):
        """端到端测试"""
        # 1. 初始化
        skill = SkillInterface({"skill_id": "skill_test_v1"})
        
        # 2. 执行
        input = SkillInput(
            request_id="integration_001",
            skill_id="skill_test_v1",
            params={"key": "value"},
            context=None,
            timeout_ms=5000,
            fallback=True
        )
        output = skill.execute(input)
        
        # 3. 验证
        assert output.status == SkillStatus.SUCCESS
        assert output.latency_ms > 0
        assert output.timestamp is not None
```

---

## 十、标准说明文档

### 10.1 SKILL.md 模板

```markdown
# {技能名称}

## 基本信息

| 项目 | 内容 |
|-----|------|
| skill_id | skill_{name}_v{version} |
| 所属层级 | {L1-L6} |
| 版本 | {version} |
| 负责人 | {负责人} |
| 状态 | {status} |

## 功能说明

{详细功能描述}

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| param1 | string | 是 | 参数说明 |
| param2 | number | 否 | 参数说明 |

## 输出结构

| 字段名 | 类型 | 说明 |
|-------|------|------|
| field1 | string | 字段说明 |
| field2 | number | 字段说明 |

## 使用示例

```python
from {skill_name} import SkillInterface

skill = SkillInterface(config)
output = skill.execute(input)
```

## 错误处理

| 错误码 | 说明 | 处理方式 |
|-------|------|---------|
| E001 | 输入参数错误 | 检查参数 |
| E002 | 依赖服务不可用 | 重试或降级 |

## 依赖关系

- 依赖服务：{依赖列表}
- 被依赖：{被依赖列表}

## 变更历史

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| 1.0.0 | 2026-04-10 | 初始版本 |
```

---

## 版本
- V1.0.0
- 创建日期：2026-04-10
