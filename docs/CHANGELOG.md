# Changelog

## [7.0.0] - 2026-04-21 闭环收口版

### 重大改变

从"架构型系统"向"可交付代理系统"的收口改造。

### 新增模块

| 模块 | 说明 |
|------|------|
| `orchestration/verify_executor.py` | 真实验证器，检查文件/数据库/消息证据 |
| `orchestration/summarize_executor.py` | 真实总结器，生成完整用户回复 |
| `orchestration/result_guard.py` | 结果守卫，五重检查总闸 |
| `application/response_service/response_schema.py` | 响应 Schema 定义 |
| `memory_context/memory_write_policy.py` | 记忆写入策略 |
| `memory_context/memory_retrieval_policy.py` | 记忆检索策略 |
| `tests/test_no_fake_success.py` | 禁止假成功测试 |
| `tests/test_end_to_end.py` | 端到端测试 |

### 核心改动

1. **删除占位成功逻辑**
   - verify 不再返回 `{"status":"completed","type":"internal"}`
   - summarize 不再返回空壳总结

2. **真实验证**
   - 文件类：检查文件是否真的存在
   - 数据类：检查记录是否真的落表
   - 消息类：检查是否真的进入消息链
   - 工具类：检查是否真的有 tool call 记录

3. **禁止空成功**
   - 没有证据不能标 success
   - result_guard 五重检查总闸

4. **统一返回格式**
   - status / reason / user_response
   - completed_items / failed_items
   - evidence / next_action
   - execution_trace / task_id / intent

5. **统一错误结构**
   - `{"code": "...", "message": "..."}`

### 主链流程

```
parse → distribute → execute → verify → summarize → guard → final_response
```

### 解决的问题

| 问题 | 解决方式 |
|------|----------|
| 页面只显示一句话 | 固定模板：执行结果/完成项/未完成项/证据/下一步 |
| 说办了其实没办 | verify_executor 真实验证 |
| 幻觉重 | memory_write_policy / memory_retrieval_policy |
| 内部成功外部失败 | result_guard 五重检查 |
| 错误结构混乱 | 统一 error 结构 |

---

## [6.0.0] - 2026-04-21 新模块融入版

### 新增

- 架构巡检器 V6.0.0
- 新模块融入检查
- 任务系统检查

---

## [5.0.0] - 2026-04-21 真实验证总结版

### 新增

- application/response_service/
- 真实总结器
- 真实验证器
- 结构化解析

---

## [8.0.0] - 2026-04-21 定版

### 文档

- README.md 更新
- DEPLOY.md 更新
- package_info.json 完善
- ARCHITECTURE.md 完善
