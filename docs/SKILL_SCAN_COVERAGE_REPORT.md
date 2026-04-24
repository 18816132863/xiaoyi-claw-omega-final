# 技能扫描覆盖率报告

## 一、扫描结果

| 项目 | 数量 |
|------|------|
| 扫描路径 | skills/ |
| 实际目录数 | 174 |
| 扫描到的技能数 | 174 |
| **扫描覆盖率** | **100.0%** |

---

## 二、分类分布

| 分类 | 数量 | 占比 |
|------|------|------|
| other | 99 | 56.9% |
| ai | 25 | 14.4% |
| document | 13 | 7.5% |
| search | 13 | 7.5% |
| finance | 7 | 4.0% |
| image | 5 | 2.9% |
| video | 5 | 2.9% |
| automation | 4 | 2.3% |
| data | 2 | 1.1% |
| code | 1 | 0.6% |

---

## 三、扫描路径清单

```
skills/
├── wecom-bot-setup/
├── scientific-slides/
├── news-extractor/
├── xiaoyi-ppt/
├── speech-to-text/
├── personas/
├── kids-book-writer/
├── skill-creator/
├── content-workflow/
├── xiaoyi-image-search/
├── ... (共 174 个)
```

---

## 四、270+ 技能纳入方案

### 4.1 当前状态

- 已扫描: 174 个技能
- 目标: 270+ 技能
- 差距: 约 96 个技能

### 4.2 差距来源分析

| 来源 | 说明 | 数量估计 |
|------|------|---------|
| 外部技能 | ClawHub/社区技能 | ~50 |
| 小艺内置技能 | 小艺帮帮忙已学技能 | ~30 |
| 待开发技能 | 规划中但未实现 | ~16 |

### 4.3 纳入方案

#### 方案一：外部技能导入

```python
from skill_asset_registry import SkillRegistry

# 导入外部技能
registry = SkillRegistry()
registry.import_from_clawhub(skill_id="xxx")
registry.import_from_url(url="https://...")
```

#### 方案二：小艺内置技能同步

```python
# 同步小艺帮帮忙已学技能
from device_capability_bus import CapabilityExecutor

executor = CapabilityExecutor()
xiaoyi_skills = executor.get_learned_skills()
registry.batch_register(xiaoyi_skills)
```

#### 方案三：动态技能发现

```python
# 运行时发现新技能
scanner = SkillScanner()
scanner.add_scan_path("/path/to/external/skills")
new_skills = scanner.scan_all()
```

---

## 五、闲置技能激活建议

| 技能 | 最后使用 | 建议 |
|------|---------|------|
| 未使用的技能 | 从未 | 考虑删除或归档 |
| 低频技能 | >30天 | 推荐使用场景 |
| 高频技能 | <7天 | 保持活跃 |

---

## 六、测试覆盖

- `tests/test_skill_scan_coverage.py` - 扫描覆盖率测试
- `tests/test_skill_registry_external_import.py` - 外部导入测试
- `tests/test_idle_skill_activation_suggestions.py` - 闲置激活测试
