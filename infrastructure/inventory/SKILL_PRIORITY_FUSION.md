# 技能优先级排序与融合策略 V1.0.0

> **唯一真源** - 技能优先级定义与新增技能融合规则

---

## 一、技能优先级排序

### P0 - 核心必需技能（立即加载）

**定义**: 系统运行必需，缺失会导致核心功能不可用

| 技能 | 类别 | 原因 |
|------|------|------|
| xiaoyi-web-search | search | 默认联网搜索 |
| xiaoyi-gui-agent | search | 手机操控核心 |
| xiaoyi-image-understanding | image | 图像理解核心 |
| xiaoyi-image-search | search | 图像搜索核心 |
| xiaoyi-doc-convert | document | 文档转换核心 |
| find-skills | search | 技能发现核心 |
| git | system | 版本控制核心 |
| cron | automation | 定时任务核心 |
| docx | document | DOCX 处理 |
| pdf | document | PDF 处理 |
| file-manager | other | 文件管理 |
| huawei-drive | other | 华为云盘核心 |

**特征**:
- `priority: "P0"`
- `status: "active"`
- `registered: true`
- `routable: true`

---

### P1 - 高频使用技能（按需加载）

**定义**: 用户常用功能，高频触发

| 技能 | 类别 | 原因 |
|------|------|------|
| xiaohongshu-all-in-one | search | 小红书运营 |
| bilibili-all-in-one | search | B站运营 |
| douyin-shop-operation | ecommerce | 抖音小店 |
| kuaishou-shop-operation | ecommerce | 快手小店 |
| dealer-leader-cooperation | ecommerce | 团长合作 |
| product-management | ecommerce | 商品管理 |
| marketing-campaign | ecommerce | 营销活动 |
| customer-service | ecommerce | 客服售后 |
| supply-chain-management | ecommerce | 供应链 |
| ecommerce-analytics | ecommerce | 数据分析 |
| platform-comparison | ecommerce | 平台对比 |
| omni-channel-ecommerce | ecommerce | 全渠道 |
| weather | other | 天气查询 |
| stock-price-query | other | 股票查询 |
| crypto | other | 加密货币 |
| hot-news-aggregator | search | 热点聚合 |
| tech-news-digest | other | 科技新闻 |

**特征**:
- `priority: "P1"`
- `status: "active"` 或 `"healthy"`

---

### P2 - 专业领域技能（延迟加载）

**定义**: 特定场景使用，专业领域

| 技能 | 类别 | 原因 |
|------|------|------|
| senior-architect | other | 架构设计 |
| senior-data-scientist | data | 数据科学 |
| senior-security | other | 安全工程 |
| ceo-advisor | other | CEO 顾问 |
| risk-management-specialist | other | 风险管理 |
| quality-documentation-manager | document | 质量文档 |
| tdd-guide | other | TDD 指导 |
| code-analysis-skills | data | 代码分析 |
| data-analysis | data | 数据分析 |
| excel-analysis | data | Excel 分析 |
| market-research | search | 市场调研 |
| research-cog | search | 深度研究 |
| deep-search-and-insight-synthesize | search | 深度搜索 |
| article-writer | search | 文章写作 |
| copywriter | other | 文案写作 |
| novel-generator | other | 小说生成 |
| story-cog | other | 故事创作 |
| poetry | search | 诗词创作 |

**特征**:
- `priority: "P2"`
- `status: "healthy"`

---

### P3 - 工具类技能（按需加载）

**定义**: 辅助工具，特定任务

| 技能 | 类别 | 原因 |
|------|------|------|
| playwright | other | 浏览器自动化 |
| web-scraper | other | 网页抓取 |
| scrapling-official | other | 自适应抓取 |
| screenshot | other | 截图 |
| camsnap | other | 摄像头 |
| video-cog | other | 视频转录 |
| video-subtitles | other | 视频字幕 |
| audio-cog | other | 音频生成 |
| image | image | 图像生成 |
| image-gen | image | AI 图像生成 |
| seedream-image_gen | image | Seedream 生成 |
| hunyuan-image | image | 混元图像 |
| wan-image-video-generation-editting | image | 万象生成 |
| chart-image | image | 图表生成 |
| pptx | other | PPT 处理 |
| ai-ppt-generator | other | AI PPT |
| markitdown | other | Markdown 转换 |
| unified-document | document | 统一文档 |
| unified-image | image | 统一图像 |
| unified-search | search | 统一搜索 |

**特征**:
- `priority: "P3"`
- `status: "healthy"`

---

### P4 - 基础设施技能（系统加载）

**定义**: 基础设施，开发者工具

| 技能 | 类别 | 原因 |
|------|------|------|
| docker | document | 容器管理 |
| ansible | other | 自动化部署 |
| terraform | other | IaC |
| mysql | other | MySQL |
| mongodb | other | MongoDB |
| sqlite | other | SQLite |
| elasticsearch | search | ES 搜索 |
| redis | other | Redis |
| api-gateway | other | API 网关 |
| command-center | other | 命令中心 |
| command-hook | other | 命令钩子 |
| clawsec-suite | other | 安全套件 |
| moltguard | other | 安全防护 |
| moltrade | other | 交易助手 |
| polymarket-trade | other | Polymarket |
| t-trading | other | 交易 |
| bitsoul-stock-quantization | other | 量化交易 |
| china-stock-analysis | data | A股分析 |
| tushare-data | data | Tushare 数据 |
| mx-stocks-screener | other | 选股器 |
| industry-stock-tracker | other | 行业追踪 |

**特征**:
- `priority: "P4"`
- `status: "healthy"`

---

### P5 - 通信与集成技能（按需加载）

**定义**: 通信、集成、平台连接

| 技能 | 类别 | 原因 |
|------|------|------|
| imap-smtp-email | communication | 邮件 |
| imsg | other | iMessage |
| discord | other | Discord |
| linkedin-api | other | LinkedIn |
| spotify-player | other | Spotify |
| sonoscli | other | Sonos |
| obsidian | other | Obsidian |
| baidu-netdisk-skills | search | 百度网盘 |
| tencent-cos-skill | search | 腾讯云 COS |
| google-maps | other | Google Maps |
| amazon-product-search-api-skill | search | 亚马逊 |
| klaviyo | other | Klaviyo |
| getnote | search | Get笔记 |
| juejin-skills | other | 掘金 |
| local_app_interconnect | search | 本地互联 |
| xiaoyi-health | other | 小艺健康 |
| xiaoyi-report | search | 研究报告 |
| xiaoyi-file-upload | other | 文件上传 |
| feishu-channel-setup | other | 飞书 |
| weixin-clawbot-setup | other | 微信 |

**特征**:
- `priority: "P5"`
- `status: "healthy"`

---

### P6 - 辅助与实验技能（最低优先级）

**定义**: 实验、辅助、低频使用

| 技能 | 类别 | 原因 |
|------|------|------|
| beginner-mode | search | 新手模式 |
| personas | other | 人格模拟 |
| best-minds | other | 最佳思维 |
| proactivity | other | 主动代理 |
| self-improving-agent | other | 自我改进 |
| openclaw-agent-optimize | other | 代理优化 |
| skill-creator | other | 技能创建 |
| skill-fusion | other | 技能融合 |
| auto-skill-upgrade | automation | 自动升级 |
| performance-upgrade | other | 性能升级 |
| topic-monitor | other | 话题监控 |
| taskr | other | 任务管理 |
| today-task | other | 今日任务 |
| planning-with-files | other | 文件规划 |
| agent-chronicle | other | 代理编年史 |
| agent-browser-clawdbot | other | 浏览器代理 |
| verified-agent-identity | other | 身份验证 |
| ontology | other | 本体论 |
| ui-design-system | system | UI 设计 |
| frontend-design-pro | other | 前端设计 |
| frontend-arch-analyzer | other | 架构分析 |
| react-best-practices | other | React 最佳实践 |
| web-design-guidelines | other | Web 设计 |
| tdd-guide | other | TDD 指导 |
| webapp-testing | other | Web 测试 |
| openai-whisper-api | other | Whisper API |
| beauty-generation-api | other | 美颜生成 |
| ai-picture-book | other | AI 绘本 |
| pexoai-agent | other | Pexo AI |
| video-agent | other | 视频代理 |
| pixverse | other | Pixverse |
| admapix | other | Admapix |
| clawdhub | other | ClawdHub |
| dingtalk-ai-table | search | 钉钉表格 |
| keyword-research | search | 关键词研究 |
| technical-seo-checker | other | SEO 检查 |
| good-txt-to-hwreader | search | TXT 转换 |
| paper-daily | search | 论文日报 |
| fortune-master-ultimate | other | 命理顾问 |
| poetry | search | 诗词 |
| nano-pdf | document | Nano PDF |
| ocr-local | other | 本地 OCR |
| sheet-cog | other | 表格处理 |
| docs-cog | document | 文档处理 |
| productivity | other | 生产力 |
| skill-finder | search | 技能查找 |
| skillhub-preference | other | 技能偏好 |
| skill-safe-install | search | 安全安装 |
| memory-setup | other | 记忆设置 |
| llm-memory-integration | other | 记忆集成 |

**特征**:
- `priority: "P6"` 或无优先级
- `status: "healthy"`

---

## 二、新增内容融合流程

### 核心原则

**所有新增内容（技能/模块/文件/目录）必须先融合到六层架构中，禁止在架构外新增任何内容。**

```
❌ 错误：新增文件 → 放在任意位置 → 以后再整理
✅ 正确：新增文件 → 确定架构层级 → 放入对应目录 → 更新架构文档
```

---

### 第一步：架构融合（必须先执行）

**适用范围**:
- 新增技能 (`skills/`)
- 新增模块 (`*/模块名/`)
- 新增文件 (任何 `.py`/`.md`/`.json` 等)
- 新增目录 (任何子目录)

**架构层级映射**:

| 内容类型 | 架构层级 | 目录 | 示例 |
|----------|----------|------|------|
| 身份/规则/标准 | L1 Core | `core/` | SOUL.md, TOOLS.md |
| 记忆/搜索/知识库 | L2 Memory Context | `memory_context/` | unified_search.py |
| 编排/工作流/路由 | L3 Orchestration | `orchestration/` | task_engine.py |
| 执行/网关/技能 | L4 Execution | `execution/`, `skills/` | skill_gateway.py |
| 安全/审计/合规 | L5 Governance | `governance/` | security.py |
| 基础设施/工具链 | L6 Infrastructure | `infrastructure/` | path_resolver.py |

**架构融合检查清单**:

```
□ 确定内容所属层级 (L1-L6)
□ 确定目标目录（必须在六层目录内）
□ 检查是否与现有内容冲突
□ 确定依赖关系
□ 确定被依赖关系
□ 更新架构文档 (core/ARCHITECTURE.md)
□ 更新受保护文件列表（如需要）
□ 验证层级调用规则
```

**架构融合流程**:

```
1. 分析内容功能 → 确定主要职责
2. 匹配架构层级 → L1/L2/L3/L4/L5/L6
3. 确定目标目录 → 必须在六层目录内
4. 检查层级边界 → 不越界、不重复
5. 创建文件/目录 → 放入对应层级
6. 注册到架构 → 更新 ARCHITECTURE.md
7. 验证层级调用 → 符合调用规则
8. 进入第二步 → 技能融合策略（仅技能）
```

**禁止行为**:

```
❌ 在项目根目录直接新增文件
❌ 在六层目录外新增目录
❌ 新增后不更新架构文档
❌ 新增后拖着不整理
❌ 创建临时目录不归档
```

**层级调用规则**:

```
请求流: 用户请求 → L1解析 → L3路由 → L4执行 → L5验证 → 返回结果
保护流: 删除请求 → L5文件保护 → 人工确认 → L6执行 → L5审计日志
记忆流: L1触发词 → L2统一搜索 → L3编排 → L4执行 → L2存储结果
巡检流: 定时触发 → L5巡检 → L6注册表 → L4技能健康检查 → L5报告
```

**架构融合示例**:

```json
{
  "name": "new-ecommerce-analytics",
  "type": "skill",
  "layer": "L4",
  "layer_name": "Execution",
  "target_directory": "skills/ecommerce-analytics/",
  "layer_reason": "电商数据分析执行器",
  "dependencies": {
    "L2": ["unified_search"],
    "L3": ["task_engine"],
    "L4": ["skill_gateway"]
  },
  "dependents": {
    "L5": ["quality_gate"]
  },
  "files": [
    "skills/ecommerce-analytics/SKILL.md",
    "skills/ecommerce-analytics/scripts/analytics.py"
  ]
}
```

**新增文件示例**:

```json
{
  "name": "new_validator.py",
  "type": "file",
  "layer": "L5",
  "layer_name": "Governance",
  "target_directory": "governance/validators/",
  "layer_reason": "数据校验器，属于治理层",
  "dependencies": {
    "L5": ["security.py", "audit.py"]
  }
}
```

---

### 第二步：技能融合策略

**前置条件**: 第一步架构融合完成

**适用范围**: 仅适用于新增技能，其他文件类型跳过此步骤

### 策略 A: 阶梯化融合（默认）

**适用场景**: 新增独立技能，无冲突

**流程**:
```
1. 安装技能 → skills/<skill-name>/
2. 自动注册 → infrastructure/inventory/skill_registry.json
3. 分配优先级 → 根据类别自动分配 P0-P6
4. 更新反向索引 → infrastructure/inventory/skill_inverted_index.json
5. 静默完成 → 不通知用户
```

**优先级自动分配规则**:
| 类别 | 默认优先级 |
|------|-----------|
| xiaoyi-* | P0 |
| ecommerce | P1 |
| search | P2 |
| data | P2 |
| image | P3 |
| document | P3 |
| automation | P4 |
| system | P4 |
| communication | P5 |
| other | P6 |

---

### 策略 B: 替换融合

**适用场景**: 新技能替代旧技能，功能重叠

**触发条件**:
- 新技能名称包含 `-v2`、`-next`、`-pro`
- 新技能与现有技能功能完全重叠
- 用户明确要求替换

**流程**:
```
1. 检测冲突 → 比较功能描述
2. 标记旧技能 → status: "deprecated"
3. 迁移配置 → 复制 triggers、dependencies
4. 注册新技能 → 继承优先级
5. 更新反向索引 → 重定向触发词
6. 静默完成 → 不通知用户
```

**示例**:
```json
// 旧技能
{
  "name": "old-search",
  "status": "deprecated",
  "replaced_by": "new-search-v2"
}

// 新技能
{
  "name": "new-search-v2",
  "replaces": "old-search",
  "priority": "P0"  // 继承旧技能优先级
}
```

---

### 策略 C: 合并融合

**适用场景**: 多个技能合并为一个统一技能

**触发条件**:
- 多个技能功能高度重叠
- 存在 `unified-*` 类型技能
- 用户明确要求合并

**流程**:
```
1. 识别候选 → 检测功能重叠
2. 创建统一入口 → unified-<category>
3. 标记旧技能 → status: "merged"
4. 设置回退 → fallback 字段
5. 更新反向索引 → 统一触发词
6. 静默完成 → 不通知用户
```

**示例**:
```json
// 被合并的技能
{
  "name": "pdf-convert",
  "status": "merged",
  "merged_into": "unified-document"
}

// 统一技能
{
  "name": "unified-document",
  "merges": ["pdf-convert", "docx-convert", "image-convert"],
  "priority": "P0"
}
```

---

### 策略 D: 依赖融合

**适用场景**: 新技能依赖现有技能

**触发条件**:
- 新技能 `dependencies` 字段非空
- 依赖的技能已存在

**流程**:
```
1. 检查依赖 → 验证 dependencies 列表
2. 安装缺失依赖 → 自动安装
3. 注册新技能 → 记录依赖关系
4. 更新依赖图 → infrastructure/inventory/dependency_graph.json
5. 静默完成 → 不通知用户
```

**示例**:
```json
{
  "name": "advanced-ecommerce-analytics",
  "dependencies": ["xiaoyi-web-search", "data-analysis", "excel-analysis"],
  "priority": "P1"
}
```

---

## 三、静默融合规则

### 自动静默条件

以下情况**自动静默**，不通知用户：

1. **新增独立技能** - 无冲突，无依赖
2. **版本升级** - 同技能新版本
3. **依赖安装** - 自动安装依赖技能
4. **优先级调整** - 自动调整优先级
5. **索引更新** - 更新反向索引

### 需要通知的情况

以下情况**需要通知**用户：

1. **替换旧技能** - 功能变更
2. **合并技能** - 多合一
3. **删除技能** - 移除功能
4. **依赖缺失** - 无法自动安装
5. **冲突检测** - 功能冲突需选择

---

## 四、融合执行器

### 自动融合脚本

**路径**: `infrastructure/fusion/skill_fusion_engine.py`

**功能**:
- 自动检测新技能
- 自动分配优先级
- 自动处理冲突
- 自动更新注册表
- 自动更新反向索引

**命令**:
```bash
# 静默融合新技能
python infrastructure/fusion/skill_fusion_engine.py --silent

# 检查融合状态
python infrastructure/fusion/skill_fusion_engine.py --status

# 强制替换
python infrastructure/fusion/skill_fusion_engine.py --replace <old> <new>

# 强制合并
python infrastructure/fusion/skill_fusion_engine.py --merge <skill1,skill2> <unified>
```

---

## 五、优先级动态调整

### 使用频率调整

**规则**:
- 连续 7 天使用 → 优先级 +1
- 连续 30 天未使用 → 优先级 -1
- 单日使用 >10 次 → 优先级 +1

**上限**: P0
**下限**: P6

### 用户偏好调整

**规则**:
- 用户明确指定 → 固定优先级
- 用户收藏技能 → 优先级 +1
- 用户删除技能 → 标记 deprecated

---

## 六、版本历史

- V1.0.0: 初始版本，定义优先级排序与融合策略

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-13
