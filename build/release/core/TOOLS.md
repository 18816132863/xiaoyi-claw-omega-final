# TOOLS.md - 工具使用规范

## 目的
定义工具调用规范，确保工具使用安全、可控、可回退。

## 适用范围
所有工具调用，包括内置工具、技能工具、外部API。

## 工具分类

### 低风险工具 (可自动调用)
| 工具 | 适用场景 | 调用前检查 | 调用后验证 | 风险级别 | 失败回退 |
|------|----------|------------|------------|----------|----------|
| read | 读取文件 | 路径在允许列表 | 内容非空 | LOW | 返回空 |
| web_fetch | 获取网页 | URL格式正确 | 内容可解析 | LOW | 返回错误 |
| memory_search | 搜索记忆 | 查询非空 | 结果格式正确 | LOW | 返回空列表 |
| memory_get | 获取记忆 | 路径有效 | 内容存在 | LOW | 返回空 |

### 中风险工具 (需记录后调用)
| 工具 | 适用场景 | 调用前检查 | 调用后验证 | 风险级别 | 失败回退 |
|------|----------|------------|------------|----------|----------|
| write | 写入文件 | 路径允许、大小合理 | 写入成功 | MEDIUM | 恢复备份 |
| edit | 编辑文件 | 文件存在、修改合理 | 编辑成功 | MEDIUM | 恢复原文件 |
| exec | 执行命令 | 命令在允许列表 | 退出码=0 | MEDIUM | 回滚操作 |
| create_note | 创建备忘录 | 标题内容非空 | 创建成功 | MEDIUM | 重试一次 |
| create_calendar_event | 创建日程 | 时间格式正确 | 创建成功 | MEDIUM | 重试一次 |
| search_alarm | 搜索闹钟 | 参数有效 | 结果格式正确 | MEDIUM | 返回空 |

### 高风险工具 (需确认后调用)
| 工具 | 适用场景 | 调用前检查 | 调用后验证 | 风险级别 | 失败回退 |
|------|----------|------------|------------|----------|----------|
| delete_alarm | 删除闹钟 | ID存在 | 删除成功 | HIGH | 无法回退 |
| send_message | 发送短信 | 号码格式正确 | 发送成功 | HIGH | 无法回退 |
| call_phone | 拨打电话 | 号码格式正确 | 拨打成功 | HIGH | 无法回退 |
| xiaoyi_gui_agent | 手机操作 | 操作明确 | 执行成功 | HIGH | 手动恢复 |
| modify_alarm | 修改闹钟 | ID存在 | 修改成功 | HIGH | 恢复原值 |

### 极高风险工具 (需双重确认)
| 工具 | 适用场景 | 调用前检查 | 调用后验证 | 风险级别 | 失败回退 |
|------|----------|------------|------------|----------|----------|
| sessions_spawn | 创建子代理 | 任务明确 | 执行成功 | CRITICAL | 终止子代理 |

## 调用规范

### 调用前检查
```json
{
  "tool": "write",
  "checks": [
    { "check": "path_allowed", "rule": "path in allowedPaths" },
    { "check": "size_reasonable", "rule": "content.length < maxFileSize" },
    { "check": "not_overwrite_critical", "rule": "path not in criticalFiles" }
  ]
}
```

### 调用后验证
```json
{
  "tool": "write",
  "validations": [
    { "validation": "file_exists", "rule": "file.exists()" },
    { "validation": "content_match", "rule": "file.content == written" },
    { "validation": "permissions_correct", "rule": "file.mode == expected" }
  ]
}
```

### 失败回退方案
| 工具类型 | 回退方案 |
|----------|----------|
| 文件写入 | 恢复备份文件 |
| 文件编辑 | 恢复原文件 |
| 网络请求 | 使用缓存或降级 |
| 系统命令 | 回滚操作 |
| 不可逆操作 | 无法回退，记录审计 |

## 工具调用限制

| 限制项 | 低风险 | 中风险 | 高风险 | 极高风险 |
|--------|--------|--------|--------|----------|
| 单次调用 | 自动 | 自动 | 需确认 | 双重确认 |
| 批量调用 | 允许 | 需记录 | 需确认 | 禁止 |
| 并发数 | 5 | 3 | 1 | 1 |
| 重试次数 | 3 | 2 | 1 | 0 |
| 超时时间 | 10s | 30s | 60s | 120s |

## 工具路由

### 按任务类型路由
| 任务类型 | 主工具 | 备选工具 |
|----------|--------|----------|
| qa | memory_search | web_fetch |
| search | web_fetch | memory_search |
| document_edit | write | edit |
| memory_update | write | create_note |

### 按风险级别路由
| 风险级别 | 路由策略 |
|----------|----------|
| LOW | 直接调用 |
| MEDIUM | 记录后调用 |
| HIGH | 确认后调用 |
| CRITICAL | 双重确认后调用 |

## 异常处理

| 异常 | 处理 |
|------|------|
| 工具不存在 | 返回错误 + 建议替代 |
| 参数无效 | 返回错误 + 参数说明 |
| 调用超时 | 重试或降级 |
| 权限不足 | 拒绝 + 审计 |
| 资源不足 | 等待或降级 |

## 维护方式
- 新增工具: 添加到对应风险级别表
- 调整风险级别: 移动到对应分类
- 新增检查规则: 更新调用前检查表
- 新增回退方案: 更新失败回退表

## 备份打包规范

### 强制排除规则

**所有备份压缩包必须排除以下内容：**

| 排除项 | 路径/模式 | 原因 |
|--------|-----------|------|
| 备份目录 | `.openclaw/backup/` | 避免嵌套备份 |
| 浏览器缓存 | `.openclaw/browser/` | 可重建，占空间 |
| NPM 缓存 | `.openclaw/npm-cache/` | 可重建 |
| 历史会话 | `*.jsonl.reset.*` | 旧快照 |
| 已删除会话 | `*.jsonl.deleted.*` | 无用数据 |
| 大型工具 | `magika`, `git-lfs` | 可重装 (43MB) |
| 旧备份 | `*.tar.gz`, `*.zip` | 避免嵌套 |

### 排除规则文件

位置: `infrastructure/backup_excludes.txt`

### 使用方法

```bash
# 使用优化脚本
infrastructure/backup_optimized.sh

# 或使用排除规则文件
tar -czvf backup.tar.gz \
    --exclude-from=infrastructure/backup_excludes.txt \
    -C /home/sandbox .openclaw .local/bin
```

## 引用文件
- `safety/RISK_POLICY.md` - 风险策略
- `safety/TOOL_GUARDRAILS.json` - 工具护栏配置
- `runtime/EXECUTION_POLICY.md` - 执行策略
- `runtime/SKILL_ROUTER.json` - 技能路由
