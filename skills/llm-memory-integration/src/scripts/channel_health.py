#!/usr/bin/env python3
"""
通道健康检查脚本
检查 xiaoyi-channel 连接状态
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
HEALTH_LOG = WORKSPACE / "memory" / "channel_health.json"

class ChannelHealthChecker:
    """通道健康检查器"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
        return {}
    
    def get_channel_config(self):
        """获取通道配置"""
        return self.config.get("channels", {}).get("xiaoyi-channel", {})
    
    def check_gateway_health(self):
        """检查 Gateway 健康状态"""
        try:
            response = requests.get(
                "http://127.0.0.1:18789/health",
                timeout=5
            )
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_channel_config(self):
        """检查通道配置完整性"""
        channel = self.get_channel_config()
        
        required_fields = ["wsUrl1", "apiKey", "agentId", "enabled"]
        missing = [f for f in required_fields if not channel.get(f)]
        
        return {
            "success": len(missing) == 0,
            "enabled": channel.get("enabled", False),
            "missing_fields": missing,
            "has_api_key": bool(channel.get("apiKey")),
            "has_agent_id": bool(channel.get("agentId"))
        }
    
    def save_result(self, result):
        """保存检查结果"""
        HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
        
        if HEALTH_LOG.exists():
            results = json.loads(HEALTH_LOG.read_text())
        else:
            results = []
        
        results.append(result)
        
        # 保留最近100条
        if len(results) > 100:
            results = results[-100:]
        
        HEALTH_LOG.write_text(json.dumps(results, indent=2))
    
    def run_check(self):
        """运行健康检查"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "gateway": self.check_gateway_health(),
            "channel_config": self.check_channel_config()
        }
        
        self.save_result(result)
        return result
    
    def print_report(self):
        """打印健康报告"""
        print("=" * 60)
        print("   通道健康报告")
        print("=" * 60)
        print(f"检查时间: {datetime.now().isoformat()}")
        print()
        
        # Gateway 检查
        gateway = self.check_gateway_health()
        status = "✅" if gateway["success"] else "❌"
        print(f"{status} Gateway")
        if gateway["success"]:
            print(f"   - 响应时间: {gateway['response_time_ms']}ms")
        else:
            print(f"   - 错误: {gateway.get('error', 'unknown')}")
        
        print()
        
        # 通道配置检查
        config = self.check_channel_config()
        status = "✅" if config["success"] else "⚠️"
        print(f"{status} 通道配置")
        print(f"   - 已启用: {'是' if config['enabled'] else '否'}")
        print(f"   - API Key: {'已配置' if config['has_api_key'] else '未配置'}")
        print(f"   - Agent ID: {'已配置' if config['has_agent_id'] else '未配置'}")
        
        if config["missing_fields"]:
            print(f"   - 缺失字段: {', '.join(config['missing_fields'])}")
        
        # 历史统计
        if HEALTH_LOG.exists():
            results = json.loads(HEALTH_LOG.read_text())
            if results:
                success_count = sum(1 for r in results if r.get("gateway", {}).get("success"))
                print()
                print(f"历史统计 (最近{len(results)}次检查):")
                print(f"   - Gateway 成功率: {success_count}/{len(results)} ({success_count*100//len(results)}%)")

def main():
    checker = ChannelHealthChecker()
    checker.run_check()
    checker.print_report()

if __name__ == "__main__":
    main()
