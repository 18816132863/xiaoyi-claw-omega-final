#!/usr/bin/env python3
"""
元数据一致性验证脚本

验证 SKILL.md、_meta.json、install.json 三个文件的元数据是否一致。
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_yaml_frontmatter(file_path: Path) -> Dict:
    """从 SKILL.md 提取 YAML frontmatter（简化版）"""
    content = file_path.read_text(encoding='utf-8')
    
    # 提取 YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    yaml_content = match.group(1)
    
    # 使用简单的正则提取 config 列表
    result = {
        'metadata': {
            'openclaw': {
                'requires': {
                    'config': []
                },
                'capabilities': []
            }
        }
    }
    
    # 提取 config 列表
    config_match = re.search(r'config:\s*\n((?:\s+- .+\n)+)', yaml_content)
    if config_match:
        config_lines = config_match.group(1)
        config_items = re.findall(r'-\s+(.+)', config_lines)
        result['metadata']['openclaw']['requires']['config'] = config_items
    
    # 提取 capabilities 列表
    capabilities_match = re.search(r'capabilities:\s*\n((?:\s+- .+\n)+)', yaml_content)
    if capabilities_match:
        capabilities_lines = capabilities_match.group(1)
        capabilities_items = re.findall(r'-\s+(.+)', capabilities_lines)
        result['metadata']['openclaw']['capabilities'] = capabilities_items
    
    return result


def extract_config_paths_from_skillmd(yaml_data: Dict) -> Tuple[Set[str], Set[str]]:
    """从 SKILL.md 提取配置路径"""
    read_paths = set()
    write_paths = set()
    
    config = yaml_data.get('metadata', {}).get('openclaw', {}).get('requires', {}).get('config', [])
    
    for path in config:
        if isinstance(path, str):
            if path.startswith('filesystem.read.'):
                read_paths.add(path.replace('filesystem.read.', ''))
            elif path.startswith('filesystem.write.'):
                write_paths.add(path.replace('filesystem.write.', ''))
    
    return read_paths, write_paths


def extract_config_paths_from_meta_json(meta_data: Dict) -> Tuple[Set[str], Set[str]]:
    """从 _meta.json 提取配置路径"""
    read_paths = set()
    write_paths = set()
    
    # 从 requiredConfigPaths 提取
    for path in meta_data.get('requiredConfigPaths', []):
        if path.startswith('filesystem.read.'):
            read_paths.add(path.replace('filesystem.read.', ''))
        elif path.startswith('filesystem.write.'):
            write_paths.add(path.replace('filesystem.write.', ''))
    
    # 从 requirements.filesystem 提取
    filesystem = meta_data.get('requirements', {}).get('filesystem', {})
    for path in filesystem.get('read', []):
        read_paths.add(path)
    for path in filesystem.get('write', []):
        write_paths.add(path)
    
    return read_paths, write_paths


def extract_config_paths_from_install_json(install_data: Dict) -> Tuple[Set[str], Set[str]]:
    """从 install.json 提取配置路径"""
    read_paths = set()
    write_paths = set()
    
    required_paths = install_data.get('required_config_paths', {})
    
    for item in required_paths.get('read', []):
        if isinstance(item, dict):
            read_paths.add(item.get('path', ''))
        else:
            read_paths.add(item)
    
    for item in required_paths.get('write', []):
        if isinstance(item, dict):
            write_paths.add(item.get('path', ''))
        else:
            write_paths.add(item)
    
    return read_paths, write_paths


def normalize_path(path: str) -> str:
    """标准化路径"""
    # 展开 ~ 为 ~/.openclaw
    if path.startswith('~') and not path.startswith('~/.openclaw'):
        path = path.replace('~', '~/.openclaw', 1)
    return path.rstrip('/')


def verify_metadata_consistency(skill_dir: Path) -> bool:
    """验证元数据一致性"""
    print("🔍 验证元数据一致性...\n")
    
    # 读取文件
    skillmd_path = skill_dir / 'SKILL.md'
    meta_json_path = skill_dir / '_meta.json'
    install_json_path = skill_dir / 'install.json'
    
    if not skillmd_path.exists():
        print("❌ SKILL.md 不存在")
        return False
    
    if not meta_json_path.exists():
        print("❌ _meta.json 不存在")
        return False
    
    if not install_json_path.exists():
        print("❌ install.json 不存在")
        return False
    
    # 提取数据
    yaml_data = extract_yaml_frontmatter(skillmd_path)
    meta_data = json.loads(meta_json_path.read_text(encoding='utf-8'))
    install_data = json.loads(install_json_path.read_text(encoding='utf-8'))
    
    # 提取配置路径
    skillmd_read, skillmd_write = extract_config_paths_from_skillmd(yaml_data)
    meta_read, meta_write = extract_config_paths_from_meta_json(meta_data)
    install_read, install_write = extract_config_paths_from_install_json(install_data)
    
    # 标准化路径
    skillmd_read = {normalize_path(p) for p in skillmd_read}
    skillmd_write = {normalize_path(p) for p in skillmd_write}
    meta_read = {normalize_path(p) for p in meta_read}
    meta_write = {normalize_path(p) for p in meta_write}
    install_read = {normalize_path(p) for p in install_read}
    install_write = {normalize_path(p) for p in install_write}
    
    # 比较读取路径
    print("📁 读取路径对比:")
    print(f"  SKILL.md:      {sorted(skillmd_read)}")
    print(f"  _meta.json:    {sorted(meta_read)}")
    print(f"  install.json:  {sorted(install_read)}")
    
    read_consistent = skillmd_read == meta_read == install_read
    if read_consistent:
        print("  ✅ 读取路径一致\n")
    else:
        print("  ❌ 读取路径不一致")
        if skillmd_read != meta_read:
            print(f"     SKILL.md vs _meta.json: {skillmd_read.symmetric_difference(meta_read)}")
        if skillmd_read != install_read:
            print(f"     SKILL.md vs install.json: {skillmd_read.symmetric_difference(install_read)}")
        if meta_read != install_read:
            print(f"     _meta.json vs install.json: {meta_read.symmetric_difference(install_read)}")
        print()
    
    # 比较写入路径
    print("📝 写入路径对比:")
    print(f"  SKILL.md:      {sorted(skillmd_write)}")
    print(f"  _meta.json:    {sorted(meta_write)}")
    print(f"  install.json:  {sorted(install_write)}")
    
    write_consistent = skillmd_write == meta_write == install_write
    if write_consistent:
        print("  ✅ 写入路径一致\n")
    else:
        print("  ❌ 写入路径不一致")
        if skillmd_write != meta_write:
            print(f"     SKILL.md vs _meta.json: {skillmd_write.symmetric_difference(meta_write)}")
        if skillmd_write != install_write:
            print(f"     SKILL.md vs install.json: {skillmd_write.symmetric_difference(install_write)}")
        if meta_write != install_write:
            print(f"     _meta.json vs install.json: {meta_write.symmetric_difference(install_write)}")
        print()
    
    # 检查高风险能力声明
    print("⚠️  高风险能力声明:")
    
    # SKILL.md
    skillmd_capabilities = yaml_data.get('metadata', {}).get('openclaw', {}).get('capabilities', [])
    print(f"  SKILL.md capabilities: {skillmd_capabilities}")
    
    # _meta.json
    meta_capabilities = meta_data.get('requirements', {}).get('capabilities', [])
    print(f"  _meta.json capabilities: {meta_capabilities}")
    
    # install.json
    install_capabilities = list(install_data.get('declared_capabilities', {}).keys())
    print(f"  install.json capabilities: {install_capabilities}")
    
    capabilities_consistent = set(skillmd_capabilities) == set(meta_capabilities) == set(install_capabilities)
    if capabilities_consistent:
        print("  ✅ 高风险能力声明一致\n")
    else:
        print("  ❌ 高风险能力声明不一致\n")
    
    # 总结
    all_consistent = read_consistent and write_consistent and capabilities_consistent
    
    print("=" * 60)
    if all_consistent:
        print("✅ 元数据一致性验证通过")
        print("\nClawHub 安全扫描应该能够正确识别声明的权限。")
    else:
        print("❌ 元数据一致性验证失败")
        print("\n请修复上述不一致问题后重新验证。")
    print("=" * 60)
    
    return all_consistent


def main():
    """主函数"""
    skill_dir = Path(__file__).parent.parent
    
    success = verify_metadata_consistency(skill_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
