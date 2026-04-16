.PHONY: verify-phase1-baseline

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
