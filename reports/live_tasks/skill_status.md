# 13个核心技能状态与提升方案

## 一、已有技能 (可直接使用)

| 任务 | 技能名称 | 状态 | 路径 |
|------|----------|------|------|
| 网文创作 | novel-generator | ✅ 已有 | skills/novel-generator/ |
| AI视频创作 | educational-video-creator | ✅ 已有 | skills/educational-video-creator/ |
| 音乐创作 | minimax-music-gen | ✅ 已有 | skills/minimax-music-gen/ |
| 绘画创作 | claw-art | ✅ 已有 | skills/claw-art/ |
| 文案剧本创作 | copywriter | ✅ 已有 | skills/copywriter/ |
| 文档转换与处理 | markitdown, docx, xiaoyi-doc-convert | ✅ 已有 | skills/markitdown/, skills/docx/ |
| APP操作与执行 | xiaoyi_gui_agent (内置) | ✅ 已有 | 内置工具 |

## 二、需要增强的技能

| 任务 | 现有技能 | 需要增强 |
|------|----------|----------|
| 数据记录与复盘 | 无专门技能 | 需要创建 `data-tracker` |
| 文档自动填写 | docx, excel-analysis | 需要增强模板填写能力 |
| AI看病与算命 | xiaoyi-health | 需要增强AI诊断能力 |
| 个人营养与食谱定制 | fitness-coach | 需要增强营养分析 |
| AI健康监控与疾病预防 | xiaoyi-health | 需要增强预警能力 |
| 万物互联与智控 | xiaoyi-HarmonyOSSmartHome-skill | 需要确认设备支持 |

## 三、需要创建的技能

### 1. data-tracker (数据记录与复盘)

**功能**:
- 记录用户指定的数据（睡眠、运动、阅读等）
- 每日自动汇总
- 生成复盘报告
- 沉淀到长期记忆

**需要什么**:
- ✅ 已有: memory.write, note.create, report.write
- ❌ 需要: 数据模板定义

### 2. doc-autofill (文档自动填写)

**功能**:
- 根据模板自动填写Word/Excel
- 从长期记忆读取数据
- 支持自定义数据源

**需要什么**:
- ✅ 已有: docx, excel-analysis
- ❌ 需要: 模板解析 + 数据映射逻辑

## 四、提升方案

### 立即可用 (7个)

```
1. 网文创作 → make 调用 novel-generator
2. 视频创作 → make 调用 educational-video-creator
3. 音乐创作 → make 调用 minimax-music-gen
4. 绘画创作 → make 调用 claw-art
5. 文案创作 → make 调用 copywriter
6. 文档转换 → make 调用 markitdown
7. APP操作 → 直接使用 xiaoyi_gui_agent
```

### 需要增强 (6个)

```
1. 数据记录 → 创建 data-tracker 技能
2. 自动填表 → 增强 docx 技能
3. AI看病 → 增强 xiaoyi-health 技能
4. 营养定制 → 增强 fitness-coach 技能
5. 健康监控 → 增强 xiaoyi-health 技能
6. 智能家居 → 确认 xiaoyi-HarmonyOSSmartHome-skill 可用性
```

## 五、需要你提供的信息

### 智能家居
- 你有哪些智能设备？（品牌/型号）
- 使用什么平台？（米家/华为HiLink/天猫精灵）

### 健康数据
- 有没有可穿戴设备？（手环/手表）
- 需要对接什么健康APP？

### 文档自动填写
- 有哪些常用表格模板？
- 需要填写哪些个人信息？

---

## 下一步

1. **立即可用的7个技能** → 我可以直接调用
2. **需要增强的6个技能** → 需要你提供上述信息
3. **创建新技能** → data-tracker 我可以现在创建

要我先创建 `data-tracker` 技能吗？
