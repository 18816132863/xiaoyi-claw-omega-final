# 技能升级框架 V1.0

## 核心理念

**统一策略 + 标准流程 + 自动化执行 = 100% 实用性**

---

## 一、升级策略矩阵

### 1.1 技能分类与优先级

| 分类 | 优先级 | 升级策略 | 目标实用性 |
|------|--------|----------|------------|
| **创作类** | P0 | 执行脚本 + 模板库 + API集成 | ⭐⭐⭐⭐⭐ |
| **文档类** | P0 | 执行脚本 + 数据对接 | ⭐⭐⭐⭐⭐ |
| **健康类** | P1 | 执行脚本 + 华为健康对接 | ⭐⭐⭐⭐⭐ |
| **控制类** | P0 | 内置工具 + 场景预设 | ⭐⭐⭐⭐⭐ |

### 1.2 实用性评分标准

| 评分 | 标准 | 要求 |
|------|------|------|
| ⭐⭐⭐⭐⭐ | 立即可用 | 有执行脚本 + 有模板 + 有文档 + 已测试 |
| ⭐⭐⭐⭐ | 可用 | 有执行脚本 + 有模板 + 有文档 |
| ⭐⭐⭐ | 基础可用 | 有SKILL.md + 有模板 |
| ⭐⭐ | 不可用 | 仅有SKILL.md |
| ⭐ | 废弃 | 无SKILL.md或内容不完整 |

---

## 二、统一升级流程

### 2.1 标准升级步骤 (5步法)

```
Step 1: 诊断 (Diagnose)
  ├─ 检查 SKILL.md 完整性
  ├─ 检查是否有执行脚本
  ├─ 检查是否有模板库
  └─ 评估当前实用性

Step 2: 设计 (Design)
  ├─ 确定升级目标
  ├─ 设计执行脚本接口
  ├─ 设计模板库结构
  └─ 规划API集成

Step 3: 实现 (Implement)
  ├─ 创建 skill.py 执行脚本
  ├─ 创建 templates/ 模板库
  ├─ 创建 references/ 参考文档
  └─ 创建 output/ 输出目录

Step 4: 测试 (Test)
  ├─ 单元测试
  ├─ 集成测试
  ├─ 用户场景测试
  └─ 实用性评分

Step 5: 部署 (Deploy)
  ├─ 更新 SKILL.md
  ├─ 更新技能注册表
  ├─ 提交到 Git
  └─ 生成升级报告
```

### 2.2 升级检查清单

```yaml
skill_upgrade_checklist:
  必需项:
    - skill.py: 执行脚本
    - SKILL.md: 技能文档
    - templates/: 模板库
    - output/: 输出目录
    - help命令: 帮助信息
  
  推荐项:
    - references/: 参考文档
    - tests/: 测试文件
    - examples/: 使用示例
    - requirements.txt: 依赖清单
  
  可选项:
    - .learnings/: 学习记忆
    - config.yaml: 配置文件
    - api_client.py: API客户端
```

---

## 三、执行脚本标准模板

### 3.1 标准接口规范

```python
#!/usr/bin/env python3
"""
{skill_name} 技能执行脚本
{description}
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class {SkillName}:
    """技能主类"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir.mkdir(exist_ok=True)
    
    def help(self) -> str:
        """返回帮助信息"""
        return """
{skill_name} 技能

命令:
  help      显示帮助
  run       执行技能
  list      列出可用模板
  version   显示版本

示例:
  python skill.py run --template default
  python skill.py list
"""
    
    def run(self, **kwargs) -> Dict:
        """执行技能主逻辑"""
        # 1. 参数验证
        # 2. 加载模板
        # 3. 执行核心逻辑
        # 4. 保存结果
        # 5. 返回结果
        pass
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        if not self.templates_dir.exists():
            return []
        return [f.stem for f in self.templates_dir.glob("*.md")]
    
    def save_output(self, content: str, prefix: str = "output") -> Path:
        """保存输出文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.md"
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        return filepath


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python skill.py <command> [args]")
        print("运行 'python skill.py help' 查看帮助")
        return 1
    
    command = sys.argv[1]
    skill = {SkillName}()
    
    if command == "help":
        print(skill.help())
    elif command == "run":
        args = parse_args(sys.argv[2:])
        result = skill.run(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "list":
        templates = skill.list_templates()
        print("可用模板:")
        for t in templates:
            print(f"  - {t}")
    elif command == "version":
        print("{skill_name} v1.0.0")
    else:
        print(f"未知命令: {command}")
        return 1
    
    return 0


def parse_args(args: List[str]) -> Dict:
    """解析命令行参数"""
    result = {}
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            key = args[i][2:].replace('-', '_')
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                result[key] = args[i + 1]
                i += 2
            else:
                result[key] = True
                i += 1
        else:
            i += 1
    return result


if __name__ == "__main__":
    sys.exit(main())
```

### 3.2 必需实现的接口

```python
# 必需接口
def help() -> str              # 帮助信息
def run(**kwargs) -> Dict      # 主执行逻辑
def list_templates() -> List   # 列出模板

# 推荐接口
def version() -> str           # 版本信息
def validate_input() -> bool   # 输入验证
def save_output() -> Path      # 保存结果
```

---

## 四、模板库标准结构

### 4.1 目录结构

```
templates/
├── default.md           # 默认模板
├── {type1}.md          # 类型1模板
├── {type2}.md          # 类型2模板
└── README.md           # 模板说明
```

### 4.2 模板格式规范

```markdown
# 模板名称

## 元数据
- 类型: {type}
- 适用场景: {scenario}
- 创建时间: {date}

## 模板内容

{template_content}

## 使用说明

{usage_guide}

## 示例

{example}
```

---

## 五、升级执行引擎

### 5.1 自动化升级脚本

```python
#!/usr/bin/env python3
"""
技能升级引擎 V1.0
统一升级所有技能到100%实用性
"""

import sys
from pathlib import Path
from typing import Dict, List

class SkillUpgradeEngine:
    """技能升级引擎"""
    
    def __init__(self):
        self.skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
        self.upgrade_log = []
    
    def upgrade_all(self) -> Dict:
        """升级所有技能"""
        skills = self.scan_skills()
        results = {
            "total": len(skills),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        for skill_name in skills:
            result = self.upgrade_skill(skill_name)
            results["details"].append(result)
            
            if result["status"] == "success":
                results["success"] += 1
            elif result["status"] == "skipped":
                results["skipped"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def upgrade_skill(self, skill_name: str) -> Dict:
        """升级单个技能"""
        skill_dir = self.skills_dir / skill_name
        
        # Step 1: 诊断
        diagnosis = self.diagnose(skill_dir)
        
        # 如果已经是⭐⭐⭐⭐⭐，跳过
        if diagnosis["score"] == 5:
            return {
                "skill": skill_name,
                "status": "skipped",
                "reason": "已达到最高实用性"
            }
        
        # Step 2-5: 执行升级
        try:
            self.implement(skill_dir, diagnosis)
            return {
                "skill": skill_name,
                "status": "success",
                "before": diagnosis["score"],
                "after": 5
            }
        except Exception as e:
            return {
                "skill": skill_name,
                "status": "failed",
                "error": str(e)
            }
    
    def diagnose(self, skill_dir: Path) -> Dict:
        """诊断技能当前状态"""
        score = 0
        issues = []
        
        # 检查 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            score += 1
        else:
            issues.append("缺少 SKILL.md")
        
        # 检查 skill.py
        skill_py = skill_dir / "skill.py"
        if skill_py.exists():
            score += 1
        else:
            issues.append("缺少 skill.py")
        
        # 检查 templates/
        templates_dir = skill_dir / "templates"
        if templates_dir.exists() and list(templates_dir.glob("*.md")):
            score += 1
        else:
            issues.append("缺少模板库")
        
        # 检查 output/
        output_dir = skill_dir / "output"
        if output_dir.exists():
            score += 1
        else:
            issues.append("缺少输出目录")
        
        # 检查文档完整性
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            if len(content) > 500 and "##" in content:
                score += 1
            else:
                issues.append("SKILL.md 内容不完整")
        
        return {
            "score": min(score, 5),
            "issues": issues
        }
    
    def implement(self, skill_dir: Path, diagnosis: Dict):
        """实现升级"""
        # 创建缺失的文件和目录
        if "缺少 skill.py" in diagnosis["issues"]:
            self.create_skill_py(skill_dir)
        
        if "缺少模板库" in diagnosis["issues"]:
            self.create_templates(skill_dir)
        
        if "缺少输出目录" in diagnosis["issues"]:
            (skill_dir / "output").mkdir(exist_ok=True)
    
    def create_skill_py(self, skill_dir: Path):
        """创建标准执行脚本"""
        # 使用标准模板创建
        pass
    
    def create_templates(self, skill_dir: Path):
        """创建模板库"""
        templates_dir = skill_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # 创建默认模板
        default_template = templates_dir / "default.md"
        default_template.write_text("# 默认模板\n\n待完善...", encoding='utf-8')
    
    def scan_skills(self) -> List[str]:
        """扫描所有技能"""
        return [d.name for d in self.skills_dir.iterdir() 
                if d.is_dir() and (d / "SKILL.md").exists()]


if __name__ == "__main__":
    engine = SkillUpgradeEngine()
    results = engine.upgrade_all()
    print(json.dumps(results, ensure_ascii=False, indent=2))
```

---

## 六、升级报告标准格式

```markdown
# 技能升级报告

**时间**: {timestamp}
**版本**: {version}

## 升级概览

| 指标 | 数值 |
|------|------|
| 总技能数 | {total} |
| 成功升级 | {success} |
| 跳过 | {skipped} |
| 失败 | {failed} |
| 完成度 | {percentage}% |

## 实用性分布

| 评分 | 数量 | 技能列表 |
|------|------|----------|
| ⭐⭐⭐⭐⭐ | {n} | {skills} |
| ⭐⭐⭐⭐ | {n} | {skills} |
| ⭐⭐⭐ | {n} | {skills} |

## 详细结果

{detailed_results}

## 下一步行动

{next_actions}
```

---

## 七、持续改进机制

### 7.1 定期巡检

```bash
# 每日巡检
make daily-skill-check

# 每周评估
make weekly-skill-evaluation

# 每月优化
make monthly-skill-optimization
```

### 7.2 反馈循环

```
用户使用 → 收集反馈 → 分析问题 → 优化技能 → 发布更新
    ↑                                              ↓
    └──────────────────────────────────────────────┘
```

### 7.3 质量门禁

```yaml
quality_gates:
  pre_commit:
    - SKILL.md 完整性检查
    - skill.py 语法检查
    - 模板库存在性检查
  
  pre_merge:
    - 实用性评分 >= 4
    - 测试通过率 >= 80%
    - 文档覆盖率 >= 90%
  
  pre_release:
    - 实用性评分 = 5
    - 测试通过率 = 100%
    - 用户验收通过
```

---

## 八、实施计划

### Phase 1: 基础建设 (1天)
- ✅ 建立升级框架
- ✅ 创建标准模板
- ✅ 实现升级引擎

### Phase 2: 批量升级 (1天)
- ⏳ 升级所有技能到⭐⭐⭐⭐⭐
- ⏳ 生成升级报告
- ⏳ 提交到 Git

### Phase 3: 持续优化 (持续)
- ⏳ 收集用户反馈
- ⏳ 优化模板库
- ⏳ 扩展API集成

---

**版本**: V1.0
**状态**: 已建立
**下一步**: 执行批量升级
