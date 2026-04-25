# 原生扩展配置说明

## ⚠️ 重要安全警告

**加载原生 SQLite 扩展存在安全风险，请谨慎使用！**

## 配置方式

本技能**不自动加载**任何原生扩展。如需使用高性能向量搜索，请按以下步骤配置：

### 步骤 1：下载扩展

```bash
# 下载 sqlite-vec 扩展
pip install sqlite-vec

# 或手动下载
wget https://github.com/asg017/sqlite-vec/releases/download/v0.1.0/vec0.so
```

### 步骤 2：配置扩展路径

在 `config/extension_config.json` 中配置：

```json
{
  "enabled": false,
  "extension_path": "~/.openclaw/extensions/vec0.so",
  "require_confirmation": true,
  "sha256_verification": true
}
```

### 步骤 3：计算并保存哈希

```bash
# 计算哈希
sha256sum ~/.openclaw/extensions/vec0.so

# 保存到信任列表
echo '{"vec0.so": "你的哈希值"}' > ~/.openclaw/extensions/.trusted_hashes.json
```

### 步骤 4：启用扩展

**重要：仅在确认安全后启用！**

```json
{
  "enabled": true,
  "extension_path": "~/.openclaw/extensions/vec0.so",
  "require_confirmation": true,
  "sha256_verification": true
}
```

## 安全建议

1. **仅从官方渠道下载**
   - GitHub: https://github.com/asg017/sqlite-vec
   - PyPI: pip install sqlite-vec

2. **验证哈希值**
   - 每次加载前验证 SHA256
   - 确保文件未被篡改

3. **定期更新**
   - 使用最新版本
   - 关注安全公告

4. **最小权限原则**
   - 仅在需要时启用
   - 不使用时禁用

## 风险说明

加载原生扩展可能导致：
- 任意代码执行
- 系统崩溃
- 数据损坏
- 安全漏洞

**请确保你信任扩展的来源！**

---

**最后更新**: 2026-04-15
**版本**: v6.3.2
