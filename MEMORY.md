# MEMORY.md - 长期记忆

此文件用于存储跨会话的重要信息、决策和上下文。

## 项目状态

- **版本**: V7.0.0
- **状态**: 全面整合完成，门禁通过
- **更新时间**: 2026-04-15

## 架构概览

六层架构：
- L1: Core - 核心认知、身份、规则、标准
- L2: Memory Context - 记忆上下文、知识库、向量存储 (4096维)
- L3: Orchestration - 任务编排、工作流
- L4: Execution - 能力执行、技能网关
- L5: Governance - 稳定治理、安全审计、加密存储
- L6: Infrastructure - 基础设施、工具链、技能注册表

## 技能生态

### 统计
- **总技能数**: 275
- **可路由**: 273
- **可测试**: 80
- **可调用**: 273

### 分类分布
| 分类 | 数量 |
|------|------|
| AI | 31 |
| Search | 24 |
| Image | 17 |
| Document | 13 |
| Video | 10 |
| Finance | 8 |
| Code | 8 |
| E-commerce | 8 |
| Data | 7 |
| Memory | 7 |
| Audio | 5 |
| Automation | 5 |
| Communication | 2 |
| Utility | 1 |
| Other | 129 |

### 核心技能
- **llm-memory-integration** (v5.1.5): LLM + 向量模型集成，4096维 Embedding
- **agent-chronicle** (v1.0.0): 日记生成，记忆集成
- **find-skills** (v1.0.0): 技能发现
- **memory-setup** (v1.0.0): 记忆系统配置

## 高级功能配置

### 向量存储 (三引擎架构)
| 引擎 | 状态 | 维度 | 说明 |
|------|------|------|------|
| sqlite-vec | ✅ 启用 | 4096 | 主引擎，本地存储 |
| qdrant | ✅ 启用 | 4096 | 副引擎，高性能 |
| tfidf | ✅ 启用 | - | 备份引擎，关键词检索 |

### LLM 配置
- **提供商**: Gitee AI
- **LLM**: Qwen3-235B-A22B
- **Embedding**: Qwen3-Embedding-8B (4096维)
- **API**: https://ai.gitee.com/v1

### 审计系统
- **加密存储**: AES-256-GCM ✅
- **工具调用审计**: ✅
- **技能调用审计**: ✅
- **内存读写审计**: ✅

### 高级依赖
| 依赖 | 版本 | 用途 |
|------|------|------|
| qdrant-client | 1.17.1 | 向量数据库 |
| chromadb | 1.5.7 | 向量存储 |
| faiss-cpu | 1.13.2 | 相似度搜索 |
| openai | 2.31.0 | OpenAI API |
| anthropic | 0.94.1 | Claude API |
| langchain | 1.2.15 | LLM 框架 |
| sentence-transformers | 5.4.0 | 句子嵌入 |
| torch | 2.11.0 | 深度学习 |
| transformers | 5.5.4 | NLP 模型 |

## V7.0.0 整合更新

### 文件同步
- 根目录 `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md` 与 `core/` 真源同步
- 移除"兼容副本"标记，直接使用真源内容

### 报告清理
- 清理旧巡检报告 (保留最近5个)
- 清理旧版本报告 (V4.3.2_Phase3_*)
- 移动空壳文件到 `archive/empty_shells/`

### JSON 契约修复
- `runtime_integrity.json`: 状态值统一为 `passed/failed/skipped`
- `skill_inverted_index.json`: 添加 `source` 和 `derived` 标注

### 技能网关修复
- `skill_adapter_gateway.py`: 支持 `skill_md` 执行器类型
- 正确处理 SKILL.md 文档型技能

### 技能分类完善
- 创建 `scripts/auto_classify_skills.py` 自动分类脚本
- 未分类技能从 46.9% 降至 11.3%
- 已分类技能达 88.7%

### 技能测试配置
- 核心技能添加 `testable`, `test_mode`, `smoke_test` 配置
- 创建测试固件目录 `tests/fixtures/`
- 可测试技能从 29.1% 提升至 35.6%
- 冒烟测试从 0% 提升至 5.8%

### 技能依赖配置
- 21 个核心技能添加 `dependencies` 字段
- 支持依赖检查和自动安装

### 技能超时配置
- 15 个技能添加自定义超时配置
- 超时范围: 30s - 180s

### 目录结构说明
- 添加 `memory_context/README.md` 明确 memory 与 memory_context 职责
- memory/ 存储会话数据，memory_context/ 存储策略文档

### 报告清理自动化
- 创建 `scripts/cleanup_reports.py` 自动清理脚本
- 支持按模式、按年龄清理和压缩

### 技能健康检查
- 创建 `scripts/skill_health_check.py` 健康检查脚本
- 检查 SKILL.md、skill.py、注册表配置、依赖配置
- 严重问题: 0, 警告: 43, 信息: 208

### 文档完善
- 创建 `MAINTENANCE_GUIDE.md` 维护指南
- 创建 `CONTRIBUTING.md` 贡献指南
- 修复断裂链接

### 版本一致性
- 统一版本号为 V7.0.0
- 更新 skill_registry.json 版本

### 门禁状态
- ✅ JSON 契约检查通过
- ✅ 唯一真源检查通过
- ✅ 层间依赖检查通过
- ✅ 仓库完整性检查通过
- ✅ 技能安全检查通过
- ✅ 架构完整性检查通过

## Git 认证

- 仓库: https://github.com/18816132863/xiaoyi-claw-omega-final.git
- Token: 见 git remote -v 输出（已配置在远程 URL 中）
- 注意: Token 不应写入文件，使用环境变量或 git credential

### 性能加速依赖
| 依赖 | 版本 | 用途 |
|------|------|------|
| numba | 0.65.0 | JIT 编译加速 |
| numpy | 1.26.4 | 向量化计算 |
| numexpr | 2.14.1 | 表达式加速 |
| bottleneck | 1.6.0 | 瓶颈优化 |

### 巡检器 V6.0.0
- 检查项: 8 项
- Workers: 8
- 目标耗时: < 6s
- 新增: Token优化检查、注入配置检查

### 模块管理
- **dependency_manager.py**: 依赖管理器，自动检测和安装依赖
- **delete_manager.py**: 删除确认模块，所有删除操作需用户确认

## 注意事项

- 受保护文件不可删除
- 使用 trash 替代 rm
- 敏感操作需确认
- Token 等敏感信息不要写入文件
- 规则检查失败会阻断门禁
- 4096 维 Embedding 已是业界最高
