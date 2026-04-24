# FEEDBACK_SYSTEM.md - 反馈系统

## 目的
收集用户反馈，持续改进系统。

## 反馈类型

| 类型 | 描述 | 特性 |
|------|------|------|
| 评分反馈 | 1-5星评分 | 自动提示 |
| 评论反馈 | 自由文本 | 情感分析 |
| 问题报告 | Bug报告 | 自动收集 |
| 功能建议 | 新功能建议 | 投票机制 |

## 核心特性

### 1. 自动分析
- 情感分析
- 趋势识别
- 问题分类

### 2. 响应通知
- 反馈状态更新
- 处理结果通知

### 3. 改进追踪
- 改进进度追踪
- 效果验证

### 4. 奖励系统
- 反馈积分
- 贡献徽章

## 使用示例

```bash
# 提交评分
openclaw feedback rate --score 5

# 提交评论
openclaw feedback comment "很好用"

# 报告问题
openclaw feedback bug --description "xxx"

# 功能建议
openclaw feedback suggest --feature "xxx"

# 查看反馈状态
openclaw feedback status --id "xxx"
```

---
*V18.0 反馈系统*
