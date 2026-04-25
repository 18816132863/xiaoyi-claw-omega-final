from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
新增技能自动接入检查机制
检查新增技能是否符合六层架构规范
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class SkillAccessChecker:
    """技能接入检查器"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.registry_path = self.workspace / "infrastructure" / "inventory" / "skill_registry.json"
        self.architecture_config_path = self.workspace / "infrastructure" / "inventory" / "architecture_config.json"
        self.errors = []
        self.warnings = []
        
    def load_registry(self) -> Dict:
        """加载技能注册表"""
        if not self.registry_path.exists():
            return {"skills": []}
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_architecture_config(self) -> Dict:
        """加载架构配置"""
        if not self.architecture_config_path.exists():
            return {"layers": []}
        with open(self.architecture_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_layer_assignment(self, skill: Dict) -> bool:
        """检查1: 是否进入正确层级"""
        entry_layer = skill.get('entry_layer', '')
        layer_path = skill.get('layer_path', '')
        
        # 检查层级是否有效
        valid_layers = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
        if entry_layer not in valid_layers:
            self.errors.append(f"[层级错误] {skill.get('skill_id')}: entry_layer '{entry_layer}' 无效，必须是 L1-L6")
            return False
        
        # 检查路径是否匹配层级
        layer_mapping = {
            'L1': 'core/',
            'L2': 'orchestration/',
            'L3': 'governance/policy/',
            'L4': 'execution/',
            'L5': 'memory_context/',
            'L6': 'infrastructure/'
        }
        
        expected_path = layer_mapping.get(entry_layer, '')
        if expected_path and not layer_path.startswith(expected_path):
            self.warnings.append(f"[路径警告] {skill.get('skill_id')}: layer_path '{layer_path}' 与 entry_layer '{entry_layer}' 不匹配，期望以 '{expected_path}' 开头")
        
        return True
    
    def check_registration(self, skill: Dict) -> bool:
        """检查2: 是否完成统一注册"""
        registry = self.load_registry()
        skill_id = skill.get('skill_id')
        
        # 检查是否在注册表中
        registered_ids = [s.get('skill_id') for s in registry.get('skills', [])]
        if skill_id not in registered_ids:
            self.errors.append(f"[注册错误] {skill_id}: 未在 skill_registry.json 中注册")
            return False
        
        return True
    
    def check_required_fields(self, skill: Dict) -> bool:
        """检查3: 是否字段完整"""
        required_fields = [
            'skill_id',
            'skill_name',
            'version',
            'entry_layer',
            'input_schema',
            'output_schema',
            'dependencies',
            'owner',
            'timeout_ms',
            'fallback_strategy',
            'status'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in skill or not skill[field]:
                missing_fields.append(field)
        
        if missing_fields:
            self.errors.append(f"[字段错误] {skill.get('skill_id')}: 缺少必填字段: {', '.join(missing_fields)}")
            return False
        
        return True
    
    def check_config_uniqueness(self, skill: Dict) -> bool:
        """检查4: 是否配置唯一"""
        registry = self.load_registry()
        skill_id = skill.get('skill_id')
        
        # 检查 skill_id 是否重复
        skill_ids = [s.get('skill_id') for s in registry.get('skills', [])]
        if skill_ids.count(skill_id) > 1:
            self.errors.append(f"[配置错误] {skill_id}: skill_id 重复")
            return False
        
        return True
    
    def check_interface_compliance(self, skill: Dict) -> bool:
        """检查5: 是否接口合规"""
        layer_path = skill.get('layer_path', '')
        skill_path = self.workspace / layer_path
        
        # 检查必需文件
        required_files = ['SKILL.md', 'config.json']
        missing_files = []
        
        for file in required_files:
            if not (skill_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.warnings.append(f"[接口警告] {skill.get('skill_id')}: 缺少标准文件: {', '.join(missing_files)}")
        
        return len(missing_files) == 0
    
    def check_test_coverage(self, skill: Dict) -> bool:
        """检查6: 是否具备测试"""
        layer_path = skill.get('layer_path', '')
        skill_path = self.workspace / layer_path
        test_path = skill_path / 'test'
        
        # 检查测试目录
        if not test_path.exists():
            self.warnings.append(f"[测试警告] {skill.get('skill_id')}: 缺少测试目录")
            return False
        
        # 检查测试文件
        test_files = list(test_path.glob('test_*.py'))
        if not test_files:
            self.warnings.append(f"[测试警告] {skill.get('skill_id')}: 缺少测试文件")
            return False
        
        return True
    
    def check_logging_and_error_handling(self, skill: Dict) -> bool:
        """检查7: 是否具备日志和错误处理"""
        layer_path = skill.get('layer_path', '')
        skill_path = self.workspace / layer_path
        
        # 检查配置中的日志设置
        config_path = skill_path / 'config.json'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'logging' not in config:
                self.warnings.append(f"[日志警告] {skill.get('skill_id')}: config.json 中缺少 logging 配置")
            
            if 'fallback' not in config:
                self.warnings.append(f"[错误处理警告] {skill.get('skill_id')}: config.json 中缺少 fallback 配置")
        
        return True
    
    def check_no_bypass_calls(self, skill: Dict) -> bool:
        """检查8: 是否存在绕过主架构的直连调用"""
        layer_path = skill.get('layer_path', '')
        skill_path = self.workspace / layer_path
        
        # 检查代码文件中的直连调用
        bypass_patterns = [
            'import sqlite3',  # 直接访问数据库
            'import redis',    # 直接访问缓存
            'import pymongo',  # 直接访问MongoDB
            'requests.get',    # 直接HTTP调用
            'httpx.get',       # 直接HTTP调用
        ]
        
        for py_file in skill_path.glob('**/*.py'):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in bypass_patterns:
                    if pattern in content:
                        self.warnings.append(f"[绕过警告] {skill.get('skill_id')}: {py_file.name} 中存在直连调用 '{pattern}'，应通过统一服务访问")
        
        return True
    
    def check_skill(self, skill: Dict) -> Tuple[bool, List[str], List[str]]:
        """检查单个技能"""
        self.errors = []
        self.warnings = []
        
        # 执行所有检查
        self.check_layer_assignment(skill)
        self.check_registration(skill)
        self.check_required_fields(skill)
        self.check_config_uniqueness(skill)
        self.check_interface_compliance(skill)
        self.check_test_coverage(skill)
        self.check_logging_and_error_handling(skill)
        self.check_no_bypass_calls(skill)
        
        passed = len(self.errors) == 0
        return passed, self.errors.copy(), self.warnings.copy()
    
    def check_all_skills(self) -> Dict:
        """检查所有技能"""
        registry = self.load_registry()
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
        
        for skill in registry.get('skills', []):
            results['total'] += 1
            passed, errors, warnings = self.check_skill(skill)
            
            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
            
            results['warnings'] += len(warnings)
            
            results['details'].append({
                'skill_id': skill.get('skill_id'),
                'skill_name': skill.get('skill_name'),
                'passed': passed,
                'errors': errors,
                'warnings': warnings
            })
        
        return results
    
    def print_report(self, results: Dict):
        """打印检查报告"""
        print("\n" + "="*60)
        print("技能接入检查报告")
        print("="*60)
        print(f"\n总计: {results['total']} 个技能")
        print(f"通过: {results['passed']} 个")
        print(f"失败: {results['failed']} 个")
        print(f"警告: {results['warnings']} 个")
        print("\n" + "-"*60)
        
        for detail in results['details']:
            status = "✅ 通过" if detail['passed'] else "❌ 失败"
            print(f"\n{status} {detail['skill_name']} ({detail['skill_id']})")
            
            if detail['errors']:
                print("  错误:")
                for error in detail['errors']:
                    print(f"    - {error}")
            
            if detail['warnings']:
                print("  警告:")
                for warning in detail['warnings']:
                    print(f"    - {warning}")
        
        print("\n" + "="*60)
        
        if results['failed'] == 0:
            print("✅ 所有技能检查通过！")
        else:
            print(f"❌ {results['failed']} 个技能检查失败，请修复后重新检查。")
        
        print("="*60 + "\n")


def main():
    """主函数"""
    workspace_path = os.environ.get('WORKSPACE_PATH', str(get_project_root()))
    checker = SkillAccessChecker(workspace_path)
    results = checker.check_all_skills()
    checker.print_report(results)
    
    # 返回退出码
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
