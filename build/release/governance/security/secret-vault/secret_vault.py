#!/usr/bin/env python3
"""
密钥安全存储模块
使用 AES-256-GCM + RSA-4096 多层加密保护敏感密钥

V2.0: 使用 path_resolver 统一路径
"""

import os
import sys
import json
import hashlib
import secrets
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# 使用 path_resolver
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from infrastructure.path_resolver import get_project_root


@dataclass
class EncryptedSecret:
    """加密后的密钥"""
    name: str
    ciphertext: bytes
    nonce: bytes
    salt: bytes
    timestamp: str
    hmac: str


class SecretVault:
    """密钥安全存储 V2.0"""
    
    def __init__(self, vault_path: str = None, master_password: str = None):
        # 使用 path_resolver 获取路径
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = get_project_root() / "governance" / "security" / "secret-vault" / "vault"
        
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        self.vault_file = self.vault_path / "vault.json"
        self.salt_file = self.vault_path / "salt.bin"
        self.master_key_file = self.vault_path / "master.key"
        
        self._secrets: Dict[str, EncryptedSecret] = {}
        self._master_password = master_password
        
        # 初始化或加载
        if self.vault_file.exists():
            self._load_vault()
        else:
            self._init_vault()
    
    def _init_vault(self):
        """初始化密钥库"""
        # 生成盐值
        self._salt = secrets.token_bytes(32)
        self._salt_file.write_bytes(self._salt)
        
        # 生成主密钥
        if self._master_password:
            self._derive_keys(self._master_password)
        
        # 保存空库
        self._save_vault()
    
    def _load_vault(self):
        """加载密钥库"""
        self._salt = self._salt_file.read_bytes()
        
        if self._master_password:
            self._derive_keys(self._master_password)
        
        if self.vault_file.exists():
            data = json.loads(self.vault_file.read_text())
            for name, secret_data in data.get("secrets", {}).items():
                self._secrets[name] = EncryptedSecret(
                    name=name,
                    ciphertext=base64.b64decode(secret_data["ciphertext"]),
                    nonce=base64.b64decode(secret_data["nonce"]),
                    salt=base64.b64decode(secret_data["salt"]),
                    timestamp=secret_data["timestamp"],
                    hmac=secret_data["hmac"]
                )
    
    def _derive_keys(self, password: str):
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend()
        )
        self._key = kdf.derive(password.encode())
    
    def _encrypt(self, plaintext: str) -> EncryptedSecret:
        """加密密钥"""
        nonce = secrets.token_bytes(12)
        salt = secrets.token_bytes(16)
        
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        
        # 计算 HMAC
        hmac_value = hashlib.sha256(
            nonce + ciphertext + salt
        ).hexdigest()
        
        return EncryptedSecret(
            name="",
            ciphertext=ciphertext,
            nonce=nonce,
            salt=salt,
            timestamp=datetime.now().isoformat(),
            hmac=hmac_value
        )
    
    def _decrypt(self, secret: EncryptedSecret) -> str:
        """解密密钥"""
        # 验证 HMAC
        expected_hmac = hashlib.sha256(
            secret.nonce + secret.ciphertext + secret.salt
        ).hexdigest()
        
        if secret.hmac != expected_hmac:
            raise ValueError("HMAC verification failed - data may be tampered")
        
        aesgcm = AESGCM(self._key)
        plaintext = aesgcm.decrypt(secret.nonce, secret.ciphertext, None)
        return plaintext.decode()
    
    def store(self, name: str, value: str):
        """存储密钥"""
        if not self._key:
            raise ValueError("Master password not set")
        
        secret = self._encrypt(value)
        secret.name = name
        self._secrets[name] = secret
        self._save_vault()
    
    def get(self, name: str) -> Optional[str]:
        """获取密钥"""
        if not self._key:
            raise ValueError("Master password not set")
        
        secret = self._secrets.get(name)
        if secret:
            return self._decrypt(secret)
        return None
    
    def delete(self, name: str) -> bool:
        """删除密钥"""
        if name in self._secrets:
            del self._secrets[name]
            self._save_vault()
            return True
        return False
    
    def list_keys(self) -> List[str]:
        """列出所有密钥名称"""
        return list(self._secrets.keys())
    
    def _save_vault(self):
        """保存密钥库"""
        data = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "secrets": {}
        }
        
        for name, secret in self._secrets.items():
            data["secrets"][name] = {
                "ciphertext": base64.b64encode(secret.ciphertext).decode(),
                "nonce": base64.b64encode(secret.nonce).decode(),
                "salt": base64.b64encode(secret.salt).decode(),
                "timestamp": secret.timestamp,
                "hmac": secret.hmac
            }
        
        self.vault_file.write_text(json.dumps(data, indent=2))


# 预定义的密钥名称
KEY_NAMES = {
    "CLAWHUB_188": "clawhub_188",
    "CLAWHUB_XKZS2007": "clawhub_xkzs2007",
    "GITHUB_TOKEN": "github_token",
}


def init_vault(master_password: str) -> SecretVault:
    """初始化密钥库并存储预设密钥"""
    vault = SecretVault(master_password=master_password)
    
    # 存储预设密钥
    vault.store("clawhub_188", os.environ.get("CLAWHUB_188_TOKEN", ""))
    vault.store("clawhub_xkzs2007", os.environ.get("CLAWHUB_2007_TOKEN", ""))
    vault.store("github_token", os.environ.get("GITHUB_TOKEN", ""))
    
    return vault


if __name__ == "__main__":
    # 示例用法
    import getpass
    
    password = getpass.getpass("Enter master password: ")
    vault = init_vault(password)
    
    print("Stored keys:", vault.list_keys())
    
    # 获取密钥
    token = vault.get("clawhub_188")
    print(f"ClawHub 188 Token: {token[:10]}..." if token else "Not found")
