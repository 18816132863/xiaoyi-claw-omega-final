# 融合策略 V1.0.0

> 定义文件融合到架构的规则和流程

---

## 一、融合原则

### 1. 核心原则

- **不影响架构**：影响架构的文件不可移动
- **核心文件保留**：核心配置文件必须保留在根目录
- **分类归档**：非核心文件按类型归档到对应目录
- **可追溯**：每次融合生成报告，记录变更

### 2. 融合时机

- 新增技能时
- 架构升级时
- 手动整理时

---

## 二、文件分类规则

### 保留在根目录的核心文件

| 文件 | 职责 | 不可移动原因 |
|------|------|--------------|
| `AGENTS.md` | 工作空间规则 | 系统启动时读取 |
| `SOUL.md` | 身份定义 | 定义 AI 人格 |
| `USER.md` | 用户信息 | 用户配置 |
| `TOOLS.md` | 工具规则 | 工具使用规范 |
| `IDENTITY.md` | 身份标识 | 身份元数据 |
| `MEMORY.md` | 长期记忆 | 记忆存储 |
| `HEARTBEAT.md` | 心跳任务 | 定时任务定义 |
| `BOOTSTRAP.md` | 启动引导 | 新会话引导 |
| `SKILL.md` | 技能说明 | 技能元信息 |
| `README.md` | 项目说明 | 项目入口文档 |

### 影响架构的文件（不可移动）

| 文件 | 原因 |
|------|------|
| `core/ARCHITECTURE.md` | 主架构定义 |
| `core/RULE_REGISTRY.json` | 规则注册表 |
| `core/RULE_EXCEPTIONS.json` | 规则例外 |
| `core/LAYER_DEPENDENCY_RULES.json` | 层间依赖规则 |
| `infrastructure/inventory/skill_registry.json` | 技能注册表 |

### 文档类文件 -> `docs/`

| 文件模式 | 说明 |
|----------|------|
| `API_REFERENCE.md` | API 参考文档 |
| `CHANGELOG.md` | 变更日志 |
| `CONTRIBUTING.md` | 贡献指南 |
| `FILE_INVENTORY.md` | 文件清单 |
| `FUSION_REPORT.md` | 融合报告 |

### 架构归档 -> `docs/archives/`

| 文件模式 | 说明 |
|----------|------|
| `*架构图*.pdf` | 架构图 PDF |
| `*架构报告*.pdf` | 架构报告 PDF |
| `FILE_INVENTORY.pdf` | 文件清单 PDF |

### 历史记录 -> `docs/history/`

| 文件模式 | 说明 |
|----------|------|
| `V4.3.*_SUMMARY.md` | 版本升级总结 |
| `V4.2.*_SUMMARY.md` | 版本升级总结 |

### 安全文档 -> `governance/docs/`

| 文件模式 | 说明 |
|----------|------|
| `SAFETY_*.md` | 安全声明 |
| `SECURITY.md` | 安全说明 |

---

## 三、融合流程

### 1. 扫描阶段

```bash
python infrastructure/fusion_engine.py --scan
```

- 扫描根目录文件
- 判断每个文件的分类
- 生成融合建议

### 2. 模拟执行

```bash
python infrastructure/fusion_engine.py --dry-run
```

- 模拟执行融合操作
- 不实际移动文件
- 显示将要执行的操作

### 3. 实际执行

```bash
python infrastructure/fusion_engine.py --execute
```

- 实际执行融合操作
- 移动文件到目标目录
- 生成融合报告

### 4. 保存报告

```bash
python infrastructure/fusion_engine.py --execute --report docs/fusion_report.md
```

---

## 四、新增技能时的融合

当安装新技能时，自动执行融合检查：

1. 检查技能目录结构
2. 判断是否有需要融合的文件
3. 按规则分类处理
4. 生成融合报告

---

## 五、融合报告格式

```markdown
# 融合报告

生成时间: 2026-04-14 19:00:00

## 统计
- 扫描文件: 20
- 已融合: 10
- 已跳过: 10
- 错误: 0

## 已移动文件
- `API_REFERENCE.md` -> `docs/API_REFERENCE.md`
- `CHANGELOG.md` -> `docs/CHANGELOG.md`

## 跳过的文件
- AGENTS.md (核心文件保留)
- README.md (核心文件保留)
```

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-14
