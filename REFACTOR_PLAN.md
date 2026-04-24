# 平台增强型强内核技能 - 整改计划

## 一、产品定位转变

**从**: 部署型任务系统（需要 PostgreSQL/Redis/Docker）
**到**: 平台增强型强内核技能（默认零配置可用）

## 二、三种运行模式

### 1. Skill Default 模式（默认）
- SQLite 持久化
- 单进程
- request-driven 执行
- 无外部依赖

### 2. Platform Enhanced 模式
- 借用平台调度能力
- 自动降级到 Default

### 3. Self-hosted Enhanced 模式（可选）
- PostgreSQL/Redis 增强
- 不影响默认模式

## 三、执行顺序

1. 统一产品定位与三种运行模式
2. 重构 6 层架构与目录
3. 抽取 platform adapter
4. 去掉 daemon 强依赖
5. 补 capability registry
6. 强化 SQLite
7. 补 degradation strategy
8. 补测试
9. 补文档

## 四、预计工作量

- 新增目录: 8 个
- 新增文件: ~50 个
- 重构文件: ~20 个
- 新增文档: 10 个
- 新增测试: 8 个

开始执行...
