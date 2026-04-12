# OpenClaw Makefile

.PHONY: verify-premerge verify-nightly verify-release

verify-premerge:
	@python scripts/run_release_gate.py premerge

verify-nightly:
	@python scripts/run_release_gate.py nightly

verify-release:
	@python scripts/run_release_gate.py release

# 快捷命令
premerge: verify-premerge
nightly: verify-nightly
release: verify-release
