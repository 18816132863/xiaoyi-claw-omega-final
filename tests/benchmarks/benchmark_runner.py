"""Benchmark runner for performance and quality benchmarks."""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import time


class BenchmarkType(Enum):
    PERFORMANCE = "performance"
    QUALITY = "quality"
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY = "memory"


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    benchmark_id: str
    benchmark_type: BenchmarkType
    name: str
    value: float
    unit: str
    baseline: Optional[float] = None
    threshold: Optional[float] = None
    passed: bool = True
    duration_ms: int = 0
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "benchmark_id": self.benchmark_id,
            "benchmark_type": self.benchmark_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "baseline": self.baseline,
            "threshold": self.threshold,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class BenchmarkSuite:
    """A suite of related benchmarks."""
    suite_id: str
    name: str
    description: str
    benchmarks: List[Dict]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None


class BenchmarkRunner:
    """
    Runs performance and quality benchmarks.
    
    Features:
    - Multiple benchmark types
    - Baseline comparison
    - Threshold validation
    - Trend tracking
    """
    
    def __init__(self, results_path: str = "tests/benchmarks/results"):
        self.results_path = results_path
        self._suites: Dict[str, BenchmarkSuite] = {}
        self._results: List[BenchmarkResult] = []
        self._baselines: Dict[str, float] = {}
        self._load_baselines()
    
    def _load_baselines(self):
        """Load baselines from file."""
        baseline_path = os.path.join(self.results_path, "baselines.json")
        if os.path.exists(baseline_path):
            try:
                with open(baseline_path, 'r') as f:
                    self._baselines = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load baselines: {e}")
    
    def _save_baselines(self):
        """Save baselines to file."""
        os.makedirs(self.results_path, exist_ok=True)
        baseline_path = os.path.join(self.results_path, "baselines.json")
        with open(baseline_path, 'w') as f:
            json.dump(self._baselines, f, indent=2)
    
    def register_suite(self, suite: BenchmarkSuite):
        """Register a benchmark suite."""
        self._suites[suite.suite_id] = suite
    
    def run_suite(self, suite_id: str) -> List[BenchmarkResult]:
        """Run a benchmark suite."""
        suite = self._suites.get(suite_id)
        if not suite:
            return []
        
        results = []
        
        # Setup
        if suite.setup:
            try:
                suite.setup()
            except Exception as e:
                print(f"Warning: Suite setup failed: {e}")
        
        # Run benchmarks
        for benchmark_config in suite.benchmarks:
            result = self._run_benchmark(benchmark_config)
            results.append(result)
            self._results.append(result)
        
        # Teardown
        if suite.teardown:
            try:
                suite.teardown()
            except Exception as e:
                print(f"Warning: Suite teardown failed: {e}")
        
        # Save results
        self._save_results(results, suite_id)
        
        return results
    
    def _run_benchmark(self, config: Dict) -> BenchmarkResult:
        """Run a single benchmark."""
        benchmark_id = config.get("id", f"bench_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        name = config.get("name", benchmark_id)
        benchmark_type = BenchmarkType(config.get("type", "performance"))
        unit = config.get("unit", "ms")
        threshold = config.get("threshold")
        runner = config.get("runner")
        iterations = config.get("iterations", 1)
        
        start_time = time.time()
        
        # Run benchmark
        values = []
        for _ in range(iterations):
            if runner:
                try:
                    value = runner()
                    values.append(value)
                except Exception as e:
                    values.append(float('inf'))
            else:
                values.append(0)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Calculate result
        if config.get("aggregate", "mean") == "mean":
            value = sum(values) / len(values) if values else 0
        elif config.get("aggregate") == "max":
            value = max(values) if values else 0
        elif config.get("aggregate") == "min":
            value = min(values) if values else 0
        else:
            value = values[-1] if values else 0
        
        # Get baseline
        baseline = self._baselines.get(benchmark_id)
        
        # Check threshold
        passed = True
        if threshold is not None:
            if config.get("comparison", "lt") == "lt":
                passed = value < threshold
            else:
                passed = value > threshold
        
        return BenchmarkResult(
            benchmark_id=benchmark_id,
            benchmark_type=benchmark_type,
            name=name,
            value=value,
            unit=unit,
            baseline=baseline,
            threshold=threshold,
            passed=passed,
            duration_ms=duration_ms,
            metadata={"iterations": iterations, "values": values}
        )
    
    def _save_results(self, results: List[BenchmarkResult], suite_id: str):
        """Save benchmark results."""
        os.makedirs(self.results_path, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{suite_id}_{timestamp}.json"
        filepath = os.path.join(self.results_path, filename)
        
        data = {
            "suite_id": suite_id,
            "timestamp": datetime.now().isoformat(),
            "results": [r.to_dict() for r in results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_baseline(self, benchmark_id: str, value: float):
        """Set baseline for a benchmark."""
        self._baselines[benchmark_id] = value
        self._save_baselines()
    
    def update_baselines_from_latest(self, suite_id: str):
        """Update baselines from latest suite run."""
        # Find latest results for suite
        suite_results = [
            r for r in self._results
            if r.benchmark_id.startswith(suite_id)
        ]
        
        if not suite_results:
            return
        
        # Get latest for each benchmark
        latest = {}
        for result in reversed(suite_results):
            if result.benchmark_id not in latest:
                latest[result.benchmark_id] = result.value
        
        # Update baselines
        for benchmark_id, value in latest.items():
            self._baselines[benchmark_id] = value
        
        self._save_baselines()
    
    def get_results(self, benchmark_id: str = None, limit: int = 100) -> List[BenchmarkResult]:
        """Get benchmark results."""
        results = self._results
        
        if benchmark_id:
            results = [r for r in results if r.benchmark_id == benchmark_id]
        
        return results[-limit:]
    
    def get_trend(self, benchmark_id: str, limit: int = 10) -> Dict:
        """Get trend for a benchmark."""
        results = [r for r in self._results if r.benchmark_id == benchmark_id][-limit:]
        
        if not results:
            return {"trend": "unknown", "values": []}
        
        values = [r.value for r in results]
        
        # Calculate trend
        if len(values) >= 2:
            first_half = sum(values[:len(values)//2]) / (len(values)//2)
            second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
            
            if second_half < first_half * 0.9:
                trend = "improving"
            elif second_half > first_half * 1.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "values": values,
            "latest": values[-1] if values else None,
            "baseline": self._baselines.get(benchmark_id)
        }
    
    def compare_with_baseline(self, benchmark_id: str) -> Dict:
        """Compare latest result with baseline."""
        baseline = self._baselines.get(benchmark_id)
        results = [r for r in self._results if r.benchmark_id == benchmark_id]
        
        if not results:
            return {"comparison": "no_data"}
        
        latest = results[-1].value
        
        if baseline is None:
            return {"comparison": "no_baseline", "latest": latest}
        
        change_pct = ((latest - baseline) / baseline) * 100 if baseline != 0 else 0
        
        return {
            "comparison": "available",
            "baseline": baseline,
            "latest": latest,
            "change_pct": change_pct,
            "improved": change_pct < 0  # Lower is better for most benchmarks
        }


# Pre-defined benchmark suites
def create_default_suites() -> List[BenchmarkSuite]:
    """Create default benchmark suites."""
    return [
        BenchmarkSuite(
            suite_id="core_performance",
            name="Core Performance Benchmarks",
            description="Basic performance benchmarks for core operations",
            benchmarks=[
                {
                    "id": "memory_search_latency",
                    "name": "Memory Search Latency",
                    "type": "latency",
                    "unit": "ms",
                    "threshold": 100,
                    "iterations": 10
                },
                {
                    "id": "skill_routing_latency",
                    "name": "Skill Routing Latency",
                    "type": "latency",
                    "unit": "ms",
                    "threshold": 50,
                    "iterations": 10
                },
                {
                    "id": "workflow_execution_time",
                    "name": "Workflow Execution Time",
                    "type": "latency",
                    "unit": "ms",
                    "threshold": 1000,
                    "iterations": 5
                }
            ]
        ),
        BenchmarkSuite(
            suite_id="quality_checks",
            name="Quality Check Benchmarks",
            description="Quality and accuracy benchmarks",
            benchmarks=[
                {
                    "id": "rule_check_accuracy",
                    "name": "Rule Check Accuracy",
                    "type": "accuracy",
                    "unit": "%",
                    "threshold": 95,
                    "comparison": "gt",
                    "iterations": 1
                },
                {
                    "id": "schema_validation_rate",
                    "name": "Schema Validation Rate",
                    "type": "accuracy",
                    "unit": "%",
                    "threshold": 100,
                    "comparison": "gt",
                    "iterations": 1
                }
            ]
        )
    ]
