# LegnaChat 借鉴分析

## V2.7.0 - 2026-04-10

分析 py-LegnaChat 项目的可借鉴之处。

---

## 一、项目概述

**LegnaChat** 是一个轻量级 AI Agent 框架，特点：
- 使用 OpenAI API 规范
- 上下文需求量小
- 敏感权限安全管理
- 插件和技能系统

---

## 二、可借鉴特性

### 2.1 记忆系统 ✅

**LegnaChat 实现**:
```
memory/
├── short.md    # 短期记忆（自动总结）
└── long.md     # 长期记忆（AI 主动写入）
```

**特点**:
- 短期记忆：自动总结，每次启动重新提炼
- 长期记忆：永久保持，AI 主动写入
- 对话日志：latest.txt + 历史备份

**借鉴价值**: ⭐⭐⭐⭐⭐

我们已有类似实现，但可以优化：
- 添加自动总结功能
- 区分短期/长期记忆的 TTL
- 对话日志自动归档

---

### 2.2 技能系统 ✅

**LegnaChat 结构**:
```
skill/[技巧名]/
├── display.txt      # 简短标题
└── description.md   # 详细说明
```

**特点**:
- 极简结构
- 动态加载
- AI 可读取学习

**借鉴价值**: ⭐⭐⭐⭐

可以简化我们的技能结构：
- 添加 display.txt 作为简短描述
- description.md 作为详细指南
- 支持动态技能发现

---

### 2.3 插件系统 ✅

**LegnaChat 结构**:
```
plugin/[插件名]/
├── main.py              # 主逻辑
├── description.yaml     # 描述
├── requirements.txt     # 依赖
└── apikey.txt           # 配置
```

**特点**:
- 标准化接口：`tool_main(arg: dict) -> str`
- YAML 描述文件
- 独立依赖管理

**借鉴价值**: ⭐⭐⭐⭐

可以统一我们的插件接口：
- 标准化 `tool_main` 函数签名
- 使用 YAML 描述
- 独立配置文件

---

### 2.4 权限管理 ✅

**LegnaChat 实现**:
- 敏感操作需要用户授权
- 安全目录白名单
- 实时开关控制

**借鉴价值**: ⭐⭐⭐⭐⭐

我们已经有 execution-validator，可以增强：
- 添加用户实时授权界面
- 安全目录白名单配置
- 操作审计日志

---

### 2.5 系统提示词 ✅

**LegnaChat 特点**:
- 简洁明了
- 分层结构
- 动态变量注入

**借鉴价值**: ⭐⭐⭐⭐

可以优化我们的提示词：
- 更简洁的结构
- 动态变量注入
- 分层加载

---

## 三、具体改进建议

### 3.1 记忆系统增强

```python
# 添加自动总结功能
def summarize_memory(latest_log: str, existing_memory: str) -> str:
    """自动总结记忆"""
    prompt = f"""
    现有记忆: {existing_memory}
    新对话: {latest_log}
    
    请总结关键信息，保留重要内容。
    """
    return llm_call(prompt)
```

### 3.2 技能结构简化

```
skills/[技能名]/
├── SKILL.md         # 主文件（保留）
├── display.txt      # 简短描述（新增）
└── config.yaml      # 配置（可选）
```

### 3.3 插件接口统一

```python
# 标准化接口
def tool_main(arg: dict) -> str:
    """
    插件主函数
    
    Args:
        arg: 输入参数字典
    
    Returns:
        str: 执行结果
    """
    pass
```

### 3.4 权限管理增强

```yaml
# config.yaml
security:
  safe_paths:
    - /home/user/projects
    - /tmp
  dangerous_commands:
    - rm
    - sudo
  require_auth: true
```

---

## 四、对比分析

| 特性 | LegnaChat | 小艺Claw | 建议 |
|------|-----------|----------|------|
| 记忆系统 | 简单有效 | 完善复杂 | 简化+自动总结 |
| 技能系统 | 极简 | 完善 | 添加 display.txt |
| 插件系统 | 标准化 | 灵活 | 统一接口 |
| 权限管理 | 实时控制 | 预检查 | 增强交互 |
| Token 消耗 | 低 | 已优化 | 保持优化 |

---

## 五、实施优先级

| 优先级 | 改进项 | 工作量 |
|--------|--------|--------|
| P0 | 记忆自动总结 | 中 |
| P1 | 技能 display.txt | 低 |
| P1 | 插件接口统一 | 中 |
| P2 | 权限实时控制 | 高 |
| P2 | 系统提示词优化 | 低 |

---

**版本**: V2.7.0
**作者**: @18816132863
