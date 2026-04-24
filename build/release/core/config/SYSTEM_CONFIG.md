# SYSTEM_CONFIG.md - 系统配置规范

## 目的
定义系统配置的结构、管理和加载规范。

## 适用范围
所有系统级配置的管理和使用。

## 配置层级

| 层级 | 来源 | 优先级 | 说明 |
|------|------|--------|------|
| 默认配置 | 代码内置 | 最低 | 系统默认值 |
| 文件配置 | 配置文件 | 中 | 部署时配置 |
| 环境变量 | 环境变量 | 高 | 运行时配置 |
| 动态配置 | 配置中心 | 最高 | 实时配置 |

## 配置结构

### 主配置文件
```yaml
# config/system.yaml
system:
  name: "OpenClaw"
  version: "1.0.0"
  env: production
  
server:
  host: 0.0.0.0
  port: 8080
  workers: 4
  
database:
  type: postgresql
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  name: ${DB_NAME:openclaw}
  user: ${DB_USER:postgres}
  password: ${DB_PASSWORD}
  pool:
    min: 5
    max: 20
    
cache:
  type: redis
  host: ${REDIS_HOST:localhost}
  port: ${REDIS_PORT:6379}
  db: 0
  
logging:
  level: INFO
  format: json
  output: stdout
  
metrics:
  enabled: true
  port: 9090
```

### 环境配置
```yaml
# config/env/production.yaml
extends: base

system:
  env: production
  
server:
  workers: 8
  
database:
  pool:
    min: 10
    max: 50
    
logging:
  level: WARN
  
features:
  debug_mode: false
  profiling: false
```

## 配置加载

### 加载顺序
```
1. 默认配置 (代码内置)
    ↓
2. 主配置文件 (config/system.yaml)
    ↓
3. 环境配置 (config/env/{env}.yaml)
    ↓
4. 环境变量覆盖
    ↓
5. 配置中心动态配置
```

### 加载逻辑
```javascript
async function loadConfig() {
  // 1. 加载默认配置
  let config = defaultConfig;
  
  // 2. 加载主配置文件
  const mainConfig = await loadYaml('config/system.yaml');
  config = merge(config, mainConfig);
  
  // 3. 加载环境配置
  const env = process.env.NODE_ENV || 'development';
  const envConfig = await loadYaml(`config/env/${env}.yaml`);
  config = merge(config, envConfig);
  
  // 4. 环境变量覆盖
  config = applyEnvOverrides(config);
  
  // 5. 配置中心
  if (config.config_center.enabled) {
    const dynamicConfig = await fetchDynamicConfig();
    config = merge(config, dynamicConfig);
  }
  
  return config;
}
```

## 配置验证

### 验证规则
```yaml
validation:
  schema:
    server:
      port:
        type: integer
        min: 1
        max: 65535
        required: true
    database:
      host:
        type: string
        required: true
      pool:
        min:
          type: integer
          min: 1
        max:
          type: integer
          min: "${database.pool.min}"
```

### 验证流程
```javascript
function validateConfig(config, schema) {
  const errors = [];
  
  for (const [path, rules] of Object.entries(schema)) {
    const value = get(config, path);
    
    if (rules.required && value === undefined) {
      errors.push(`${path} is required`);
    }
    
    if (rules.type && typeof value !== rules.type) {
      errors.push(`${path} must be ${rules.type}`);
    }
    
    if (rules.min !== undefined && value < rules.min) {
      errors.push(`${path} must be >= ${rules.min}`);
    }
  }
  
  if (errors.length > 0) {
    throw new ConfigValidationError(errors);
  }
}
```

## 配置热更新

### 热更新配置
```yaml
hot_reload:
  enabled: true
  watch:
    - config/system.yaml
    - config/env/*.yaml
  interval: 10s
  callback: onConfigChange
```

### 更新处理
```javascript
async function onConfigChange(newConfig) {
  // 1. 验证新配置
  validateConfig(newConfig, schema);
  
  // 2. 计算配置差异
  const diff = computeDiff(currentConfig, newConfig);
  
  // 3. 应用可热更新配置
  for (const [path, value] of Object.entries(diff)) {
    if (isHotReloadable(path)) {
      applyConfig(path, value);
    }
  }
  
  // 4. 记录需要重启的配置
  const requireRestart = diff.filter(
    ([path]) => !isHotReloadable(path)
  );
  
  if (requireRestart.length > 0) {
    notifyRestartRequired(requireRestart);
  }
}
```

## 敏感配置

### 加密存储
```yaml
secrets:
  storage: vault
  paths:
    - database/password
    - api/keys
    - jwt/secret
  encryption: aes-256-gcm
```

### 访问控制
```yaml
access_control:
  secrets:
    read:
      - admin
      - service_account
    write:
      - admin
    audit: true
```

## 配置文档

### 文档生成
```yaml
documentation:
  auto_generate: true
  output: docs/config.md
  include:
    - description
    - type
    - default
    - required
    - example
```

### 文档示例
```markdown
## server.port

- **类型**: integer
- **必需**: 是
- **默认值**: 8080
- **范围**: 1-65535
- **说明**: 服务监听端口
- **示例**: 8080
```

## 维护方式
- 新增配置: 更新配置文件和schema
- 调整默认值: 更新默认配置
- 新增环境: 创建环境配置文件

## 引用文件
- `runtime/EXECUTION_POLICY.md` - 执行策略
- `safety/RISK_POLICY.md` - 风险策略
