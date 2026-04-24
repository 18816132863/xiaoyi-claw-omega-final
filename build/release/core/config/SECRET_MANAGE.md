# SECRET_MANAGE.md - 密钥管理规范

## 目的
定义密钥的存储、访问和轮换规范。

## 适用范围
所有敏感信息的管理，包括密码、密钥、证书。

## 密钥类型

| 类型 | 说明 | 存储方式 | 轮换周期 |
|------|------|----------|----------|
| 数据库密码 | 数据库访问 | Vault | 90天 |
| API密钥 | 外部API访问 | Vault | 180天 |
| JWT密钥 | Token签名 | Vault | 365天 |
| 加密密钥 | 数据加密 | HSM | 365天 |
| 证书 | TLS证书 | 证书管理 | 365天 |

## 密钥存储

### 存储架构
```yaml
storage:
  primary: vault
  backup: encrypted_file
  hsm:
    enabled: true
    type: aws_cloudhsm
```

### Vault配置
```yaml
vault:
  address: ${VAULT_ADDR}
  auth:
    method: kubernetes
    role: openclaw
  secrets:
    - path: secret/data/database
      key: password
    - path: secret/data/api
      key: keys
  cache:
    enabled: true
    ttl: 300
```

## 密钥访问

### 访问控制
```yaml
access_control:
  policies:
    - name: database_readonly
      paths:
        - secret/data/database
      capabilities: [read]
    - name: api_full
      paths:
        - secret/data/api
      capabilities: [read, update]
```

### 访问流程
```javascript
async function getSecret(path, key) {
  // 1. 检查缓存
  const cached = await cache.get(`secret:${path}:${key}`);
  if (cached) return cached;
  
  // 2. 从Vault获取
  const secret = await vault.read(path);
  const value = secret.data[key];
  
  // 3. 缓存
  await cache.set(`secret:${path}:${key}`, value, { ttl: 300 });
  
  // 4. 审计
  await audit.log({
    action: 'secret_access',
    path,
    key,
    timestamp: Date.now()
  });
  
  return value;
}
```

## 密钥轮换

### 轮换策略
```yaml
rotation:
  database_password:
    enabled: true
    period: 90d
    grace_period: 7d
    auto_rotate: true
  api_key:
    enabled: true
    period: 180d
    grace_period: 14d
    auto_rotate: false
  jwt_secret:
    enabled: true
    period: 365d
    grace_period: 30d
    auto_rotate: true
```

### 轮换流程
```
轮换触发
    ↓
┌─────────────────────────────────────┐
│ 1. 生成新密钥                        │
│    - 生成新密钥                      │
│    - 存储到Vault                     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 宽限期运行                        │
│    - 新旧密钥同时有效                │
│    - 逐步切换服务                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 废弃旧密钥                        │
│    - 确认所有服务已切换              │
│    - 废弃旧密钥                      │
└─────────────────────────────────────┘
```

## 密钥注入

### 注入方式
| 方式 | 说明 | 适用场景 |
|------|------|----------|
| 环境变量 | 启动时注入 | 容器部署 |
| 文件挂载 | 运行时挂载 | Kubernetes |
| API获取 | 运行时获取 | 动态密钥 |

### Kubernetes注入
```yaml
# Pod配置
spec:
  containers:
    - name: app
      env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
  volumes:
    - name: secrets
      secret:
        secretName: app-secrets
```

## 密钥审计

### 审计日志
```yaml
audit:
  events:
    - secret_access
    - secret_create
    - secret_update
    - secret_delete
    - secret_rotate
  fields:
    - timestamp
    - user
    - action
    - path
    - key
    - source_ip
  retention: 365d
```

### 审计报告
```yaml
reports:
  - name: access_summary
    frequency: daily
    content:
      - total_accesses
      - unique_users
      - suspicious_access
  - name: rotation_status
    frequency: weekly
    content:
      - pending_rotations
      - overdue_rotations
      - failed_rotations
```

## 密钥泄露处理

### 泄露检测
```yaml
leak_detection:
  enabled: true
  sources:
    - git_commits
    - logs
    - error_messages
  patterns:
    - password_pattern
    - api_key_pattern
    - token_pattern
```

### 泄露响应
```yaml
leak_response:
  steps:
    - name: revoke
      action: immediate_revoke
    - name: rotate
      action: force_rotate
    - name: notify
      action: alert_security_team
    - name: investigate
      action: security_audit
  timeline:
    revoke: 0
    rotate: 1h
    notify: 15m
    investigate: 24h
```

## 监控告警

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 访问异常 | 异常访问模式 | 触发规则 |
| 轮换延迟 | 超期未轮换 | >7天 |
| 访问失败 | 访问失败次数 | >10次/小时 |
| 泄露检测 | 检测到泄露 | 立即 |

## 维护方式
- 新增密钥: 创建密钥配置
- 调整轮换: 更新轮换策略
- 泄露处理: 执行泄露响应流程

## 引用文件
- `safety/RISK_POLICY.md` - 风险策略
- `governance/AUDIT_LOG.md` - 审计日志
