# 接入设计卡：天气查询服务

## 一、基本信息

| 项目 | 内容 |
|-----|------|
| skill_id | skill_weather_query_v1 |
| skill_name | 天气查询服务 |
| 版本 | 1.0.0 |
| 状态 | 设计中 |

---

## 二、所属层级

| 项目 | 内容 |
|-----|------|
| entry_layer | L4 |
| layer_name | 服务能力层 |
| layer_path | execution/weather_query/ |

---

## 三、挂层理由

| 理由 | 说明 |
|-----|------|
| 可复用工具 | 天气查询是通用能力，可被多个上层服务调用 |
| 外部接口适配 | 需要调用外部天气API，属于服务能力层职责 |
| 无业务规则 | 不包含复杂业务判断，仅做数据获取和格式转换 |
| 无数据存储 | 不直接操作数据库，符合L4层定位 |

---

## 四、入口位置

```
execution/weather_query/
├── SKILL.md
├── config.json
├── main.py
├── interface.py
├── test/
│   └── test_main.py
└── README.md
```

---

## 五、注册位置

**文件**：`infrastructure/inventory/skill_registry.json`

**注册信息**：
```json
{
  "skill_id": "skill_weather_query_v1",
  "skill_name": "天气查询服务",
  "version": "1.0.0",
  "entry_layer": "L4",
  "layer_name": "服务能力层",
  "layer_path": "execution/weather_query/",
  "input_schema": "city, date, unit",
  "output_schema": "temperature, weather, humidity, wind",
  "dependencies": "weather_api, cache",
  "owner": "系统管理员",
  "timeout_ms": 10000,
  "fallback_strategy": "cache->degrade->abort",
  "status": "draft",
  "call_scope": "internal"
}
```

---

## 六、配置源

**文件**：`execution/weather_query/config.json`

**配置内容**：
```json
{
  "skill_id": "skill_weather_query_v1",
  "version": "1.0.0",
  "entry_layer": "L4",
  "timeout_ms": 10000,
  "api": {
    "provider": "openweathermap",
    "base_url": "https://api.openweathermap.org/data/2.5",
    "api_key": "${WEATHER_API_KEY}"
  },
  "cache": {
    "enabled": true,
    "ttl_seconds": 1800
  },
  "logging": {
    "level": "INFO",
    "format": "json"
  },
  "fallback": {
    "strategy": "cache->degrade->abort",
    "degrade_output": {
      "temperature": "未知",
      "weather": "服务暂时不可用"
    }
  }
}
```

---

## 七、依赖模块

| 依赖项 | 类型 | 来源 | 说明 |
|-------|------|------|------|
| weather_api | 外部API | OpenWeatherMap | 天气数据源 |
| cache | 内部服务 | L5数据访问层 | 缓存天气数据 |
| http_client | 内部服务 | L6基础设施层 | HTTP请求客户端 |
| logger | 内部服务 | L6基础设施层 | 日志记录 |

---

## 八、输出去向

| 输出 | 去向 | 说明 |
|-----|------|------|
| 天气数据 | L1表达层 | 直接返回给用户 |
| 天气数据 | L2应用编排层 | 被其他技能调用 |
| 日志 | L6基础设施层 | 记录到日志系统 |
| 监控指标 | L6基础设施层 | 上报到监控系统 |

---

## 九、对现有链路的影响

| 影响项 | 影响程度 | 说明 |
|-------|---------|------|
| 新增依赖 | 低 | 仅依赖外部API，不影响内部模块 |
| 新增注册 | 低 | 在注册表中新增一条记录 |
| 新增目录 | 低 | 在execution/下新增目录 |
| 调用链变化 | 无 | 不影响现有调用链 |
| 配置变化 | 无 | 不影响现有配置 |

---

## 十、风险点

| 风险项 | 风险等级 | 缓解措施 |
|-------|---------|---------|
| 外部API不可用 | 中 | 实现缓存和降级机制 |
| API调用超时 | 低 | 设置合理超时时间 |
| API密钥泄露 | 中 | 使用环境变量存储 |
| 缓存数据过期 | 低 | 设置合理TTL |

---

## 十一、回滚点

| 回滚项 | 回滚方式 |
|-------|---------|
| 技能目录 | 删除 execution/weather_query/ |
| 注册记录 | 从 skill_registry.json 中删除 |
| 配置文件 | 删除 config.json |
| 依赖服务 | 无需回滚（外部服务） |

**回滚命令**：
```bash
# 删除技能目录
rm -rf execution/weather_query/

# 从注册表中删除
# 手动编辑 infrastructure/inventory/skill_registry.json
```

---

## 十二、审批状态

| 审批项 | 状态 | 审批人 | 时间 |
|-------|------|-------|------|
| 层级归属 | ✅ 通过 | 系统 | 2026-04-10 |
| 接入设计 | ✅ 通过 | 系统 | 2026-04-10 |
| 风险评估 | ✅ 通过 | 系统 | 2026-04-10 |
| 回滚方案 | ✅ 通过 | 系统 | 2026-04-10 |

---

## 版本
- V1.0.0
- 创建日期：2026-04-10
