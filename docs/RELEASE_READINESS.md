# 发布就绪检查

## 版本
- V8.4.0 最终发布版
- 日期: 2026-04-24

## 一、发布前检查项

### 1.1 测试检查

```bash
# 全量测试
python -m pytest -q

# 预期: 全绿，无失败
```

### 1.2 演示检查

```bash
# 初始化演示环境
python scripts/demo_bootstrap.py

# 运行一键演示
bash scripts/demo_run_all.sh

# 预期: 所有命令成功执行，输出非空
```

### 1.3 发布检查

```bash
# 发布检查
python scripts/release_check.py

# 技能上传前检查
python scripts/skill_preflight_check.py

# 安全检查
python scripts/security_sanity_check.py

# 预期: 所有检查通过
```

### 1.4 打包检查

```bash
# 打包
python scripts/package_release.py --format tar.gz

# 预期: 生成发布包，无缓存文件
```

## 二、发布物清单

| # | 项目 | 说明 |
|---|------|------|
| 1 | 代码 | scripts/, platform_adapter/, capabilities/ |
| 2 | 配置 | config/ |
| 3 | 测试 | tests/ |
| 4 | 文档 | *.md, docs/ |
| 5 | 技能 | skills/ |
| 6 | 报告 | FINAL_RELEASE_READINESS_REPORT.txt |

## 三、排除项

以下内容不包含在发布包中：

- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`
- `*.pyo`
- `node_modules/`
- `.venv/`
- `.git/`
- `logs/`
- `backups/`
- `demo_outputs/`
- `reports/` (运行时生成)

## 四、回滚办法

### 4.1 版本回滚

```bash
# 解压旧版本
tar -xzvf release_v8.3.0_YYYYMMDD_HHMMSS.tar.gz

# 替换当前版本
rm -rf /path/to/current
mv release /path/to/current
```

### 4.2 数据库回滚

```bash
# 从备份恢复
cp backups/platform_invocations_YYYYMMDD.json data/

# 重新初始化
python scripts/seed_platform_invocations.py --preset demo_standard --reset-before-seed
```

## 五、发布流程

### 5.1 标准流程

```
1. 代码冻结
   ↓
2. 运行全量测试
   ↓
3. 运行发布检查
   ↓
4. 运行技能上传前检查
   ↓
5. 运行安全检查
   ↓
6. 打包
   ↓
7. 验证发布包
   ↓
8. 上传
```

### 5.2 快速流程

```bash
# 一键执行所有检查
bash scripts/ci_local.sh

# 打包
python scripts/package_release.py --format tar.gz
```

## 六、发布后验证

### 6.1 基本验证

```bash
# 解压发布包
tar -xzvf release_v8.4.0_*.tar.gz

# 运行演示
python scripts/demo_bootstrap.py
```

### 6.2 完整验证

```bash
# 运行 CI
bash scripts/ci_local.sh
```

## 七、注意事项

1. **不要提交敏感信息**: authCode、真实手机号等
2. **不要提交缓存文件**: __pycache__、.pytest_cache 等
3. **不要提交运行时数据**: logs、backups、demo_outputs 等
4. **确保文档一致**: 文档示例与实际输出一致
5. **确保测试通过**: 所有测试必须通过
