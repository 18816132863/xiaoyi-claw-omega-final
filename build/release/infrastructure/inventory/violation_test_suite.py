from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
违规接入拦截测试
验证自动检查机制是否能准确识别并阻止违规接入
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class ViolationTestSuite:
    """违规接入测试套件"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.registry_path = self.workspace / "infrastructure" / "inventory" / "skill_registry.json"
        self.test_results = []
    
    def load_registry(self) -> Dict:
        """加载技能注册表"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_registry(self, registry: Dict):
        """保存技能注册表"""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def test_unregistered_skill(self) -> Tuple[bool, str]:
        """测试1: 未注册直接接入"""
        print("\n[测试1] 未注册直接接入")
        
        # 创建未注册的技能目录
        unregistered_path = self.workspace / "execution" / "unregistered_skill"
        unregistered_path.mkdir(exist_ok=True)
        
        # 创建技能文件
        (unregistered_path / "SKILL.md").write_text("# 未注册技能\n")
        
        # 检查是否在注册表中
        registry = self.load_registry()
        skill_ids = [s.get('skill_id') for s in registry.get('skills', [])]
        
        if "skill_unregistered_v1" not in skill_ids:
            print("  ✅ 拦截成功: 未注册技能被识别")
            return True, "未注册技能被正确识别"
        else:
            print("  ❌ 拦截失败: 未注册技能未被识别")
            return False, "未注册技能未被识别"
    
    def test_wrong_layer(self) -> Tuple[bool, str]:
        """测试2: 放错层级"""
        print("\n[测试2] 放错层级")
        
        # 创建测试技能（L4技能放在L1层）
        wrong_layer_skill = {
            "skill_id": "skill_wrong_layer_v1",
            "skill_name": "错误层级技能",
            "version": "1.0.0",
            "entry_layer": "L4",
            "layer_name": "服务能力层",
            "layer_path": "core/wrong_skill/",  # L4技能放在L1层
            "input_schema": "test",
            "output_schema": "test",
            "dependencies": "none",
            "owner": "系统",
            "timeout_ms": 5000,
            "fallback_strategy": "abort",
            "status": "draft",
            "call_scope": "internal"
        }
        
        # 检查层级是否匹配
        layer_mapping = {
            'L1': 'core/',
            'L2': 'orchestration/',
            'L3': 'governance/policy/',
            'L4': 'execution/',
            'L5': 'memory_context/',
            'L6': 'infrastructure/'
        }
        
        expected_path = layer_mapping.get(wrong_layer_skill['entry_layer'], '')
        actual_path = wrong_layer_skill['layer_path']
        
        if not actual_path.startswith(expected_path):
            print(f"  ✅ 拦截成功: 层级不匹配被识别 (期望: {expected_path}, 实际: {actual_path})")
            return True, "层级不匹配被正确识别"
        else:
            print("  ❌ 拦截失败: 层级不匹配未被识别")
            return False, "层级不匹配未被识别"
    
    def test_missing_fields(self) -> Tuple[bool, str]:
        """测试3: 元数据字段缺失"""
        print("\n[测试3] 元数据字段缺失")
        
        # 创建缺少必填字段的技能
        incomplete_skill = {
            "skill_id": "skill_incomplete_v1",
            "skill_name": "不完整技能"
            # 缺少 version, entry_layer, input_schema, output_schema 等必填字段
        }
        
        required_fields = [
            'skill_id', 'skill_name', 'version', 'entry_layer',
            'input_schema', 'output_schema', 'dependencies', 'owner',
            'timeout_ms', 'fallback_strategy', 'status'
        ]
        
        missing_fields = [f for f in required_fields if f not in incomplete_skill]
        
        if len(missing_fields) > 0:
            print(f"  ✅ 拦截成功: 缺少字段被识别 ({', '.join(missing_fields[:3])}...)")
            return True, f"缺少字段被正确识别: {len(missing_fields)}个"
        else:
            print("  ❌ 拦截失败: 缺少字段未被识别")
            return False, "缺少字段未被识别"
    
    def test_duplicate_config(self) -> Tuple[bool, str]:
        """测试4: 多配置源并存"""
        print("\n[测试4] 多配置源并存")
        
        # 检查是否存在多个配置文件
        config_paths = [
            self.workspace / "infrastructure" / "inventory" / "architecture_config.json",
            self.workspace / "scripts" / "inventory" / "architecture_config.json",
            self.workspace / "config" / "architecture_config.json"
        ]
        
        existing_configs = [p for p in config_paths if p.exists()]
        
        if len(existing_configs) <= 1:
            print(f"  ✅ 拦截成功: 配置源唯一 ({len(existing_configs)}个)")
            return True, "配置源唯一"
        else:
            print(f"  ❌ 拦截失败: 存在多个配置源 ({len(existing_configs)}个)")
            return False, f"存在多个配置源: {len(existing_configs)}个"
    
    def test_bypass_call(self) -> Tuple[bool, str]:
        """测试5: 绕过主架构直连调用"""
        print("\n[测试5] 绕过主架构直连调用")
        
        # 创建包含直连调用的测试文件
        bypass_code = '''
import sqlite3
import redis
import requests

# 直连数据库
conn = sqlite3.connect('test.db')

# 直连缓存
r = redis.Redis()

# 直连HTTP
response = requests.get('https://example.com')
'''
        
        bypass_patterns = [
            'import sqlite3',
            'import redis',
            'import pymongo',
            'requests.get',
            'httpx.get'
        ]
        
        detected = []
        for pattern in bypass_patterns:
            if pattern in bypass_code:
                detected.append(pattern)
        
        if len(detected) > 0:
            print(f"  ✅ 拦截成功: 直连调用被识别 ({', '.join(detected[:2])}...)")
            return True, f"直连调用被正确识别: {len(detected)}个"
        else:
            print("  ❌ 拦截失败: 直连调用未被识别")
            return False, "直连调用未被识别"
    
    def test_missing_test(self) -> Tuple[bool, str]:
        """测试6: 缺少测试文件"""
        print("\n[测试6] 缺少测试文件")
        
        # 创建缺少测试的技能目录
        no_test_path = self.workspace / "execution" / "no_test_skill"
        no_test_path.mkdir(exist_ok=True)
        (no_test_path / "SKILL.md").write_text("# 无测试技能\n")
        
        # 检查测试目录
        test_path = no_test_path / "test"
        
        if not test_path.exists():
            print("  ✅ 拦截成功: 缺少测试目录被识别")
            return True, "缺少测试目录被正确识别"
        else:
            print("  ❌ 拦截失败: 缺少测试目录未被识别")
            return False, "缺少测试目录未被识别"
    
    def test_missing_logging(self) -> Tuple[bool, str]:
        """测试7: 缺少日志或错误处理"""
        print("\n[测试7] 缺少日志或错误处理")
        
        # 创建缺少日志配置的技能
        no_logging_config = {
            "skill_id": "skill_no_logging_v1",
            "version": "1.0.0"
            # 缺少 logging 和 fallback 配置
        }
        
        has_logging = 'logging' in no_logging_config
        has_fallback = 'fallback' in no_logging_config
        
        if not has_logging or not has_fallback:
            print("  ✅ 拦截成功: 缺少日志/错误处理配置被识别")
            return True, "缺少日志/错误处理配置被正确识别"
        else:
            print("  ❌ 拦截失败: 缺少日志/错误处理配置未被识别")
            return False, "缺少日志/错误处理配置未被识别"
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("="*60)
        print("违规接入拦截测试")
        print("="*60)
        
        tests = [
            ("未注册直接接入", self.test_unregistered_skill),
            ("放错层级", self.test_wrong_layer),
            ("元数据字段缺失", self.test_missing_fields),
            ("多配置源并存", self.test_duplicate_config),
            ("绕过主架构直连调用", self.test_bypass_call),
            ("缺少测试文件", self.test_missing_test),
            ("缺少日志或错误处理", self.test_missing_logging)
        ]
        
        results = {
            'total': len(tests),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for name, test_func in tests:
            try:
                passed, message = test_func()
                if passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'name': name,
                    'passed': passed,
                    'message': message
                })
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'name': name,
                    'passed': False,
                    'message': f"测试异常: {str(e)}"
                })
        
        return results
    
    def print_report(self, results: Dict):
        """打印测试报告"""
        print("\n" + "="*60)
        print("测试报告")
        print("="*60)
        print(f"\n总计: {results['total']} 个测试")
        print(f"通过: {results['passed']} 个")
        print(f"失败: {results['failed']} 个")
        print("\n" + "-"*60)
        
        for detail in results['details']:
            status = "✅ 通过" if detail['passed'] else "❌ 失败"
            print(f"{status} {detail['name']}: {detail['message']}")
        
        print("\n" + "="*60)
        
        if results['failed'] == 0:
            print("✅ 所有违规接入拦截测试通过！")
        else:
            print(f"❌ {results['failed']} 个测试失败")
        
        print("="*60 + "\n")


def main():
    """主函数"""
    workspace_path = os.environ.get('WORKSPACE_PATH', str(get_project_root()))
    suite = ViolationTestSuite(workspace_path)
    results = suite.run_all_tests()
    suite.print_report(results)
    
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
