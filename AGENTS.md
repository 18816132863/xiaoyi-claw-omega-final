# AGENTS.md V4.3.0 - 六层架构 + 文件保护

---

## 每次会话

1. `SOUL.md` — 身份
2. `USER.md` — 用户
3. `TOOLS.md` — 工具规则
4. `memory/YYYY-MM-DD.md` — 今日日记

---

## 六层架构 (唯一正式架构)

```
L1: Core              → 核心认知、身份、规则
L2: Memory Context    → 记忆上下文、知识库
L3: Orchestration     → 任务编排、工作流
L4: Execution         → 能力执行、技能网关
L5: Governance        → 稳定治理、安全审计
L6: Infrastructure    → 基础设施、工具链
```

---

## Token 预算

| 层级 | Token | 加载 | 技能数 | 模块数 |
|------|-------|------|--------|--------|
| L1 | 3000 | 立即 | 0 | 6文件 |
| L2 | 2000 | 按需 | 3 | 2文件 |
| L3 | 1500 | 按需 | 8 | 2模块 |
| L4 | 1500 | 分类 | 161 | 2模块 |
| L5 | 800 | 敏感 | 6 | 5模块 |
| L6 | 700 | 系统 | 17 | 4模块 |

**总计**: 9500 Token | 195 技能 | 21 模块

---

## 受保护文件 (按真实目录)

### L1 核心文件 (6个)

| 文件 | 作用 | 可删除 |
|------|------|--------|
| AGENTS.md | 工作空间规则 | ❌ |
| SOUL.md | 身份定义 | ❌ |
| USER.md | 用户信息 | ❌ |
| TOOLS.md | 工具规则 | ❌ |
| IDENTITY.md | 身份标识 | ❌ |
| core/ARCHITECTURE.md | 唯一主架构 | ❌ |

### L2 记忆文件 (2个)

| 文件 | 作用 | 可删除 |
|------|------|--------|
| MEMORY.md | 长期记忆 | ❌ |
| memory/*.md | 日记文件 | 需确认 |

### L3 编排文件 (2个)

| 文件 | 作用 | 可删除 |
|------|------|--------|
| orchestration/router/skill_router.py | 技能路由器 | ❌ |
| orchestration/task_engine.py | 任务引擎 | ❌ |

### L4 执行文件 (2个)

| 文件 | 作用 | 可删除 |
|------|------|--------|
| execution/skill_gateway.py | 技能网关 | ❌ |
| execution/ecommerce/ | 电商执行器 | ❌ |

### L5 治理文件 (5个)

| 文件 | 作用 | 可删除 |
|------|------|--------|
| governance/security.py | 安全检查 | ❌ |
| governance/permissions.py | 权限管理 | ❌ |
| governance/audit.py | 审计日志 | ❌ |
| governance/validator.py | 结果验证器 | ❌ |
| governance/compliance.py | 合规检查 | ❌ |

### L6 基础设施文件 (4个)

| 文件 | 作用 | 可删除 |
|------|------|--------|
| infrastructure/loader/ | 懒加载器 | ❌ |
| infrastructure/cache/ | 缓存管理 | ❌ |
| infrastructure/optimization/ | 优化模块 | ❌ |
| infrastructure/inventory/skill_registry.json | 技能注册表 | ❌ |

---

## 改动前检查规则

任何对主干文件的改动，需检查：
1. 是否破坏六层边界
2. 是否影响已有技能路由
3. 是否影响注册表字段一致性
4. 是否影响历史兼容映射

---

## 安全规则

- **禁止**禁用 execution-validator
- **禁止**绕过文件保护删除文件
- **禁止**直接使用 rm 删除文件
- **使用** trash 替代 rm
- **安装技能前**检查 skill-scope
- **敏感操作**需确认
- **删除文件**需二次确认 + 说明必要性

---

## Heartbeat

收到心跳时:
- 读 `HEARTBEAT.md`
- 无需处理则回复 `HEARTBEAT_OK`
- **禁止**用 Heartbeat 做定时提醒

---

**版本**: V4.3.0 | 六层架构收口 + 治理校准
