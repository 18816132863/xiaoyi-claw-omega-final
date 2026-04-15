---
name: auto-skill-upgrade
description: auto-skill-upgrade 技能模块
---

# Auto Skill Upgrade - 自动技能升级系统

## 版本信息
- **当前版本**: 3.0-ULTIMATE
- **配置文件**: `upgrade-config.json`

## 核心定位
自动检查、整合和升级已安装技能的系统。当添加新技能时，自动融合并升级整个技能体系。

## 触发条件
- 用户说"自动升级"、"升级技能"、"自动升级记忆"
- 用户安装新技能后
- 用户要求"检查技能"、"整合技能"
- 定期心跳检查时（可选）
- 用户说"优化我的技能库"

## 🚀 自动升级 v3.0-ULTIMATE 完整流程

当用户说"自动升级"时，执行以下 **7 大阶段**：

### 第一阶段：🔍 自动检测
1. **扫描技能库** (`scan-skills.sh`)
   - 扫描 `~/.openclaw/workspace/skills/` 目录
   - 获取所有已安装技能清单
   - 输出: `skills-inventory.json`

2. **检测冲突** (`detect-conflicts.sh`)
   - 功能重叠检测
   - 命名冲突检测
   - 依赖冲突检测
   - 输出: `conflicts-report.md`

3. **检测冗余** (`detect-redundancy.sh`)
   - 识别重复功能技能
   - 标记低使用率技能
   - 输出: `redundant-skills.txt`

### 第二阶段：⚡ 性能优化
1. **性能分析** (`performance-optimizer.sh`)
   - 分析技能加载时间
   - 识别大文件技能
   - 优化建议

2. **Token 监控** (`token-monitor.sh`)
   - 监控 Token 消耗
   - 生成优化报告
   - 输出: `token-report.md`

3. **懒加载优化** (`lazy-loader.sh`)
   - 更新懒加载索引
   - 优化 P0-P3 优先级
   - 输出: `quick-load.txt`

### 第三阶段：🧠 记忆管理
1. **记忆压缩** (`memory-compress.sh`)
   - 压缩 MEMORY.md
   - 归档旧记录
   - 保留关键信息

2. **会话压缩** (`session-compress.sh`)
   - 压缩会话历史
   - 提取关键决策
   - 归档到 memory/

3. **知识图谱更新** (`update-ontology.sh`)
   - 更新实体关系
   - 补全技能图谱
   - 输出: `ontology-graph.json`

4. **学习捕获** (`learning-capture.sh`)
   - 捕获本次会话学习
   - 更新 .learnings/
   - 输出: `LEARNINGS.md`, `ERRORS.md`

### 第四阶段：🧹 冗余清理
1. **冗余清理** (`redundancy-cleanup.sh`)
   - 清理重复配置
   - 合并相似文件
   - 输出: 清理报告

2. **自动清理** (`auto-cleanup.sh`)
   - 清理临时文件
   - 清理过期日志
   - 清理缓存

3. **技能修剪** (`skill-pruner.sh`)
   - 移除未使用技能（需确认）
   - 禁用低优先级技能
   - 输出: 修剪报告

### 第五阶段：🔄 整合升级
1. **技能整合** (`merge-skills.sh`)
   - 合并功能重叠技能
   - 建立调用链
   - 输出: `skills-config.json`

2. **技能链合并** (`skill-chain-merge.sh`)
   - 优化工作流链
   - 建立依赖关系
   - 输出: 链配置

3. **配置合并** (`config-merge.sh`)
   - 合并配置文件
   - 解决配置冲突
   - 输出: 统一配置

4. **使用频率追踪** (`usage-tracker.sh`)
   - 追踪技能使用频率
   - 更新优先级
   - 输出: `usage-stats.json`

5. **技能推荐** (`skill-recommender.sh`)
   - 基于使用推荐技能
   - 推荐新技能安装
   - 输出: 推荐列表

### 第六阶段：🌱 自我进化
1. **自动进化** (`auto-evolve.sh`)
   - 自我优化系统
   - 学习用户偏好
   - 输出: 进化报告

2. **本体优化** (`ontology-optimize.sh`)
   - 优化知识图谱
   - 实体关系优化
   - 输出: 优化后的图谱

### 第七阶段：🏗️ 架构升级
1. **架构分析** (`architecture-upgrade.sh`)
   - 系统架构检查（核心文件、目录结构）
   - 技能架构分析（分类统计、工作流链）
   - 记忆架构分析（三层画像系统）
   - 架构健康度评估
   - 输出: `architecture-report.md`

2. **架构优化建议**
   - 缺失文件检测与创建
   - 技能链完整性检查
   - 记忆归档建议
   - 冗余清理建议

## 输出格式

### 升级报告
```markdown
## 📊 自动升级报告 - YYYY-MM-DD HH:MM

### 执行阶段
| 阶段 | 内容 | 状态 |
|------|------|------|
| 🔍 自动检测 | 扫描/冲突/冗余 | ✅ |
| ⚡ 性能优化 | 性能/Token/懒加载 | ✅ |
| 🧠 记忆管理 | 压缩/会话/图谱 | ✅ |
| 🧹 冗余清理 | 清理/修剪 | ✅ |
| 🔄 整合升级 | 整合/链/配置 | ✅ |
| 🌱 自我进化 | 进化/本体 | ✅ |
| 🏗️ 架构升级 | 系统架构/技能架构/记忆架构 | ✅ |

### 统计数据
- 技能总数: XXX
- 检测冲突: XX
- 冗余技能: XX
- 架构健康度: XX/100
```

## 配置文件

### upgrade-config.json (v3.0-ULTIMATE)
```json
{
  "auto_upgrade": {
    "version": "3.0-ULTIMATE",
    "stages": [ ... ],
    "backup": { "enable": true, "keep_versions": 5 },
    "rollback": { "enable": true }
  }
}
```

### skills-config.json
```json
{
  "version": "2.0.0",
  "lastUpgrade": "2026-04-06T09:30:00+08:00",
  "categories": { ... },
  "chains": { ... },
  "priority": { ... }
}
```

## 快速命令

```bash
# 完整自动升级 v3.0-ULTIMATE（7大阶段）
bash scripts/auto-upgrade-ultimate.sh

# 或使用原版
bash scripts/auto-upgrade-full.sh

# 单独执行某阶段
bash scripts/scan-skills.sh          # 扫描
bash scripts/detect-conflicts.sh    # 冲突检测
bash scripts/performance-optimizer.sh  # 性能优化
bash scripts/memory-compress.sh     # 记忆压缩
bash scripts/redundancy-cleanup.sh  # 冗余清理
bash scripts/merge-skills.sh        # 技能整合
bash scripts/architecture-upgrade.sh # 架构升级
```

## 详细文档

请参阅 [references/details.md](references/details.md)
