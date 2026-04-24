# 技能产品架构

## 产品定位

这是一个**平台增强型强内核技能**，不是部署型后端系统。

### 核心特征

1. **上传即可分享** - 无需用户配置数据库、中间件
2. **默认零配置可用** - 开箱即用
3. **可降级可扩展** - 平台能力不可用时自动降级

## 六层架构

```
┌─────────────────────────────────────────┐
│         skill_entry (入口层)             │
│   input_router / validators / formatter │
├─────────────────────────────────────────┤
│       orchestration (编排层)             │
│   task / workflow / batch orchestrator  │
├─────────────────────────────────────────┤
│       capabilities (能力层)              │
│   registry / send / schedule / retry    │
├─────────────────────────────────────────┤
│        execution (执行层)                │
│   executor / state_machine / checkpoint │
├─────────────────────────────────────────┤
│     platform_adapter (适配层)            │
│   runtime_probe / xiaoyi / null adapter │
├─────────────────────────────────────────┤
│       diagnostics (诊断层)               │
│   self_check / timeline / error_explain │
└─────────────────────────────────────────┘
```

## 目录结构

```
project_root/
├── skill_entry/           # 入口层
│   ├── input_router.py    # 输入路由
│   ├── validators.py      # 参数校验
│   ├── response_formatter.py  # 响应格式化
│   └── error_codes.py     # 错误码定义
│
├── orchestration/         # 编排层
│   ├── task_orchestrator.py   # 任务编排
│   ├── workflow_orchestrator.py  # 工作流编排
│   └── batch_orchestrator.py  # 批量编排
│
├── capabilities/          # 能力层
│   ├── registry.py        # 能力注册表
│   ├── send_message.py    # 发送消息
│   ├── schedule_task.py   # 调度任务
│   └── ...                # 其他能力
│
├── execution/             # 执行层（已有）
│   ├── executor.py        # 执行器
│   └── state_machine.py   # 状态机
│
├── platform_adapter/      # 平台适配层
│   ├── base.py            # 适配器基类
│   ├── null_adapter.py    # 空适配器
│   ├── runtime_probe.py   # 运行时探测
│   └── xiaoyi_adapter.py  # 小艺适配器
│
├── diagnostics/           # 诊断层
│   ├── runtime_self_check.py  # 自检
│   ├── event_timeline.py  # 事件时间线
│   ├── error_explainer.py # 错误解释
│   └── capability_report.py   # 能力报告
│
└── config/                # 配置层
    ├── default_skill_config.py  # 默认配置
    ├── runtime_modes.py   # 运行模式
    └── feature_flags.py   # 功能开关
```

## 设计原则

1. **默认可用** - 不依赖外部服务
2. **优雅降级** - 平台能力不可用时自动回退
3. **可扩展** - 通过适配器接入新平台
4. **可诊断** - 完整的错误解释和自检能力
