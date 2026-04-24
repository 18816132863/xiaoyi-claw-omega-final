# TEMPLATE_SYSTEM.md - 智能模板系统

## 目的
定义智能模板系统，支持模板管理、匹配、渲染、进化。

## 适用范围
所有文档、配置、策略文件的模板创建和管理。

---

## 一、模板系统架构

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    智能模板系统                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  模板管理层   │    │  智能匹配层   │    │  渲染引擎层   │
│ MANAGER       │    │ MATCHER       │    │ RENDERER      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ 模板存储      │    │ 意图分析      │    │ 变量替换      │
│ 模板索引      │    │ 模板推荐      │    │ 条件渲染      │
│ 模板版本      │    │ 相似匹配      │    │ 循环渲染      │
│ 模板继承      │    │ 上下文匹配    │    │ 嵌套渲染      │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 1.2 模板类型
| 类型 | 后缀 | 说明 | 使用场景 |
|------|------|------|----------|
| Markdown 模板 | .md.tmpl | Markdown 文档模板 | 文档创建 |
| JSON 模板 | .json.tmpl | JSON 配置模板 | 配置创建 |
| YAML 模板 | .yaml.tmpl | YAML 配置模板 | 配置创建 |
| 混合模板 | .mix.tmpl | 多格式混合模板 | 复杂文档 |

---

## 二、模板库结构

### 2.1 目录结构
```
templates/
├── core/                           # 核心模板
│   ├── document.md.tmpl            # 通用文档模板
│   ├── config.json.tmpl            # 通用配置模板
│   ├── policy.md.tmpl              # 策略文档模板
│   └── readme.md.tmpl              # README 模板
│
├── security/                       # 安全模板
│   ├── threat_model.md.tmpl        # 威胁模型模板
│   ├── risk_policy.md.tmpl         # 风险策略模板
│   ├── audit_log.md.tmpl           # 审计日志模板
│   ├── boundary.json.tmpl          # 安全边界模板
│   └── incident_response.md.tmpl   # 事件响应模板
│
├── governance/                     # 治理模板
│   ├── memory_policy.md.tmpl       # 记忆策略模板
│   ├── compliance.md.tmpl          # 合规文档模板
│   ├── audit.md.tmpl               # 审计文档模板
│   └── data_governance.md.tmpl     # 数据治理模板
│
├── optimization/                   # 优化模板
│   ├── performance.md.tmpl         # 性能优化模板
│   ├── cache.md.tmpl               # 缓存策略模板
│   ├── batch.md.tmpl               # 批量处理模板
│   └── monitoring.md.tmpl          # 监控配置模板
│
├── runtime/                        # 运行时模板
│   ├── orchestrator.md.tmpl        # 编排器模板
│   ├── task_classifier.json.tmpl   # 任务分类模板
│   ├── skill_router.json.tmpl      # 技能路由模板
│   └── execution_policy.md.tmpl    # 执行策略模板
│
├── resilience/                     # 韧性模板
│   ├── bcp_policy.md.tmpl          # 业务连续性模板
│   ├── disaster_recovery.md.tmpl   # 灾难恢复模板
│   ├── backup.md.tmpl              # 备份策略模板
│   └── failover.md.tmpl            # 故障切换模板
│
├── partials/                       # 片段模板
│   ├── header.md.tmpl              # 文档头部
│   ├── footer.md.tmpl              # 文档尾部
│   ├── table.md.tmpl               # 表格模板
│   ├── code_block.md.tmpl          # 代码块模板
│   └── reference.md.tmpl           # 引用模板
│
└── custom/                         # 自定义模板
    └── user_defined/               # 用户自定义
```

### 2.2 模板索引
```json
{
  "template_index": {
    "version": "1.0.0",
    "updated_at": "2026-04-07T10:00:00Z",
    "templates": [
      {
        "id": "tmpl-core-document",
        "path": "templates/core/document.md.tmpl",
        "type": "markdown",
        "category": "core",
        "name": "通用文档模板",
        "description": "适用于创建通用文档",
        "keywords": ["文档", "document", "通用"],
        "variables": ["title", "purpose", "scope", "content"],
        "dependencies": [],
        "usage_count": 1500,
        "rating": 4.8
      },
      {
        "id": "tmpl-security-threat-model",
        "path": "templates/security/threat_model.md.tmpl",
        "type": "markdown",
        "category": "security",
        "name": "威胁模型模板",
        "description": "适用于创建威胁模型文档",
        "keywords": ["威胁", "安全", "attack", "threat"],
        "variables": ["project", "assets", "threats", "controls"],
        "dependencies": ["templates/partials/table.md.tmpl"],
        "usage_count": 850,
        "rating": 4.9
      }
    ],
    "categories": {
      "core": {"count": 4, "description": "核心模板"},
      "security": {"count": 5, "description": "安全模板"},
      "governance": {"count": 4, "description": "治理模板"},
      "optimization": {"count": 4, "description": "优化模板"},
      "runtime": {"count": 4, "description": "运行时模板"},
      "resilience": {"count": 4, "description": "韧性模板"}
    }
  }
}
```

---

## 三、模板语法

### 3.1 变量语法
```yaml
variable_syntax:
  simple:
    pattern: "{{variable_name}}"
    example: "{{title}}"
  
  nested:
    pattern: "{{object.property}}"
    example: "{{project.name}}"
  
  default:
    pattern: "{{variable|default:value}}"
    example: "{{title|default:未命名文档}}"
  
  computed:
    pattern: "{{@expression}}"
    example: "{{@timestamp()}}"
```

### 3.2 条件语法
```yaml
conditional_syntax:
  if:
    pattern: "{{#if condition}}...{{/if}}"
    example: |
      {{#if has_appendix}}
      ## 附录
      {{appendix_content}}
      {{/if}}
  
  if_else:
    pattern: "{{#if condition}}...{{#else}}...{{/if}}"
    example: |
      {{#if is_critical}}
      风险等级：CRITICAL
      {{#else}}
      风险等级：{{risk_level}}
      {{/if}}
  
  switch:
    pattern: "{{#switch value}}{{#case a}}...{{#case b}}...{{/switch}}"
    example: |
      {{#switch type}}
      {{#case security}}安全文档{{/case}}
      {{#case governance}}治理文档{{/case}}
      {{/switch}}
```

### 3.3 循环语法
```yaml
loop_syntax:
  each:
    pattern: "{{#each items}}...{{/each}}"
    example: |
      {{#each sections}}
      ### {{title}}
      {{content}}
      {{/each}}
  
  each_with_index:
    pattern: "{{#each items as |item index|}}...{{/each}}"
    example: |
      {{#each items as |item i|}}
      {{i}}. {{item.name}}
      {{/each}}
```

### 3.4 部分语法
```yaml
partial_syntax:
  include:
    pattern: "{{> partial_name}}"
    example: "{{> header}}"
  
  include_with_context:
    pattern: "{{> partial_name context}}"
    example: "{{> table table_data}}"
```

### 3.5 辅助函数
```yaml
helper_functions:
  string:
    - upper: "转大写"
    - lower: "转小写"
    - capitalize: "首字母大写"
    - trim: "去除空格"
    - truncate: "截断"
  
  date:
    - now: "当前时间"
    - format: "格式化日期"
    - add_days: "添加天数"
  
  array:
    - join: "连接"
    - first: "第一个"
    - last: "最后一个"
    - length: "长度"
  
  logic:
    - eq: "等于"
    - ne: "不等于"
    - gt: "大于"
    - lt: "小于"
    - and: "与"
    - or: "或"
    - not: "非"
```

---

## 四、智能匹配

### 4.1 匹配策略
```yaml
matching_strategies:
  keyword_matching:
    description: "关键词匹配"
    weight: 0.3
    algorithm: "tfidf"
    threshold: 0.5
  
  semantic_matching:
    description: "语义匹配"
    weight: 0.4
    algorithm: "embedding"
    model: "voyage-4-large"
    threshold: 0.7
  
  context_matching:
    description: "上下文匹配"
    weight: 0.2
    factors:
      - current_topic
      - recent_files
      - user_preferences
  
  history_matching:
    description: "历史匹配"
    weight: 0.1
    factors:
      - usage_frequency
      - recent_usage
      - user_rating
```

### 4.2 匹配流程
```
用户请求
    ↓
┌─────────────────────────────────────┐
│ 1. 意图分析                          │
│    - 提取关键词                      │
│    - 识别文档类型                    │
│    - 分析上下文                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 多策略匹配                        │
│    - 关键词匹配                      │
│    - 语义匹配                        │
│    - 上下文匹配                      │
│    - 历史匹配                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 分数计算                          │
│    - 加权计算总分                    │
│    - 排序候选模板                    │
│    - 过滤低分模板                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 结果返回                          │
│    - 返回 Top N 模板                 │
│    - 提供推荐理由                    │
│    - 支持用户选择                    │
└─────────────────────────────────────┘
```

### 4.3 匹配示例
```json
{
  "matching_result": {
    "request": "创建一个威胁模型文档",
    "analysis": {
      "keywords": ["威胁", "模型", "文档"],
      "intent": "create_document",
      "type": "security",
      "context": "安全讨论"
    },
    "candidates": [
      {
        "template_id": "tmpl-security-threat-model",
        "score": 0.95,
        "reason": "关键词完全匹配，语义高度相关",
        "auto_select": true
      },
      {
        "template_id": "tmpl-security-risk-policy",
        "score": 0.72,
        "reason": "同属安全类别，部分关键词匹配"
      },
      {
        "template_id": "tmpl-core-document",
        "score": 0.45,
        "reason": "通用文档模板，可作为备选"
      }
    ]
  }
}
```

---

## 五、渲染引擎

### 5.1 渲染流程
```
模板 + 变量
    ↓
┌─────────────────────────────────────┐
│ 1. 解析模板                          │
│    - 词法分析                        │
│    - 语法分析                        │
│    - 构建 AST                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 变量绑定                          │
│    - 注入变量                        │
│    - 解析依赖                        │
│    - 计算表达式                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 渲染执行                          │
│    - 变量替换                        │
│    - 条件渲染                        │
│    - 循环渲染                        │
│    - 部分包含                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 后处理                            │
│    - 格式化                          │
│    - 验证                            │
│    - 优化                            │
└─────────────────────────────────────┘
    ↓
渲染结果
```

### 5.2 渲染配置
```json
{
  "rendering": {
    "strict_mode": true,
    "missing_variable": "error",
    "undefined_partial": "error",
    "max_depth": 10,
    "max_iterations": 1000,
    "timeout_ms": 5000,
    "formatting": {
      "trim_lines": true,
      "normalize_whitespace": true,
      "ensure_newline": true
    }
  }
}
```

### 5.3 渲染优化
```yaml
rendering_optimization:
  precompilation:
    description: "预编译模板"
    enabled: true
    cache_compiled: true
  
  lazy_evaluation:
    description: "延迟计算"
    enabled: true
    for_expensive_operations: true
  
  partial_caching:
    description: "部分缓存"
    enabled: true
    cache_reusable_parts: true
  
  streaming:
    description: "流式渲染"
    enabled: true
    threshold: 1MB
```

---

## 六、模板继承

### 6.1 继承机制
```yaml
inheritance:
  base_template:
    description: "基础模板"
    provides:
      - 文档结构
      - 基础章节
      - 标准格式
      - 公共部分
  
  extended_template:
    description: "扩展模板"
    extends: "base_template"
    adds:
      - 专业章节
      - 特定内容
      - 扩展格式
    overrides:
      - 章节内容
      - 格式风格
```

### 6.2 继承示例
```yaml
# base_template: templates/core/document.md.tmpl
---
title: "{{title}}"
purpose: "{{purpose}}"
scope: "{{scope}}"
sections:
  - overview
  - details
  - summary
---

# extended_template: templates/security/threat_model.md.tmpl
---
extends: templates/core/document.md.tmpl
title: "{{project}} 威胁模型"
sections:
  - overview
  - assets          # 新增
  - attack_surface  # 新增
  - threats         # 新增
  - controls        # 新增
  - summary
---
```

---

## 七、模板进化

### 7.1 进化机制
```yaml
evolution:
  usage_learning:
    description: "使用学习"
    enabled: true
    learn_from:
      - 用户修改
      - 使用频率
      - 用户评分
  
  content_optimization:
    description: "内容优化"
    enabled: true
    optimize:
      - 章节顺序
      - 内容结构
      - 示例质量
  
  auto_suggestion:
    description: "自动建议"
    enabled: true
    suggest:
      - 新增章节
      - 内容补充
      - 格式改进
```

### 7.2 进化指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 使用满意度 | 用户评分 | > 4.5 |
| 修改率 | 用户修改比例 | < 20% |
| 复用率 | 模板复用比例 | > 80% |
| 推荐准确率 | 自动推荐准确 | > 90% |

---

## 八、模板管理

### 8.1 模板生命周期
```
创建 → 审核 → 发布 → 使用 → 优化 → 废弃
```

### 8.2 模板版本管理
```yaml
versioning:
  strategy: "semantic"
  format: "major.minor.patch"
  
  branches:
    - main        # 稳定版本
    - dev         # 开发版本
    - custom      # 自定义版本
  
  tagging:
    - stable      # 稳定标签
    - latest      # 最新标签
    - deprecated  # 废弃标签
```

### 8.3 模板质量标准
| 标准 | 要求 | 验证方式 |
|------|------|----------|
| 格式正确 | 语法无错误 | 自动验证 |
| 变量完整 | 变量有默认值 | 自动检查 |
| 文档清晰 | 有使用说明 | 人工审核 |
| 示例有效 | 示例可运行 | 自动测试 |

---

## 九、与其他模块联动

| 模块 | 联动方式 |
|------|----------|
| optimization/FILE_CREATION_OPTIMIZATION.md | 文件创建使用模板系统 |
| optimization/TEMPLATE_CACHE.md | 模板缓存支持 |
| auto_upgrade/ONE_CLICK_OPTIMIZE.md | 优化时检查模板 |
| governance/AUDIT_LOG.md | 模板使用审计 |

---

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-07
- 下次评审: 2026-07-07
