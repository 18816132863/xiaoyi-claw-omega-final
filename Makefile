.PHONY: verify-phase1-baseline verify-phase3-final fusion-check fusion-auto inspect

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
	@python tests/integration/test_minimum_loop.py
	@python scripts/demo_minimum_loop.py
	@$(MAKE) verify-phase1-baseline
	@python tests/integration/test_phase3_group2_final.py
	@python tests/integration/test_recovery_chain.py
	@python tests/integration/test_skill_platform.py
	@python tests/integration/test_skill_platform_main_chain.py
	@python tests/integration/test_memory_context_kernel.py
	@python tests/benchmarks/task_success_bench.py
	@python tests/benchmarks/skill_latency_bench.py
	@python tests/benchmarks/memory_retrieval_bench.py
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
