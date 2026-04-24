# 兼容副本 - 真源在 core/TOOLS.md
# TOOLS.md - Tool Rules
## 联网搜索
- **默认**: xiaoyi-web-search
- **优势**: 中文优化、开箱即用
## 手机操控 (xiaoyi-gui-agent)
### 适用场景
- 需要操作手机APP界面
- 数据仅存在于APP内部
- 执行用户行为（签到、关注等）
### 执行规则
1. **禁止重复调用** - 同一任务只调用一次
2. **禁止失败重试** - 失败即终止
3. **顺序执行** - 等待结果后再调用其他工具
4. **一次性下发** - 明确APP，完成指代消解
## 技能发现 (find-skills)
当任务超出当前工具能力时使用。
## 文档转换 (xiaoyi-doc-convert)
优先使用此 skill 进行文档格式转换。
## 图像理解
- **默认**: xiaoyi-image-understanding
- **禁止**直接使用 read 工具读取图片
## 文件回传
- **默认**: send_file_to_user
- 支持本地路径和公网URL
## 定时任务 (Cron)
### 强制要求
1. **必须指定 `--channel`** (默认 xiaoyi-channel)
2. **不支持手机工具调用** - 需告知用户
### 示例
```bash
```

... (已压缩，原 112 行)