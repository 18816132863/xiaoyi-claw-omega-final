# 实用性提升方案

**技能**: xiaoyi-health
**分类**: 健康类
**优先级**: P1
**创建时间**: 2026-04-18 07:47:03

---

## 提升目标

让技能从"能用"变成"好用、想用、爱用"。

---

## 增强项

1. 添加症状分析
2. 支持健康风险评估
3. 添加中医体质辨识
4. 支持用药提醒
5. 添加算命娱乐功能


---

## 实施步骤

### 第一步：检查现有功能

```bash
# 检查技能目录结构
ls -la /home/sandbox/.openclaw/workspace/skills/xiaoyi-health

# 检查是否有执行脚本
ls -la /home/sandbox/.openclaw/workspace/skills/xiaoyi-health/*.py 2>/dev/null || echo "无执行脚本"

# 检查是否有模板
ls -la /home/sandbox/.openclaw/workspace/skills/xiaoyi-health/templates/ 2>/dev/null || echo "无模板目录"
```

### 第二步：创建执行脚本

如果缺少 `skill.py`，创建一个：

```python
#!/usr/bin/env python3
"""
xiaoyi-health 执行脚本
"""

import sys
import json
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("用法: python skill.py <command> [args]")
        return 1
    
    command = sys.argv[1]
    
    if command == "help":
        print_help()
    elif command == "run":
        run_skill(sys.argv[2:] if len(sys.argv) > 2 else [])
    else:
        print(f"未知命令: {command}")
        return 1
    
    return 0

def print_help():
    print("""xiaoyi-health 技能

命令:
  help    显示帮助
  run     执行技能
""")

def run_skill(args):
    # TODO: 实现具体逻辑
    print("执行技能...")
    result = {"status": "success", "message": "技能执行完成"}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    sys.exit(main())
```

### 第三步：添加中文模板

创建 `templates/` 目录，添加常用模板。

### 第四步：集成长期记忆

在 `skill.py` 中添加记忆读写功能。

### 第五步：测试验证

```bash
# 测试执行脚本
python /home/sandbox/.openclaw/workspace/skills/xiaoyi-health/skill.py help

# 测试模板
python /home/sandbox/.openclaw/workspace/skills/xiaoyi-health/skill.py run --template default
```

---

## 预期效果

- ✅ 一句话调用
- ✅ 中文友好
- ✅ 自动记忆
- ✅ 批量处理
- ✅ 错误恢复

---

## 下一步

1. 实施上述步骤
2. 添加单元测试
3. 编写使用文档
4. 收集用户反馈
5. 持续优化
