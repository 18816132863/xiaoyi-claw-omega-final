#!/usr/bin/env python3
"""实时告警模块 V1.0.0

监控关键指标，触发告警
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class Alert:
    """告警"""
    def __init__(self, level: str, message: str, details: dict = None):
        self.level = level  # info, warning, error, critical
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class RealtimeAlerter:
    """实时告警器"""
    
    THRESHOLDS = {
        'health_score': {'warning': 0.7, 'critical': 0.5},
        'active_skill_ratio': {'warning': 0.2, 'critical': 0.1},
        'security_issues': {'warning': 1, 'critical': 5},
        'dependency_violations': {'warning': 50, 'critical': 100},
        'startup_time_ms': {'warning': 100, 'critical': 500},
    }
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.history_file = Path('reports/alert_history.json')
        self._load_history()
    
    def _load_history(self):
        """加载历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def _save_history(self):
        """保存历史"""
        self.history_file.parent.mkdir(exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history[-100:], f)
    
    def check(self, metrics: Dict) -> List[Alert]:
        """检查指标"""
        self.alerts = []
        
        # 检查健康度
        health = metrics.get('health_score', 1.0)
        if health < self.THRESHOLDS['health_score']['critical']:
            self.alerts.append(Alert('critical', f'健康度严重不足: {health:.2f}'))
        elif health < self.THRESHOLDS['health_score']['warning']:
            self.alerts.append(Alert('warning', f'健康度偏低: {health:.2f}'))
        
        # 检查技能激活率
        skill_ratio = metrics.get('active_skill_ratio', 1.0)
        if skill_ratio < self.THRESHOLDS['active_skill_ratio']['critical']:
            self.alerts.append(Alert('critical', f'技能激活率过低: {skill_ratio*100:.1f}%'))
        elif skill_ratio < self.THRESHOLDS['active_skill_ratio']['warning']:
            self.alerts.append(Alert('warning', f'技能激活率偏低: {skill_ratio*100:.1f}%'))
        
        # 检查安全问题
        security = metrics.get('security_issues', 0)
        if security >= self.THRESHOLDS['security_issues']['critical']:
            self.alerts.append(Alert('critical', f'发现 {security} 个安全问题'))
        elif security >= self.THRESHOLDS['security_issues']['warning']:
            self.alerts.append(Alert('warning', f'发现 {security} 个安全问题'))
        
        # 检查依赖违规
        violations = metrics.get('dependency_violations', 0)
        if violations >= self.THRESHOLDS['dependency_violations']['critical']:
            self.alerts.append(Alert('critical', f'依赖违规过多: {violations} 处'))
        elif violations >= self.THRESHOLDS['dependency_violations']['warning']:
            self.alerts.append(Alert('warning', f'依赖违规较多: {violations} 处'))
        
        # 记录历史
        if self.alerts:
            for alert in self.alerts:
                self.history.append({
                    'level': alert.level,
                    'message': alert.message,
                    'timestamp': alert.timestamp
                })
            self._save_history()
        
        return self.alerts
    
    def report(self):
        """生成报告"""
        if not self.alerts:
            print("✅ 无告警")
            return
        
        print("=" * 50)
        print("实时告警报告")
        print("=" * 50)
        
        for alert in self.alerts:
            icon = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'critical': '🔴'}
            print(f"{icon.get(alert.level, '⚠️')} [{alert.level.upper()}] {alert.message}")

if __name__ == '__main__':
    alerter = RealtimeAlerter()
    
    # 测试
    metrics = {
        'health_score': 0.80,
        'active_skill_ratio': 0.555,
        'security_issues': 0,
        'dependency_violations': 8
    }
    
    alerts = alerter.check(metrics)
    alerter.report()
