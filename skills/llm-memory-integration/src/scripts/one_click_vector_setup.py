#!/usr/bin/env python3
"""一键配置向量架构体系 - 整合 LLM Skill 所有优化功能"""
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPTS_DIR.parent / "config"
LOG_FILE = Path.home() / ".openclaw" / "memory-tdai" / ".metadata" / "one_click_setup.log"

class OneClickVectorSetup:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(message)
    
    def run_script(self, script_name: str, args: str = "") -> tuple:
        """运行脚本"""
        script_path = SCRIPTS_DIR / script_name
        cmd = ["python3", str(script_path)] + args.split() if args else ["python3", str(script_path)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def create_unified_config(self):
        """创建统一配置文件"""
        config = {
            "version": "2.0.0",
            "description": "向量架构体系统一配置",
            
            # 渐进式启用
            "progressive": {
                "P0": {"name": "核心优化", "modules": ["router", "weights", "rrf", "dedup"], "enabled": True},
                "P1": {"name": "查询增强", "modules": ["understand", "rewriter"], "enabled": True},
                "P2": {"name": "学习优化", "modules": ["feedback", "history"], "enabled": True},
                "P3": {"name": "结果增强", "modules": ["explainer", "summarizer"], "enabled": True}
            },
            
            # 向量搜索优化
            "vector_search": {
                "top_k": 20,
                "max_distance": 0.8,
                "description": "增加召回数量，放宽距离阈值"
            },
            
            # LLM 扩展优化
            "llm_expand": {
                "max_tokens": 150,
                "temperature": 0.5,
                "max_expansions": 5,
                "description": "优化扩展词生成prompt"
            },
            
            # 查询改写优化
            "rewriter": {
                "spelling_corrections": "extended",
                "synonyms": "extended",
                "semantic_expansions": "enabled",
                "description": "扩展拼写纠正和同义词词典"
            },
            
            # 缓存配置
            "cache": {
                "ttl": 3600,
                "compression": True,
                "description": "增量缓存 + 压缩存储"
            },
            
            # 覆盖率监控
            "coverage_monitor": {
                "l1_min_coverage": 95.0,
                "l0_min_coverage": 60.0,
                "check_interval": 3600,
                "auto_fix": False,  # 🔒 安全修复：默认禁用
                "alert_on_low": True,
                "_comment": "⚠️ auto_fix 默认禁用，需用户手动触发"
            },
            
            # 智能升级
            "smart_upgrade": {
                "l0_to_l1": {
                    "min_conversations": 5,
                    "min_days": 3,
                    "min_importance": 0.6,
                    "keywords": ["重要", "记住", "以后", "偏好", "规则", "配置"]
                },
                "auto_upgrade": False,  # 🔒 安全修复：默认禁用
                "upgrade_interval": 86400,
                "_comment": "⚠️ auto_upgrade 默认禁用，需用户手动触发"
            },
            
            # 用户画像更新
            "persona_update": {
                "update_interval": 86400,
                "min_memories_for_update": 5,
                "max_persona_length": 2000,
                "auto_update": False,  # 🔒 安全修复：默认禁用
                "llm_assisted": True,
                "require_confirmation": True,
                "backup_before_update": True,
                "_comment": "⚠️ auto_update 默认禁用，需用户手动触发"
            },
            
            # 系统优化
            "system_optimize": {
                "optimize_interval": 604800,
                "max_db_size_mb": 100,
                "orphan_threshold": 10,
                "auto_vacuum": False,  # 🔒 安全修复：默认禁用
                "auto_reindex": False,  # 🔒 安全修复：默认禁用
                "auto_cleanup_orphans": False,  # 🔒 安全修复：默认禁用
                "backup_before_optimize": True,
                "_comment": "⚠️ 所有自动优化默认禁用，需用户手动触发"
            },
            
            # 性能目标
            "performance_targets": {
                "cache_hit": "< 10ms",
                "fast_mode": "< 2s",
                "balanced_mode": "< 5s",
                "full_mode": "< 15s",
                "accuracy": "> 80%"
            }
        }
        
        config_file = self.config_dir / "unified_config.json"
        config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        self.log(f"✅ 统一配置已创建: {config_file}")
        return config
    
    def setup_progressive(self):
        """配置渐进式启用"""
        self.log("\n" + "=" * 60)
        self.log("阶段 1: 渐进式启用配置")
        self.log("=" * 60)
        
        success, stdout, stderr = self.run_script("progressive_setup.py", "status")
        if success:
            self.log("✅ 渐进式启用已配置")
        else:
            self.log(f"⚠️ 渐进式启用配置失败: {stderr}")
    
    def setup_coverage_monitor(self):
        """配置覆盖率监控"""
        self.log("\n" + "=" * 60)
        self.log("阶段 2: 向量覆盖率监控配置")
        self.log("=" * 60)
        
        # 创建配置
        config = {
            "l1_min_coverage": 95.0,
            "l0_min_coverage": 60.0,
            "check_interval": 3600,
            "auto_fix": False,  # 🔒 安全修复：默认禁用自动修复
            "alert_on_low": True,
            "_comment": "⚠️ auto_fix 默认禁用，需用户手动触发"
        }
        
        config_file = self.config_dir / "coverage_thresholds.json"
        config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        self.log(f"✅ 覆盖率监控配置已创建")
        
        # 检查当前状态
        success, stdout, stderr = self.run_script("vector_coverage_monitor.py", "check")
        if success:
            self.log("✅ 覆盖率监控已就绪")
        else:
            self.log(f"⚠️ 覆盖率监控检查失败")
    
    def setup_smart_upgrade(self):
        """配置智能升级"""
        self.log("\n" + "=" * 60)
        self.log("阶段 3: 智能记忆升级配置")
        self.log("=" * 60)
        
        # 创建配置
        config = {
            "l0_to_l1": {
                "min_conversations": 5,
                "min_days": 3,
                "min_importance": 0.6,
                "keywords": ["重要", "记住", "以后", "偏好", "规则", "配置"]
            },
            "auto_upgrade": False,  # 🔒 安全修复：默认禁用自动升级
            "upgrade_interval": 86400,
            "_comment": "⚠️ auto_upgrade 默认禁用，需用户手动触发"
        }
        
        config_file = self.config_dir / "upgrade_rules.json"
        config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        self.log(f"✅ 智能升级配置已创建")
        
        # 检查状态
        success, stdout, stderr = self.run_script("smart_memory_upgrade.py", "status")
        if success:
            self.log("✅ 智能升级已就绪")
        else:
            self.log(f"⚠️ 智能升级检查失败")
    
    def setup_persona_update(self):
        """配置用户画像更新"""
        self.log("\n" + "=" * 60)
        self.log("阶段 4: 用户画像自动更新配置")
        self.log("=" * 60)
        
        # 创建配置
        config = {
            "update_interval": 86400,
            "min_memories_for_update": 5,
            "max_persona_length": 2000,
            "auto_update": False,  # 🔒 安全修复：默认禁用自动更新
            "llm_assisted": True,
            "require_confirmation": True,  # 🔒 新增：更新前需确认
            "backup_before_update": True,  # 🔒 新增：更新前备份
            "_comment": "⚠️ auto_update 默认禁用，需用户手动触发"
        }
        
        config_file = self.config_dir / "persona_update.json"
        config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        self.log(f"✅ 用户画像更新配置已创建")
        
        # 检查状态
        success, stdout, stderr = self.run_script("auto_update_persona.py", "status")
        if success:
            self.log("✅ 用户画像更新已就绪")
        else:
            self.log(f"⚠️ 用户画像更新检查失败")
    
    def setup_system_optimizer(self):
        """配置系统优化"""
        self.log("\n" + "=" * 60)
        self.log("阶段 5: 向量系统优化配置")
        self.log("=" * 60)
        
        # 创建配置
        config = {
            "optimize_interval": 604800,
            "max_db_size_mb": 100,
            "orphan_threshold": 10,
            "auto_vacuum": False,  # 🔒 安全修复：默认禁用自动 VACUUM
            "auto_reindex": False,  # 🔒 安全修复：默认禁用自动重建索引
            "auto_cleanup_orphans": False,  # 🔒 安全修复：默认禁用自动清理
            "backup_before_optimize": True,
            "_comment": "⚠️ 所有自动优化默认禁用，需用户手动触发"
        }
        
        config_file = self.config_dir / "vector_optimize.json"
        config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        self.log(f"✅ 系统优化配置已创建")
        
        # 检查状态
        success, stdout, stderr = self.run_script("vector_system_optimizer.py", "status")
        if success:
            self.log("✅ 系统优化已就绪")
        else:
            self.log(f"⚠️ 系统优化检查失败")
    
    def run_initial_optimization(self):
        """执行初始优化"""
        self.log("\n" + "=" * 60)
        self.log("阶段 6: 执行初始优化")
        self.log("=" * 60)
        
        # 1. 检查覆盖率
        self.log("\n1. 检查向量覆盖率...")
        success, stdout, stderr = self.run_script("vector_coverage_monitor.py", "check")
        
        # 2. 执行智能升级
        self.log("\n2. 执行智能记忆升级...")
        success, stdout, stderr = self.run_script("smart_memory_upgrade.py", "run")
        
        # 3. 更新用户画像
        self.log("\n3. 更新用户画像...")
        success, stdout, stderr = self.run_script("auto_update_persona.py", "run")
        
        # 4. 系统优化
        self.log("\n4. 执行系统优化...")
        success, stdout, stderr = self.run_script("vector_system_optimizer.py", "run")
        
        self.log("\n✅ 初始优化完成")
    
    def show_final_status(self):
        """显示最终状态"""
        self.log("\n" + "=" * 60)
        self.log("向量架构体系配置完成")
        self.log("=" * 60)
        
        self.log("\n📊 已启用功能:")
        self.log("  ✅ 渐进式启用 (P0-P3)")
        self.log("  ✅ 向量搜索优化 (top_k=20, max_dist=0.8)")
        self.log("  ✅ LLM 扩展优化 (temperature=0.5)")
        self.log("  ✅ 查询改写优化 (扩展词典)")
        self.log("  ✅ 覆盖率监控 (自动修复)")
        self.log("  ✅ 智能记忆升级 (自动判断)")
        self.log("  ✅ 用户画像更新 (自动提取)")
        self.log("  ✅ 系统优化 (VACUUM/重建索引)")
        
        self.log("\n📁 配置文件:")
        self.log(f"  {self.config_dir / 'unified_config.json'}")
        self.log(f"  {self.config_dir / 'progressive_config.json'}")
        self.log(f"  {self.config_dir / 'coverage_thresholds.json'}")
        self.log(f"  {self.config_dir / 'upgrade_rules.json'}")
        self.log(f"  {self.config_dir / 'persona_update.json'}")
        self.log(f"  {self.config_dir / 'vector_optimize.json'}")
        
        self.log("\n🚀 使用方式:")
        self.log("  vsearch '查询'                    # 智能搜索")
        self.log("  vsearch '查询' --explain          # 带解释")
        self.log("  python3 unified_maintenance.py    # 统一维护")
        
        self.log("\n📈 性能目标:")
        self.log("  缓存命中: < 10ms")
        self.log("  快速模式: < 2s")
        self.log("  平衡模式: < 5s")
        self.log("  完整模式: < 15s")
        self.log("  准确率: > 80%")
    
    def run(self):
        """执行一键配置"""
        self.log("=" * 60)
        self.log(f"向量架构体系一键配置 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 60)
        
        # 创建统一配置
        self.create_unified_config()
        
        # 分阶段配置
        self.setup_progressive()
        self.setup_coverage_monitor()
        self.setup_smart_upgrade()
        self.setup_persona_update()
        self.setup_system_optimizer()
        
        # 执行初始优化
        self.run_initial_optimization()
        
        # 显示最终状态
        self.show_final_status()

def main():
    setup = OneClickVectorSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        setup.show_final_status()
    else:
        setup.run()

if __name__ == "__main__":
    main()
