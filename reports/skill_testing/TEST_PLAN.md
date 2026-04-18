# 技能实战测试方案 V1.0

## 测试目标

对13个核心技能进行商业级别实战测试，验证其实用性和商业价值。

---

## 测试标准

### 商业级别标准

| 维度 | 标准 | 权重 |
|------|------|------|
| **功能完整性** | 核心功能可用，无明显bug | 30% |
| **输出质量** | 输出内容专业、可用、有价值 | 30% |
| **易用性** | 命令简单、参数清晰、文档完善 | 20% |
| **商业价值** | 能解决真实商业问题 | 20% |

### 评分标准

| 评分 | 标准 |
|------|------|
| ⭐⭐⭐⭐⭐ | 商业级别，可直接商用 |
| ⭐⭐⭐⭐ | 接近商用，需小幅优化 |
| ⭐⭐⭐ | 基础可用，需大幅优化 |
| ⭐⭐ | 不可商用 |
| ⭐ | 废弃 |

---

## 测试用例

### 1. copywriter (文案创作)

**测试场景**: 为智能水杯产品创作小红书种草文案

**商业价值**: 电商营销、内容创作

**测试命令**:
```bash
python skill.py run --template default \
  --product "智能水杯" \
  --platform "小红书" \
  --target "25-35岁白领女性" \
  --selling-points "智能提醒,保温12小时,颜值高"
```

**预期输出**:
- 完整的小红书文案
- 包含标题、正文、标签
- 符合小红书风格

---

### 2. novel-generator (网文创作)

**测试场景**: 生成都市重生爽文第一章

**商业价值**: 网文创作、IP孵化

**测试命令**:
```bash
python skill.py run --template default \
  --theme "都市" \
  --protagonist "落魄富二代" \
  --golden-finger "重生系统" \
  --chapter 1
```

**预期输出**:
- 完整的章节内容
- 符合爽文节奏
- 人物设定清晰

---

### 3. claw-art (绘画创作)

**测试场景**: 生成国风少女插画提示词

**商业价值**: 商业插画、设计素材

**测试命令**:
```bash
python skill.py run --template default \
  --description "穿着汉服的少女站在桃花树下" \
  --style "国风" \
  --aspect-ratio "16:9"
```

**预期输出**:
- 中英文提示词
- 可直接用于AI绘图
- 风格明确

---

### 4. minimax-music-gen (音乐创作)

**测试场景**: 生成轻快背景音乐

**商业价值**: 视频配乐、广告音乐

**测试命令**:
```bash
python skill.py run --template default \
  --prompt "轻快、阳光、正能量" \
  --type "纯音乐"
```

**预期输出**:
- 音乐生成提示词
- 风格描述清晰

---

### 5. educational-video-creator (视频创作)

**测试场景**: 生成AI科普视频脚本

**商业价值**: 知识付费、短视频创作

**测试命令**:
```bash
python skill.py run --template default \
  --topic "AI如何改变我们的生活" \
  --duration "3分钟"
```

**预期输出**:
- 完整的视频脚本
- 分镜头描述
- 时长合理

---

### 6. markitdown (文档转换)

**测试场景**: 测试文档转换能力

**商业价值**: 文档处理、办公自动化

**测试命令**:
```bash
python skill.py run --template default \
  --action "convert" \
  --format "markdown"
```

**预期输出**:
- 转换功能说明
- 支持格式列表

---

### 7. doc-autofill (文档填写)

**测试场景**: 自动填写周报模板

**商业价值**: 办公自动化、效率提升

**测试命令**:
```bash
python skill.py run --template default \
  --type "周报" \
  --content "完成技能升级系统开发"
```

**预期输出**:
- 填写后的周报
- 格式规范

---

### 8. data-tracker (数据记录)

**测试场景**: 记录每日健康数据

**商业价值**: 健康管理、数据分析

**测试命令**:
```bash
python skill.py run --template default \
  --type "健康" \
  --data "睡眠7小时,运动30分钟,步数8000"
```

**预期输出**:
- 数据记录
- 趋势分析

---

### 9. xiaoyi-health (健康监控)

**测试场景**: 健康风险评估

**商业价值**: 健康管理、医疗辅助

**测试命令**:
```bash
python skill.py run --template default \
  --action "assess" \
  --symptoms "疲劳,失眠"
```

**预期输出**:
- 健康建议
- 风险提示

---

### 10. fitness-coach (营养定制)

**测试场景**: 生成减脂食谱

**商业价值**: 健康饮食、体重管理

**测试命令**:
```bash
python skill.py run --template default \
  --goal "减脂" \
  --calories "1500" \
  --meals "3"
```

**预期输出**:
- 一日三餐食谱
- 营养分析

---

### 11. xiaoyi-HarmonyOSSmartHome-skill (智能家居)

**测试场景**: 智能家居场景控制

**商业价值**: 智能家居、IoT

**测试命令**:
```bash
python skill.py run --template default \
  --scene "回家模式" \
  --devices "灯光,空调,窗帘"
```

**预期输出**:
- 场景配置
- 设备联动方案

---

## 测试流程

```
1. 执行测试命令
   ↓
2. 检查输出结果
   ↓
3. 评估商业价值
   ↓
4. 记录测试报告
   ↓
5. 提交到 reports/ (真源)
```

---

## 测试报告格式

```markdown
# 技能实战测试报告

**技能**: {skill_name}
**测试时间**: {timestamp}
**测试场景**: {scenario}

## 测试结果

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | X/5 | {description} |
| 输出质量 | X/5 | {description} |
| 易用性 | X/5 | {description} |
| 商业价值 | X/5 | {description} |
| **总分** | **X/5** | {conclusion} |

## 输出内容

{output}

## 改进建议

{suggestions}

## 商业价值评估

{business_value}
```

---

**版本**: V1.0
**创建时间**: 2026-04-18
