# 系统维护指南

## 日常维护

### 1. 巡检检查
```bash
python scripts/unified_inspector.py
```

### 2. 门禁检查
```bash
python scripts/run_release_gate.py premerge
```

### 3. 报告清理
```bash
python scripts/cleanup_reports.py
```

## 定期维护

### 每周
- 检查技能健康状态
- 清理旧报告
- 审查异常规则

### 每月
- 更新依赖版本
- 审查技能分类
- 检查安全配置

## 故障排查

### 门禁失败
1. 检查 JSON 契约: `python scripts/check_json_contracts.py`
2. 检查仓库完整性: `python scripts/check_repo_integrity.py`
3. 检查层间依赖: `python scripts/check_layer_dependencies.py`

### 技能加载失败
1. 检查 SKILL.md 是否存在
2. 检查 skill_registry.json 配置
3. 检查 executor_type 是否正确

## 备份恢复

### 备份
```bash
infrastructure/backup_optimized.sh
```

### 恢复
```bash
tar -xzvf backup.tar.gz -C /home/sandbox
```

## 联系方式

- GitHub: https://github.com/openclaw/openclaw
- Discord: https://discord.com/invite/clawd
