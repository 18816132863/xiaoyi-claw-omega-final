#!/usr/bin/env python3
"""
技能审计日志分析器 - L5 Governance 模块

职责:
- 审计日志分析
- 异常检测
- 统计报告
- 合规性检查

依赖:
- L1 Core: 读取审计规则
- reports/: 读取审计日志
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class AuditAnalyzer:
    """审计日志分析器"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.audit_file = self.workspace / "reports" / "skill_upgrades" / "audit.jsonl"
        
        # 加载审计日志
        self.logs = self._load_logs()
    
    def _load_logs(self) -> List[Dict]:
        """加载审计日志"""
        if not self.audit_file.exists():
            return []
        
        logs = []
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        
        return logs
    
    def analyze(self, days: int = 7) -> Dict:
        """分析审计日志"""
        print("=" * 60)
        print("L5 Governance - 审计日志分析")
        print("=" * 60)
        
        # 过滤最近N天的日志
        cutoff = datetime.now() - timedelta(days=days)
        recent_logs = [
            log for log in self.logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff
        ]
        
        # 统计分析
        stats = {
            "period": f"最近 {days} 天",
            "total_events": len(recent_logs),
            "event_types": defaultdict(int),
            "skills": defaultdict(int),
            "success_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
            "anomalies": []
        }
        
        for log in recent_logs:
            # 统计事件类型
            event_type = log.get("event_type", "unknown")
            stats["event_types"][event_type] += 1
            
            # 统计技能
            skill = log.get("skill_name", "unknown")
            stats["skills"][skill] += 1
            
            # 统计成功/失败
            if event_type == "upgrade_success":
                stats["success_count"] += 1
            elif event_type == "upgrade_failed":
                stats["failed_count"] += 1
            elif event_type == "upgrade_skipped":
                stats["skipped_count"] += 1
            
            # 异常检测
            if event_type == "upgrade_failed":
                stats["anomalies"].append({
                    "type": "upgrade_failure",
                    "skill": skill,
                    "error": log.get("error", "未知错误"),
                    "timestamp": log["timestamp"]
                })
        
        # 打印报告
        self._print_report(stats)
        
        # 保存报告
        self._save_report(stats)
        
        return stats
    
    def _print_report(self, stats: Dict):
        """打印分析报告"""
        print(f"\n时间范围: {stats['period']}")
        print(f"总事件数: {stats['total_events']}")
        
        print("\n事件类型分布:")
        for event_type, count in sorted(stats["event_types"].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {event_type}: {count}")
        
        print(f"\n升级统计:")
        print(f"  - 成功: {stats['success_count']}")
        print(f"  - 失败: {stats['failed_count']}")
        print(f"  - 跳过: {stats['skipped_count']}")
        
        if stats["anomalies"]:
            print(f"\n异常检测 ({len(stats['anomalies'])} 个):")
            for anomaly in stats["anomalies"][:5]:  # 只显示前5个
                print(f"  - [{anomaly['type']}] {anomaly['skill']}: {anomaly['error']}")
        
        print("\n" + "=" * 60)
    
    def _save_report(self, stats: Dict):
        """保存分析报告"""
        reports_dir = self.workspace / "reports" / "skill_quality"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"audit_analysis_{timestamp}.json"
        
        # 转换 defaultdict 为普通 dict
        stats_copy = dict(stats)
        stats_copy["event_types"] = dict(stats_copy["event_types"])
        stats_copy["skills"] = dict(stats_copy["skills"])
        
        report_file.write_text(json.dumps(stats_copy, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"分析报告: {report_file}")
    
    def check_compliance(self) -> Dict:
        """合规性检查"""
        print("\n合规性检查:")
        
        checks = {
            "audit_log_exists": self.audit_file.exists(),
            "audit_log_not_empty": len(self.logs) > 0,
            "recent_activity": any(
                datetime.fromisoformat(log["timestamp"]) >= datetime.now() - timedelta(days=1)
                for log in self.logs
            ) if self.logs else False
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        return checks


def main():
    """主函数"""
    analyzer = AuditAnalyzer()
    
    # 分析最近7天的日志
    stats = analyzer.analyze(days=7)
    
    # 合规性检查
    compliance = analyzer.check_compliance()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
