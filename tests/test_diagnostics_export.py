"""测试诊断和导出"""
import pytest
from diagnostics.runtime_self_check import RuntimeSelfCheck
from diagnostics.capability_report import CapabilityReport


@pytest.mark.asyncio
async def test_self_check():
    """测试自检"""
    checker = RuntimeSelfCheck()
    result = await checker.run_all_checks()
    
    assert "success" in result
    assert "overall_status" in result
    assert "checks" in result
    assert len(result["checks"]) > 0


@pytest.mark.asyncio
async def test_capability_report():
    """测试能力报告"""
    report = CapabilityReport.generate()
    
    assert "generated_at" in report
    assert "runtime_mode" in report
    assert "capabilities" in report


def test_capability_report_markdown():
    """测试Markdown格式报告"""
    report = CapabilityReport.generate()
    md = CapabilityReport.format_markdown(report)
    
    assert "# Capability Report" in md
    assert "Runtime Mode:" in md
