# 兼容副本 - 真源在 core/TOOLS.md
# TOOLS.md - Tool Rules

## 联网搜索

- **默认**: xiaoyi-web-search
- **优势**: 中文优化、开箱即用

## 手机操控 (xiaoyi-gui-agent)

### 适用场景
- 需要操作手机APP界面
- 数据仅存在于APP内部
- 执行用户行为（签到、关注等）

### 执行规则
1. **禁止重复调用** - 同一任务只调用一次
2. **禁止失败重试** - 失败即终止
3. **顺序执行** - 等待结果后再调用其他工具
4. **一次性下发** - 明确APP，完成指代消解

## 技能发现 (find-skills)

当任务超出当前工具能力时使用。

## 文档转换 (xiaoyi-doc-convert)

优先使用此 skill 进行文档格式转换。

## 图像理解

- **默认**: xiaoyi-image-understanding
- **禁止**直接使用 read 工具读取图片

## 文件回传

- **默认**: send_file_to_user
- 支持本地路径和公网URL

## 定时任务 (Cron)

### 强制要求
1. **必须指定 `--channel`** (默认 xiaoyi-channel)
2. **不支持手机工具调用** - 需告知用户

### 示例
```bash
openclaw cron add "0 18 * * *" --message "提醒" --channel xiaoyi-channel
```

## Git 代码下载

- **目标目录**: `$OPENCLAW_GIT_DIR` (/home/sandbox/.openclaw/workspace/repo)

## Node.js / Python 包

- **Node**: 安装到 `$OPENCLAW_GIT_DIR/node_modules`
- **Python**: 使用 `--prefix` 安装到 `$OPENCLAW_GIT_DIR/python_libs`

## ReportLab 中文

使用 reportlab 生成 PDF 时，**必须先注册中文字体**。

## 插件安装

安装前执行 `umask 0022`，防止权限问题。

## 备份打包

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

### 使用方法

```bash
# 使用优化脚本（自动应用排除规则）
/home/sandbox/.openclaw/workspace/infrastructure/backup_optimized.sh

# 或使用排除规则文件
tar -czvf backup.tar.gz \
    --exclude-from=/home/sandbox/.openclaw/workspace/infrastructure/backup_excludes.txt \
    -C /home/sandbox .openclaw .local/bin
```

### 清理工具

```bash
# 查看可清理空间
clean-backup status

# 清理 7 天前的备份
clean-backup clean

# 激进清理
clean-backup aggressive
```

---

## 规则硬化检查

### 层间依赖检查

```bash
python scripts/check_layer_dependencies.py
```

检查显式违规：
- core/ import execution/orchestration/governance/infrastructure
- execution/ import governance
- governance/ import execution/skills

### JSON 契约检查

```bash
python scripts/check_json_contracts.py
```

校验文件：
- reports/runtime_integrity.json
- reports/quality_gate.json
- reports/release_gate.json
- reports/alerts/latest_alerts.json
- reports/remediation/approval_history.json
- reports/ops/control_plane_state.json
- reports/ops/control_plane_audit.json

### 仓库完整性检查

```bash
python scripts/check_repo_integrity.py --strict
```

包含：
- 必需文件/目录检查
- 唯一真源文件检查
- Makefile 目标检查
- 审批历史一致性检查
- 调用层间依赖检查
- 调用 JSON 契约检查

### 门禁命令

```bash
# CI 门禁
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release
```

---

## 变更影响规则

| 变更对象 | 必跑命令 |
|----------|----------|
| `skill_registry.json` | `check_repo_integrity.py --strict`<br>`run_release_gate.py premerge` |
| `execution/*` | `run_release_gate.py premerge`<br>`run_release_gate.py nightly` |
| `governance/*` | `run_release_gate.py premerge`<br>`run_release_gate.py release` |
| `approval_manager.py` | `check_repo_integrity.py --strict`<br>`run_release_gate.py nightly` |
| `control_plane*.py` | `check_repo_integrity.py --strict` |
| `core/contracts/*` | `check_json_contracts.py`<br>`check_repo_integrity.py --strict` |

---

**版本**: V3.0.0
