# Security Documentation

## 安全声明

本技能是一个 LLM + 向量记忆集成工具，所有代码和行为都是透明的、可审计的。

---

## 🔐 安全保证

### 1. 代码透明性

- **源码完全开放**：`src/` 目录包含所有源代码，可供安全审计
- **无隐藏行为**：所有网络调用、文件操作、扩展加载都在源码中明确声明
- **可验证构建**：`dist/` 版本由 `src/` 版本通过 `build.sh` 构建，功能完全一致

### 2. 用户控制

- **所有自动功能默认禁用**：用户必须手动触发所有操作
- **操作前确认**：所有敏感操作都需要用户确认
- **备份机制**：所有修改操作前都会自动备份

### 3. 安全缓解措施

- **原生扩展加载**：
  - SHA256 哈希验证
  - 信任列表管理
  - 文件完整性检查
  - 用户手动确认

- **文件系统操作**：
  - 仅限 `~/.openclaw` 目录
  - 操作前备份
  - 用户确认机制

- **网络访问**：
  - 仅访问用户配置的 API 端点
  - 不内置任何 API 密钥
  - 所有请求添加 timeout

---

## 📦 双重包说明

本技能提供两个版本以确保安全透明性：

### 版本对比

| 版本 | 位置 | 用途 | 特点 |
|------|------|------|------|
| **源码版** | `src/` | 安全审计、开发测试 | 完全透明，可审计 |
| **保护版** | `dist/` | 生产环境使用 | VMP 保护，防篡改 |

### VMP 保护说明

VMP（Virtual Machine Protection）保护仅用于：
- 防止代码被恶意篡改
- 保护知识产权
- **不改变任何功能行为**
- **不隐藏任何安全敏感操作**

**重要声明**：
- 所有网络调用、文件操作、扩展加载等敏感行为在 `src/` 中完全可见
- 用户可选择使用 `src/` 版本（自行审计）或 `dist/` 版本（VMP 保护）
- 两个版本的功能行为完全一致

---

## ⚠️ 高风险能力声明

### 1. 原生 SQLite 扩展加载（vec0.so）

**风险等级**：HIGH

**风险描述**：加载原生 SQLite 扩展提供任意代码执行路径

**缓解措施**：
- ✅ SHA256 哈希验证（`safe_extension_loader.py`）
- ✅ 信任列表管理（`.trusted_hashes.json`）
- ✅ 文件完整性检查（大小、权限、路径验证）
- ✅ 生产环境禁止自动确认
- ✅ 用户必须手动确认才能加载扩展

**用户操作**：用户必须显式调用 `confirm_extension_load()` 才能加载扩展

**审计建议**：在生产环境使用前，请先审查 `src/core/sqlite_ext.py` 和 `src/scripts/safe_extension_loader.py` 的代码

### 2. 广泛的文件系统操作

**风险等级**：MEDIUM

**风险描述**：读写 `~/.openclaw` 目录，可能修改全局配置

**缓解措施**：
- ✅ 所有自动功能默认禁用
- ✅ 用户必须手动触发所有操作
- ✅ 操作前需要用户确认
- ✅ 备份机制（`backup_before_update: true`）

**受影响文件**：
- `vectors.db`（向量数据库）
- `MEMORY.md`（记忆文件）
- `persona.md`（用户画像）
- `logs/*`（日志文件）

### 3. 网络访问

**风险等级**：LOW

**风险描述**：调用用户配置的 LLM/embedding API 端点

**缓解措施**：
- ✅ 用户自行配置 API 端点
- ✅ 不内置任何 API 密钥
- ✅ 所有网络请求添加 timeout
- ✅ 仅访问用户配置的端点

**必需环境变量**：
- `EMBEDDING_API_KEY`（必需）
- `LLM_API_KEY`（可选）

---

## 📋 安全检查清单

在安装和使用本技能前，请确认：

- [ ] 已阅读并理解本安全声明
- [ ] 已审查 `src/` 目录的源代码
- [ ] 已配置 `EMBEDDING_API_KEY` 环境变量
- [ ] 已了解原生扩展加载的风险和缓解措施
- [ ] 已了解文件系统操作的范围和影响
- [ ] 已了解网络访问的目的和范围

---

## 🔍 安全审计指南

### 审计重点文件

1. **原生扩展加载**：
   - `src/core/sqlite_ext.py`
   - `src/scripts/safe_extension_loader.py`

2. **文件系统操作**：
   - `src/scripts/smart_memory_update.py`
   - `src/scripts/auto_update_persona.py`

3. **网络访问**：
   - `src/scripts/core/embedding.py`
   - `src/scripts/core/llm.py`

### 审计方法

```bash
# 1. 检查原生扩展加载
grep -r "load_extension\|enable_load_extension" src/

# 2. 检查文件系统操作
grep -r "open\|write\|remove\|rmtree" src/

# 3. 检查网络访问
grep -r "requests\|urllib\|http" src/

# 4. 检查环境变量使用
grep -r "os.environ\|getenv" src/
```

---

## 📥 构建和验证

### 构建流程

```bash
# 1. 从源码构建保护版本
./build.sh

# 2. 验证校验和
./verify.sh

# 3. 发布到 ClawHub（源码版）
clawhub publish . --version x.x.x
```

### 校验和验证

```bash
# 验证源码版本
sha256sum src/core/sqlite_ext.py
sha256sum src/scripts/safe_extension_loader.py

# 验证保护版本
sha256sum dist/core/sqlite_ext.py
sha256sum dist/scripts/safe_extension_loader.py
```

---

## 📞 安全问题报告

如果您发现任何安全问题，请通过以下方式报告：

- **GitHub Issues**：https://github.com/xkzs2007/llm-memory-integration/issues
- **Email**：[待补充]

---

## 📜 版本历史

| 版本 | 安全改进 |
|------|----------|
| **v5.1.5** | 禁用所有自动功能 |
| **v5.1.6** | 修复资源泄漏和异常处理 |
| **v5.1.7** | 删除 Web API |
| **v5.1.8** | 全面修复资源泄漏 |
| **v5.1.9** | 添加 install.json 安装规范 |
| **v5.2.0** | 修复文档不一致问题 |
| **v5.2.1** | 添加 dist/ 目录说明 |
| **v5.2.2** | 删除 HTTP 监控 + 高风险能力声明 |
| **v5.2.3** | 修复注册表元数据不一致问题 |
| **v5.2.4** | 增强高风险能力声明和审计建议 |
| **v5.2.5** | 修复注册表元数据不一致问题（添加 primaryCredential） |
| **v5.2.6** | 更新版本号，确保注册表元数据同步 |
| **v5.2.7** | 修复 subprocess 和 SQL 注入漏洞 |
| **v5.2.8** | 添加详细的安全声明和审计指南 |

---

*最后更新：2026-04-14*
