#!/usr/bin/env python3
"""
自动融合钩子 - 在 git commit 前自动运行融合引擎

使用方式：
1. 作为 git pre-commit hook
2. 作为 Makefile 命令
3. 作为 CI/CD 步骤

V7.2.1 新增：
- 文档同步检查
- 代码变更 → 文档自动同步

V7.2.2 新增：
- 架构文档自动更新
- 新模块自动注册
- 能力矩阵自动更新

V8.8.3 新增：
- 模块融合引擎集成
- 手动创建模块自动融合
- 扫描未注册模块并自动注册
"""

import sys
import subprocess
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def run_fusion_check(root: Path) -> bool:
    """运行融合检查"""
    print("\n🔍 运行融合引擎检查...")
    
    # 1. 检查新文件是否在架构目录中
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=A'],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    new_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    if not new_files:
        print("  ✅ 没有新增文件")
        return True
    
    # 架构目录
    ARCH_DIRS = [
        'core/', 'memory_context/', 'orchestration/', 
        'execution/', 'skills/', 'governance/', 'infrastructure/',
        'tests/', 'scripts/', 'reports/', 'memory/', 'docs/'
    ]
    
    # 检查新文件
    not_in_arch = []
    for f in new_files:
        if f.endswith('.py') and not any(f.startswith(d) for d in ARCH_DIRS):
            not_in_arch.append(f)
    
    if not_in_arch:
        print("  ⚠️  以下文件未融入架构:")
        for f in not_in_arch:
            print(f"    - {f}")
        print("\n  建议运行: python infrastructure/fusion_engine.py --auto-fuse")
        return False
    
    print(f"  ✅ 所有新增文件 ({len(new_files)} 个) 已融入架构")
    return True


def run_fusion_engine(root: Path) -> bool:
    """运行融合引擎"""
    print("\n🔧 运行融合引擎...")
    
    result = subprocess.run(
        [sys.executable, str(root / 'infrastructure/fusion_engine.py'), '--execute'],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  ✅ 融合引擎执行成功")
        return True
    else:
        print(f"  ❌ 融合引擎执行失败: {result.stderr}")
        return False


def run_doc_sync(root: Path, execute: bool = False) -> bool:
    """运行文档同步"""
    print("\n📄 运行文档同步检查 (V2.0)...")
    
    cmd = [sys.executable, str(root / 'infrastructure/doc_sync_engine.py')]
    if execute:
        cmd.append('--execute')
    else:
        cmd.append('--scan')
    
    result = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        # 检查是否有同步建议
        if "发现建议: 0" in result.stdout:
            print("  ✅ 文档已是最新")
            return True
        elif "自动同步: 0" in result.stdout and execute:
            print("  ⚠️  发现需要手动确认的同步建议")
            return True
        else:
            print("  ✅ 文档同步完成")
            return True
    else:
        print(f"  ❌ 文档同步失败: {result.stderr}")
        return False


def run_architecture_check(root: Path) -> bool:
    """运行架构完整性检查"""
    print("\n🏗️ 运行架构完整性检查...")
    
    # 检查核心架构文件
    arch_file = root / 'core' / 'ARCHITECTURE.md'
    if not arch_file.exists():
        print("  ❌ 架构文档不存在")
        return False
    
    # 检查关键章节
    content = arch_file.read_text(encoding='utf-8')
    required_sections = [
        "六层架构",
        "技能生态",
        "治理层扩展",
        "能力矩阵"
    ]
    
    missing = [s for s in required_sections if s not in content]
    if missing:
        print(f"  ⚠️  架构文档缺少章节: {missing}")
        return False
    
    print("  ✅ 架构文档完整")
    return True


def run_module_fusion(root: Path) -> bool:
    """运行模块融合引擎"""
    print("\n📦 运行模块融合引擎 (V8.8.3)...")
    
    module_fusion_path = root / 'infrastructure' / 'fusion' / 'module_fusion_engine.py'
    
    if not module_fusion_path.exists():
        print("  ⚠️  模块融合引擎不存在，跳过")
        return True
    
    result = subprocess.run(
        [sys.executable, str(module_fusion_path), 'scan'],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        # 检查是否融合了新模块
        if "融合 0 个" in result.stdout:
            print("  ✅ 所有模块已注册")
            return True
        else:
            print("  ✅ 新模块已自动融合")
            return True
    else:
        print(f"  ❌ 模块融合失败: {result.stderr}")
        return False


def run_skill_fusion(root: Path) -> bool:
    """运行技能融合引擎"""
    print("\n🎯 运行技能融合引擎...")
    
    skill_fusion_path = root / 'infrastructure' / 'fusion' / 'skill_fusion_engine.py'
    
    if not skill_fusion_path.exists():
        print("  ⚠️  技能融合引擎不存在，跳过")
        return True
    
    # 使用 auto_fuse_all 方法
    result = subprocess.run(
        [sys.executable, '-c', 
         f"import sys; sys.path.insert(0, '{root}'); "
         f"from infrastructure.fusion.skill_fusion_engine import SkillFusionEngine; "
         f"engine = SkillFusionEngine(); result = engine.auto_fuse_all(); "
         f"print(f'扫描: {{result.get(\"scanned\", 0)}} 融合: {{result.get(\"fused\", 0)}}')"],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        print("  ✅ 技能融合完成")
        return True
    else:
        print(f"  ⚠️  技能融合警告: {result.stderr}")
        return True  # 不阻断流程


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="自动融合钩子 V8.8.3")
    parser.add_argument("--execute", action="store_true", help="执行文档同步")
    parser.add_argument("--check-arch", action="store_true", help="检查架构完整性")
    parser.add_argument("--skip-modules", action="store_true", help="跳过模块融合")
    parser.add_argument("--skip-skills", action="store_true", help="跳过技能融合")
    args = parser.parse_args()
    
    root = get_project_root()
    
    print("=" * 60)
    print("  自动融合钩子 V8.8.3")
    print("=" * 60)
    
    all_passed = True
    
    # 1. 检查新文件
    check_passed = run_fusion_check(root)
    if not check_passed:
        all_passed = False
    
    # 2. 如果有文件未融入，运行融合引擎
    if not check_passed:
        fuse_passed = run_fusion_engine(root)
        if not fuse_passed:
            all_passed = False
    
    # 3. 运行模块融合（V8.8.3 新增）
    if not args.skip_modules:
        module_passed = run_module_fusion(root)
        if not module_passed:
            all_passed = False
    
    # 4. 运行技能融合
    if not args.skip_skills:
        skill_passed = run_skill_fusion(root)
        if not skill_passed:
            all_passed = False
    
    # 5. 运行文档同步检查
    doc_passed = run_doc_sync(root, execute=args.execute)
    if not doc_passed:
        all_passed = False
    
    # 6. 检查架构完整性
    if args.check_arch:
        arch_passed = run_architecture_check(root)
        if not arch_passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ 融合检查通过")
    else:
        print("  ⚠️  融合检查发现问题，请处理")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
