# 新增技能接入规范

## 概述

本文档定义新增技能/模块的接入规范，确保系统一致性。

## 接入原则

1. **不能绕过 task_manager** - 所有任务必须通过统一入口
2. **不能绕过 executor** - 所有执行必须通过统一执行器
3. **不能绕过 event_repo** - 所有事件必须记录
4. **不能创建第二套状态流转** - 使用统一状态机
5. **不能创建第二套 delivery 逻辑** - 使用统一送达网关

## 必备要素

每个新技能必须具备：

### 1. Manifest

```json
{
  "name": "skill_name",
  "version": "1.0.0",
  "description": "技能描述",
  "timeout": 60,
  "retry_policy": {
    "max_attempts": 3,
    "backoff_seconds": 60
  }
}
```

### 2. Input Schema

```json
{
  "type": "object",
  "properties": {
    "param1": {"type": "string"},
    "param2": {"type": "integer"}
  },
  "required": ["param1"]
}
```

### 3. Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "result": {"type": "string"},
    "error": {"type": "string"}
  }
}
```

### 4. Timeout

- 默认: 60 秒
- 长时间任务: 明确声明

### 5. Retry Policy

- max_attempts: 最大重试次数
- backoff_seconds: 退避时间

### 6. Idempotency Rule

- 幂等键定义
- 重复调用处理

### 7. Event Mapping

- 开始事件
- 成功事件
- 失败事件

### 8. Error Mapping

- 错误类型
- 错误码
- 错误消息

### 9. Test File

- 单元测试
- 集成测试

## 接入流程

1. 创建技能目录 `skills/<skill_name>/`
2. 编写 SKILL.md
3. 实现 skill.py
4. 编写测试
5. 注册到 skill_registry.json
6. 通过架构检查

## 禁止事项

- ❌ 直接操作数据库
- ❌ 直接写文件队列
- ❌ 自定义状态流转
- ❌ 绕过日志系统
- ❌ 硬编码配置
