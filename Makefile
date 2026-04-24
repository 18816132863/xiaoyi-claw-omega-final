.PHONY: test verify-phase1-baseline verify-phase3-final fusion-check fusion-auto inspect verify-premerge verify-nightly verify-release daily-growth-personal daily-growth-enterprise midday-check daily-review weekly-review

# ═══════════════════════════════════════════════════════════════
# 测试（自动安装依赖）
# ═══════════════════════════════════════════════════════════════
test:
	@echo "=== 安装测试依赖 ==="
	@pip install -r requirements-test.txt -q
	@echo ""
	@echo "=== 运行测试 ==="
	@python -m pytest tests/ -q

# ═══════════════════════════════════════════════════════════════
# Phase 1 基线验证
# ═══════════════════════════════════════════════════════════════
verify-phase1-baseline:
	@echo "=== Phase 1 Baseline Verification ==="
	@echo ""
	@echo "Running integration tests..."
	@python tests/integration/test_minimum_loop.py
	@echo ""
	@echo "Running minimum loop demo..."
	@python scripts/demo_minimum_loop.py
	@echo ""
	@echo "=== Phase 1 Baseline PASSED ==="

# ═══════════════════════════════════════════════════════════════
# Phase 3 Final 验证
# ═══════════════════════════════════════════════════════════════
verify-phase3-final:
	@echo "=== Phase 3 Final Verification ==="
	@python scripts/generate_observability_reports.py
	@python scripts/generate_release_reports.py
	@python scripts/verify_phase3_final.py
	@echo ""
	@echo "=== Phase 3 Final PASSED ==="

# ═══════════════════════════════════════════════════════════════
# 融合引擎
# ═══════════════════════════════════════════════════════════════
fusion-check:
	@echo "=== 融合检查 ==="
	@python scripts/auto_fusion_hook.py

fusion-auto:
	@echo "=== 自动融合 ==="
	@python infrastructure/fusion_engine.py --execute

fusion-sync:
	@echo "=== 文档同步 ==="
	@python scripts/auto_fusion_hook.py --execute

# ═══════════════════════════════════════════════════════════════
# 统一巡检
# ═══════════════════════════════════════════════════════════════
inspect:
	@echo "=== V7.2.0 统一巡检 ==="
	@python scripts/unified_inspector_v7.py

# ═══════════════════════════════════════════════════════════════
# Metrics 生成
# ═══════════════════════════════════════════════════════════════
metrics:
	@echo "=== 生成 Metrics ==="
	@python scripts/generate_metrics.py

# ═══════════════════════════════════════════════════════════════
# 完整验证（提交前）
# ═══════════════════════════════════════════════════════════════
verify-all: verify-phase1-baseline fusion-check inspect
	@echo ""
	@echo "=== 所有验证通过 ==="

# ═══════════════════════════════════════════════════════════════
# 门禁验证 (Gate Targets)
# ═══════════════════════════════════════════════════════════════
verify-premerge:
	@echo "=== Pre-merge Gate ==="
	@python scripts/run_release_gate.py premerge
	@echo ""
	@echo "=== Pre-merge Gate PASSED ==="

verify-nightly:
	@echo "=== Nightly Gate ==="
	@python scripts/run_release_gate.py nightly
	@echo ""
	@echo "=== Nightly Gate PASSED ==="

verify-release:
	@echo "=== Release Gate ==="
	@python scripts/run_release_gate.py release
	@echo ""
	@echo "=== Release Gate PASSED ==="

# ═══════════════════════════════════════════════════════════════
# Daily Growth Loop - 日引导养成层
# ═══════════════════════════════════════════════════════════════
daily-growth-personal:
	@echo "=== Daily Growth Loop (Personal) ==="
	@python scripts/run_daily_growth_loop.py --mode personal

daily-growth-enterprise:
	@echo "=== Daily Growth Loop (Enterprise) ==="
	@python scripts/run_daily_growth_loop.py --mode enterprise

midday-check:
	@echo "=== Midday Check ==="
	@python scripts/run_midday_check.py

daily-review:
	@echo "=== End of Day Review ==="
	@python scripts/run_end_of_day_review.py

weekly-review:
	@echo "=== Weekly Growth Review ==="
	@python scripts/run_weekly_growth_review.py
