# FEEDBACK_LEARNING.md - 反馈学习机制

## 目的
定义反馈学习机制，通过用户反馈持续优化检索排序和路由决策。

## 适用范围
所有检索、排序、路由场景的反馈学习和优化。

---

## 一、反馈信号定义

### 1.1 反馈信号类型
| 信号类型 | 代码 | 来源 | 权重 | 说明 |
|----------|------|------|------|------|
| 点击信号 | click | 用户行为 | 0.25 | 用户点击了哪个结果 |
| 停留时间 | dwell | 用户行为 | 0.20 | 用户查看结果的时间 |
| 显式评分 | rating | 用户主动 | 0.30 | 用户主动评分 |
| 重试模式 | retry | 用户行为 | 0.15 | 用户是否重新查询 |
| 复制行为 | copy | 用户行为 | 0.10 | 用户是否复制结果 |

### 1.2 信号收集
```yaml
signal_collection:
  click:
    description: "点击信号"
    events:
      - result_clicked
      - result_viewed
      - result_expanded
    attributes:
      - result_id
      - result_rank
      - query_id
      - timestamp
  
  dwell:
    description: "停留时间"
    events:
      - result_view_start
      - result_view_end
    calculation: "end_time - start_time"
    normalization: "dwell / avg_dwell"
  
  rating:
    description: "显式评分"
    events:
      - result_rated
      - feedback_submitted
    scale: 1-5
    normalization: "rating / 5"
  
  retry:
    description: "重试模式"
    events:
      - query_reformulated
      - query_refined
    calculation: "1 if retry else 0"
  
  copy:
    description: "复制行为"
    events:
      - result_copied
      - result_selected
    calculation: "1 if copy else 0"
```

---

## 二、反馈处理流程

### 2.1 处理流程
```
用户行为
    ↓
┌─────────────────────────────────────┐
│ 1. 信号收集                          │
│    - 事件监听                        │
│    - 数据提取                        │
│    - 格式标准化                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 信号验证                          │
│    - 有效性检查                      │
│    - 异常过滤                        │
│    - 去重处理                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 信号聚合                          │
│    - 按查询聚合                      │
│    - 按结果聚合                      │
│    - 时间窗口聚合                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 模型更新                          │
│    - 权重调整                        │
│    - 参数优化                        │
│    - 模型持久化                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 5. 效果评估                          │
│    - A/B 测试                        │
│ - 指标监控                        │
│    - 效果报告                        │
└─────────────────────────────────────┘
```

### 2.2 信号验证
```yaml
signal_validation:
  validity_check:
    - user_id_exists
    - query_id_exists
    - result_id_exists
    - timestamp_valid
  
  anomaly_filter:
    - click_bots: "过滤异常高频点击"
    - dwell_outliers: "过滤异常停留时间"
    - rating_spam: "过滤异常评分模式"
  
  deduplication:
    method: "time_window"
    window: 60s
    by: ["user_id", "query_id", "result_id"]
```

---

## 三、学习算法

### 3.1 权重学习
```python
def update_weights(current_weights, feedback, learning_rate=0.01):
    """
    基于反馈更新检索权重
    
    Args:
        current_weights: 当前权重 {route: weight}
        feedback: 反馈数据
        learning_rate: 学习率
    
    Returns:
        dict: 更新后的权重
    """
    new_weights = current_weights.copy()
    
    for route, weight in current_weights.items():
        # 计算该路由的反馈分数
        route_feedback = feedback.get(route, {})
        
        # 正反馈：用户选择了该路由的结果
        positive = route_feedback.get('positive', 0)
        # 负反馈：用户忽略了该路由的结果
        negative = route_feedback.get('negative', 0)
        
        # 计算梯度
        total = positive + negative
        if total > 0:
            gradient = (positive - negative) / total
            # 更新权重
            new_weights[route] = weight + learning_rate * gradient
            # 归一化
            new_weights[route] = max(0.1, min(0.9, new_weights[route]))
    
    # 归一化所有权重
    total = sum(new_weights.values())
    for route in new_weights:
        new_weights[route] /= total
    
    return new_weights
```

### 3.2 排序学习
```python
def update_ranking_model(model, feedback_samples, learning_rate=0.01):
    """
    基于反馈更新排序模型
    
    Args:
        model: 当前排序模型
        feedback_samples: 反馈样本列表
        learning_rate: 学习率
    
    Returns:
        dict: 更新后的模型参数
    """
    for sample in feedback_samples:
        query = sample['query']
        results = sample['results']
        clicked = sample['clicked_result']
        
        # 获取点击结果的排名
        clicked_rank = None
        for i, result in enumerate(results):
            if result['id'] == clicked:
                clicked_rank = i
                break
        
        if clicked_rank is None:
            continue
        
        # 学习：提升点击结果的分数，降低未点击结果的分数
        for i, result in enumerate(results):
            result_id = result['id']
            current_score = model.get(result_id, 0.5)
            
            if i == clicked_rank:
                # 点击结果：提升分数
                adjustment = learning_rate * (1 - current_score)
            else:
                # 未点击结果：降低分数（与排名差距成反比）
                rank_diff = abs(i - clicked_rank)
                adjustment = -learning_rate * current_score / (rank_diff + 1)
            
            model[result_id] = current_score + adjustment
    
    return model
```

### 3.3 路由学习
```python
def update_routing_thresholds(thresholds, feedback, learning_rate=0.005):
    """
    基于反馈更新路由阈值
    
    Args:
        thresholds: 当前阈值 {mode: threshold}
        feedback: 路由反馈数据
        learning_rate: 学习率
    
    Returns:
        dict: 更新后的阈值
    """
    new_thresholds = thresholds.copy()
    
    for mode, data in feedback.items():
        # 该模式的成功率和延迟
        success_rate = data.get('success_rate', 0.5)
        avg_latency = data.get('avg_latency', 0)
        target_latency = data.get('target_latency', 0)
        
        # 如果成功率低，提高阈值（减少使用该模式）
        if success_rate < 0.8:
            adjustment = learning_rate * (0.8 - success_rate)
            new_thresholds[mode] = min(thresholds[mode] - adjustment, 0.9)
        
        # 如果延迟超标，提高阈值
        if avg_latency > target_latency * 1.5:
            adjustment = learning_rate * 0.5
            new_thresholds[mode] = min(thresholds[mode] - adjustment, 0.9)
        
        # 如果表现好，可以降低阈值（更多使用该模式）
        if success_rate > 0.9 and avg_latency < target_latency:
            adjustment = learning_rate * 0.2
            new_thresholds[mode] = max(thresholds[mode] + adjustment, 0.1)
    
    return new_thresholds
```

---

## 四、学习策略

### 4.1 在线学习
```yaml
online_learning:
  enabled: true
  
  update:
    method: "stochastic_gradient_descent"
    rate: 0.01
    decay: 0.99
    min_rate: 0.001
  
  batch:
    size: 100
    timeout: 60s
  
  storage:
    path: "~/.openclaw/memory/learning_model.json"
    backup_interval: 3600
```

### 4.2 批量学习
```yaml
batch_learning:
  enabled: true
  
  schedule: "0 2 * * *"  # 每天凌晨2点
  
  process:
    - load_feedback_data
    - aggregate_signals
    - train_model
    - validate_model
    - deploy_model
  
  validation:
    method: "holdout"
    ratio: 0.2
    metrics: [ndcg, mrr, precision]
```

### 4.3 强化学习
```yaml
reinforcement_learning:
  enabled: false  # 高级功能，默认关闭
  
  algorithm: "policy_gradient"
  
  state:
    - query_complexity
    - system_load
    - history_context
  
  action:
    - select_mode
    - adjust_weights
  
  reward:
    - user_satisfaction
    - latency_penalty
    - accuracy_bonus
  
  training:
    episodes: 1000
    gamma: 0.99
    epsilon: 0.1
```

---

## 五、模型管理

### 5.1 模型版本
```yaml
model_versioning:
  strategy: "semantic"
  
  versions:
    current: "1.0.0"
    staging: "1.1.0-beta"
    production: "1.0.0"
  
  rollback:
    enabled: true
    keep_versions: 10
    auto_rollback_threshold: 0.7
```

### 5.2 模型部署
```yaml
model_deployment:
  strategy: "canary"
  
  canary:
    traffic: 10%
    duration: 24h
    metrics: [accuracy, latency, satisfaction]
    rollback_threshold: 0.8
  
  full_deploy:
    condition: "canary_success"
    gradual: true
    steps: [10%, 30%, 50%, 100%]
```

### 5.3 模型存储
```json
{
  "model_metadata": {
    "version": "1.0.0",
    "created_at": "2026-04-07T10:00:00Z",
    "updated_at": "2026-04-07T11:00:00Z",
    "training_samples": 10000,
    "validation_score": 0.92
  },
  "weights": {
    "vector": 0.5,
    "fts": 0.3,
    "llm": 0.15,
    "time": 0.05
  },
  "thresholds": {
    "fast": 0.3,
    "balanced": 0.6,
    "full": 0.8
  },
  "ranking_adjustments": {
    "doc_001": 0.05,
    "doc_002": -0.02
  }
}
```

---

## 六、效果评估

### 6.1 评估指标
| 指标 | 说明 | 目标 | 告警阈值 |
|------|------|------|----------|
| NDCG@10 | 归一化折损累积增益 | > 0.85 | < 0.75 |
| MRR | 平均倒数排名 | > 0.7 | < 0.6 |
| 点击率 | 首位点击率 | > 60% | < 40% |
| 满意度 | 用户满意度 | > 4.0 | < 3.5 |
| 学习速度 | 模型改进速度 | > 1%/周 | < 0.5%/周 |

### 6.2 A/B 测试框架
```yaml
ab_testing:
  enabled: true
  
  experiments:
    - id: "exp_001"
      name: "权重优化实验"
      start: "2026-04-07"
      variants:
        control:
          weights: {vector: 0.5, fts: 0.3, llm: 0.15, time: 0.05}
        treatment:
          weights: {vector: 0.45, fts: 0.35, llm: 0.15, time: 0.05}
      metrics: [ndcg, mrr, latency]
      traffic: 20%
      duration: 7d
    
    - id: "exp_002"
      name: "路由阈值实验"
      start: "2026-04-07"
      variants:
        control:
          thresholds: {fast: 0.3, balanced: 0.6, full: 0.8}
        treatment:
          thresholds: {fast: 0.25, balanced: 0.55, full: 0.75}
      metrics: [accuracy, latency, mode_distribution]
      traffic: 10%
      duration: 14d
```

---

## 七、反馈报告

### 7.1 日报格式
```markdown
## 反馈学习日报

### 统计概览
| 指标 | 今日 | 昨日 | 变化 |
|------|------|------|------|
| 反馈样本数 | 1,234 | 1,100 | +12% |
| 平均满意度 | 4.2 | 4.1 | +2% |
| 首位点击率 | 65% | 63% | +2% |
| 模型更新次数 | 3 | 2 | +1 |

### 权重变化
| 路由 | 当前权重 | 昨日权重 | 变化 |
|------|----------|----------|------|
| vector | 0.48 | 0.50 | -2% |
| fts | 0.32 | 0.30 | +7% |
| llm | 0.15 | 0.15 | 0% |
| time | 0.05 | 0.05 | 0% |

### 效果评估
- NDCG@10: 0.88 (目标: > 0.85) ✅
- MRR: 0.72 (目标: > 0.70) ✅
- 平均延迟: 280ms (目标: < 500ms) ✅
```

### 7.2 周报格式
```markdown
## 反馈学习周报

### 本周亮点
1. 权重优化：FTS 权重提升 5%，检索准确率提升 3%
2. 路由优化：fast 模式阈值下调，使用率提升 10%
3. 新增反馈信号：复制行为信号上线

### 模型演进
| 版本 | 发布时间 | 主要变更 | 效果 |
|------|----------|----------|------|
| 1.0.0 | 04-01 | 初始版本 | 基线 |
| 1.0.1 | 04-03 | 权重微调 | +2% NDCG |
| 1.0.2 | 04-05 | 阈值优化 | +5% 准确率 |

### 下周计划
1. 上线强化学习实验
2. 优化停留时间信号处理
3. 启动路由阈值 A/B 测试
```

---

## 八、配置汇总

### 8.1 完整配置
```json
{
  "feedback_learning": {
    "enabled": true,
    
    "signals": {
      "click": {"weight": 0.25, "enabled": true},
      "dwell": {"weight": 0.20, "enabled": true},
      "rating": {"weight": 0.30, "enabled": true},
      "retry": {"weight": 0.15, "enabled": true},
      "copy": {"weight": 0.10, "enabled": true}
    },
    
    "learning": {
      "online": {
        "enabled": true,
        "rate": 0.01,
        "batch_size": 100
      },
      "batch": {
        "enabled": true,
        "schedule": "0 2 * * *"
      }
    },
    
    "model": {
      "versioning": true,
      "rollback": true,
      "deployment": "canary"
    },
    
    "evaluation": {
      "metrics": ["ndcg", "mrr", "click_rate", "satisfaction"],
      "ab_testing": true
    }
  }
}
```

---

## 九、与其他模块联动

| 模块 | 联动方式 |
|------|----------|
| optimization/RRF_FUSION.md | 反馈学习优化 RRF 权重 |
| optimization/SMART_ROUTING.md | 反馈学习优化路由阈值 |
| optimization/PERFORMANCE_MONITORING.md | 监控学习效果 |
| governance/AUDIT_LOG.md | 反馈操作审计 |

---

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-07
- 下次评审: 2026-07-07
