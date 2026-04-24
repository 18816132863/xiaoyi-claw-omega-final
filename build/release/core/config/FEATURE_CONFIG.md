# FEATURE_CONFIG.md - 功能配置规范

## 目的
定义功能配置的管理、开关和灰度规范。

## 适用范围
所有功能特性的配置管理。

## 功能配置结构

### 功能定义
```yaml
feature:
  id: smart_recommend
  name: "智能推荐"
  version: "2.0"
  status: enabled
  
  config:
    algorithm: collaborative_filtering
    max_results: 10
    min_score: 0.5
    cache_ttl: 300
    
  rollout:
    strategy: percentage
    percentage: 50
    
  targeting:
    rules:
      - condition: "user.segment == 'premium'"
        enabled: true
      - condition: "user.region == 'cn'"
        enabled: true
        
  dependencies:
    - feature: user_profile
      required: true
    - feature: analytics
      required: false
```

## 功能状态

| 状态 | 说明 | 可见性 | 控制方式 |
|------|------|--------|----------|
| development | 开发中 | 内部 | 开发团队 |
| testing | 测试中 | 测试用户 | 测试团队 |
| beta | 灰度中 | 部分用户 | 产品团队 |
| released | 已发布 | 全部用户 | 运维团队 |
| deprecated | 已废弃 | 逐步下线 | 运维团队 |
| disabled | 已禁用 | 不可见 | 运维团队 |

## 配置管理

### 配置存储
```yaml
storage:
  type: database
  table: feature_configs
  cache:
    enabled: true
    ttl: 60
  versioning: true
```

### 配置版本
```yaml
versioning:
  enabled: true
  max_versions: 10
  rollback_enabled: true
  audit: true
```

## 功能开关

### 开关类型
| 类型 | 说明 | 生命周期 |
|------|------|----------|
| 发布开关 | 新功能发布控制 | 短期 |
| 实验开关 | A/B测试控制 | 中期 |
| 运维开关 | 运维控制 | 长期 |
| 权限开关 | 权限控制 | 长期 |

### 开关配置
```yaml
switches:
  - id: new_ui_enabled
    type: release
    default: false
    rollout:
      internal: true
      beta: 10%
      production: 0%
      
  - id: experiment_v2
    type: experiment
    experiment_id: exp_001
    variants:
      - control: false
      - treatment: true
```

## 灰度发布

### 灰度策略
| 策略 | 说明 | 配置 |
|------|------|------|
| 百分比 | 按比例放量 | percentage: 50 |
| 白名单 | 指定用户 | whitelist: [user1, user2] |
| 地域 | 按地域 | regions: [cn-north, cn-south] |
| 用户属性 | 按用户属性 | attributes: {segment: premium} |

### 灰度计划
```yaml
rollout_plan:
  feature: smart_recommend
  stages:
    - name: internal
      percentage: 1
      targets: [internal]
      duration: 1d
      metrics:
        - error_rate < 0.1%
    - name: beta
      percentage: 10
      targets: [beta_users]
      duration: 3d
    - name: production
      percentage: 100
      targets: [all]
```

## 功能依赖

### 依赖类型
| 类型 | 说明 | 处理方式 |
|------|------|----------|
| 强依赖 | 必须可用 | 功能不可用 |
| 弱依赖 | 可选可用 | 降级处理 |
| 互斥 | 不能共存 | 禁用其一 |

### 依赖检查
```javascript
function checkDependencies(featureId) {
  const feature = getFeature(featureId);
  const dependencies = feature.dependencies;
  
  for (const dep of dependencies) {
    const depFeature = getFeature(dep.feature);
    
    if (dep.required && depFeature.status !== 'enabled') {
      return {
        available: false,
        reason: `Dependency ${dep.feature} not available`
      };
    }
  }
  
  return { available: true };
}
```

## 配置继承

### 继承规则
```yaml
inheritance:
  global:
    - logging
    - monitoring
  service:
    extends: global
    adds:
      - database
      - cache
  feature:
    extends: service
    adds:
      - feature_specific
```

### 覆盖规则
```yaml
override:
  priority:
    - feature_config
    - service_config
    - global_config
  merge_strategy: deep_merge
```

## 监控告警

### 监控指标
| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 功能可用性 | 功能是否可用 | <99% |
| 配置加载延迟 | 配置加载时间 | >1s |
| 灰度比例偏差 | 实际vs预期 | >5% |

### 告警配置
```yaml
alerting:
  - condition: feature_availability < 99%
    level: P1
    channels: [sms, im]
  - condition: config_load_time > 1s
    level: P2
    channels: [im]
```

## 维护方式
- 新增功能: 创建功能配置
- 调整灰度: 更新灰度计划
- 功能下线: 更新状态为deprecated

## 引用文件
- `experiments/FEATURE_FLAGS.md` - 功能开关
- `experiments/ROLLOUT_STRATEGY.md` - 发布策略
