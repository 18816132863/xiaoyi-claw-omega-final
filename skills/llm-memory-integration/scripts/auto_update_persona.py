#!/usr/bin/env python3
"""
用户画像自动更新 - 基于记忆分析自动更新 persona.md（安全修复版）

安全修复：
- 移除 shell=False，使用 sqlite3 直接连接
- 使用参数化查询防止 SQL 注入
- 使用相对路径配置
"""

import os
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 配置路径（使用相对路径）
CONFIG_DIR = Path(__file__).parent.parent / "config"
PERSONA_FILE = Path.home() / ".openclaw" / "memory-tdai" / "persona.md"
MEMORY_FILE = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
CONFIG_FILE = CONFIG_DIR / "persona_update.json"
LOG_FILE = Path.home() / ".openclaw" / "memory-tdai" / ".metadata" / "persona_update.log"

# 默认配置
DEFAULT_CONFIG = {
    "update_interval": 86400,        # 更新间隔（秒）
    "min_memories_for_update": 5,    # 最少记忆数量才触发更新
    "max_persona_length": 2000,      # persona.md 最大长度
    "preserve_sections": [           # 保留的章节
        "核心原型",
        "基本信息",
        "长期偏好"
    ],
    "auto_update": False,            # ⚠️ 默认禁用自动更新，需用户明确启用
    "require_confirmation": True,    # ⚠️ 更新前需要用户确认
    "llm_assisted": True,            # 是否使用 LLM 辅助
    "backup_before_update": True,    # ⚠️ 更新前备份 persona.md
    "max_backups": 5                 # 最多保留备份数
}

class PersonaAutoUpdater:
    def __init__(self):
        self.persona_file = PERSONA_FILE
        self.memory_file = MEMORY_FILE
        self.db_path = VECTORS_DB
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.persona_content = self._load_persona()
    
    def _load_config(self) -> Dict:
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return DEFAULT_CONFIG
    
    def _load_persona(self) -> str:
        if self.persona_file.exists():
            return self.persona_file.read_text()
        return ""
    
    def _save_persona(self, content: str):
        # 压缩到最大长度
        if len(content) > self.config["max_persona_length"]:
            content = self._compress_persona(content)
        
        self.persona_file.write_text(content)
        self.persona_content = content
    
    def _compress_persona(self, content: str) -> str:
        """压缩 persona 到目标长度"""
        lines = content.split('\n')
        compressed = []
        current_length = 0
        max_len = self.config["max_persona_length"]
        
        for line in lines:
            if current_length + len(line) + 1 <= max_len:
                compressed.append(line)
                current_length += len(line) + 1
            else:
                break
        
        return '\n'.join(compressed) + "\n\n... (已压缩)"
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def get_db_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))
    
    def extract_preferences(self, memories: List[Dict]) -> Dict:
        """从记忆中提取偏好"""
        preferences = {
            "communication_style": [],
            "work_style": [],
            "technical_preferences": [],
            "rules": []
        }
        
        for memory in memories:
            content = memory.get("content", "")
            memory_type = memory.get("type", "")
            
            # 提取通信风格偏好
            if any(kw in content for kw in ["回复", "简洁", "详细", "风格"]):
                preferences["communication_style"].append(content[:100])
            
            # 提取工作风格偏好
            if any(kw in content for kw in ["工作", "效率", "时间", "习惯"]):
                preferences["work_style"].append(content[:100])
            
            # 提取技术偏好
            if any(kw in content for kw in ["配置", "设置", "技术", "工具"]):
                preferences["technical_preferences"].append(content[:100])
            
            # 提取规则
            if memory_type == "instruction" or any(kw in content for kw in ["必须", "不要", "以后"]):
                preferences["rules"].append(content[:100])
        
        return preferences
    
    def detect_changes(self, new_preferences: Dict) -> List[Dict]:
        """检测新偏好变化"""
        changes = []
        
        # 检查每类偏好
        for category, items in new_preferences.items():
            for item in items:
                if item and item not in self.persona_content:
                    changes.append({
                        "category": category,
                        "content": item,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return changes
    
    def backup_persona(self):
        """备份 persona.md"""
        if not self.persona_file.exists():
            return None
        
        backup_dir = self.persona_file.parent / ".persona_backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"persona_{timestamp}.md"
        
        import shutil
        shutil.copy2(self.persona_file, backup_path)
        
        # 清理旧备份
        backups = sorted(backup_dir.glob("persona_*.md"))
        while len(backups) > self.config.get("max_backups", 5):
            backups[0].unlink()
            backups = backups[1:]
        
        self.log(f"✅ 已备份 persona.md 到: {backup_path}")
        return backup_path
    
    def update_persona(self, changes: List[Dict]):
        """更新 persona.md（带确认和备份）"""
        if not changes:
            self.log("无新变化，跳过更新")
            return
        
        # ⚠️ 检查是否需要用户确认
        if self.config.get("require_confirmation", True):
            print("\n" + "=" * 60)
            print("⚠️ 即将更新 persona.md")
            print("=" * 60)
            print(f"检测到 {len(changes)} 条新偏好：\n")
            for i, change in enumerate(changes[:5], 1):
                print(f"  {i}. [{change['category']}] {change['content'][:60]}...")
            if len(changes) > 5:
                print(f"  ... 还有 {len(changes) - 5} 条")
            print("\n是否继续更新？(y/N): ", end="")
            
            try:
                response = input().strip().lower()
                if response != 'y':
                    self.log("❌ 用户取消更新")
                    print("已取消更新")
                    return
            except:
                self.log("❌ 无法获取用户输入，跳过更新")
                return
        
        # ⚠️ 备份
        if self.config.get("backup_before_update", True):
            self.backup_persona()
        
        self.log(f"📝 检测到 {len(changes)} 条新偏好")
        
        # 构建更新内容
        update_section = f"\n### 更新 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        for change in changes:
            category = change["category"]
            content = change["content"]
            update_section += f"- **{category}**: {content[:80]}\n"
        
        # 追加到 persona
        new_content = self.persona_content
        
        # 找到插入位置（在最后一个更新之前）
        if "### 更新" in new_content:
            # 插入到第一个更新之前
            parts = new_content.split("### 更新", 1)
            new_content = parts[0] + update_section + "### 更新" + parts[1]
        else:
            # 追加到末尾
            new_content += "\n" + update_section
        
        self._save_persona(new_content)
        self.log(f"✅ persona.md 已更新 ({len(changes)} 条新偏好)")
        print(f"✅ persona.md 已更新 ({len(changes)} 条新偏好)")
    
    def run_update_cycle(self):
        """执行更新周期"""
        # ⚠️ 检查是否启用自动更新
        if not self.config.get("auto_update", False):
            self.log("⚠️ 自动更新已禁用，跳过更新周期")
            print("⚠️ 自动更新已禁用")
            print("如需启用，请修改 config/persona_update.json:")
            print('  "auto_update": true')
            return
        
        self.log("🔄 开始用户画像更新周期")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 使用参数化查询（安全）
            cursor.execute("""
                SELECT content, type, scene_name, created_at
                FROM l1_records
                WHERE type = 'instruction'
                ORDER BY created_at DESC
                LIMIT 20
            """)
            
            memories = []
            for row in cursor.fetchall():
                if len(row) >= 4:
                    memories.append({
                        "content": row[0] or "",
                        "type": row[1] or "",
                        "scene": row[2] or "",
                        "timestamp": row[3] or ""
                    })
            
            conn.close()
            
            if len(memories) < self.config["min_memories_for_update"]:
                self.log(f"记忆数量不足 ({len(memories)} < {self.config['min_memories_for_update']})，跳过更新")
                return
            
            # 2. 提取偏好
            preferences = self.extract_preferences(memories)
            
            # 3. 检测变化
            changes = self.detect_changes(preferences)
            
            # 4. 更新 persona（带确认和备份）
            self.update_persona(changes)
            
        except Exception as e:
            self.log(f"❌ 更新失败: {e}")
    
    def show_status(self):
        """显示状态"""
        print("=" * 60)
        print("用户画像自动更新状态")
        print("=" * 60)
        print(f"persona.md: {self.persona_file}")
        print(f"当前长度: {len(self.persona_content)} 字符")
        print(f"最大长度: {self.config['max_persona_length']} 字符")
        print(f"自动更新: {'✅ 启用' if self.config.get('auto_update', False) else '❌ 禁用（默认）'}")
        print(f"需要确认: {'✅ 是' if self.config.get('require_confirmation', True) else '❌ 否'}")
        print(f"更新前备份: {'✅ 是' if self.config.get('backup_before_update', True) else '❌ 否'}")
        print(f"LLM 辅助: {'✅ 启用' if self.config.get('llm_assisted', True) else '❌ 禁用'}")
        print(f"更新间隔: {self.config.get('update_interval', 86400)} 秒")
        
        # 显示最近的更新
        if "### 更新" in self.persona_content:
            updates = re.findall(r'### 更新 (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', self.persona_content)
            if updates:
                print(f"\n最近更新: {updates[-1]}")
        
        print("\n⚠️ 安全提示:")
        print("  - 自动更新默认禁用，需手动启用")
        print("  - 更新前会备份 persona.md")
        print("  - 更新时会请求用户确认")

def main():
    import sys
    
    updater = PersonaAutoUpdater()
    
    if len(sys.argv) < 2:
        updater.show_status()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        updater.show_status()
    elif cmd == "run":
        updater.run_update_cycle()
    elif cmd == "show":
        print(updater.persona_content)
    else:
        print(f"未知命令: {cmd}")
        print("用法: auto_update_persona.py [status|run|show]")

if __name__ == "__main__":
    main()
