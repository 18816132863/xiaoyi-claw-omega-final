#!/usr/bin/env python3
"""
批量技能实用性提升脚本
提升13个核心技能的实用性
"""

import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILLS_DIR = WORKSPACE / "skills"
REPORTS_DIR = WORKSPACE / "reports" / "skill_upgrades"

# 13个核心技能配置
SKILLS_TO_UPGRADE = {
    # 创作类 (5个)
    "novel-generator": {
        "category": "创作类",
        "priority": "P0",
        "enhancements": [
            "添加中文场景模板",
            "创建 skill.py 执行脚本",
            "集成长期记忆",
            "添加爽点节奏分析",
            "支持多题材模板"
        ]
    },
    "claw-art": {
        "category": "创作类",
        "priority": "P0",
        "enhancements": [
            "添加中文提示词支持",
            "创建 skill.py 执行脚本",
            "添加风格预设",
            "支持批量生成",
            "集成主流绘图API"
        ]
    },
    "minimax-music-gen": {
        "category": "创作类",
        "priority": "P1",
        "enhancements": [
            "添加更多风格模板",
            "支持歌词续写",
            "添加音乐风格混搭",
            "支持纯音乐BGM",
            "添加历史记录管理"
        ]
    },
    "copywriter": {
        "category": "创作类",
        "priority": "P0",
        "enhancements": [
            "添加中文文案模板",
            "支持短视频脚本",
            "添加营销文案生成",
            "支持多平台适配",
            "添加A/B测试变体"
        ]
    },
    "educational-video-creator": {
        "category": "创作类",
        "priority": "P1",
        "enhancements": [
            "添加视频脚本生成",
            "支持多风格视频",
            "添加字幕生成",
            "支持批量生成",
            "添加模板库"
        ]
    },
    
    # 文档类 (3个)
    "markitdown": {
        "category": "文档类",
        "priority": "P0",
        "enhancements": [
            "支持PDF/Word/Excel互转",
            "添加批量转换",
            "支持格式保留",
            "添加OCR支持",
            "支持云端文档"
        ]
    },
    "doc-autofill": {
        "category": "文档类",
        "priority": "P0",
        "enhancements": [
            "添加更多模板",
            "支持华为健康数据",
            "添加表格智能识别",
            "支持批量生成",
            "添加历史记录"
        ]
    },
    "data-tracker": {
        "category": "文档类",
        "priority": "P0",
        "enhancements": [
            "添加更多数据类型",
            "支持华为健康同步",
            "添加趋势图表",
            "支持习惯追踪",
            "添加周报/月报"
        ]
    },
    
    # 健康类 (3个)
    "xiaoyi-health": {
        "category": "健康类",
        "priority": "P1",
        "enhancements": [
            "添加症状分析",
            "支持健康风险评估",
            "添加中医体质辨识",
            "支持用药提醒",
            "添加算命娱乐功能"
        ]
    },
    "fitness-coach": {
        "category": "健康类",
        "priority": "P1",
        "enhancements": [
            "添加食谱生成",
            "支持营养计算",
            "添加购物清单",
            "支持饮食记录",
            "添加体重管理"
        ]
    },
    
    # 控制类 (2个)
    "xiaoyi_gui_agent": {
        "category": "控制类",
        "priority": "P0",
        "enhancements": [
            "添加常用APP预设",
            "支持复杂操作流程",
            "添加操作录制",
            "支持定时执行",
            "添加异常处理"
        ]
    },
    "xiaoyi-HarmonyOSSmartHome-skill": {
        "category": "控制类",
        "priority": "P1",
        "enhancements": [
            "添加场景联动",
            "支持语音控制",
            "添加自动化规则",
            "支持设备监控",
            "添加能耗统计"
        ]
    }
}


def create_skill_enhancement(skill_name: str, config: dict) -> dict:
    """为技能创建增强内容"""
    skill_dir = SKILLS_DIR / skill_name
    
    if not skill_dir.exists():
        return {
            "skill": skill_name,
            "status": "not_found",
            "message": f"技能目录不存在: {skill_dir}"
        }
    
    # 读取现有 SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {
            "skill": skill_name,
            "status": "no_skill_md",
            "message": "SKILL.md 不存在"
        }
    
    # 创建增强目录
    enhancements_dir = skill_dir / "enhancements"
    enhancements_dir.mkdir(exist_ok=True)
    
    # 创建实用性提升文件
    enhancement_file = enhancements_dir / "practical_upgrade.md"
    
    enhancement_content = f"""# 实用性提升方案

**技能**: {skill_name}
**分类**: {config['category']}
**优先级**: {config['priority']}
**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 提升目标

让技能从"能用"变成"好用、想用、爱用"。

---

## 增强项

"""
    for i, enhancement in enumerate(config['enhancements'], 1):
        enhancement_content += f"{i}. {enhancement}\n"
    
    enhancement_content += """

---

## 实施步骤

### 第一步：检查现有功能

```bash
# 检查技能目录结构
ls -la {skill_dir}

# 检查是否有执行脚本
ls -la {skill_dir}/*.py 2>/dev/null || echo "无执行脚本"

# 检查是否有模板
ls -la {skill_dir}/templates/ 2>/dev/null || echo "无模板目录"
```

### 第二步：创建执行脚本

如果缺少 `skill.py`，创建一个：

```python
#!/usr/bin/env python3
\"\"\"
{skill_name} 执行脚本
\"\"\"

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
        print(f"未知命令: {{command}}")
        return 1
    
    return 0

def print_help():
    print(\"\"\"{skill_name} 技能

命令:
  help    显示帮助
  run     执行技能
\"\"\")

def run_skill(args):
    # TODO: 实现具体逻辑
    print("执行技能...")
    result = {{"status": "success", "message": "技能执行完成"}}
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
python {skill_dir}/skill.py help

# 测试模板
python {skill_dir}/skill.py run --template default
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
""".format(skill_dir=skill_dir, skill_name=skill_name)
    
    enhancement_file.write_text(enhancement_content, encoding='utf-8')
    
    return {
        "skill": skill_name,
        "status": "success",
        "category": config['category'],
        "priority": config['priority'],
        "enhancements": config['enhancements'],
        "file": str(enhancement_file)
    }


def main():
    """主函数"""
    print("=" * 60)
    print("批量技能实用性提升")
    print("=" * 60)
    
    # 创建报告目录
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total": len(SKILLS_TO_UPGRADE),
        "success": 0,
        "failed": 0,
        "skills": []
    }
    
    for skill_name, config in SKILLS_TO_UPGRADE.items():
        print(f"\n处理: {skill_name} ({config['category']})")
        result = create_skill_enhancement(skill_name, config)
        results["skills"].append(result)
        
        if result["status"] == "success":
            results["success"] += 1
            print(f"  ✅ 已创建提升方案")
        else:
            results["failed"] += 1
            print(f"  ❌ {result['message']}")
    
    # 保存报告
    report_file = REPORTS_DIR / f"upgrade_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print("\n" + "=" * 60)
    print(f"完成: {results['success']}/{results['total']} 成功")
    print(f"报告: {report_file}")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()
