# LEARNINGS.md - 学习记录

记录最佳实践、用户纠正、知识更新和优化发现。

---

## [LRN-20260405-001] best_practice

**Logged**: 2026-04-05T23:30:00+08:00
**Priority**: high
**Status**: resolved
**Area**: skills

### Summary
技能安装受 ClawHub API 速率限制影响，每分钟约 30 次请求

### Details
- ClawHub API 有严格的速率限制
- 连续安装会触发限流，需要等待重试
- 最佳策略：每安装 1-2 个技能后等待 1-2 秒

### Suggested Action
在批量安装脚本中添加 `sleep 1` 延迟

### Metadata
- Source: error
- Related Files: /tmp/install_200_skills.sh
- Tags: api, rate-limit, installation

---

## [LRN-20260405-002] best_practice

**Logged**: 2026-04-05T23:30:00+08:00
**Priority**: high
**Status**: promoted
**Area**: architecture

### Summary
技能架构应按优先级分层：P0(xiaoyi+core) > P1(search+document) > P2(development) > P3(utility)

### Details
- 106 个技能需要清晰的优先级体系
- xiaoyi 系列优先级最高 (100)
- 核心技能次之 (95)
- 工具类最低 (25-50)

### Suggested Action
在 skills-config.json 中维护优先级配置

### Metadata
- Source: user_feedback
- Related Files: skills-config.json
- Tags: architecture, priority, organization

---

## [LRN-20260405-003] best_practice

**Logged**: 2026-04-05T23:30:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: skills

### Summary
工作流链比单一技能更有效，应建立技能调用链

### Details
- 文档转换链: xiaoyi-doc-convert → [file-upload, docx, pdf, pptx]
- 图像处理链: xiaoyi-image-understanding → [image-search, seedream]
- 搜索调研链: deep-search → [web-search-exa, prismfy-search]
- 自进化链: self-improving-agent → [auto-skill-upgrade, ontology, skill-creator]

### Suggested Action
在 skills-config.json 中维护工作流链配置

### Metadata
- Source: best_practice
- Related Files: skills-config.json
- Tags: workflow, chain, integration

---

## [LRN-20260405-005] best_practice

**Logged**: 2026-04-05T23:53:00+08:00
**Priority**: high
**Status**: promoted
**Area**: performance

### Summary
大文件技能影响加载性能，需要精简 SKILL.md

### Details
- 优化前: 31 个技能 > 10KB，总大小 910KB，平均 8.5KB
- 优化后: 0 个技能 > 10KB，总大小 494KB，平均 4KB
- 减少: 45% 总大小

### Suggested Action
✅ 已完成: 将详细文档移至 references/ 目录

### Metadata
- Source: performance_analysis
- Related Files: performance-report.md
- Tags: performance, optimization, large-files

---

## [LRN-20260405-006] best_practice

**Logged**: 2026-04-05T23:53:00+08:00
**Priority**: high
**Status**: promoted
**Area**: performance

### Summary
懒加载机制可显著减少启动加载时间

### Details
- P0 核心技能 20 个，会话启动加载
- P1-P3 技能按需加载
- 预计减少启动时间 70%

### Suggested Action
✅ 已完成: 创建 lazy-loader.sh 和 quick-load.txt

### Metadata
- Source: optimization
- Related Files: lazy-loader.sh, quick-load.txt
- Tags: performance, lazy-loading, startup

---

## [LRN-20260405-007] best_practice

**Logged**: 2026-04-06T00:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: performance

### Summary
SKILL.md 精简策略：保留前100行，其余移至 references/

### Details
优化了 31 个大文件技能:
- klaviyo: 37KB → 2.9KB (92%)
- api-gateway: 34KB → 3.5KB (90%)
- web-scraper: 31KB → 5.3KB (83%)
- beauty-generation-api: 29KB → 3.6KB (88%)
- linkedin-api: 28KB → 2.8KB (90%)

### Suggested Action
新技能创建时遵循此模式

### Metadata
- Source: optimization
- Tags: performance, skill-structure, references

---

## [LRN-20260405-004] knowledge_gap

**Logged**: 2026-04-05T23:30:00+08:00
**Priority**: medium
**Status**: pending
**Area: memory

### Summary
需要建立完整的自进化学习系统

### Details
- 已创建 .learnings/ 目录结构
- 已创建 memory/ontology/ 知识图谱
- 需要在 AGENTS.md 中添加自进化检查流程

### Suggested Action
更新 AGENTS.md 添加学习文件读取流程

### Metadata
- Source: self_discovery
- Related Files: AGENTS.md, .learnings/, memory/ontology/
- Tags: self-evolution, learning, memory

## [LRN-20260405-2346] auto_evolution

**Logged**: 2026-04-05T23:46:19+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 107 个新技能，已完成架构升级

### Details
- 技能总数: 107
- 新增技能: 107
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260405-2354] auto_evolution

**Logged**: 2026-04-05T23:54:41+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到  个新技能，已完成架构升级

### Details
- 技能总数: 107
- 新增技能: 
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-0002] auto_evolution

**Logged**: 2026-04-06T00:02:32+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到  个新技能，已完成架构升级

### Details
- 技能总数: 107
- 新增技能: 
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-0110] auto_evolution

**Logged**: 2026-04-06T01:10:17+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 38 个新技能，已完成架构升级

### Details
- 技能总数: 145
- 新增技能: 38
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-0128] auto_evolution

**Logged**: 2026-04-06T01:28:38+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 6 个新技能，已完成架构升级

### Details
- 技能总数: 151
- 新增技能: 6
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-0223] auto_evolution

**Logged**: 2026-04-06T02:23:29+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到  个新技能，已完成架构升级

### Details
- 技能总数: 151
- 新增技能: 
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-0234] auto_evolution

**Logged**: 2026-04-06T02:34:53+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 3 个新技能，已完成架构升级

### Details
- 技能总数: 154
- 新增技能: 3
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


---

## [LRN-20260406-001] best_practice

**Logged**: 2026-04-06T02:30:00+08:00
**Priority**: high
**Status**: promoted
**Area**: performance

### Summary
懒加载机制可减少 70% 启动 Token 消耗

### Details
- 优化前: 启动加载所有 151 技能元数据
- 优化后: 只加载 P0 核心技能 + 索引文件
- AGENTS.md 已更新为懒加载模式

### Metadata
- Source: optimization
- Tags: token, lazy-loading, startup

---

## [LRN-20260406-002] best_practice

**Logged**: 2026-04-06T02:32:00+08:00
**Priority**: high
**Status**: promoted
**Area**: performance

### Summary
SKILL.md 精简策略：保留前 80 行，其余移至 references/

### Details
- 精简 70 个技能
- 优化前: 713KB, 182K tokens
- 优化后: 538KB, 137K tokens
- 减少: 25%

### Metadata
- Source: optimization
- Tags: token, skill-size, references

---

## [LRN-20260406-003] best_practice

**Logged**: 2026-04-06T02:34:00+08:00
**Priority**: high
**Status**: resolved
**Area**: architecture

### Summary
技能链合并：创建统一入口减少重复加载

### Details
- 创建 3 个统一入口技能
- 文档链: 6技能 → unified-document
- 图像链: 4技能 → unified-image
- 搜索链: 4技能 → unified-search
- 预计减少 Token: 30%

### Metadata
- Source: optimization
- Tags: token, skill-chain, unified-entry

## [LRN-20260406-0245] auto_evolution

**Logged**: 2026-04-06T02:45:01+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到  个新技能，已完成架构升级

### Details
- 技能总数: 154
- 新增技能: 
- 冗余检测: 已完成
- 知识图谱: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-0933] auto_evolution

**Logged**: 2026-04-06T09:33:19+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 12 个新技能，已完成架构升级

### Details
- 技能总数: 166
- 新增技能: 12
- 冗余检测: 已完成
- 知识图谱: 已更新
- 使用统计: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260406-1003] auto_evolution

**Logged**: 2026-04-06T10:03:20+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 2 个新技能，已完成架构升级

### Details
- 技能总数: 168
- 新增技能: 2
- 冗余检测: 已完成
- 知识图谱: 已更新
- 使用统计: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---


## [LRN-20260418-0743] auto_evolution

**Logged**: 2026-04-18T07:43:31+08:00
**Priority**: medium
**Status**: resolved
**Area**: self_evolution

### Summary
自动检测到 113 个新技能，已完成架构升级

### Details
- 技能总数: 281
- 新增技能: 113
- 冗余检测: 已完成
- 知识图谱: 已更新
- 使用统计: 已更新

### Metadata
- Source: auto_evolution
- Tags: self-evolution, auto-upgrade

---

