# 定时任务需求分析

## 📊 当前已有定时任务

### 1. 心跳任务（每30分钟）
- ✅ 自动 Git 同步
- ✅ 自动备份上传
- ✅ 自动触发器
- ✅ 永久守护器刷新

### 2. 自动触发场景
- ✅ 新增 Python 文件 → 技能安全检查
- ✅ Core 文件变更 → 架构巡检
- ✅ Governance 文件变更 → 规则检查
- ✅ 每日首次启动 → 日引导检查
- ✅ 每周首次启动 → 周复盘
- ✅ 每天 09:00 → 健康提醒
- ✅ 每天 18:00 → 工作总结
- ✅ 周一 09:00 → 技能报告

---

## 🔍 潜在需要定时的任务

### 1. 夜间巡检 ⏰
**脚本**: `scripts/run_nightly_audit.py`

**建议触发时间**: 每天 02:00

**功能**:
- 运行 nightly 门禁
- 与上次结果比较
- 检测强回归/弱回归
- 生成审计报告

**优先级**: 高

---

### 2. 报告清理 ⏰
**脚本**: `scripts/cleanup_reports.py`

**建议触发时间**: 每天 03:00

**功能**:
- 清理旧报告
- 保留最近 N 个
- 压缩超过 30 天的报告
- 释放磁盘空间

**优先级**: 中

---

### 3. 技能健康检查 ⏰
**脚本**: `scripts/skill_health_check.py`

**建议触发时间**: 每周一 10:00

**功能**:
- 检查技能完整性
- 检查配置正确性
- 生成健康报告
- 发现潜在问题

**优先级**: 中

---

### 4. 全面备份 ⏰
**脚本**: `scripts/full_backup.py`

**建议触发时间**: 每周日 03:00

**功能**:
- 备份核心配置
- 备份规则注册表
- 备份技能注册表
- 备份记忆数据
- 备份报告历史

**优先级**: 高

---

### 5. AI API 状态检查 ⏰
**脚本**: `scripts/check_ai_apis.py`

**建议触发时间**: 每天 08:00

**功能**:
- 检查 AI 模型 API 配置
- 验证 API 密钥有效性
- 提醒配置缺失
- 确保服务可用

**优先级**: 低

---

### 6. 依赖更新检查 ⏰
**脚本**: `scripts/dependency_manager.py`

**建议触发时间**: 每周一 08:00

**功能**:
- 检查依赖更新
- 检测安全漏洞
- 生成更新建议
- 保持依赖最新

**优先级**: 中

---

### 7. 记忆清理 ⏰
**建议触发时间**: 每月 1 日 03:00

**功能**:
- 清理过期记忆
- 压缩历史记忆
- 优化向量存储
- 释放存储空间

**优先级**: 低

---

### 8. 性能监控 ⏰
**建议触发时间**: 每小时

**功能**:
- 监控系统性能
- 记录资源使用
- 检测异常情况
- 生成性能报告

**优先级**: 中

---

## 📋 建议新增的定时任务

### 高优先级

#### 1. 夜间巡检 ✨
```json
{
  "id": "nightly_audit",
  "name": "夜间巡检",
  "trigger": "time:daily:02:00",
  "action": "run_nightly_audit",
  "command": ["python", "scripts/run_nightly_audit.py"],
  "enabled": true,
  "priority": "high"
}
```

#### 2. 全面备份 ✨
```json
{
  "id": "full_backup",
  "name": "全面备份",
  "trigger": "time:weekly:sunday:03:00",
  "action": "run_full_backup",
  "command": ["python", "scripts/full_backup.py"],
  "enabled": true,
  "priority": "high"
}
```

---

### 中优先级

#### 3. 报告清理 ✨
```json
{
  "id": "report_cleanup",
  "name": "报告清理",
  "trigger": "time:daily:03:00",
  "action": "cleanup_reports",
  "command": ["python", "scripts/cleanup_reports.py"],
  "enabled": true,
  "priority": "medium"
}
```

#### 4. 技能健康检查 ✨
```json
{
  "id": "skill_health_check",
  "name": "技能健康检查",
  "trigger": "time:weekly:monday:10:00",
  "action": "check_skill_health",
  "command": ["python", "scripts/skill_health_check.py"],
  "enabled": true,
  "priority": "medium"
}
```

#### 5. 依赖更新检查 ✨
```json
{
  "id": "dependency_check",
  "name": "依赖更新检查",
  "trigger": "time:weekly:monday:08:00",
  "action": "check_dependencies",
  "command": ["python", "scripts/dependency_manager.py", "--check"],
  "enabled": true,
  "priority": "medium"
}
```

---

### 低优先级

#### 6. AI API 状态检查
```json
{
  "id": "ai_api_check",
  "name": "AI API 状态检查",
  "trigger": "time:daily:08:00",
  "action": "check_ai_apis",
  "command": ["python", "scripts/check_ai_apis.py"],
  "enabled": true,
  "priority": "low"
}
```

#### 7. 记忆清理
```json
{
  "id": "memory_cleanup",
  "name": "记忆清理",
  "trigger": "time:monthly:1st:03:00",
  "action": "cleanup_memory",
  "command": ["python", "scripts/cleanup_memory.py"],
  "enabled": true,
  "priority": "low"
}
```

---

## 📊 定时任务总览

| 任务 | 触发时间 | 优先级 | 状态 |
|------|----------|--------|------|
| 夜间巡检 | 每天 02:00 | 高 | ⏳ 待实现 |
| 全面备份 | 周日 03:00 | 高 | ⏳ 待实现 |
| 报告清理 | 每天 03:00 | 中 | ⏳ 待实现 |
| 技能健康检查 | 周一 10:00 | 中 | ⏳ 待实现 |
| 依赖更新检查 | 周一 08:00 | 中 | ⏳ 待实现 |
| AI API 检查 | 每天 08:00 | 低 | ⏳ 待实现 |
| 记忆清理 | 每月 1 日 | 低 | ⏳ 待实现 |

---

## 🎯 实施建议

### 第一阶段（高优先级）
1. ✅ 夜间巡检
2. ✅ 全面备份

### 第二阶段（中优先级）
3. ✅ 报告清理
4. ✅ 技能健康检查
5. ✅ 依赖更新检查

### 第三阶段（低优先级）
6. ✅ AI API 检查
7. ✅ 记忆清理

---

**更新时间**: 2026-04-19 03:55
**版本**: V1.0.0
