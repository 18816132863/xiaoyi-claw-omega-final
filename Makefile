.PHONY: verify-phase1-baseline fusion-check fusion-auto inspect

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
# 融合引擎
# ═══════════════════════════════════════════════════════════════
fusion-check:
	@echo "=== 融合检查 ==="
	@python scripts/auto_fusion_hook.py

fusion-auto:
	@echo "=== 自动融合 ==="
	@python infrastructure/fusion_engine.py --execute

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
