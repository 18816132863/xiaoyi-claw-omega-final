# ENV_CONFIG.md - 环境配置规范

## 目的
定义不同环境的配置管理和切换规范。

## 适用范围
所有部署环境的配置管理。

## 环境类型

| 环境 | 用途 | 数据 | 访问权限 |
|------|------|------|----------|
| development | 开发 | 模拟数据 | 开发团队 |
| testing | 测试 | 测试数据 | 测试团队 |
| staging | 预发布 | 生产副本 | 运维团队 |
| production | 生产 | 真实数据 | 运维团队 |

## 环境配置

### 开发环境
```yaml
# config/env/development.yaml
env: development

system:
  debug: true
  profiling: true
  
server:
  host: localhost
  port: 8080
  workers: 1
  
database:
  host: localhost
  port: 5432
  name: openclaw_dev
  pool:
    min: 1
    max: 5
    
cache:
  host: localhost
  port: 6379
  
logging:
  level: DEBUG
  format: text
  
features:
  all_enabled: true
  mock_external: true
```

### 测试环境
```yaml
# config/env/testing.yaml
env: testing

system:
  debug: true
  
server:
  host: 0.0.0.0
  port: 8080
  workers: 2
  
database:
  host: ${DB_HOST}
  name: openclaw_test
  pool:
    min: 2
    max: 10
    
logging:
  level: INFO
  
features:
  test_mode: true
```

### 预发布环境
```yaml
# config/env/staging.yaml
env: staging

system:
  debug: false
  
server:
  host: 0.0.0.0
  port: 8080
  workers: 4
  
database:
  host: ${DB_HOST}
  name: openclaw_staging
  pool:
    min: 5
    max: 20
    
logging:
  level: INFO
  
features:
  production_like: true
```

### 生产环境
```yaml
# config/env/production.yaml
env: production

system:
  debug: false
  profiling: false
  
server:
  host: 0.0.0.0
  port: 8080
  workers: 8
  
database:
  host: ${DB_HOST}
  name: openclaw_prod
  pool:
    min: 10
    max: 50
  ssl: true
  
cache:
  cluster: true
  nodes:
    - ${REDIS_NODE_1}
    - ${REDIS_NODE_2}
    - ${REDIS_NODE_3}
    
logging:
  level: WARN
  format: json
  
monitoring:
  enabled: true
  metrics_port: 9090
  
features:
  production_only: true
```

## 环境切换

### 切换方式
| 方式 | 说明 | 适用场景 |
|------|------|----------|
| 环境变量 | NODE_ENV | 本地开发 |
| 配置文件 | --config | 部署切换 |
| 配置中心 | 动态获取 | 运行时切换 |

### 切换流程
```bash
# 开发环境
export NODE_ENV=development
npm start

# 测试环境
export NODE_ENV=testing
npm start

# 生产环境
export NODE_ENV=production
npm start
```

## 环境隔离

### 数据隔离
```yaml
data_isolation:
  database:
    development: openclaw_dev
    testing: openclaw_test
    staging: openclaw_staging
    production: openclaw_prod
  cache:
    prefix:
      development: dev:
      testing: test:
      staging: staging:
      production: prod:
```

### 网络隔离
```yaml
network:
  development:
    vpc: vpc-dev
    subnet: subnet-dev
  testing:
    vpc: vpc-test
    subnet: subnet-test
  staging:
    vpc: vpc-staging
    subnet: subnet-staging
  production:
    vpc: vpc-prod
    subnet: subnet-prod
    security_group: sg-prod
```

## 环境验证

### 验证清单
```yaml
checklist:
  pre_deploy:
    - config_validated
    - secrets_configured
    - dependencies_available
  post_deploy:
    - health_check_passed
    - smoke_tests_passed
    - metrics_reporting
```

### 健康检查
```yaml
health_check:
  endpoint: /health
  checks:
    - database
    - cache
    - external_services
  interval: 30s
  timeout: 10s
```

## 环境同步

### 配置同步
```yaml
sync:
  source: production
  targets:
    - staging
  exclude:
    - secrets
    - endpoints
  schedule: daily
```

### 数据同步
```yaml
data_sync:
  source: production
  target: staging
  tables:
    - users
    - products
  anonymize: true
  schedule: weekly
```

## 环境监控

### 监控配置
```yaml
monitoring:
  development:
    enabled: false
  testing:
    enabled: true
    alerting: false
  staging:
    enabled: true
    alerting: true
  production:
    enabled: true
    alerting: true
    escalation: true
```

## 维护方式
- 新增环境: 创建环境配置文件
- 调整配置: 更新对应环境配置
- 环境同步: 执行同步流程

## 引用文件
- `config/SYSTEM_CONFIG.md` - 系统配置
- `runtime/EXECUTION_POLICY.md` - 执行策略
