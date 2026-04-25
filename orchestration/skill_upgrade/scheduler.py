#!/usr/bin/env python3
"""
技能升级调度器 - L3 Orchestration 模块

职责:
- 调度升级任务
- 管理升级队列
- 处理升级失败
- 触发后续流程

依赖:
- L1 Core: 读取升级策略
- L4 Execution: 调用升级引擎
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from queue import Queue
from threading import Thread
import time

class SkillUpgradeScheduler:
    """技能升级调度器"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.queue = Queue()
        self.results = []
        self.running = False
        
        # 读取 L1 Core 配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """从 L1 Core 读取配置"""
        # 硬编码配置 (实际应从 core/SKILL_UPGRADE_ARCHITECTURE.md 解析)
        return {
            "max_workers": 1,  # 单线程执行
            "retry_count": 1,  # 失败重试次数
            "timeout": 300,    # 超时时间 (秒)
            "batch_size": 50   # 批量大小
        }
    
    def schedule(self, skill_names: List[str]) -> Dict:
        """调度升级任务"""
        print("=" * 60)
        print("L3 Orchestration - 技能升级调度器")
        print("=" * 60)
        
        # 分批调度
        batches = self._create_batches(skill_names)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total": len(skill_names),
            "batches": len(batches),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for i, batch in enumerate(batches, 1):
            print(f"\n批次 {i}/{len(batches)}: {len(batch)} 个技能")
            
            # 调用 L4 Execution
            batch_result = self._execute_batch(batch)
            results["details"].extend(batch_result["details"])
            results["success"] += batch_result["success"]
            results["failed"] += batch_result["failed"]
        
        # 保存调度报告
        self._save_report(results)
        
        print("\n" + "=" * 60)
        print(f"调度完成: {results['success']}/{results['total']} 成功")
        print("=" * 60)
        
        return results
    
    def _create_batches(self, skills: List[str]) -> List[List[str]]:
        """创建批次"""
        batch_size = self.config["batch_size"]
        return [skills[i:i + batch_size] for i in range(0, len(skills), batch_size)]
    
    def _execute_batch(self, batch: List[str]) -> Dict:
        """执行批次升级 - 调用 L4 Execution"""
        # 导入 L4 Execution 模块
        sys.path.insert(0, str(self.workspace / "skills"))
        from skill_upgrade_engine_v2 import SkillUpgradeEngine
        
        # 创建引擎实例
        engine = SkillUpgradeEngine()
        
        # 执行升级
        return engine.upgrade_all(batch)
    
    def _save_report(self, results: Dict):
        """保存调度报告"""
        reports_dir = self.workspace / "reports" / "skill_upgrades"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"schedule_{timestamp}.json"
        report_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"\n调度报告: {report_file}")


def main():
    """主函数"""
    scheduler = SkillUpgradeScheduler()
    
    # 扫描所有技能
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    all_skills = [d.name for d in skills_dir.iterdir() 
                  if d.is_dir() and (d / "SKILL.md").exists()]
    
    # 调度升级
    results = scheduler.schedule(all_skills)
    
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
