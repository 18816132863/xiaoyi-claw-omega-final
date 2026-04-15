---
name: local_app_interconnect
description: local_app_interconnect 技能模块
---

# Search-Phone Interconnect Skill

## 目的
建立**网络搜索**与**手机操作**的通用联动能力，适用于任何需要结合两者完成的任务。

## 核心能力

### 1. 双通道并行
```
┌─────────────────────────────────────────────────────────────┐
│                    用户任务                                  │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    ┌───────────────┐               ┌───────────────┐
    │   网络搜索     │               │   手机操作     │
    │   browser     │               │ xiaoyi_gui   │
    │   web_fetch   │               │   _agent      │
    └───────────────┘               └───────────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
                    ┌───────────────┐
                    │   结果融合     │
                    └───────────────┘
```

### 2. 适用场景

| 场景 | 网络搜索 | 手机操作 | 联动方式 |
|------|----------|----------|----------|
| 找房源列表 | ✅ 主导 | ✅ 辅助 | 并行 |
| 获取联系方式 | ❌ 受限 | ✅ 主导 | 手机优先 |
| 查看商品详情 | ✅ 可用 | ✅ 主导 | 手机优先 |
| 比价购物 | ✅ 主导 | ✅ 辅助 | 并行 |
| 查找商家 | ✅ 主导 | ✅ 辅助 | 并行 |
| 预约服务 | ✅ 搜索 | ✅ 操作 | 串行 |
| 查询订单 | ✅ 搜索 | ✅ 操作 | 串行 |

### 3. 工具组合规则

```python
# 规则1: 信息获取类 - 网络优先
def info_task(query):
    web_result = browser.search(query)      # 快速获取列表
    phone_result = gui_agent(query)        # 获取详细信息
    return merge(web_result, phone_result)

# 规则2: 操作执行类 - 手机优先
def action_task(action):
    phone_result = gui_agent(action)       # 手机执行操作
    if phone_result.failed:
        web_result = browser.action(action) # 降级到网页
    return phone_result or web_result

# 规则3: 混合类 - 并行执行
def mixed_task(query, action):
    with parallel() as p:
        p.submit(browser.search, query)
        p.submit(gui_agent, action)
    return p.results
```

### 4. 超时与降级

| 工具 | 超时 | 降级方案 |
|------|------|----------|
| browser | 30s | web_fetch |
| web_fetch | 10s | 返回缓存 |
| xiaoyi_gui_agent | 60s | 返回网页信息 |

### 5. 结果融合

```python
def merge_results(web_data, phone_data):
    """
    融合规则:
    1. 手机数据优先（更准确）
    2. 网络数据补充（更全面）
    3. 冲突时以手机数据为准
    """
    result = {}
    
    # 手机数据覆盖
    if phone_data:
        result.update(phone_data)
    
    # 网络数据补充缺失字段
    if web_data:
        for key, value in web_data.items():
            if key not in result:
                result[key] = value
    
    return result
```

## 使用示例

### 示例1: 找商家并获取联系方式
```
用户: 帮我找淄博附近的装修公司，要电话

执行:
1. browser.search("淄博装修公司") → 列表
2. gui_agent("打开手机地图APP，搜索装修公司，获取电话") → 联系方式
3. merge() → 完整信息
```

### 示例2: 比价购物
```
用户: 帮我比价iPhone 15，找最便宜的

执行:
1. browser.search("iPhone 15 价格") → 网页价格
2. gui_agent("打开淘宝/京东，搜索iPhone 15") → APP价格
3. merge() → 比价结果
```

### 示例3: 预约服务
```
用户: 帮我预约附近的理发店

执行:
1. browser.search("附近理发店") → 店铺列表
2. gui_agent("打开美团，预约理发") → 完成预约
```

## 技能文件

| 文件 | 用途 |
|------|------|
| SKILL.md | 技能文档 |
| interconnect.py | 联动模块 |

## 版本
- 版本: V1.0
- 更新时间: 2026-04-08
- 说明: 通用搜索-手机联动能力，非特定任务技能
