.PHONY: verify-phase1-baseline verify-phase3-final fusion-check fusion-auto inspect verify-premerge verify-nightly verify-release

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
