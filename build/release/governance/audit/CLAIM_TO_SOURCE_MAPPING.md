# CLAIM_TO_SOURCE_MAPPING.md - 结论来源映射规范

## 目的
定义"结论-来源"映射规范，确保平台能清楚说明哪句话基于哪份证据。

## 适用范围
- 结论来源绑定
- 多来源合并
- 来源冲突标记
- 推断内容标识

## 核心规则

### 1. 关键 Claim 绑定来源

```yaml
claim_binding:
  # 绑定要求
  requirements:
    - 每个 claim 必须有至少一个来源
    - 来源必须可追溯
    - 来源必须可验证
  
  # 绑定格式
  format:
    claim_id: "claim_001"
    claim_text: "公司2023年营收增长15%"
    sources:
      - source_id: "src_001"
        source_type: "document"
        source_title: "2023年度报告"
        source_location: "第12页第3段"
        source_url: "https://..."
        relevance: "direct"
        confidence: 0.95
  
  # 绑定规则
  rules:
    - 直接引用必须标注原文位置
    - 间接引用必须标注推理链
    - 多来源必须标注合并方式
```

### 2. 多来源合并

```yaml
source_merging:
  # 合并场景
  scenarios:
    consistent:
      description: "多来源一致"
      action: "合并为一个来源组"
      confidence: "取最高"
    
    complementary:
      description: "多来源互补"
      action: "保留所有来源"
      confidence: "加权平均"
    
    conflicting:
      description: "多来源冲突"
      action: "标记冲突，保留所有"
      confidence: "标注不确定性"
  
  # 合并规则
  rules:
    - 优先使用一手来源
    - 标注每个来源的贡献
    - 记录合并逻辑
    - 保留原始来源链接
```

### 3. 来源冲突标记

```yaml
conflict_marking:
  # 冲突类型
  types:
    factual_conflict:
      description: "事实性冲突"
      example: "来源A说增长15%，来源B说增长12%"
      marking: "[冲突: 来源A vs 来源B]"
    
    interpretation_conflict:
      description: "解读性冲突"
      example: "来源A认为正面，来源B认为负面"
      marking: "[解读分歧]"
    
    temporal_conflict:
      description: "时效性冲突"
      example: "来源A是2023年数据，来源B是2022年数据"
      marking: "[时效差异]"
  
  # 冲突处理
  handling:
    - 明确标注冲突存在
    - 提供所有冲突来源
    - 说明选择理由（如有）
    - 建议用户自行判断
```

### 4. 推断内容标识

```yaml
inference_marking:
  # 推断类型
  types:
    logical_inference:
      description: "逻辑推断"
      marking: "[推断: 基于...逻辑]"
      example: "基于历史趋势推断"
    
    statistical_inference:
      description: "统计推断"
      marking: "[推断: 统计模型]"
      example: "基于回归分析预测"
    
    expert_inference:
      description: "专家推断"
      marking: "[推断: 专家观点]"
      example: "基于专家访谈"
  
  # 推断标识规则
  rules:
    - 推断必须与事实区分
    - 推断必须标注依据
    - 推断必须标注置信度
    - 推断不能作为唯一依据
```

### 5. 来源质量评估

```yaml
source_quality:
  # 质量维度
  dimensions:
    credibility:
      description: "可信度"
      factors:
        - 来源权威性
        - 发布机构
        - 同行评审
    
    recency:
      description: "时效性"
      factors:
        - 发布时间
        - 数据时效
        - 更新频率
    
    relevance:
      description: "相关性"
      factors:
        - 与结论的直接程度
        - 覆盖范围
        - 适用场景
  
  # 质量评分
  scoring:
    high:
      score: ">= 0.8"
      description: "高质量来源"
    
    medium:
      score: "0.5 - 0.8"
      description: "中等质量来源"
    
    low:
      score: "< 0.5"
      description: "低质量来源"
```

### 6. 来源追溯查询

```yaml
traceability:
  # 查询能力
  query:
    by_claim: true
    by_source: true
    by_confidence: true
    by_type: true
  
  # 追溯路径
  path:
    - 从结论找到来源
    - 从来源找到原文
    - 从原文找到上下文
  
  # 追溯展示
  display:
    - 结论原文
    - 来源列表
    - 来源原文片段
    - 置信度说明
```

### 7. 来源更新机制

```yaml
source_update:
  # 更新触发
  triggers:
    - 来源内容变更
    - 来源失效
    - 新来源发现
    - 置信度变化
  
  # 更新动作
  actions:
    - 重新评估结论
    - 更新置信度
    - 通知相关方
    - 记录变更历史
  
  # 失效处理
  invalidation:
    - 标记来源失效
    - 评估结论影响
    - 寻找替代来源
    - 更新结论说明
```

## 异常处理

### 来源缺失
- 标注来源缺失
- 降低结论置信度
- 提示用户注意

### 来源失效
- 标注来源失效
- 尝试寻找替代
- 记录失效时间

### 冲突无法解决
- 保留所有来源
- 标注冲突状态
- 建议用户判断

## 完成标准
- [x] 关键 Claim 绑定规则完整
- [x] 多来源合并规则清晰
- [x] 来源冲突标记规则明确
- [x] 推断内容标识规则完整
- [x] 来源质量评估规则清晰
- [x] 来源追溯查询能力明确
- [x] 来源更新机制完整
- [x] 平台能清楚说明哪句话基于哪份证据

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-07
