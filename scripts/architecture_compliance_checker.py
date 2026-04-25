#!/usr/bin/env python3
"""
架构遵循检查器 - V2.0.0

职责：
1. 检查任务处理是否遵循六层架构
2. 记录执行轨迹
3. 检测违规行为
4. 生成合规报告
5. V2.0.0: 强制执行机制，违规阻断

使用方式：
- python scripts/architecture_compliance_checker.py --check
- python scripts/architecture_compliance_checker.py --report
- 在代码中调用: start_task(), mark_layer_completed(), end_task()
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class Layer(Enum):
    """架构层级"""
    L1_CORE = "L1_core"
    L2_MEMORY = "L2_memory"
    L3_ORCHESTRATION = "L3_orchestration"
    L4_EXECUTION = "L4_execution"
    L5_GOVERNANCE = "L5_governance"
    L6_INFRASTRUCTURE = "L6_infrastructure"


class ViolationSeverity(Enum):
    """违规严重程度"""
    CRITICAL = "CRITICAL"  # 跳过 L1 Core，立即终止
    HIGH = "HIGH"          # 跳过 L2/L3，警告并补充
    MEDIUM = "MEDIUM"      # 跳过 L4/L5/L6，警告并修正
    LOW = "LOW"            # 缺少轨迹，记录


@dataclass
class LayerState:
    """层级状态"""
    status: str = "pending"  # pending, completed, skipped, failed
    files_read: List[str] = field(default_factory=list)
    queries: List[str] = field(default_factory=list)
    tools_called: List[str] = field(default_factory=list)
    duration_ms: int = 0
    error: Optional[str] = None


@dataclass
class ComplianceTrace:
    """合规轨迹"""
    task_id: str
    timestamp: str
    layers: Dict[str, LayerState]
    total_duration_ms: int = 0
    compliant: bool = True
    violations: List[str] = field(default_factory=list)


@dataclass
class Violation:
    """违规记录"""
    violation_id: str
    timestamp: str
    task_id: str
    layer: str
    severity: str
    description: str
    stack_trace: Optional[str] = None
    resolved: bool = False


class ArchitectureComplianceChecker:
    """架构遵循检查器"""
    
    def __init__(self, root: Path = None):
        self.root = root or Path(__file__).resolve().parent.parent
        self.reports_dir = self.root / "reports" / "ops"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.trace_file = self.reports_dir / "architecture_compliance.jsonl"
        self.violation_file = self.reports_dir / "architecture_violations.jsonl"
        
        # 当前任务状态
        self.current_task_id: Optional[str] = None
        self.current_trace: Optional[ComplianceTrace] = None
        self.layer_states: Dict[str, LayerState] = {}
    
    def start_task(self, task_id: str = None) -> str:
        """开始任务"""
        import time
        self.current_task_id = task_id or f"task_{int(time.time() * 1000)}"
        
        # 初始化层级状态
        self.layer_states = {
            Layer.L1_CORE.value: LayerState(),
            Layer.L2_MEMORY.value: LayerState(),
            Layer.L3_ORCHESTRATION.value: LayerState(),
            Layer.L4_EXECUTION.value: LayerState(),
            Layer.L5_GOVERNANCE.value: LayerState(),
            Layer.L6_INFRASTRUCTURE.value: LayerState(),
        }
        
        return self.current_task_id
    
    def mark_layer_completed(
        self, 
        layer: Layer, 
        files_read: List[str] = None,
        queries: List[str] = None,
        tools_called: List[str] = None,
        duration_ms: int = 0
    ):
        """标记层级完成"""
        state = self.layer_states[layer.value]
        state.status = "completed"
        state.files_read = files_read or []
        state.queries = queries or []
        state.tools_called = tools_called or []
        state.duration_ms = duration_ms
    
    def mark_layer_skipped(self, layer: Layer, reason: str = None):
        """标记层级跳过"""
        state = self.layer_states[layer.value]
        state.status = "skipped"
        state.error = reason
    
    def mark_layer_failed(self, layer: Layer, error: str):
        """标记层级失败"""
        state = self.layer_states[layer.value]
        state.status = "failed"
        state.error = error
    
    def end_task(self) -> ComplianceTrace:
        """结束任务 - V3.0.0: 增强违规检测 + 自动改进"""
        import time
        
        # 检查合规性
        violations = []
        compliant = True
        has_critical = False
        
        for layer_name, state in self.layer_states.items():
            if state.status != "completed":
                violations.append(f"{layer_name} 未完成 (状态: {state.status})")
                
                # V3.0.0: 根据层级确定严重程度
                if layer_name == Layer.L1_CORE.value:
                    severity = ViolationSeverity.CRITICAL
                    compliant = False
                    has_critical = True
                elif layer_name in [Layer.L2_MEMORY.value, Layer.L3_ORCHESTRATION.value]:
                    severity = ViolationSeverity.HIGH
                    compliant = False
                else:
                    severity = ViolationSeverity.MEDIUM
                
                # 记录违规
                self._record_violation(layer_name, severity, violations[-1])
        
        # V3.0.0: CRITICAL 违规立即抛出异常
        if has_critical:
            error_msg = f"架构违规 (CRITICAL): {violations[0]}"
            print(f"\n❌ {error_msg}")
            print("必须重新开始任务，严格按照架构流程执行！\n")
            
            # V3.0.0: 触发自动改进
            self._trigger_auto_improvement()
            
            raise ArchitectureViolationError(error_msg)
        
        # 计算总耗时
        total_duration = sum(s.duration_ms for s in self.layer_states.values())
        
        # 创建轨迹
        trace = ComplianceTrace(
            task_id=self.current_task_id,
            timestamp=datetime.now().isoformat(),
            layers={k: asdict(v) for k, v in self.layer_states.items()},
            total_duration_ms=total_duration,
            compliant=compliant,
            violations=violations
        )
        
        # 保存轨迹
        self._save_trace(trace)
        
        # V3.0.0: 非 CRITICAL 违规输出警告并触发自动改进
        if violations:
            print(f"\n⚠️  架构违规警告:")
            for v in violations:
                print(f"  - {v}")
            print()
            
            # V3.0.0: 触发自动改进
            self._trigger_auto_improvement()
        
        # 清理状态
        self.current_task_id = None
        self.current_trace = None
        self.layer_states = {}
        
        return trace
    
    def _trigger_auto_improvement(self):
        """V3.0.0: 触发自动改进"""
        print("🔄 触发自动改进机制...")
        
        try:
            # 调用自动改进器
            from scripts.architecture_auto_improver import AutoImprover
            
            improver = AutoImprover(self.root)
            result = improver.auto_upgrade_rule()
            
            if result["status"] == "upgraded":
                print(f"✅ 规则已自动升级: {result['old_version']} → {result['new_version']}")
                print(f"   新增检查项: {result['check_items_added']}")
            else:
                print(f"ℹ️  当前规则版本: {result['current_version']}")
        
        except Exception as e:
            print(f"⚠️  自动改进失败: {e}")
        
        print()
    
    def _record_violation(self, layer: str, severity: ViolationSeverity, description: str):
        """记录违规"""
        import time
        import traceback
        
        violation = Violation(
            violation_id=f"viol_{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            task_id=self.current_task_id,
            layer=layer,
            severity=severity.value,
            description=description,
            stack_trace=traceback.format_exc()
        )
        
        # 保存违规记录
        with open(self.violation_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(violation), ensure_ascii=False) + '\n')
    
    def _save_trace(self, trace: ComplianceTrace):
        """保存轨迹"""
        with open(self.trace_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(trace), ensure_ascii=False) + '\n')
    
    def check_recent_compliance(self, hours: int = 24) -> Dict[str, Any]:
        """检查最近的合规性"""
        traces = []
        violations = []
        
        # 读取最近的轨迹
        if self.trace_file.exists():
            cutoff = datetime.now().timestamp() - hours * 3600
            
            with open(self.trace_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        trace = json.loads(line)
                        trace_time = datetime.fromisoformat(trace['timestamp']).timestamp()
                        if trace_time >= cutoff:
                            traces.append(trace)
                    except:
                        pass
        
        # 读取最近的违规
        if self.violation_file.exists():
            cutoff = datetime.now().timestamp() - hours * 3600
            
            with open(self.violation_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        violation = json.loads(line)
                        viol_time = datetime.fromisoformat(violation['timestamp']).timestamp()
                        if viol_time >= cutoff:
                            violations.append(violation)
                    except:
                        pass
        
        # 统计
        total_tasks = len(traces)
        compliant_tasks = sum(1 for t in traces if t.get('compliant', False))
        total_violations = len(violations)
        
        critical_violations = sum(1 for v in violations if v.get('severity') == 'CRITICAL')
        high_violations = sum(1 for v in violations if v.get('severity') == 'HIGH')
        medium_violations = sum(1 for v in violations if v.get('severity') == 'MEDIUM')
        low_violations = sum(1 for v in violations if v.get('severity') == 'LOW')
        
        return {
            "period_hours": hours,
            "total_tasks": total_tasks,
            "compliant_tasks": compliant_tasks,
            "compliance_rate": f"{compliant_tasks / total_tasks * 100:.1f}%" if total_tasks > 0 else "N/A",
            "total_violations": total_violations,
            "violations_by_severity": {
                "CRITICAL": critical_violations,
                "HIGH": high_violations,
                "MEDIUM": medium_violations,
                "LOW": low_violations
            },
            "recent_traces": traces[-10:],
            "recent_violations": violations[-10:]
        }
    
    def generate_report(self) -> str:
        """生成合规报告"""
        stats = self.check_recent_compliance(24)
        
        lines = []
        lines.append("=" * 60)
        lines.append("  架构遵循合规报告")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"📊 过去 24 小时统计:")
        lines.append(f"  总任务数: {stats['total_tasks']}")
        lines.append(f"  合规任务: {stats['compliant_tasks']}")
        lines.append(f"  合规率: {stats['compliance_rate']}")
        lines.append("")
        
        lines.append(f"⚠️  违规统计:")
        lines.append(f"  总违规数: {stats['total_violations']}")
        lines.append(f"  CRITICAL: {stats['violations_by_severity']['CRITICAL']}")
        lines.append(f"  HIGH: {stats['violations_by_severity']['HIGH']}")
        lines.append(f"  MEDIUM: {stats['violations_by_severity']['MEDIUM']}")
        lines.append(f"  LOW: {stats['violations_by_severity']['LOW']}")
        lines.append("")
        
        if stats['recent_violations']:
            lines.append("📋 最近违规:")
            for v in stats['recent_violations'][-5:]:
                lines.append(f"  [{v['severity']}] {v['layer']}: {v['description']}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 全局检查器
_checker: Optional[ArchitectureComplianceChecker] = None


def get_checker() -> ArchitectureComplianceChecker:
    """获取全局检查器"""
    global _checker
    if _checker is None:
        _checker = ArchitectureComplianceChecker()
    return _checker


def start_task(task_id: str = None) -> str:
    """开始任务（便捷函数）"""
    return get_checker().start_task(task_id)


def mark_layer_completed(layer: Layer, **kwargs):
    """标记层级完成（便捷函数）"""
    get_checker().mark_layer_completed(layer, **kwargs)


def mark_layer_skipped(layer: Layer, reason: str = None):
    """标记层级跳过（便捷函数）"""
    get_checker().mark_layer_skipped(layer, reason)


def end_task() -> ComplianceTrace:
    """结束任务（便捷函数）"""
    return get_checker().end_task()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="架构遵循检查器 V2.0.0")
    parser.add_argument("--check", action="store_true", help="检查最近 24 小时合规性")
    parser.add_argument("--report", action="store_true", help="生成合规报告")
    parser.add_argument("--test", action="store_true", help="测试强制执行机制")
    
    args = parser.parse_args()
    
    checker = get_checker()
    
    if args.check:
        stats = checker.check_recent_compliance(24)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.report:
        report = checker.generate_report()
        print(report)
    
    elif args.test:
        # V2.0.0: 测试强制执行机制
        print("=" * 60)
        print("  测试架构遵循强制执行机制")
        print("=" * 60)
        print()
        
        # 测试正常流程
        print("✅ 测试正常流程...")
        task_id = start_task("test_normal")
        mark_layer_completed(Layer.L1_CORE, files_read=["test"])
        mark_layer_completed(Layer.L2_MEMORY, queries=["test"])
        mark_layer_completed(Layer.L3_ORCHESTRATION)
        mark_layer_completed(Layer.L4_EXECUTION)
        mark_layer_completed(Layer.L5_GOVERNANCE)
        mark_layer_completed(Layer.L6_INFRASTRUCTURE)
        trace = end_task()
        print(f"  结果: {'✅ 通过' if trace.compliant else '❌ 失败'}")
        print()
        
        # 测试 CRITICAL 违规
        print("❌ 测试 CRITICAL 违规（跳过 L1 Core）...")
        try:
            task_id = start_task("test_critical")
            mark_layer_completed(Layer.L2_MEMORY, queries=["test"])
            trace = end_task()
            print("  结果: ❌ 应该抛出异常但没有")
        except Exception as e:
            print(f"  结果: ✅ 正确抛出异常: {e}")
        print()
        
        print("=" * 60)
    
    else:
        parser.print_help()


class ArchitectureViolationError(Exception):
    """架构违规异常"""
    pass


if __name__ == "__main__":
    main()
