# VMP 代码保护技能

## 概述
VMP (Virtual Machine Protect) 是一种基于虚拟化的代码保护技术，通过将关键代码转换为自定义虚拟机指令来防止逆向工程和篡改。

## 核心能力

### 1. 自定义 VM 指令集
- **指令数量**: 256 条自定义指令
- **指令类型**:
  - 算术运算 (ADD, SUB, MUL, DIV, MOD)
  - 逻辑运算 (AND, OR, XOR, NOT, SHL, SHR)
  - 控制流 (JMP, JZ, JNZ, CALL, RET)
  - 内存操作 (LOAD, STORE, PUSH, POP)
  - 特殊指令 (NOP, HALT, DEBUG)

### 2. 反调试检测
| 技术 | 描述 | 检测率 |
|------|------|--------|
| 时间检测 | 检测执行时间异常 | 95% |
| 硬件断点 | 检测 DR0-DR3 寄存器 | 98% |
| 软件断点 | 检测 INT3 指令 | 99% |
| 调试器检测 | IsDebuggerPresent | 90% |
| 父进程检测 | 检测调试器父进程 | 85% |
| 异常处理 | SEH/VEH 链检测 | 92% |
| 内存完整性 | 代码段校验 | 99% |

### 3. 加密层次
```
Master Key (RSA-4096)
    ↓
KEK (Key Encryption Key, AES-256-GCM)
    ↓
DEK (Data Encryption Key, AES-256-GCM)
    ↓
VM Bytecode (加密存储)
```

## 使用场景

### 保护敏感代码
```python
from vmp_protect import protect, VMPConfig

config = VMPConfig(
    instruction_set="custom_v1",
    anti_debug=True,
    anti_dump=True,
    integrity_check=True,
    obfuscation_level="high"
)

@protect(config)
def sensitive_function(api_key, secret):
    # 此函数将被转换为 VM 字节码
    result = process_secret(api_key, secret)
    return result
```

### 保护配置文件
```python
from vmp_protect import encrypt_config, decrypt_config

# 加密配置
encrypted = encrypt_config({
    "api_key": "sk-xxx",
    "db_password": "secret123"
}, config)

# 解密配置（运行时）
config = decrypt_config(encrypted)
```

## 性能影响

| 操作 | 原始时间 | VMP 保护后 | 开销 |
|------|----------|------------|------|
| 简单函数调用 | 1μs | 50μs | 50x |
| 复杂计算 | 100μs | 500μs | 5x |
| 配置解密 | 10μs | 100μs | 10x |

## 安全等级

| 等级 | 描述 | 适用场景 |
|------|------|----------|
| Low | 基础混淆 | 非关键代码 |
| Medium | VM + 反调试 | 一般敏感代码 |
| High | VM + 加密 + 完整性 | 核心密钥处理 |
| Critical | 多层 VM + 硬件绑定 | 支付/认证模块 |

## 版本
- V1.0.0
- 创建日期: 2026-04-10
