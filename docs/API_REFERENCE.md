# API_REFERENCE.md - API 参考文档

## 概述

本文档描述小艺 Claw OMEGA_FINAL 的核心 API 和接口规范。

## 核心 API

### 1. 系统状态 API

#### 获取系统状态
```yaml
endpoint: /api/status
method: GET
description: 获取系统当前状态

response:
  health_score: 100
  modules: 40
  skills: 168
  workflows: 8
  entities: 182
```

#### 获取健康度
```yaml
endpoint: /api/health
method: GET
description: 获取系统健康度详情

response:
  completeness: 100
  consistency: 100
  extensibility: 100
  maintainability: 100
  documentation: 100
  overall: 100
```

### 2. 记忆 API

#### 搜索记忆
```yaml
endpoint: /api/memory/search
method: POST
description: 语义搜索记忆

request:
  query: "string"      # 搜索查询
  max_results: 10      # 最大结果数
  min_score: 0.5       # 最小相关度

response:
  results:
    - path: "memory/file.md"
      lines: [1, 10]
      content: "..."
      score: 0.95
```

#### 获取记忆
```yaml
endpoint: /api/memory/get
method: GET
description: 获取指定记忆内容

request:
  path: "memory/file.md"
  from: 1
  lines: 50

response:
  content: "..."
```

#### 写入记忆
```yaml
endpoint: /api/memory/write
method: POST
description: 写入新记忆

request:
  type: "user_profile|system_config|knowledge|event|preference"
  content: "..."
  scope: "session|scenario|permanent"
  source: "user_explicit|user_inferred|system_inferred"

response:
  id: "mem_001"
  status: "created"
```

### 3. 技能 API

#### 列出技能
```yaml
endpoint: /api/skills
method: GET
description: 获取技能列表

request:
  category: "xiaoyi|core|search|document"  # 可选
  priority: "P0|P1|P2|P3"                   # 可选

response:
  skills:
    - name: "xiaoyi-web-search"
      category: "xiaoyi"
      priority: 100
      status: "active"
```

#### 执行技能
```yaml
endpoint: /api/skills/execute
method: POST
description: 执行指定技能

request:
  skill: "xiaoyi-web-search"
  input: "搜索内容"
  params: {}

response:
  result: "..."
  status: "success"
  duration_ms: 1500
```

### 4. 工作流 API

#### 列出工作流
```yaml
endpoint: /api/workflows
method: GET
description: 获取工作流列表

response:
  workflows:
    - id: "wf_doc_convert"
      name: "document-convert"
      status: "active"
      priority: 85
```

#### 执行工作流
```yaml
endpoint: /api/workflows/execute
method: POST
description: 执行指定工作流

request:
  workflow: "document-convert"
  input: "file_url"
  params: {}

response:
  workflow_id: "wf_001"
  status: "running"
  steps:
    - id: "step_1"
      status: "completed"
    - id: "step_2"
      status: "running"
```

### 5. 任务 API

#### 创建任务
```yaml
endpoint: /api/tasks
method: POST
description: 创建新任务

request:
  type: "qa|search|document_edit|planning|multi_step_agent"
  input: "任务内容"
  params: {}

response:
  task_id: "task_001"
  status: "created"
  estimated_steps: 5
```

#### 获取任务状态
```yaml
endpoint: /api/tasks/{task_id}
method: GET
description: 获取任务状态

response:
  task_id: "task_001"
  status: "running|completed|failed"
  progress: 0.6
  steps_completed: 3
  steps_total: 5
```

### 6. 审计 API

#### 查询审计日志
```yaml
endpoint: /api/audit/logs
method: GET
description: 查询审计日志

request:
  start_time: "2026-04-01T00:00:00Z"
  end_time: "2026-04-06T23:59:59Z"
  type: "operation|decision|security"
  limit: 100

response:
  logs:
    - id: "log_001"
      timestamp: "2026-04-06T10:32:00+08:00"
      type: "operation"
      action: "file_write"
      result: "success"
```

### 7. 监控 API

#### 获取指标
```yaml
endpoint: /api/metrics
method: GET
description: 获取系统指标

request:
  type: "response_time|error_rate|throughput"
  period: "1h|1d|1w"

response:
  metrics:
    - timestamp: "2026-04-06T10:00:00Z"
      name: "response_time"
      value: 2.5
      unit: "seconds"
```

#### 获取告警
```yaml
endpoint: /api/alerts
method: GET
description: 获取告警列表

request:
  status: "active|resolved"
  severity: "critical|warning|info"
  limit: 50

response:
  alerts:
    - id: "alert_001"
      timestamp: "2026-04-06T10:32:00+08:00"
      severity: "warning"
      message: "响应时间超过阈值"
      status: "active"
```

## 配置 API

### 获取配置
```yaml
endpoint: /api/config
method: GET
description: 获取系统配置

response:
  system:
    name: "小艺Claw"
    version: "OMEGA_FINAL"
  auto_upgrade:
    enable: true
    full_auto: true
```

### 更新配置
```yaml
endpoint: /api/config
method: PUT
description: 更新系统配置

request:
  key: "config.path"
  value: "new_value"

response:
  status: "updated"
  requires_restart: false
```

## 错误响应

### 错误格式
```json
{
  "error": {
    "code": "E001",
    "message": "系统错误",
    "details": "详细错误信息",
    "timestamp": "2026-04-06T10:32:00+08:00"
  }
}
```

### 错误代码
| 代码 | 说明 |
|------|------|
| E001 | 系统错误 |
| E101 | 工具不存在 |
| E102 | 参数无效 |
| E201 | 技能不存在 |
| E301 | 数据格式错误 |
| E401 | 网络连接失败 |
| E501 | 权限不足 |

## 速率限制

| API 类型 | 限制 |
|----------|------|
| 读取 API | 100/分钟 |
| 写入 API | 30/分钟 |
| 执行 API | 10/分钟 |

## 认证

所有 API 请求需要携带认证信息：

```yaml
headers:
  Authorization: "Bearer {token}"
  X-Request-ID: "{request_id}"
```

## 版本控制

API 版本通过 URL 前缀控制：

```yaml
current: /api/v1/*
deprecated: /api/v0/* (将在下个版本移除)
```

---

*本 API 参考由 OMEGA_FINAL 自动生成*
