# skills/ - 技能平台

## 定位

技能平台是**标准化的技能注册、路由和生命周期管理系统**。

## 职责

1. **注册管理** - 技能注册、发现、索引
2. **运行时** - 技能路由、执行、验证
3. **生命周期** - 实验期、稳定期、废弃期、退役期

## 目录结构

```
skills/
├── registry/            # 注册管理
│   └── skill_registry.py
├── runtime/             # 运行时
│   └── skill_router.py
├── lifecycle/           # 生命周期
│   └── lifecycle_manager.py
├── policies/            # 技能策略
└── README.md
```

## 核心接口

### 技能注册

```python
from skills.registry.skill_registry import SkillRegistry, SkillManifest, SkillCategory

registry = SkillRegistry()

manifest = SkillManifest(
    skill_id="my_skill",
    name="My Skill",
    version="1.0.0",
    description="A useful skill",
    category=SkillCategory.UTILITY,
    executor_type="skill_md",
    entry_point="skills/my_skill/SKILL.md"
)

registry.register(manifest)
```

### 技能路由

```python
from skills.runtime.skill_router import SkillRouter

router = SkillRouter(registry=registry)
result = router.route("my_skill", {"input": "data"})

if result.success:
    print(result.output)
else:
    print(result.error)
```

### 技能发现

```python
# 搜索技能
matches = registry.search(query="image", category=SkillCategory.IMAGE)

# 按标签查找
tagged = registry.get_by_tag("vision")

# 解析依赖
deps = registry.resolve_dependencies("my_skill")
```

### 生命周期管理

```python
from skills.lifecycle.lifecycle_manager import LifecycleManager

lifecycle = LifecycleManager(registry=registry)

# 推广技能
lifecycle.promote("my_skill", reason="Stable and well-tested")

# 废弃技能
lifecycle.deprecate("old_skill", reason="Replaced by new_skill", deprecation_period_days=90)

# 获取即将过期的技能
expiring = lifecycle.get_expiring_skills(days=30)
```

## 技能清单格式

每个技能需要提供清单：

```json
{
  "skill_id": "my_skill",
  "name": "My Skill",
  "version": "1.0.0",
  "description": "Description",
  "category": "utility",
  "executor_type": "skill_md",
  "entry_point": "skills/my_skill/SKILL.md",
  "timeout_seconds": 60,
  "dependencies": [],
  "input_contract": {},
  "output_contract": {}
}
```

## 纵向能力带

技能平台带贯穿：
- skills (本层)
- orchestration (工作流调用)
- governance (权限控制)

## 扩展方式

1. 新增执行器类型 → 在 `runtime/` 添加 executor
2. 新增生命周期策略 → 在 `lifecycle/` 添加 policy
