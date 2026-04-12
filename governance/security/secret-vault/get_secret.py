#!/usr/bin/env python3
"""
密钥读取工具 - 从加密库中获取密钥
"""

import os
import json
import hashlib
import base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def get_secret(name: str, master_password: str = None) -> str:
    """从密钥库获取密钥"""
    # 使用环境变量或默认路径
    vault_dir = os.environ.get("OPENCLAW_VAULT_DIR", 
                               os.path.expanduser("~/.openclaw/vault"))
    vault_path = Path(vault_dir)
    
    if not vault_path.exists():
        raise ValueError("Vault not initialized")
    
    # 加载盐值
    salt = (vault_path / "salt.bin").read_bytes()
    
    # 使用默认主密码或自定义
    if not master_password:
        master_password = os.environ.get("OPENCLAW_VAULT_PASSWORD", "OpenClaw_Ultimate_Pigeon_King_2026")
    
    # 派生密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode())
    
    # 加载密钥库
    vault_data = json.loads((vault_path / "vault.json").read_text())
    
    if name not in vault_data["secrets"]:
        raise ValueError(f"Secret '{name}' not found")
    
    secret = vault_data["secrets"][name]
    
    # 解密
    nonce = base64.b64decode(secret["nonce"])
    ciphertext = base64.b64decode(secret["ciphertext"])
    
    # 验证 HMAC
    expected_hmac = hashlib.sha256(nonce + ciphertext).hexdigest()
    if secret["hmac"] != expected_hmac:
        raise ValueError("HMAC verification failed")
    
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    
    return plaintext.decode()


def get_clawhub_188_token() -> str:
    """获取 @18816132863 的 ClawHub Token"""
    return get_secret("clawhub_188")


def get_clawhub_xkzs2007_token() -> str:
    """获取 @xkzs2007 的 ClawHub Token"""
    return get_secret("clawhub_xkzs2007")


def get_github_token() -> str:
    """获取 GitHub Token"""
    return get_secret("github_token")


if __name__ == "__main__":
    import sys
    
    vault_dir = os.environ.get("OPENCLAW_VAULT_DIR", 
                               os.path.expanduser("~/.openclaw/vault"))
    vault_path = Path(vault_dir)
    
    if len(sys.argv) > 1:
        name = sys.argv[1]
        print(get_secret(name))
    else:
        print("Available secrets:")
        vault_data = json.loads((vault_path / "vault.json").read_text())
        for name in vault_data["secrets"]:
            print(f"  - {name}")
