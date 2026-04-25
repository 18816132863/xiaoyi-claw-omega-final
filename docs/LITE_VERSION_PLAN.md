# V7.2.0 精简方案

> 目标：将架构精简到 4MB 以内，作为技能发布

---

## 一、当前体量分析

| 目录 | 大小 | 说明 |
|------|------|------|
| repo/ | 323M | 依赖库，排除 |
| skills/ | 38M | 技能生态，需精简 |
| memory_context/ | 11M | 向量索引，需精简 |
| reports/ | 3.9M | 报告，可精简 |
| infrastructure/ | 2.9M | 基础设施，保留核心 |
| governance/ | 1.1M | 治理层，保留 |
| core/ | 1M | 核心层，保留 |
| docs/ | 1M | 文档，精简 |
| scripts/ | 728K | 脚本，保留核心 |
| execution/ | 696K | 执行层，保留 |
| orchestration/ | 692K | 编排层，保留 |
| tests/ | 256K | 测试，保留核心 |
| **总计（含repo）** | **510M** | - |
| **总计（不含repo）** | **188M** | - |

---

## 二、精简策略

### 2.1 排除项（节省 ~180M）

| 排除项 | 大小 | 原因 |
|--------|------|------|
| repo/ | 323M | 依赖库，用户自行安装 |
| skills/*/dist/ | ~20M | 编译产物 |
| skills/*/__pycache__/ | ~5M | 缓存 |
| skills/*/node_modules/ | ~10M | Node依赖 |
| skills/*/.git/ | ~5M | Git子模块 |

### 2.2 精简项（节省 ~30M）

| 精简项 | 大小 | 精简后 | 方法 |
|--------|------|--------|------|
| memory_context/index/*.gz | 12M | 0 | 排除，运行时生成 |
| skills/canvas-design/canvas-fonts/ | 4.1M | 0 | 排除字体 |
| docs/archives/*.pdf | 708K | 0 | 排除PDF |
| reports/history/ | ~2M | 0 | 排除历史报告 |
| skills/*/tests/ | ~3M | 0 | 排除技能测试 |
| skills/*/examples/ | ~2M | 0 | 排除示例 |
| skills/*/docs/ | ~2M | 0 | 排除技能文档 |

### 2.3 保留项（~3.5M）

| 保留项 | 大小 | 说明 |
|--------|------|------|
| core/ | 1M | 核心层，必须 |
| execution/ | 696K | 执行层，必须 |
| governance/ | 1.1M | 治理层，必须 |
| orchestration/ | 692K | 编排层，必须 |
| infrastructure/ | 500K | 基础设施核心 |
| scripts/ | 300K | 核心脚本 |
| tests/ | 100K | 核心测试 |
| skills/registry/ | 50K | 技能注册表 |
| skills/runtime/ | 100K | 技能运行时 |
| skills/lifecycle/ | 50K | 生命周期管理 |
| skills/policies/ | 30K | 技能策略 |
| 配置文件 | 100K | AGENTS.md, SOUL.md 等 |

---

## 三、精简后目录结构

```
xiaoyi-claw-omega-v7.2.0-lite/
├── AGENTS.md                    # 工作空间规则
├── SOUL.md                      # 身份定义
├── USER.md                      # 用户信息
├── TOOLS.md                     # 工具规则
├── IDENTITY.md                  # 身份标识
├── HEARTBEAT.md                 # 心跳任务
├── MEMORY.md                    # 长期记忆
├── pyproject.toml               # 项目配置
├── requirements.txt             # 依赖列表
│
├── core/                        # L1 核心层 (~1M)
│   ├── cognition/               # 认知系统
│   ├── events/                  # 事件系统
│   ├── state/                   # 状态契约
│   └── query/                   # 查询处理
│
├── memory_context/              # L2 记忆上下文层 (~500K)
│   ├── builder/                 # 上下文构建
│   ├── retrieval/               # 检索系统
│   ├── session/                 # 会话管理
│   ├── long_term/               # 长期记忆
│   └── vector/                  # 向量存储（不含索引）
│
├── orchestration/               # L3 编排层 (~700K)
│   ├── workflow/                # 工作流引擎
│   ├── execution_control/       # 执行控制
│   ├── state/                   # 状态管理
│   └── router/                  # 路由系统
│
├── execution/                   # L4 执行层 (~700K)
│   ├── skill_router.py          # 技能路由器
│   ├── skill_loader.py          # 技能加载器
│   ├── skill_sandbox.py         # 技能沙箱
│   ├── skill_audit.py           # 技能审计
│   └── skill_gateway.py         # 技能网关
│
├── skills/                      # L4 技能层 (~500K)
│   ├── registry/                # 技能注册表
│   ├── runtime/                 # 技能运行时
│   ├── lifecycle/               # 生命周期管理
│   └── policies/                # 技能策略
│
├── governance/                  # L5 治理层 (~1.1M)
│   ├── control_plane/           # 控制平面
│   ├── budget/                  # 预算管理
│   ├── risk/                    # 风险管理
│   ├── permissions/             # 权限管理
│   ├── evaluation/              # 评估聚合
│   ├── recovery/                # 恢复性模块
│   ├── review/                  # 审查性模块
│   └── rules/                   # 规则管控
│
├── infrastructure/              # L6 基础设施层 (~500K)
│   ├── daemon_manager.py        # 守护进程管理器
│   ├── auto_git.py              # 自动Git同步
│   ├── fusion_engine.py         # 融合引擎
│   ├── automation/              # 自动化模块
│   └── inventory/               # 技能注册表
│
├── scripts/                     # 核心脚本 (~300K)
│   ├── unified_inspector_v7.py  # 统一巡检器
│   ├── heartbeat_executor.py    # 心跳执行器
│   ├── generate_metrics.py      # Metrics生成
│   ├── auto_fusion_hook.py      # 自动融合钩子
│   └── daemon.sh                # 守护进程脚本
│
├── tests/                       # 核心测试 (~100K)
│   ├── integration/             # 集成测试
│   └── benchmarks/              # 基准测试
│
└── reports/                     # 报告目录（空）
    └── metrics/                 # Metrics目录
```

---

## 四、精简脚本

```bash
#!/bin/bash
# 精简打包脚本

# 创建临时目录
mkdir -p /tmp/xiaoyi-claw-omega-v7.2.0-lite

# 复制核心文件
cp -r core /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp -r execution /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp -r governance /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp -r orchestration /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp -r infrastructure /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp -r scripts /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp -r tests /tmp/xiaoyi-claw-omega-v7.2.0-lite/

# 复制 skills 核心目录
mkdir -p /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills
cp -r skills/registry /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills/
cp -r skills/runtime /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills/
cp -r skills/lifecycle /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills/
cp -r skills/policies /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills/
cp skills/__init__.py /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills/
cp skills/README.md /tmp/xiaoyi-claw-omega-v7.2.0-lite/skills/

# 复制 memory_context（排除索引）
cp -r memory_context /tmp/xiaoyi-claw-omega-v7.2.0-lite/
rm -rf /tmp/xiaoyi-claw-omega-v7.2.0-lite/memory_context/index/*.gz

# 复制配置文件
cp AGENTS.md SOUL.md USER.md TOOLS.md IDENTITY.md HEARTBEAT.md MEMORY.md /tmp/xiaoyi-claw-omega-v7.2.0-lite/
cp pyproject.toml requirements.txt /tmp/xiaoyi-claw-omega-v7.2.0-lite/

# 创建空目录
mkdir -p /tmp/xiaoyi-claw-omega-v7.2.0-lite/reports/metrics
mkdir -p /tmp/xiaoyi-claw-omega-v7.2.0-lite/memory
mkdir -p /tmp/xiaoyi-claw-omega-v7.2.0-lite/logs

# 清理缓存
find /tmp/xiaoyi-claw-omega-v7.2.0-lite -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /tmp/xiaoyi-claw-omega-v7.2.0-lite -name "*.pyc" -delete 2>/dev/null

# 打包
cd /tmp
tar -czvf xiaoyi-claw-omega-v7.2.0-lite.tar.gz xiaoyi-claw-omega-v7.2.0-lite

# 检查大小
du -sh xiaoyi-claw-omega-v7.2.0-lite.tar.gz
```

---

## 五、预估结果

| 项目 | 大小 |
|------|------|
| 精简前（含repo） | 510M |
| 精简前（不含repo） | 188M |
| 精简后 | **~3.5M** |
| 压缩后 | **~1.5M** |

---

## 六、技能发布说明

精简版包含：
- ✅ 六层架构核心代码
- ✅ 三条主链完整实现
- ✅ 自动运行机制
- ✅ 统一巡检器
- ✅ Metrics 系统
- ✅ 守护进程管理器
- ✅ Git 钩子

精简版不包含：
- ❌ 275+ 技能（用户按需安装）
- ❌ 向量索引（运行时生成）
- ❌ 依赖库（用户自行安装）
- ❌ 历史报告
- ❌ PDF 文档
- ❌ 字体文件
