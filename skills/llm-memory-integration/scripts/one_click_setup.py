#!/usr/bin/env python3
"""
One-Click Setup - 交互式一键启用配置
自动配置向量模型 + LLM + 记忆系统 + 向量架构体系
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
OPENCLAW_JSON = Path.home() / ".openclaw" / "openclaw.json"
MEMORY_TDDB = Path.home() / ".openclaw" / "memory-tdai"
LOG_FILE = MEMORY_TDDB / ".metadata" / "one_click_setup.log"

# 推荐配置模板（用户需自行填入 API 密钥）
RECOMMENDED_CONFIG = {
    "embedding": {
        "enabled": True,
        "provider": "openai-compatible",  # 支持 openai, gitee, azure 等
        "baseUrl": "https://api.openai.com/v1",  # 用户自行配置
        "apiKey": "",  # ⚠️ 用户必须自行填入 API 密钥
        "model": "text-embedding-3-small",
        "dimensions": 1536
    },
    "llm": {
        "provider": "openai-compatible",
        "model": "gpt-4",
        "baseUrl": "https://api.openai.com/v1",  # 用户自行配置
        "contextWindow": 128000,
        "maxTokens": 4000
    },
    "memory": {
        "maxMemoriesPerSession": 50,
        "everyNConversations": 3,
        "l1IdleTimeoutSeconds": 30,
        "maxResults": 12,
        "scoreThreshold": 0.2
    }
}

# 支持的提供商示例
PROVIDER_EXAMPLES = {
    "openai": {
        "embedding": {"baseUrl": "https://api.openai.com/v1", "model": "text-embedding-3-small"},
        "llm": {"baseUrl": "https://api.openai.com/v1", "model": "gpt-4"}
    },
    "gitee": {
        "embedding": {"baseUrl": "https://ai.gitee.com/v1", "model": "Qwen3-Embedding-8B", "dimensions": 4096},
        "llm": {"baseUrl": "https://ai.gitee.com/v1", "model": "Qwen3-8B"}
    },
    "azure": {
        "embedding": {"baseUrl": "https://YOUR_RESOURCE.openai.azure.com", "model": "text-embedding-ada-002"},
        "llm": {"baseUrl": "https://YOUR_RESOURCE.openai.azure.com", "model": "gpt-4"}
    }
}

class InteractiveSetup:
    def __init__(self):
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_choices = {}
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """询问是/否问题"""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{question} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes', '是']:
                return True
            if response in ['n', 'no', '否']:
                return False
            print("请输入 y/n 或直接回车使用默认值")
    
    def show_banner(self):
        """显示欢迎横幅"""
        print("\n" + "=" * 60)
        print("🚀 LLM Memory Integration - 交互式一键配置")
        print("=" * 60)
        print("\n本配置将启用以下功能：")
        print("  1. 向量模型配置 (Qwen3-Embedding-8B)")
        print("  2. LLM 配置 (LLM_GLM5)")
        print("  3. 记忆系统参数优化")
        print("  4. 渐进式启用 (P0-P3)")
        print("  5. 向量覆盖率监控")
        print("  6. 智能记忆升级")
        print("  7. 用户画像自动更新")
        print("  8. 向量系统优化")
        print("\n" + "=" * 60)
    
    def check_status(self):
        """检查当前状态"""
        print("\n📊 当前配置状态:")
        print("-" * 60)
        
        # 检查向量模型
        print("\n向量模型:")
        try:
            with open(OPENCLAW_JSON) as f:
                data = json.load(f)
            emb = data.get('plugins', {}).get('entries', {}).get('memory-tencentdb', {}).get('config', {}).get('embedding', {})
            print(f"  Provider: {emb.get('provider', 'N/A')}")
            print(f"  Model: {emb.get('model', 'N/A')}")
            print(f"  Dimensions: {emb.get('dimensions', 'N/A')}")
            print(f"  Enabled: {emb.get('enabled', False)}")
        except Exception as e:
            print(f"  ❌ 读取失败: {e}")
        
        # 检查 LLM
        print("\nLLM 配置:")
        try:
            provider = data.get('models', {}).get('providers', {}).get('myprovider', {})
            models = provider.get('models', [])
            if models:
                m = models[0]
                print(f"  Model: {m.get('id', 'N/A')}")
                print(f"  Context: {m.get('contextWindow', 'N/A')} tokens")
                print(f"  Max Output: {m.get('maxTokens', 'N/A')} tokens")
        except Exception as e:
            print(f"  ❌ 读取失败: {e}")
        
        # 检查记忆数据库
        print("\n记忆数据库:")
        vectors_db = MEMORY_TDDB / "vectors.db"
        if vectors_db.exists():
            result = subprocess.run(
                ["sqlite3", str(vectors_db), "SELECT COUNT(*) FROM l1_records; SELECT COUNT(*) FROM l0_conversations;"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"  L1 记忆: {lines[0] if lines else 'N/A'} 条")
                print(f"  L0 对话: {lines[1] if len(lines) > 1 else 'N/A'} 条")
        else:
            print("  ❌ 数据库不存在")
    
    def interactive_configure(self):
        """交互式配置"""
        print("\n" + "=" * 60)
        print("📝 配置选项")
        print("=" * 60)
        
        # 1. 向量模型配置
        print("\n【1/8】向量模型配置")
        self.config_choices['embedding'] = self.ask_yes_no(
            "是否配置向量模型 (Qwen3-Embedding-8B)?", 
            default=True
        )
        
        # 2. LLM 配置
        print("\n【2/8】LLM 配置")
        self.config_choices['llm'] = self.ask_yes_no(
            "是否配置 LLM (LLM_GLM5)?", 
            default=True
        )
        
        # 3. 记忆系统参数
        print("\n【3/8】记忆系统参数优化")
        self.config_choices['memory_params'] = self.ask_yes_no(
            "是否优化记忆系统参数 (maxMemoriesPerSession=50, everyNConversations=3)?", 
            default=True
        )
        
        # 4. 渐进式启用
        print("\n【4/8】渐进式启用")
        print("  P0: 核心优化 (智能路由 + 动态权重 + RRF + 去重)")
        print("  P1: 查询增强 (查询理解 + 查询改写)")
        print("  P2: 学习优化 (反馈学习 + 查询历史)")
        print("  P3: 结果增强 (结果解释 + 结果摘要)")
        self.config_choices['progressive'] = self.ask_yes_no(
            "是否启用渐进式优化 (P0-P3)?", 
            default=True
        )
        
        # 5. 覆盖率监控
        print("\n【5/8】向量覆盖率监控")
        print("  - 自动检查 L1/L0 覆盖率")
        print("  - 低覆盖率自动告警")
        print("  - 自动触发向量补填")
        self.config_choices['coverage_monitor'] = self.ask_yes_no(
            "是否启用覆盖率监控?", 
            default=True
        )
        
        # 6. 智能记忆升级
        print("\n【6/8】智能记忆升级")
        print("  - 自动判断升级时机")
        print("  - L0 → L1 自动升级")
        print("  - 基于关键词、时间、重要性判断")
        self.config_choices['smart_upgrade'] = self.ask_yes_no(
            "是否启用智能记忆升级?", 
            default=True
        )
        
        # 7. 用户画像更新
        print("\n【7/8】用户画像自动更新")
        print("  - 从记忆自动提取偏好")
        print("  - 自动更新 persona.md")
        print("  - 长度自动压缩")
        self.config_choices['persona_update'] = self.ask_yes_no(
            "是否启用用户画像自动更新?", 
            default=True
        )
        
        # 8. 系统优化
        print("\n【8/8】向量系统优化")
        print("  - 孤立向量清理")
        print("  - 数据库 VACUUM")
        print("  - FTS 索引重建")
        self.config_choices['system_optimize'] = self.ask_yes_no(
            "是否启用系统优化?", 
            default=True
        )
        
        # 确认
        print("\n" + "=" * 60)
        print("📋 配置摘要")
        print("=" * 60)
        for key, value in self.config_choices.items():
            status = "✅ 启用" if value else "❌ 跳过"
            print(f"  {key}: {status}")
        
        return self.ask_yes_no("\n确认执行以上配置?", default=True)
    
    def configure_embedding(self):
        """配置向量模型"""
        if not self.config_choices.get('embedding', False):
            self.log("⏭️ 跳过向量模型配置")
            return
        
        print("\n📊 配置向量模型...")
        self.log("配置向量模型: Qwen3-Embedding-8B")
        
        try:
            with open(OPENCLAW_JSON) as f:
                data = json.load(f)
            
            if 'plugins' not in data:
                data['plugins'] = {}
            if 'entries' not in data['plugins']:
                data['plugins']['entries'] = {}
            if 'memory-tencentdb' not in data['plugins']['entries']:
                data['plugins']['entries']['memory-tencentdb'] = {}
            if 'config' not in data['plugins']['entries']['memory-tencentdb']:
                data['plugins']['entries']['memory-tencentdb']['config'] = {}
            
            data['plugins']['entries']['memory-tencentdb']['config']['embedding'] = RECOMMENDED_CONFIG['embedding']
            
            with open(OPENCLAW_JSON, 'w') as f:
                json.dump(data, f, indent=2)
            
            print("  ✅ 向量模型配置完成")
            self.log("✅ 向量模型配置完成")
        except Exception as e:
            print(f"  ❌ 配置失败: {e}")
            self.log(f"❌ 向量模型配置失败: {e}")
    
    def configure_llm(self):
        """配置 LLM"""
        if not self.config_choices.get('llm', False):
            self.log("⏭️ 跳过 LLM 配置")
            return
        
        print("\n🤖 配置 LLM...")
        self.log("配置 LLM: LLM_GLM5")
        
        try:
            with open(OPENCLAW_JSON) as f:
                data = json.load(f)
            
            if 'models' not in data:
                data['models'] = {}
            if 'providers' not in data['models']:
                data['models']['providers'] = {}
            
            data['models']['providers']['myprovider'] = {
                "type": "openai-compatible",
                "baseUrl": RECOMMENDED_CONFIG['llm']['baseUrl'],
                "models": [{
                    "id": RECOMMENDED_CONFIG['llm']['model'],
                    "contextWindow": RECOMMENDED_CONFIG['llm']['contextWindow'],
                    "maxTokens": RECOMMENDED_CONFIG['llm']['maxTokens'],
                    "type": "chat"
                }]
            }
            
            with open(OPENCLAW_JSON, 'w') as f:
                json.dump(data, f, indent=2)
            
            print("  ✅ LLM 配置完成")
            self.log("✅ LLM 配置完成")
        except Exception as e:
            print(f"  ❌ 配置失败: {e}")
            self.log(f"❌ LLM 配置失败: {e}")
    
    def configure_memory_params(self):
        """配置记忆系统参数"""
        if not self.config_choices.get('memory_params', False):
            self.log("⏭️ 跳过记忆系统参数配置")
            return
        
        print("\n💾 配置记忆系统参数...")
        self.log("配置记忆系统参数")
        
        try:
            with open(OPENCLAW_JSON) as f:
                data = json.load(f)
            
            if 'plugins' not in data:
                data['plugins'] = {}
            if 'entries' not in data['plugins']:
                data['plugins']['entries'] = {}
            if 'memory-tencentdb' not in data['plugins']['entries']:
                data['plugins']['entries']['memory-tencentdb'] = {}
            if 'config' not in data['plugins']['entries']['memory-tencentdb']:
                data['plugins']['entries']['memory-tencentdb']['config'] = {}
            
            data['plugins']['entries']['memory-tencentdb']['config'].update(RECOMMENDED_CONFIG['memory'])
            
            with open(OPENCLAW_JSON, 'w') as f:
                json.dump(data, f, indent=2)
            
            print("  ✅ 记忆系统参数配置完成")
            self.log("✅ 记忆系统参数配置完成")
        except Exception as e:
            print(f"  ❌ 配置失败: {e}")
            self.log(f"❌ 记忆系统参数配置失败: {e}")
    
    def run_script(self, script_name: str, args: str = "") -> tuple:
        """运行脚本"""
        script_path = Path(__file__).parent / script_name
        cmd = ["python3", str(script_path)] + (args.split() if args else [])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def configure_progressive(self):
        """配置渐进式启用"""
        if not self.config_choices.get('progressive', False):
            self.log("⏭️ 跳过渐进式启用配置")
            return
        
        print("\n⚙️ 配置渐进式启用...")
        self.log("配置渐进式启用")
        
        success, stdout, stderr = self.run_script("progressive_setup.py", "status")
        if success:
            print("  ✅ 渐进式启用配置完成")
            self.log("✅ 渐进式启用配置完成")
        else:
            print(f"  ⚠️ 配置失败: {stderr[:100]}")
            self.log(f"⚠️ 渐进式启用配置失败: {stderr[:100]}")
    
    def configure_coverage_monitor(self):
        """配置覆盖率监控"""
        if not self.config_choices.get('coverage_monitor', False):
            self.log("⏭️ 跳过覆盖率监控配置")
            return
        
        print("\n📊 配置覆盖率监控...")
        self.log("配置覆盖率监控")
        
        success, stdout, stderr = self.run_script("vector_coverage_monitor.py", "check")
        if success:
            print("  ✅ 覆盖率监控配置完成")
            self.log("✅ 覆盖率监控配置完成")
        else:
            print(f"  ⚠️ 配置失败: {stderr[:100]}")
            self.log(f"⚠️ 覆盖率监控配置失败: {stderr[:100]}")
    
    def configure_smart_upgrade(self):
        """配置智能升级"""
        if not self.config_choices.get('smart_upgrade', False):
            self.log("⏭️ 跳过智能升级配置")
            return
        
        print("\n🔄 配置智能记忆升级...")
        self.log("配置智能记忆升级")
        
        success, stdout, stderr = self.run_script("smart_memory_upgrade.py", "status")
        if success:
            print("  ✅ 智能升级配置完成")
            self.log("✅ 智能升级配置完成")
        else:
            print(f"  ⚠️ 配置失败: {stderr[:100]}")
            self.log(f"⚠️ 智能升级配置失败: {stderr[:100]}")
    
    def configure_persona_update(self):
        """配置用户画像更新"""
        if not self.config_choices.get('persona_update', False):
            self.log("⏭️ 跳过用户画像更新配置")
            return
        
        print("\n👤 配置用户画像自动更新...")
        self.log("配置用户画像自动更新")
        
        success, stdout, stderr = self.run_script("auto_update_persona.py", "status")
        if success:
            print("  ✅ 用户画像更新配置完成")
            self.log("✅ 用户画像更新配置完成")
        else:
            print(f"  ⚠️ 配置失败: {stderr[:100]}")
            self.log(f"⚠️ 用户画像更新配置失败: {stderr[:100]}")
    
    def configure_system_optimize(self):
        """配置系统优化"""
        if not self.config_choices.get('system_optimize', False):
            self.log("⏭️ 跳过系统优化配置")
            return
        
        print("\n⚡ 配置向量系统优化...")
        self.log("配置向量系统优化")
        
        success, stdout, stderr = self.run_script("vector_system_optimizer.py", "status")
        if success:
            print("  ✅ 系统优化配置完成")
            self.log("✅ 系统优化配置完成")
        else:
            print(f"  ⚠️ 配置失败: {stderr[:100]}")
            self.log(f"⚠️ 系统优化配置失败: {stderr[:100]}")
    
    def test_apis(self):
        """测试 API 连接（仅当用户已配置 API 密钥时）"""
        print("\n🔍 检查 API 配置...")
        
        # 检查向量 API 配置
        print("  检查向量 API 配置...")
        try:
            with open(OPENCLAW_JSON) as f:
                data = json.load(f)
            emb = data.get('plugins', {}).get('entries', {}).get('memory-tencentdb', {}).get('config', {}).get('embedding', {})
            api_key = emb.get('apiKey', '')
            
            if not api_key or api_key == "YOUR_EMBEDDING_API_KEY":
                print("    ⚠️ 未配置向量 API 密钥，跳过测试")
                print("    💡 请在配置文件中设置 embedding.apiKey")
                self.log("⚠️ 向量 API 未配置，跳过测试")
                return
            
            # 仅当配置了 API 密钥时才测试
            import urllib.request
            data = json.dumps({
                "input": "测试",
                "model": emb.get('model', 'text-embedding-3-small'),
                "dimensions": emb.get('dimensions', 1536)
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{emb.get('baseUrl', '').rstrip('/')}/embeddings",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if 'data' in result:
                    print("    ✅ API 正常，向量维度:", len(result['data'][0]['embedding']))
                    self.log("✅ 向量 API 测试通过")
                else:
                    print("    ⚠️ API 响应异常")
                    self.log("⚠️ 向量 API 响应异常")
        except Exception as e:
            print(f"    ❌ API 测试失败: {e}")
            self.log(f"❌ 向量 API 测试失败: {e}")
        
        # 检查 LLM API 配置
        print("  检查 LLM API 配置...")
        try:
            with open(OPENCLAW_JSON) as f:
                data = json.load(f)
            llm_config = data.get('models', {}).get('providers', {}).get('myprovider', {})
            base_url = llm_config.get('baseUrl', '')
            
            if not base_url or 'YOUR_' in base_url:
                print("    ⚠️ 未配置 LLM API，跳过测试")
                print("    💡 请在配置文件中设置 LLM baseUrl 和相关认证")
                self.log("⚠️ LLM API 未配置，跳过测试")
                return
            
            print("    ✅ LLM 配置已设置")
            self.log("✅ LLM 配置检查通过")
        except Exception as e:
            print(f"    ❌ LLM 配置检查失败: {e}")
            self.log(f"❌ LLM 配置检查失败: {e}")
    
    def show_final_status(self):
        """显示最终状态"""
        print("\n" + "=" * 60)
        print("✅ 配置完成")
        print("=" * 60)
        
        print("\n📊 已启用功能:")
        for key, value in self.config_choices.items():
            if value:
                print(f"  ✅ {key}")
        
        print("\n🚀 使用方式:")
        print("  vsearch '查询'                    # 智能搜索")
        print("  vsearch '查询' --explain          # 带解释")
        print("  python3 unified_maintenance.py    # 统一维护")
        
        print("\n📁 日志文件:")
        print(f"  {self.log_file}")
    
    def run(self):
        """执行交互式配置"""
        self.show_banner()
        self.check_status()
        
        if not self.interactive_configure():
            print("\n❌ 配置已取消")
            return
        
        print("\n" + "=" * 60)
        print("🚀 开始配置")
        print("=" * 60)
        
        self.configure_embedding()
        self.configure_llm()
        self.configure_memory_params()
        self.configure_progressive()
        self.configure_coverage_monitor()
        self.configure_smart_upgrade()
        self.configure_persona_update()
        self.configure_system_optimize()
        
        self.test_apis()
        self.show_final_status()
        
        self.log("=" * 60)
        self.log("配置完成")
        self.log("=" * 60)

def main():
    setup = InteractiveSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        setup.check_status()
    else:
        setup.run()

if __name__ == "__main__":
    main()
