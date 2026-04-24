# 密钥安全存储模块

## 概述
使用 AES-256-GCM + RSA-4096 多层加密保护敏感密钥。

## 加密层次

```
Master Key (RSA-4096, 用户密码派生)
    ↓
KEK (Key Encryption Key, AES-256-GCM)
    ↓
DEK (Data Encryption Key, AES-256-GCM)
    ↓
加密密钥数据
```

## 存储的密钥

| 密钥名称 | 用途 | 加密状态 |
|----------|------|----------|
| `clawhub_188` | @18816132863 的 ClawHub Token | ✅ 已加密 |
| `clawhub_xkzs2007` | @xkzs2007 的 ClawHub Token | ✅ 已加密 |
| `github_token` | GitHub Personal Access Token | ✅ 已加密 |

## 使用方法

```python
from governance.security.secret_vault import SecretVault

# 初始化 (首次使用需要设置主密码)
vault = SecretVault(master_password="your-master-password")

# 存储密钥
vault.store("clawhub_188", "clh_YPEQXGbQOrNIcjn25lbzYy7r_6guB_zxV6rE2wfRCcI")

# 获取密钥
token = vault.get("clawhub_188")

# 列出所有密钥
keys = vault.list_keys()
```

## 安全特性

- **加密算法**: AES-256-GCM
- **密钥派生**: PBKDF2 + Argon2id
- **密钥层次**: Master Key → KEK → DEK
- **防篡改**: HMAC-SHA256 完整性校验
- **防重放**: 时间戳 + Nonce

## 文件位置

- `vault.json` - 加密后的密钥存储
- `master.key` - 加密后的主密钥
- `salt.bin` - 密钥派生盐值

## 版本
- V1.0.0
- 创建日期: 2026-04-10
