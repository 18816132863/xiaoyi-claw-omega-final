#!/usr/bin/env python3
"""
会话结束检测器 - V1.0.0

职责：
1. 检测会话空闲时间
2. 判断会话是否结束
3. 触发会话结束任务（备份、提交等）

使用方式：
- python scripts/session_end_detector.py
- 由心跳执行器自动调用
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class SessionEndDetector:
    """会话结束检测器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.state_file = root / "reports" / "ops" / "session_state.json"
        self.idle_threshold = timedelta(minutes=30)  # 30 分钟无交互视为会话结束
        
    def load_state(self) -> Dict[str, Any]:
        """加载会话状态"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {
            "last_interaction": None,
            "session_ended": False,
            "last_backup": None
        }
    
    def save_state(self, state: Dict[str, Any]):
        """保存会话状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def update_interaction(self):
        """更新最后交互时间"""
        state = self.load_state()
        state["last_interaction"] = datetime.now().isoformat()
        state["session_ended"] = False
        self.save_state(state)
    
    def check_session_end(self) -> bool:
        """检查会话是否结束"""
        state = self.load_state()
        last_interaction = state.get("last_interaction")
        
        if not last_interaction:
            # 没有交互记录，视为新会话
            self.update_interaction()
            return False
        
        try:
            last_time = datetime.fromisoformat(last_interaction)
            idle_time = datetime.now() - last_time
            
            # 空闲时间超过阈值，视为会话结束
            if idle_time > self.idle_threshold:
                # 检查是否已经标记为结束
                if state.get("session_ended"):
                    return False  # 已经处理过
                
                # 标记为会话结束
                state["session_ended"] = True
                self.save_state(state)
                return True
            
            return False
        except Exception:
            return False
    
    def should_backup(self) -> bool:
        """判断是否需要备份"""
        state = self.load_state()
        last_backup = state.get("last_backup")
        
        if not last_backup:
            return True
        
        try:
            last_backup_time = datetime.fromisoformat(last_backup)
            # 距离上次备份超过 1 小时
            if datetime.now() - last_backup_time > timedelta(hours=1):
                return True
            return False
        except Exception:
            return True
    
    def mark_backup_done(self):
        """标记备份已完成"""
        state = self.load_state()
        state["last_backup"] = datetime.now().isoformat()
        self.save_state(state)
    
    def run(self) -> Dict[str, Any]:
        """运行检测器"""
        print("=" * 60)
        print("  会话结束检测器 V1.0.0")
        print("=" * 60)
        print()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "session_ended": False,
            "should_backup": False,
            "actions": []
        }
        
        # 检查会话是否结束
        if self.check_session_end():
            print("🔔 检测到会话结束")
            result["session_ended"] = True
            
            # 检查是否需要备份
            if self.should_backup():
                print("📦 需要执行备份")
                result["should_backup"] = True
                result["actions"].append("backup")
                
                # 执行备份
                import subprocess
                try:
                    print("  执行备份...")
                    proc = subprocess.run(
                        [sys.executable, str(self.root / "infrastructure" / "auto_backup_uploader.py")],
                        cwd=str(self.root),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if proc.returncode == 0:
                        print("  ✅ 备份完成")
                        self.mark_backup_done()
                        result["backup_success"] = True
                    else:
                        print(f"  ❌ 备份失败: {proc.stderr[:100]}")
                        result["backup_success"] = False
                except Exception as e:
                    print(f"  ❌ 备份异常: {e}")
                    result["backup_success"] = False
            
            # 检查是否需要 Git 提交
            try:
                proc = subprocess.run(
                    [sys.executable, str(self.root / "infrastructure" / "auto_git.py"), "sync", "会话结束自动提交"],
                    cwd=str(self.root),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if proc.returncode == 0:
                    print("  ✅ Git 提交完成")
                    result["git_success"] = True
                    result["actions"].append("git_commit")
                else:
                    print(f"  ⚠️  Git 提交跳过: {proc.stdout[:100]}")
                    result["git_success"] = False
            except Exception as e:
                print(f"  ⚠️  Git 提交异常: {e}")
                result["git_success"] = False
        else:
            print("✅ 会话活跃中")
            
            # 更新交互时间
            self.update_interaction()
        
        print()
        return result


def main():
    root = get_project_root()
    detector = SessionEndDetector(root)
    result = detector.run()
    
    # 保存结果
    result_file = root / "reports" / "ops" / "session_end_detection.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
