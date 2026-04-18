# 技能升级架构定义 V1.0.0

> **唯一真源** - 本文档是技能升级体系的唯一架构定义

---

## 一、架构定位

### 1.1 层级归属

| 层级 | 模块 | 职责 |
|------|------|------|
| L1 Core | `core/SKILL_UPGRADE_ARCHITECTURE.md` | 升级策略、评分标准、规则定义 |
| L3 Orchestration | `orchestration/skill_upgrade/` | 升级流程编排、任务调度 |
| L4 Execution | `skills/skill_upgrade_engine.py` | 升级执行引擎 |
| L5 Governance | `governance/skill_quality/` | 质量门禁、审计日志 |
| L6 Infrastructure | `infrastructure/skill_templates/` | 模板库、工具链 |

### 1.2 依赖关系

**白名单**:
- L4 Execution 可读取 L1 Core (升级规则)
- L4 Execution 可读取 L6 Infrastructure (模板库)
- L3 Orchestration 可读取 L1 Core (策略定义)
- L5 Governance 可读取 L1 Core (评分标准)

**黑名单**:
- L1 Core 禁止依赖 L3/L4/L5/L6
- L4 Execution 禁止直接依赖 L5 Governance
- L5 Governance 禁止依赖具体技能实现

---

## 二、真源清单

### 2.1 升级策略真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 升级架构定义 | `core/SKILL_UPGRADE_ARCHITECTURE.md` | 唯一真源 |
| 评分标准 | `core/SKILL_UPGRADE_ARCHITECTURE.md#评分标准` | 唯一真源 |
| 升级流程 | `core/SKILL_UPGRADE_ARCHITECTURE.md#升级流程` | 唯一真源 |

### 2.2 模板库真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 执行脚本模板 | `infrastructure/skill_templates/skill.py.template` | 唯一真源 |
| SKILL.md 模板 | `infrastructure/skill_templates/SKILL.md.template` | 唯一真源 |
| 默认模板 | `infrastructure/skill_templates/default.md.template` | 唯一真源 |

### 2.3 升级报告真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 升级报告 | `reports/skill_upgrades/upgrade_*.json` | 真源 |
| 升级日志 | `reports/skill_upgrades/upgrade_*.log` | 真源 |

### 2.4 派生物标注

所有派生物必须包含：

```json
{
  "derived": true,
  "source": "core/SKILL_UPGRADE_ARCHITECTURE.md",
  "generated_at": "2026-04-18T08:00:00Z",
  "generator": "skill_upgrade_engine.py"
}
```

---

## 三、评分标准

### 3.1 五星评分体系

| 评分 | 标准 | 必需项 | 文档质量 |
|------|------|--------|----------|
| ⭐⭐⭐⭐⭐ | 立即可用 | 5项全满 | 优秀 |
| ⭐⭐⭐⭐ | 可用 | 4项满足 | 良好 |
| ⭐⭐⭐ | 基础可用 | 3项满足 | 合格 |
| ⭐⭐ | 不可用 | 2项满足 | 不合格 |
| ⭐ | 废弃 | ≤1项满足 | 缺失 |

### 3.2 必需项定义

| 序号 | 必需项 | 路径 | 权重 |
|------|--------|------|------|
| 1 | 执行脚本 | `skill.py` | 20% |
| 2 | 技能文档 | `SKILL.md` | 20% |
| 3 | 模板库 | `templates/` | 20% |
| 4 | 输出目录 | `output/` | 20% |
| 5 | 文档质量 | SKILL.md 内容 | 20% |

### 3.3 文档质量标准

| 指标 | 要求 | 分值 |
|------|------|------|
| 描述完整 | description 字段存在且 > 50字 | 5分 |
| 用法说明 | 包含"用法"或"使用"或"example" | 5分 |
| 结构清晰 | 包含至少3个二级标题 (##) | 5分 |
| 内容充实 | 总字数 > 500字 | 5分 |

**文档质量评分**:
- 20分: 优秀 (⭐⭐⭐⭐⭐)
- 15-19分: 良好 (⭐⭐⭐⭐)
- 10-14分: 合格 (⭐⭐⭐)
- 5-9分: 不合格 (⭐⭐)
- 0-4分: 缺失 (⭐)

---

## 四、升级流程

### 4.1 五步升级法

```
Step 1: 诊断 (Diagnose)
  ├─ 读取 L1 Core 评分标准
  ├─ 检查必需项存在性
  ├─ 评估文档质量
  └─ 计算当前评分

Step 2: 设计 (Design)
  ├─ 读取 L6 Infrastructure 模板库
  ├─ 确定升级目标
  ├─ 设计文件结构
  └─ 规划实现路径

Step 3: 实现 (Implement)
  ├─ 创建 skill.py (从模板)
  ├─ 创建 templates/ (从模板)
  ├─ 创建 output/
  └─ 增强 SKILL.md

Step 4: 测试 (Test)
  ├─ 验证文件存在
  ├─ 测试命令执行
  ├─ 重新计算评分
  └─ 确认达标

Step 5: 部署 (Deploy)
  ├─ 提交到 Git
  ├─ 生成升级报告 (真源)
  ├─ 更新技能注册表
  └─ 触发质量门禁
```

### 4.2 流程编排规则

**L3 Orchestration 职责**:
- 调度升级任务
- 管理升级队列
- 处理升级失败
- 触发后续流程

**L4 Execution 职责**:
- 执行具体升级逻辑
- 读取模板库
- 生成文件
- 返回执行结果

**L5 Governance 职责**:
- 质量门禁检查
- 审计日志记录
- 合规性验证
- 异常告警

---

## 五、质量门禁

### 5.1 Pre-Commit 门禁

```yaml
pre_commit:
  checks:
    - name: skill_py_exists
      rule: skill.py 文件存在
      severity: error
    
    - name: skill_md_exists
      rule: SKILL.md 文件存在
      severity: error
    
    - name: templates_dir_exists
      rule: templates/ 目录存在
      severity: error
    
    - name: output_dir_exists
      rule: output/ 目录存在
      severity: warning
    
    - name: skill_md_quality
      rule: SKILL.md 文档质量 >= 10分
      severity: warning
```

### 5.2 Pre-Merge 门禁

```yaml
pre_merge:
  checks:
    - name: skill_score
      rule: 技能评分 >= 4⭐
      severity: error
    
    - name: test_passed
      rule: skill.py help 命令执行成功
      severity: error
    
    - name: template_valid
      rule: 至少有一个有效模板
      severity: warning
```

### 5.3 Pre-Release 门禁

```yaml
pre_release:
  checks:
    - name: skill_score_max
      rule: 技能评分 = 5⭐
      severity: error
    
    - name: all_tests_passed
      rule: 所有测试通过
      severity: error
    
    - name: user_acceptance
      rule: 用户验收通过
      severity: error
```

---

## 六、硬规则

### 6.1 架构规则

```
❌ L1 Core 禁止依赖 L3/L4/L5/L6
❌ L4 Execution 禁止直接依赖 L5 Governance
❌ L5 Governance 禁止依赖具体技能实现
❌ 手动修改派生物
❌ 同一对象两套真源
❌ 真源变更不更新派生
```

### 6.2 升级规则

```
✅ 升级必须从 L1 Core 读取评分标准
✅ 模板必须从 L6 Infrastructure 读取
✅ 报告必须写入 reports/ (真源)
✅ 派生物必须标注 derived 字段
✅ 升级失败必须回滚
✅ 质量门禁必须通过
```

### 6.3 评分规则

```
✅ 评分必须基于 5 项必需项
✅ 文档质量必须量化评分
✅ 评分结果必须记录到报告
✅ 评分变更必须触发审计
```

---

## 七、审计日志

### 7.1 审计事件

| 事件类型 | 说明 | 记录位置 |
|----------|------|----------|
| upgrade_start | 升级开始 | `reports/skill_upgrades/audit.jsonl` |
| upgrade_success | 升级成功 | `reports/skill_upgrades/audit.jsonl` |
| upgrade_failed | 升级失败 | `reports/skill_upgrades/audit.jsonl` |
| score_changed | 评分变更 | `reports/skill_upgrades/audit.jsonl` |
| gate_passed | 门禁通过 | `reports/skill_upgrades/audit.jsonl` |
| gate_failed | 门禁失败 | `reports/skill_upgrades/audit.jsonl` |

### 7.2 审计日志格式

```json
{
  "timestamp": "2026-04-18T08:00:00Z",
  "event_type": "upgrade_success",
  "skill_name": "novel-generator",
  "before_score": 2,
  "after_score": 5,
  "executor": "skill_upgrade_engine.py",
  "duration_ms": 1234,
  "details": {
    "files_created": ["skill.py", "templates/default.md"],
    "files_modified": ["SKILL.md"]
  }
}
```

---

## 八、持续改进机制

### 8.1 定期巡检

| 巡检类型 | 频率 | 触发方式 |
|----------|------|----------|
| 快速巡检 | 每日 | Heartbeat |
| 完整巡检 | 每周 | Cron |
| 深度巡检 | 每月 | 手动触发 |

### 8.2 反馈循环

```
用户使用 → 收集反馈 → 分析问题 → 优化策略 → 更新 L1 Core
    ↑                                              ↓
    └──────────────────────────────────────────────┘
```

### 8.3 版本管理

| 版本 | 变更内容 | 日期 |
|------|----------|------|
| V1.0.0 | 初始版本 | 2026-04-18 |

---

## 九、实施路径

### 9.1 Phase 1: 基础建设

- ✅ 创建 L1 Core 架构定义
- ✅ 创建 L6 Infrastructure 模板库
- ✅ 创建 L4 Execution 升级引擎

### 9.2 Phase 2: 批量升级

- ✅ 升级所有技能到 ⭐⭐⭐⭐⭐
- ✅ 生成升级报告
- ✅ 提交到 Git

### 9.3 Phase 3: 持续优化

- ⏳ 收集用户反馈
- ⏳ 优化模板库
- ⏳ 扩展API集成

---

## 十、版本历史

- V1.0.0: 初始版本，建立架构化升级体系

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-18
**状态**: ✅ 已实施
