# Orchestration - 编排层

## 职责
- 任务编排与调度
- 工作流管理
- 路由决策
- 策略执行

## 目录结构
```
orchestration/
├── router/         # 路由器
├── workflow/       # 工作流
└── strategy/       # 策略引擎
```

## 核心模块
- router/router.py - 技能路由器
- workflow/ - 工作流引擎

## 健康指标
- 路由准确率: > 90%
- 工作流完成率: > 95%
- 错误恢复率: > 80%
