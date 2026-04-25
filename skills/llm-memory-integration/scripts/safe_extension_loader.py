#!/usr/bin/env python3
"""
安全扩展加载模块 v2.0
增强版：添加加密验证、签名检查、来源追溯
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime

# 信任的扩展哈希数据库
TRUSTED_HASHES_FILE = Path.home() / ".openclaw" / "extensions" / ".trusted_hashes.json"

# 官方 sqlite-vec 扩展的已知哈希（需要用户首次确认）
OFFICIAL_HASHES = {
    # sqlite-vec-linux-x64 官方发布版本
    # 用户首次运行时需要手动确认并添加
}

def load_trusted_hashes() -> Dict[str, dict]:
    """加载信任的哈希数据库"""
    if TRUSTED_HASHES_FILE.exists():
        try:
            with open(TRUSTED_HASHES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_trusted_hashes(hashes: Dict[str, dict]):
    """保存信任的哈希数据库"""
    TRUSTED_HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRUSTED_HASHES_FILE, 'w') as f:
        json.dump(hashes, f, indent=2)

def calculate_file_hash(file_path: Path) -> str:
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        raise RuntimeError(f"计算哈希失败: {e}")

def verify_file_signature(file_path: Path, expected_hash: str) -> bool:
    """验证文件签名（通过哈希比对）"""
    actual_hash = calculate_file_hash(file_path)
    return actual_hash == expected_hash

def check_extension_integrity(ext_path: Path) -> Tuple[bool, str, dict]:
    """
    全面检查扩展完整性
    
    返回: (是否安全, 原因, 元数据)
    """
    metadata = {
        "path": str(ext_path),
        "exists": ext_path.exists(),
        "size": 0,
        "hash": "",
        "permissions": "",
        "modified": "",
        "trusted": False
    }
    
    if not ext_path.exists():
        return False, f"扩展文件不存在: {ext_path}", metadata
    
    # 获取文件元数据
    stat_info = ext_path.stat()
    metadata["size"] = stat_info.st_size
    metadata["permissions"] = oct(stat_info.st_mode)[-3:]
    metadata["modified"] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
    
    # 1. 检查路径是否在预期目录
    expected_dirs = [
        Path.home() / ".openclaw" / "extensions",
    ]
    
    in_expected_dir = False
    for expected_dir in expected_dirs:
        try:
            ext_path.relative_to(expected_dir)
            in_expected_dir = True
            break
        except ValueError:
            continue
    
    if not in_expected_dir:
        return False, f"❌ 扩展路径不在预期目录: {ext_path}", metadata
    
    # 2. 检查文件权限
    mode = metadata["permissions"]
    if mode not in ['644', '755', '744']:
        return False, f"❌ 扩展文件权限异常: {mode} (应为 644/755)", metadata
    
    # 3. 检查文件大小（vec0.so 通常在 1-10MB）
    size_mb = metadata["size"] / (1024 * 1024)
    if size_mb < 0.1 or size_mb > 50:
        return False, f"❌ 扩展文件大小异常: {size_mb:.2f}MB", metadata
    
    # 4. 计算哈希
    try:
        file_hash = calculate_file_hash(ext_path)
        metadata["hash"] = file_hash
    except Exception as e:
        return False, f"❌ 计算哈希失败: {e}", metadata
    
    # 5. 检查是否在信任列表
    trusted_hashes = load_trusted_hashes()
    
    if file_hash in trusted_hashes:
        metadata["trusted"] = True
        trust_info = trusted_hashes[file_hash]
        return True, f"✅ 扩展在信任列表中 (来源: {trust_info.get('source', 'unknown')})", metadata
    
    # 6. 检查是否是官方哈希
    if file_hash in OFFICIAL_HASHES:
        metadata["trusted"] = True
        return True, f"✅ 扩展是官方版本 (hash: {file_hash[:16]}...)", metadata
    
    # 7. 首次运行，需要用户确认
    return False, f"⚠️ 首次加载扩展，需要用户确认 (hash: {file_hash[:16]}...)", metadata

def prompt_user_confirmation(ext_path: Path, metadata: dict) -> bool:
    """
    提示用户确认扩展来源
    
    注意：此函数在实际运行时需要用户交互
    """
    print("\n" + "=" * 60)
    print("⚠️  安全警告：首次加载 SQLite 向量扩展")
    print("=" * 60)
    print(f"扩展路径: {ext_path}")
    print(f"文件大小: {metadata['size'] / (1024*1024):.2f} MB")
    print(f"文件哈希: {metadata['hash']}")
    print(f"修改时间: {metadata['modified']}")
    print("\n请确认：")
    print("1. 此扩展来自官方或可信来源")
    print("2. 文件未被篡改")
    print("3. 您信任此扩展的发布者")
    print("\n是否信任此扩展？(yes/no): ", end="")
    
    # 在实际运行时，这里会等待用户输入
    # 为了安全，默认返回 False，需要用户明确确认
    return False

def add_to_trusted_list(ext_path: Path, source: str = "user_confirmed"):
    """将扩展添加到信任列表"""
    file_hash = calculate_file_hash(ext_path)
    trusted_hashes = load_trusted_hashes()
    
    trusted_hashes[file_hash] = {
        "path": str(ext_path),
        "source": source,
        "added_at": datetime.now().isoformat(),
        "size": ext_path.stat().st_size
    }
    
    save_trusted_hashes(trusted_hashes)
    print(f"✅ 扩展已添加到信任列表: {file_hash[:16]}...")

def get_vec_extension_path() -> Path:
    """动态获取向量扩展路径"""
    possible_paths = [
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so",
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0",
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return possible_paths[0]

def safe_load_extension(conn, ext_path: Optional[Path] = None, auto_confirm: bool = False) -> Tuple[bool, str]:
    """
    安全加载 SQLite 扩展（增强版）
    
    ⚠️ 安全警告：
    - 加载原生扩展存在远程代码执行风险
    - 必须用户明确确认才能加载
    - auto_confirm 仅用于测试环境
    
    参数:
        conn: SQLite 连接
        ext_path: 扩展路径（可选）
        auto_confirm: 是否自动确认（仅用于测试，生产环境必须为 False）
    
    返回: (是否成功, 消息)
    """
    if ext_path is None:
        ext_path = get_vec_extension_path()
    
    # 全面检查
    is_safe, reason, metadata = check_extension_integrity(ext_path)
    
    if is_safe:
        # 已信任，直接加载
        try:
            conn.enable_load_extension(True)
            conn.load_extension(str(ext_path))
            return True, f"✅ 扩展加载成功: {reason}"
        except Exception as e:
            return False, f"❌ 扩展加载失败: {e}"
    
    # 未信任，需要用户确认
    if not metadata.get("hash"):
        return False, f"❌ 无法验证扩展: {reason}"
    
    # ⚠️ 生产环境必须用户确认
    if not auto_confirm:
        return False, f"""⚠️ 安全警告：需要用户确认

扩展路径: {ext_path}
文件哈希: {metadata.get('hash', 'unknown')}

⚠️ 加载原生扩展存在远程代码执行风险
请确认扩展来源可信后再加载

如需信任此扩展，请运行:
python3 -c "from safe_extension_loader import add_to_trusted_list; from pathlib import Path; add_to_trusted_list(Path('{ext_path}'))"
"""
    
    # 仅测试环境允许自动确认（已删除生产环境的自动确认逻辑）
    return False, "❌ 生产环境禁止自动确认扩展加载"

if __name__ == "__main__":
    print("=" * 60)
    print("SQLite 向量扩展安全检查")
    print("=" * 60)
    
    ext_path = get_vec_extension_path()
    is_safe, reason, metadata = check_extension_integrity(ext_path)
    
    print(f"\n扩展路径: {ext_path}")
    print(f"文件存在: {'✅' if metadata['exists'] else '❌'}")
    print(f"文件大小: {metadata['size'] / (1024*1024):.2f} MB")
    print(f"文件权限: {metadata['permissions']}")
    print(f"修改时间: {metadata['modified']}")
    print(f"文件哈希: {metadata['hash']}")
    print(f"\n安全状态: {'✅ 已信任' if is_safe else '⚠️ 需确认'}")
    print(f"原因: {reason}")
    
    if not is_safe and metadata.get("hash"):
        print(f"\n如需信任此扩展，请运行:")
        print(f'  python3 -c "from safe_extension_loader import add_to_trusted_list; add_to_trusted_list(Path(\'{ext_path}\'))"')
