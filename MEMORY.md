# MEMORY.md - 长期记忆

此文件用于存储跨会话的重要信息、决策和上下文。

## 项目状态

- **版本**: V6.0.0
- **状态**: 全面整合完成
- **更新时间**: 2026-04-14

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

## V6.0.0 新增/更新

### 技能注册表
- `infrastructure/inventory/skill_registry.json`: V5.0.0，275 个技能
- `infrastructure/inventory/skill_inverted_index.json`: 倒排索引

### 统一巡检器
- `scripts/unified_inspector.py`: V5.0.0
- 6 项检查，并行执行

### 技能安全识别
- `scripts/check_skill_security.py`: V5.0.0
- 白名单机制，误报抑制

### 架构文档
- `core/ARCHITECTURE.md`: V6.0.0，技能生态章节

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



### 巡检器 V5.0.0
- 检查项: 8 项
- Workers: 8
- 目标耗时: < 6s
- 新增: Token优化检查、注入配置检查

## 注意事项

- 受保护文件不可删除
- 使用 trash 替代 rm
- 敏感操作需确认
- Token 等敏感信息不要写入文件
- 规则检查失败会阻断门禁
- 4096 维 Embedding 已是业界最高
