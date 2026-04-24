# 贡献指南

## 如何贡献

### 1. 报告问题
- 在 GitHub Issues 中提交问题
- 包含复现步骤和错误信息

### 2. 提交代码
1. Fork 仓库
2. 创建分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -m "Add your feature"`
4. 推送分支: `git push origin feature/your-feature`
5. 创建 Pull Request

### 3. 添加技能
1. 在 `skills/` 目录创建技能文件夹
2. 添加 `SKILL.md` 描述文件
3. 添加 `skill.py` 实现文件 (可选)
4. 更新 `skill_registry.json`

## 代码规范

### Python
- 使用 4 空格缩进
- 添加类型注解
- 编写文档字符串

### Markdown
- 使用标准 Markdown 格式
- 添加适当的标题层级
- 包含示例代码

## 测试要求

- 所有新功能需要测试
- 运行门禁检查确保通过
```bash
python scripts/run_release_gate.py premerge
```

## 许可证

MIT License
