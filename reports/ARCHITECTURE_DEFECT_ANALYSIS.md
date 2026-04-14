# 架构缺陷分析报告

**生成时间**: 2026-04-15
**版本**: V7.0.0

---

## 一、已修复问题

### 1. JSON 契约不一致 ✅
- **问题**: `runtime_integrity.json` 使用 `fail/partial` 而非 schema 定义的 `passed/failed/skipped`
- **修复**: 统一状态值，更新 `verify_runtime_integrity.py`

### 2. 唯一真源标注缺失 ✅
- **问题**: `skill_inverted_index.json` 未标注为派生物
- **修复**: 添加 `source` 和 `derived` 字段

### 3. 技能网关执行器类型 ✅
- **问题**: `skill_adapter_gateway.py` 无法处理 `skill_md` 类型
- **修复**: 支持 SKILL.md 文档型技能，自动查找 `skill.py`

### 4. 根目录文件不同步 ✅
- **问题**: `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md` 与 `core/` 真源不同步
- **修复**: 同步内容，移除"兼容副本"标记

---

## 二、当前缺陷

### 1. 技能测试覆盖率低 🔴 严重

| 指标 | 当前 | 目标 | 差距 |
|------|------|------|------|
| 可测试技能 | 29.1% (80/275) | 80% | -50.9% |
| 冒烟测试 | 0% (0/275) | 30% | -30% |

**影响**: 无法验证技能功能，生产风险高

**建议**:
1. 为核心技能添加 `testable: true` 和 `test_mode`
2. 创建测试固件目录 `tests/fixtures/`
3. 实现 CI 自动测试

### 2. 技能分类不完善 🟡 中等

| 分类 | 数量 | 占比 |
|------|------|------|
| other | 129 | 46.9% |
| 已分类 | 146 | 53.1% |

**影响**: 技能发现困难，路由效率低

**建议**:
1. 审查 `other` 分类技能，重新归类
2. 建立分类标准文档
3. 自动化分类建议

### 3. P2 硬编码路径 🟡 中等

| 级别 | 数量 | 风险 |
|------|------|------|
| P0 | 0 | 无 |
| P1 | 0 | 无 |
| P2 | 207 | 低 |

**影响**: 路径可移植性问题

**建议**:
1. 逐步替换为 `get_project_root()` 调用
2. 使用环境变量配置
3. 添加路径检查工具

### 4. memory 与 memory_context 职责重叠 🟡 中等

| 目录 | 内容 | 职责 |
|------|------|------|
| memory/ | 日记文件 | 会话记忆 |
| memory_context/ | 策略文档 | 记忆策略 |

**影响**: 概念混淆，维护困难

**建议**:
1. 明确边界：`memory/` 存数据，`memory_context/` 存策略
2. 合并或重命名目录
3. 更新文档说明

### 5. 报告文件累积 🟢 轻微

| 指标 | 当前 | 建议 |
|------|------|------|
| 目录大小 | 892K | < 500K |
| 文件数 | 128 | < 50 |

**影响**: 磁盘占用，查找效率

**建议**:
1. 自动清理旧报告 (保留最近10个)
2. 压缩历史报告
3. 添加清理定时任务

---

## 三、架构优化建议

### 1. 技能测试框架

```
tests/
├── fixtures/
│   ├── smoke/          # 冒烟测试固件
│   ├── integration/    # 集成测试固件
│   └── external/       # 外部测试固件
├── test_skills/        # 技能测试用例
│   ├── test_pdf.py
│   ├── test_docx.py
│   └── ...
└── conftest.py         # pytest 配置
```

### 2. 技能分类标准

| 分类 | 描述 | 示例 |
|------|------|------|
| ai | AI/LLM 相关 | llm-memory, agent-chronicle |
| search | 搜索/查询 | web-search, arxiv-search |
| document | 文档处理 | pdf, docx, pptx |
| image | 图像处理 | image-gen, ocr |
| video | 视频处理 | video-gen, video-edit |
| audio | 音频处理 | tts, whisper |
| code | 代码相关 | git, docker, ansible |
| data | 数据处理 | mysql, mongodb, excel |
| automation | 自动化 | cron, workflow |
| communication | 通讯 | email, message |
| finance | 金融 | stock, crypto |
| ecommerce | 电商 | shop, coupon |
| memory | 记忆/知识 | memory-setup, brain |
| utility | 工具类 | file-manager, backup |
| other | 未分类 | 待审查 |

### 3. 路径规范化

```python
# 推荐
from infrastructure.path_resolver import get_project_root, resolve_path

# 避免
path = "/home/sandbox/.openclaw/workspace/..."
path = "~/..."
```

---

## 四、优先级排序

| 优先级 | 问题 | 工作量 | 影响 |
|--------|------|--------|------|
| P0 | 技能测试覆盖率 | 高 | 严重 |
| P1 | 技能分类完善 | 中 | 中等 |
| P1 | memory 职责明确 | 低 | 中等 |
| P2 | P2 硬编码清理 | 高 | 低 |
| P3 | 报告清理自动化 | 低 | 轻微 |

---

## 五、下一步行动

1. **立即**: 为 top 20 核心技能添加测试
2. **本周**: 完成技能分类审查
3. **本月**: 实现 memory 目录整合
4. **持续**: P2 硬编码逐步清理

---

**报告生成**: 统一巡检器 V6.0.0
