# CONTRIBUTING.md - 贡献指南

## 欢迎贡献

感谢你对小艺 Claw 项目的关注！本文档说明如何为项目做出贡献。

## 贡献方式

### 1. 报告问题
- 在 Issues 中搜索是否已有类似问题
- 使用问题模板创建新 Issue
- 提供详细的问题描述和复现步骤

### 2. 提交改进
- Fork 项目仓库
- 创建功能分支
- 提交 Pull Request

### 3. 完善文档
- 修复文档错误
- 补充缺失文档
- 改进文档结构

## 开发规范

### 代码风格
```yaml
code_style:
  markdown:
    - 使用标准 Markdown 格式
    - 标题层级清晰
    - 代码块指定语言
  
  json:
    - 使用 2 空格缩进
    - 保持键名一致性
    - 添加必要注释
  
  naming:
    - 文件名: UPPER_CASE.md / lower_case.json
    - 目录名: lower_case
    - ID格式: {TYPE}-{YYYY}-{NNN}
```

### 提交规范
```yaml
commit_message:
  format: "{type}: {description}"
  
  types:
    - feat: 新功能
    - fix: 修复问题
    - docs: 文档更新
    - refactor: 重构
    - test: 测试相关
    - chore: 其他修改
  
  examples:
    - "feat: 添加新的工作流模板"
    - "fix: 修复记忆冲突处理逻辑"
    - "docs: 更新维护指南"
```

## 文件结构

### 核心文件
```
workspace/
├── AGENTS.md          # 系统行为总纲
├── MEMORY.md          # 记忆系统索引
├── TOOLS.md           # 工具使用规范
├── SOUL.md            # 核心性格
├── USER.md            # 用户画像
├── HEARTBEAT.md       # 心跳任务
└── IDENTITY.md        # 身份定义
```

### 模块目录
```
workspace/
├── core/              # 核心配置
├── runtime/           # 运行时系统
├── safety/            # 安全系统
├── governance/        # 治理模块
├── evaluation/        # 评估系统
├── observability/     # 可观测性
├── optimization/      # 性能优化
├── learning/          # 学习系统
├── autonomy/          # 自主能力
├── orchestration/     # 外部编排
├── domain_agents/     # 行业专属
├── memory_quality/    # 记忆质量
├── graph/             # 知识图谱
├── resources/         # 资源治理
├── portfolio/         # 多项目治理
├── strategy/          # 策略系统
├── state/             # 状态管理
├── multiagent/        # 多代理协作
├── automation/        # 自动化
├── projects/          # 项目管理
├── experiments/       # 实验系统
├── context/           # 上下文治理
├── retrieval/         # 检索治理
├── answer/            # 答案校验
├── user_model/        # 用户目标
├── audit/             # 审计系统
├── alert/             # 告警系统
├── canary/            # 灰度发布
├── rollback/          # 回滚模块
├── release/           # 发布管理
├── quality/           # 质量管理
├── profile/           # 用户画像
├── goals/             # 目标管理
├── config/            # 配置管理
├── prompts/           # 提示管理
├── tests/             # 测试模块
├── ops/               # 运维管理
└── workflows/         # 工作流
```

## 新增模块指南

### 创建新模块
1. 在 workspace/ 下创建新目录
2. 创建模块主文件 (MODULE_NAME.md)
3. 创建配置文件 (如需要)
4. 更新 AGENTS.md 中的索引

### 模块文件模板
```markdown
# MODULE_NAME.md - 模块说明

## 目的
说明模块的目的和作用。

## 适用范围
说明模块的适用范围。

## 核心内容
模块的核心内容。

## 引用文件
- `related/file.md` - 相关文件
```

## 测试规范

### 测试类型
| 类型 | 说明 | 位置 |
|------|------|------|
| 单元测试 | 单个功能测试 | tests/ |
| 集成测试 | 模块集成测试 | tests/ |
| 回归测试 | 版本回归测试 | evaluation/ |

### 测试要求
```yaml
test_requirements:
  - 所有新功能必须有测试
  - 测试覆盖率 > 80%
  - 所有测试必须通过
  - 性能测试不退化
```

## 审核流程

### Pull Request 审核
```yaml
review_process:
  1_check:
    - 代码风格检查
    - 测试覆盖检查
    - 文档完整性检查
  
  2_review:
    - 功能正确性审核
    - 架构合理性审核
    - 安全性审核
  
  3_approve:
    - 至少 1 人审核通过
    - 所有检查通过
    - 无冲突
```

### 合并要求
```yaml
merge_requirements:
  - 所有 CI 检查通过
  - 至少 1 个审核通过
  - 无合并冲突
  - 符合提交规范
```

## 发布流程

### 版本管理
```yaml
versioning:
  format: "v{major}.{minor}.{patch}"
  
  major: 不兼容变更
  minor: 新功能
  patch: 问题修复
```

### 发布检查
```yaml
release_checklist:
  - 所有测试通过
  - 文档已更新
  - 变更日志已更新
  - 版本号已更新
```

## 社区准则

### 行为准则
- 尊重所有贡献者
- 保持专业和友善
- 接受建设性批评
- 关注对社区最有利的事情

### 沟通渠道
- Issues: 问题报告和讨论
- Pull Requests: 代码贡献
- Discussions: 一般讨论

## 许可证

本项目采用 MIT 许可证。贡献的代码将按照相同许可证授权。

## 联系方式

如有问题，请通过 Issues 联系维护团队。

---

感谢你的贡献！
