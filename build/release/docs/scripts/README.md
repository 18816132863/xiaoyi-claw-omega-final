# 脚本文档

## 核心脚本

### 统一巡检器
**文件**: `scripts/unified_inspector.py`

运行所有架构检查，包括：
- 变更影响分析
- 层间依赖检查
- 仓库完整性检查
- JSON 契约检查
- 技能安全检查
- 架构完整性检查

```bash
python scripts/unified_inspector.py
```

### 门禁检查
**文件**: `scripts/run_release_gate.py`

运行门禁检查，支持三种模式：
- `premerge`: 合并前检查
- `nightly`: 每日检查
- `release`: 发布检查

```bash
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release
```

### 技能健康检查
**文件**: `scripts/skill_health_check.py`

检查技能的完整性和配置正确性。

```bash
python scripts/skill_health_check.py
```

### 技能自动分类
**文件**: `scripts/auto_classify_skills.py`

根据技能描述和名称自动分类。

```bash
python scripts/auto_classify_skills.py --apply
```

### 报告清理
**文件**: `scripts/cleanup_reports.py`

自动清理旧报告。

```bash
python scripts/cleanup_reports.py
```

## 检查脚本

### JSON 契约检查
**文件**: `scripts/check_json_contracts.py`

验证 JSON 文件是否符合 schema。

```bash
python scripts/check_json_contracts.py
```

### 仓库完整性检查
**文件**: `scripts/check_repo_integrity.py`

检查仓库文件结构和唯一真源规则。

```bash
python scripts/check_repo_integrity.py
```

### 层间依赖检查
**文件**: `scripts/check_layer_dependencies.py`

检查六层架构的依赖关系。

```bash
python scripts/check_layer_dependencies.py
```

### 变更影响分析
**文件**: `scripts/check_change_impact.py`

分析代码变更的影响范围。

```bash
python scripts/check_change_impact.py
```

### 技能安全检查
**文件**: `scripts/check_skill_security.py`

检查技能的安全风险。

```bash
python scripts/check_skill_security.py
```

## 工具脚本

### 依赖管理器
**文件**: `scripts/dependency_manager.py`

自动检测和安装依赖。

### 删除管理器
**文件**: `scripts/delete_manager.py`

安全删除文件，需要用户确认。

### 自动摘要
**文件**: `scripts/auto_summarizer.py`

自动生成会话摘要。

## 使用建议

1. **日常开发**: 使用 `make verify` 运行门禁检查
2. **提交前**: 使用 `make check-all` 运行所有检查
3. **定期维护**: 使用 `make health` 检查技能健康
4. **清理空间**: 使用 `make cleanup` 清理旧报告
