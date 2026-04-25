# 部署指南 V8.0.0

## 运行模式

**当前交付模式**: `cloud_broker_mode`

- **数据库**: PostgreSQL (Neon)
- **Broker**: Redis (Upstash)
- **Result Backend**: Redis (Upstash)

## 环境要求

- Python 3.11+
- Node.js 18+
- Git

## 环境检查命令

```bash
# 检查 Python 版本
python --version

# 检查 Node.js 版本
node --version

# 检查 Git 版本
git --version

# 检查依赖安装
pip install -r requirements.txt
```

## 配置验证命令

```bash
# 验证六层架构完整性
python scripts/check_layer_dependencies.py

# 验证 JSON 契约
python scripts/check_json_contracts.py

# 验证仓库完整性
python scripts/check_repo_integrity.py --strict

# 验证规则引擎
python scripts/run_rule_engine.py --profile premerge --save

# 验证架构巡检
python infrastructure/architecture_inspector.py
```

## 启动命令

```bash
# 启动 OpenClaw Gateway（生产入口）
openclaw gateway start

# 检查 Gateway 状态
openclaw gateway status

# 启动 Agent（开发模式）
openclaw agent run

# 启动 Agent（生产模式）
openclaw agent start
```

## 健康检查命令

```bash
# 检查 Gateway 健康状态
openclaw gateway status

# 检查数据库连接
python -c "from infrastructure.storage.repositories.task_repository import TaskRepository; print('OK')"

# 检查记忆系统
python -c "from memory_context.retrieval.retrieval_router import RetrievalRouter; print('OK')"

# 检查技能注册表
python -c "import json; json.load(open('infrastructure/inventory/skill_registry.json')); print('OK')"
```

## 冒烟测试命令

```bash
# 运行架构测试
python tests/test_architecture.py

# 运行技能注册表测试
python tests/test_skill_registry.py

# 运行 premerge 门禁
python scripts/run_release_gate.py premerge

# 运行统一巡检
python scripts/unified_inspector_v7.py
```

## 完整验证流程

```bash
# 1. 环境检查
python --version && node --version && git --version

# 2. 依赖安装
pip install -r requirements.txt

# 3. 配置验证
python scripts/check_layer_dependencies.py
python scripts/check_json_contracts.py
python scripts/check_repo_integrity.py --strict

# 4. 启动服务
openclaw gateway start

# 5. 健康检查
openclaw gateway status

# 6. 冒烟测试
python tests/test_architecture.py
python scripts/run_release_gate.py premerge
```

## 常见问题

### Q: Gateway 启动失败

```bash
# 检查端口占用
lsof -i :3000

# 检查日志
tail -f ~/.openclaw/logs/gateway.log
```

### Q: 数据库初始化失败

```bash
# 手动初始化
python infrastructure/storage/init_db.py

# 检查数据库文件
ls -la data/*.db
```

### Q: 规则检查失败

```bash
# 查看规则报告
cat reports/ops/rule_engine_report.json

# 查看例外债务
cat reports/ops/rule_exception_debt.json
```
