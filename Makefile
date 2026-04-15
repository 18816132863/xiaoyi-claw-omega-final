# OpenClaw Makefile
# 项目管理和常用命令

.PHONY: help verify test clean lint install format check-all

# 默认目标
help:
	@echo "OpenClaw 工作空间管理"
	@echo ""
	@echo "使用方法: make <目标>"
	@echo ""
	@echo "目标:"
	@echo "  verify      运行门禁检查"
	@echo "  test        运行测试"
	@echo "  clean       清理临时文件"
	@echo "  lint        代码检查"
	@echo "  format      代码格式化"
	@echo "  install     安装依赖"
	@echo "  check-all   运行所有检查"
	@echo "  health      技能健康检查"
	@echo "  classify    技能自动分类"
	@echo "  cleanup     清理旧报告"

# 门禁检查
verify:
	@echo "运行门禁检查..."
	python scripts/run_release_gate.py premerge

# 测试
test:
	@echo "运行测试..."
	python -m pytest tests/ -v

# 清理
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ 2>/dev/null || true

# 代码检查
lint:
	@echo "运行代码检查..."
	python -m ruff check scripts/ infrastructure/ execution/ governance/ orchestration/ || true

# 代码格式化
format:
	@echo "格式化代码..."
	python -m black scripts/ infrastructure/ execution/ governance/ orchestration/ || true

# 安装依赖
install:
	@echo "安装依赖..."
	pip install -r requirements.txt

# 运行所有检查
check-all: clean lint verify test
	@echo "所有检查完成!"

# 技能健康检查
health:
	@echo "技能健康检查..."
	python scripts/skill_health_check.py

# 技能自动分类
classify:
	@echo "技能自动分类..."
	python scripts/auto_classify_skills.py --apply

# 清理旧报告
cleanup:
	@echo "清理旧报告..."
	python scripts/cleanup_reports.py

# 统一巡检
inspect:
	@echo "运行统一巡检..."
	python scripts/unified_inspector.py

# 快速检查
quick:
	@echo "快速检查..."
	python scripts/check_repo_integrity.py

# 门禁检查 - premerge
verify-premerge:
	@echo "运行 premerge 门禁..."
	python scripts/run_release_gate.py premerge

# 门禁检查 - nightly
verify-nightly:
	@echo "运行 nightly 门禁..."
	python scripts/run_release_gate.py nightly

# 门禁检查 - release
verify-release:
	@echo "运行 release 门禁..."
	python scripts/run_release_gate.py release

# 完整备份
backup:
	@echo "创建备份..."
	infrastructure/backup_optimized.sh

# Git 同步
sync:
	@echo "Git 同步..."
	python infrastructure/auto_git.py sync "自动提交"

# 查看状态
status:
	@echo "项目状态..."
	python scripts/unified_inspector.py
	@echo ""
	@echo "技能健康:"
	python scripts/skill_health_check.py

# 一键满验收
verify-all-final:
	@echo "=== 开始一键满验收 ==="
	@echo ""
	@echo "1. 检查仓库完整性..."
	python scripts/check_repo_integrity.py --strict
	@echo ""
	@echo "2. 运行 premerge 规则引擎..."
	python scripts/run_rule_engine.py --profile premerge --save
	@echo ""
	@echo "3. 运行 premerge 门禁..."
	python scripts/run_release_gate.py premerge
	@echo ""
	@echo "4. 运行 nightly 规则引擎..."
	python scripts/run_rule_engine.py --profile nightly --save
	@echo ""
	@echo "5. 运行 nightly 门禁..."
	python scripts/run_release_gate.py nightly
	@echo ""
	@echo "6. 运行 release 规则引擎..."
	python scripts/run_rule_engine.py --profile release --save
	@echo ""
	@echo "7. 运行 release 门禁..."
	python scripts/run_release_gate.py release
	@echo ""
	@echo "8. 快速检查..."
	python scripts/check_repo_integrity.py
	@echo ""
	@echo "=== 生成最终验收包 ==="
	python scripts/generate_final_verification_bundle.py
	@echo ""
	@echo "=== 一键满验收完成 ==="
