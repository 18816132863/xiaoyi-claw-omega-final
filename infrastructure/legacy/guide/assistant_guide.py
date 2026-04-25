#!/usr/bin/env python3
"""
小艺 Claw 终极星空鸽子王 - 完整引导模块
V2.8.1 - 2026-04-11
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

from infrastructure.path_resolver import get_project_root

class GuideSection(Enum):
    WELCOME = "welcome"
    CAPABILITIES = "capabilities"
    SKILLS = "skills"
    WORKFLOWS = "workflows"
    COMMANDS = "commands"
    ARCHITECTURE = "architecture"
    NEW_FEATURES = "new_features"
    ALL_FEATURES = "all_features"
    ALL_SKILLS = "all_skills"
    ALL_MODULES = "all_modules"
    USAGE_GUIDE = "usage_guide"

@dataclass
class SkillInfo:
    name: str
    display_name: str
    category: str
    description: str
    usage: str
    example: str

class CompleteGuide:
    """完整引导模块"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.skills: Dict[str, SkillInfo] = {}
        self.workflows: Dict[str, Dict] = {}
        self.commands: List[Dict] = []
        self._init_all()
    
    def _init_all(self):
        self._init_skills()
        self._init_workflows()
        self._init_commands()
    
    def _init_skills(self):
        self.skills["docx"] = SkillInfo("docx", "Word文档", "文档处理", "生成Word文档", "说'生成Word'", "生成销售报告")
        self.skills["pdf"] = SkillInfo("pdf", "PDF文档", "文档处理", "生成PDF文档", "说'生成PDF'", "转换为PDF")
        self.skills["pptx"] = SkillInfo("pptx", "PPT演示", "文档处理", "生成PPT", "说'制作PPT'", "制作产品介绍PPT")
        self.skills["data-analysis"] = SkillInfo("data-analysis", "数据分析", "数据分析", "数据分析", "说'分析数据'", "分析销售数据")
        self.skills["excel-analysis"] = SkillInfo("excel-analysis", "Excel分析", "数据分析", "Excel处理", "说'分析Excel'", "分析Excel文件")
        self.skills["sqlite"] = SkillInfo("sqlite", "SQLite", "数据分析", "数据库操作", "说'查询数据库'", "查询用户数据")
        self.skills["xiaoyi-web-search"] = SkillInfo("xiaoyi-web-search", "网页搜索", "网络服务", "搜索互联网", "说'搜索xxx'", "搜索电商趋势")
        self.skills["web-browsing"] = SkillInfo("web-browsing", "浏览器", "网络服务", "自动化浏览", "说'打开网页'", "打开淘宝搜索")
        self.skills["image-cog"] = SkillInfo("image-cog", "图片理解", "图片处理", "识别图片", "说'识别图片'", "识别图片文字")
        self.skills["seedream-image-gen"] = SkillInfo("seedream-image-gen", "图片生成", "图片处理", "AI生成图片", "说'生成图片'", "生成宣传图")
        self.skills["cron"] = SkillInfo("cron", "定时任务", "自动化", "定时执行", "说'每天提醒'", "每天9点提醒")
        self.skills["xiaoyi-gui-agent"] = SkillInfo("xiaoyi-gui-agent", "手机自动化", "自动化", "操作手机", "说'在手机上'", "在淘宝搜索")
        self.skills["git"] = SkillInfo("git", "Git", "代码开发", "版本控制", "说'git提交'", "提交代码")
        self.skills["code-analysis"] = SkillInfo("code-analysis", "代码分析", "代码开发", "代码审计", "说'审计代码'", "审计项目代码")
        self.skills["market-research"] = SkillInfo("market-research", "市场研究", "商业分析", "市场调研", "说'市场分析'", "分析咖啡市场")
        self.skills["stock-price-query"] = SkillInfo("stock-price-query", "股票查询", "商业分析", "股价查询", "说'查股价'", "查询茅台股价")
        self.skills["article-writer"] = SkillInfo("article-writer", "文章写作", "内容创作", "生成文章", "说'写文章'", "写AI发展文章")
        self.skills["copywriter"] = SkillInfo("copywriter", "文案创作", "内容创作", "营销文案", "说'写文案'", "写产品文案")
        self.skills["weather"] = SkillInfo("weather", "天气查询", "工具", "查天气", "说'天气'", "今天天气")
        self.skills["spotify-player"] = SkillInfo("spotify-player", "音乐播放", "工具", "控制音乐", "说'播放音乐'", "播放周杰伦")
        self.skills["memory"] = SkillInfo("memory", "记忆管理", "核心功能", "保存信息", "说'记住xxx'", "记住店铺名")
    
    def _init_workflows(self):
        self.workflows = {
            "电商选品分析": {"description": "分析产品趋势，生成选品建议", "example": "分析淘宝蓝牙耳机选品趋势"},
            "工厂筛选比价": {"description": "筛选供应商，对比价格质量", "example": "找手机壳工厂对比价格"},
            "主播/团长筛选": {"description": "筛选合作主播团长", "example": "找美妆主播"},
            "店铺启动": {"description": "新店铺启动指导", "example": "开淘宝店规划"},
            "代码审计": {"description": "检查代码质量", "example": "审计项目代码"},
            "市场分析报告": {"description": "深度市场调研", "example": "分析咖啡市场"}
        }
    
    def _init_commands(self):
        self.commands = [
            {"category": "基础", "command": "帮助", "description": "查看能力"},
            {"category": "基础", "command": "架构", "description": "架构功能"},
            {"category": "基础", "command": "新增功能", "description": "新功能介绍"},
            {"category": "基础", "command": "全部功能", "description": "功能大全"},
            {"category": "基础", "command": "所有技能", "description": "技能列表"},
            {"category": "基础", "command": "所有模块", "description": "模块列表"},
            {"category": "基础", "command": "使用引导", "description": "使用教程"},
            {"category": "搜索", "command": "搜索 xxx", "description": "网页搜索"},
            {"category": "文档", "command": "生成报告", "description": "创建文档"},
            {"category": "数据", "command": "分析数据", "description": "数据分析"},
            {"category": "自动化", "command": "每天提醒我", "description": "定时任务"},
            {"category": "记忆", "command": "记住 xxx", "description": "保存信息"},
        ]
    
    def get_quick_reference(self) -> str:
        return """## 📋 快速参考

### 常用命令
| 命令 | 说明 |
|------|------|
| `帮助` | 查看能力 |
| `架构` | 架构功能 |
| `新增功能` | 新功能介绍 |
| `全部功能` | 功能大全 |
| `所有技能` | 技能列表(175个) |
| `所有模块` | 模块列表(50+) |
| `使用引导` | 使用教程 |
| `搜索 xxx` | 网页搜索 |
| `生成报告` | 创建文档 |

### 工作流
| 工作流 | 用途 |
|--------|------|
| 电商选品分析 | 产品趋势 |
| 工厂筛选比价 | 供应商对比 |
| 市场分析报告 | 市场调研 |

---

💡 **提示**: 直接用自然语言描述需求！"""
    
    def get_architecture_guide(self) -> str:
        return """## 🏗️ 架构完整功能

### 核心六层 (L1-L6)
| 层级 | 名称 | 核心功能 |
|------|------|----------|
| L1 | 核心认知层 | 架构真源、动态提示词、引导模块 |
| L2 | 记忆上下文层 | 记忆管理、上下文治理、质量评估 |
| L3 | 任务编排层 | 工作流引擎、任务调度、目标追踪 |
| L4 | 能力执行层 | 技能网关、健康检查、能力报告 |
| L5 | 稳定治理层 | 守门器、架构检查、路由表 |
| L6 | 基础设施层 | 路径解析、插件标准、服务包 |

### 已归档 (已归档)
| 层级 | 名称 | 核心功能 |
|------|------|----------|
| E7 | 战略目标层 | goal_engine.py - 四级目标管理 |
| E6 | 自治治理层 | bounded_governor.py - 受控自治 |
| E5 | 组织协同层 | org_orchestrator.py - 跨团队协作 |
| E4 | 资源组合层 | resource_scheduler.py - 资源调度 |
| E3 | 决策模拟层 | decision_lab.py - 决策预演 |
| E2 | 可靠性层 | resilience_center.py - 可靠性保障 |
| E1 | 合规信任层 | trust_center.py - 合规管理 |
| E0 | 开放接入层 | integration_contract.py - 外部接入 |

### 已归档 (已归档)
| 层级 | 名称 | 核心功能 |
|------|------|----------|
| X7 | 生态伙伴层 | partner_manager.py - 伙伴管理 |
| X6 | 标准资产层 | asset_registry.py - 资产注册 |
| X5 | 产品封装层 | surface_manager.py - 产品封装 |
| X4 | 多租户层 | workspace_manager.py - 租户管理 |
| X3 | 多端交付层 | multi_surface_hub.py - 四端统一 |
| X2 | 成本核算层 | cost_center.py - 成本核算 |
| X1 | 商业封装层 | packaging_manager.py - 商业封装 |
| X0 | 版本发布层 | release_manager.py - 版本管理 |

### 已归档 (已归档)
| 层级 | 名称 | 核心功能 |
|------|------|----------|
| Y3 | 运维监控层 | dashboard.py - 监控面板 |
| Y2 | 扩展协议层 | contract_manager.py - 扩展协议 |
| Y1 | 模板复制层 | replication_engine.py - 模板复制 |

### 架构统计
- **总层级**: 六层 (L1-L6)
- **技能**: 175个
- **工作流**: 8个
- **服务包**: 7个
- **安全机制**: 5层防护

### 架构版本
**V2.8.1** - 完整架构已融合！"""
    
    def get_new_features_guide(self) -> str:
        return """## 🆕 新增功能展示

### V2.8.1 新增功能

#### 🎯 引导模块（核心新增）
- 每次对话自动加载
- 智能意图识别
- 上下文相关引导
- 21个技能介绍
- 6个工作流

#### 🏗️ 架构升级
- 六层架构体系 L1-L6
- 十阶段升级
- 50+新增模块
- 5层安全防护

#### 🛡️ 安全加固
- 路径白名单
- 内容脱敏
- 沙箱执行
- 权限声明
- 预注册机制

#### 📊 数据化能力
- 指标中心
- 反馈学习
- 工作流优选器

#### 🏢 企业级功能
- 可靠性中心
- 合规信任中心
- 开放接入契约

#### 🎯 战略级功能
- 战略目标引擎
- 受控自治治理器
- 决策模拟实验室

---

💡 **提示**: 所有新增功能已自动启用！"""
    
    def get_all_features_guide(self) -> str:
        return """## 📚 全部功能引导

### 🎯 核心功能
| 功能 | 使用方式 |
|------|----------|
| 智能对话 | 直接说话 |
| 记忆管理 | 说'记住xxx' |
| 引导模块 | 说'帮助' |
| 架构系统 | 说'架构' |

### 🔍 搜索功能
| 功能 | 使用方式 |
|------|----------|
| 网页搜索 | 说'搜索xxx' |
| 市场研究 | 说'市场分析xxx' |

### 📝 文档功能
| 功能 | 使用方式 |
|------|----------|
| Word文档 | 说'生成Word报告' |
| PDF文档 | 说'生成PDF' |
| PPT演示 | 说'制作PPT' |

### 📊 数据功能
| 功能 | 使用方式 |
|------|----------|
| 数据分析 | 说'分析数据' |
| Excel处理 | 说'分析Excel' |
| 数据库 | 说'查询数据库' |

### 🖼️ 图片功能
| 功能 | 使用方式 |
|------|----------|
| 图片识别 | 发送图片后说'识别' |
| 图片生成 | 说'生成图片xxx' |

### ⏰ 自动化功能
| 功能 | 使用方式 |
|------|----------|
| 定时任务 | 说'每天xxx提醒我' |
| 手机自动化 | 说'在手机上xxx' |

### 🔄 工作流功能
| 工作流 | 使用方式 |
|--------|----------|
| 电商选品分析 | 说'电商选品分析' |
| 工厂筛选比价 | 说'工厂筛选' |
| 市场分析报告 | 说'市场分析报告' |

### 🤝 协作功能
| 功能 | 使用方式 |
|------|----------|
| 任务分配 | 说'分配任务给xxx' |
| 审批流程 | 说'发起审批' |

### 📈 决策功能
| 功能 | 使用方式 |
|------|----------|
| 方案对比 | 说'对比方案A和B' |
| 风险评估 | 说'预估风险' |

### 🛠️ 开发功能
| 功能 | 使用方式 |
|------|----------|
| Git操作 | 说'git提交' |
| 代码分析 | 说'审计代码' |

### 📦 服务包功能
| 服务包 | 功能范围 |
|--------|----------|
| 基础包 | 基础技能、文档生成 |
| 标准包 | 数据分析、自动化 |
| 专业包 | 市场研究、代码审计 |
| 企业包 | 多租户、权限管理 |
| 旗舰包 | 全功能、专属支持 |

---

💡 **提示**: 所有功能都支持自然语言！"""
    
    def get_all_skills_guide(self) -> str:
        return """## 🛠️ 所有技能完整介绍 (175个技能)

### 📝 文档处理技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| docx | Word文档生成 | 说'生成Word报告' |
| pdf | PDF文档处理 | 说'生成PDF' |
| pptx | PPT演示文稿 | 说'制作PPT' |
| markitdown | Markdown转换 | 说'转换为MD' |

### 📊 数据分析技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| data-analysis | 数据分析 | 说'分析数据' |
| excel-analysis | Excel分析 | 说'分析Excel' |
| sqlite | SQLite数据库 | 说'查询数据库' |
| mysql | MySQL数据库 | 说'连接MySQL' |
| mongodb | MongoDB数据库 | 说'查询MongoDB' |

### 🔍 搜索网络技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| xiaoyi-web-search | 网页搜索 | 说'搜索xxx' |
| web-browsing | 浏览器自动化 | 说'打开网页' |
| web-scraping | 网页抓取 | 说'抓取网页' |

### 🖼️ 图片处理技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| image-cog | 图片理解 | 发送图片后说'识别' |
| xiaoyi-image-understanding | 图片识别 | 发送图片后说'分析' |
| seedream-image-gen | 图片生成 | 说'生成图片' |

### ⏰ 自动化技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| cron | 定时任务 | 说'每天提醒我' |
| xiaoyi-gui-agent | 手机自动化 | 说'在手机上xxx' |
| playwright | 浏览器自动化 | 说'自动浏览' |

### 🛠️ 开发工具技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| git | Git版本控制 | 说'git提交' |
| code-analysis | 代码分析 | 说'审计代码' |
| docker | Docker容器 | 说'Docker操作' |

### 📈 商业分析技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| market-research | 市场研究 | 说'市场分析' |
| stock-price-query | 股票查询 | 说'查股价' |

### ✍️ 内容创作技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| article-writer | 文章写作 | 说'写文章' |
| copywriter | 文案创作 | 说'写文案' |
| poetry | 诗歌创作 | 说'写诗' |

### 🎵 多媒体技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| audio-cog | 音频处理 | 说'处理音频' |
| video-cog | 视频处理 | 说'处理视频' |
| spotify-player | 音乐播放 | 说'播放音乐' |

### 📱 社交平台技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| xiaohongshu-all-in-one | 小红书 | 说'小红书xxx' |
| bilibili-all-in-one | B站 | 说'B站xxx' |
| linkedin-api | LinkedIn | 说'LinkedInxxx' |

### 📁 文件管理技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| file-manager | 文件管理 | 说'管理文件' |
| baidu-netdisk-skills | 百度网盘 | 说'百度网盘xxx' |

### 🌤️ 实用工具技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| weather | 天气查询 | 说'今天天气' |
| google-maps | 谷歌地图 | 说'地图xxx' |

### 🔧 系统工具技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| find-skills | 技能发现 | 说'查找技能' |
| skill-creator | 技能创建 | 说'创建技能' |

### 🎯 专业领域技能
| 技能 | 说明 | 使用方式 |
|------|------|----------|
| senior-architect | 架构师助手 | 说'架构设计' |
| senior-security | 安全专家 | 说'安全分析' |
| ceo-advisor | CEO顾问 | 说'战略建议' |

---

💡 **提示**: 共175个技能，直接说出需求自动匹配！"""
    
    def get_all_modules_guide(self) -> str:
        return """## 🏗️ 所有模块完整介绍 (70+模块)

### L1: 核心认知层 (core/)
| 模块 | 说明 |
|------|------|
| ARCHITECTURE.md | 架构唯一真源 |
| dynamic_prompt.py | 动态提示词（安全加固） |
| llm.py | LLM调用封装 |
| query/ | 查询理解模块 |
| layer_bridge/ | 层级桥接器 |

### L2: 记忆上下文层 (memory_context/)
| 模块 | 说明 |
|------|------|
| memory_manager.py | 记忆管理器 |
| context_governor.py | 上下文治理 |
| memory_quality.py | 记忆质量评估 |
| conflict_detector.py | 冲突检测器 |

### L3: 任务编排层 (orchestration/)
| 模块 | 说明 |
|------|------|
| workflow_engine.py | 工作流引擎 |
| task_scheduler.py | 任务调度器 |
| goal_tracker.py | 目标追踪器 |
| task_reviewer.py | 任务复盘器 |

### L4: 能力执行层 (execution/)
| 模块 | 说明 |
|------|------|
| skill_gateway.py | 技能接入网关 |
| health_checker.py | 健康检查器 |
| capability_reporter.py | 能力报告器 |
| result_validator.py | 结果验证器 |

### L5: 稳定治理层 (governance/)
| 模块 | 说明 |
|------|------|
| gatekeeper.py | 守门器 |
| architecture_check.py | 架构完整性检查 |
| skill_router.py | 技能路由表 |
| security_boundary.py | 安全边界控制 |

### L6: 基础设施层 (infrastructure/)
| 模块 | 说明 |
|------|------|
| path_resolver.py | 路径解析器 |
| plugin_standard.py | 插件标准（安全加固） |
| service_packages/ | 服务包目录 |
| inventory/ | 资产清单 |

### 战略层 (strategy/)
| 模块 | 说明 |
|------|------|
| goal_engine.py | 战略目标引擎 |
| kpi_tracker.py | KPI追踪器 |

### 自治层 (autonomy/)
| 模块 | 说明 |
|------|------|
| bounded_governor.py | 受控自治治理器 |
| risk_assessor.py | 风险评估器 |

### 协作层 (collaboration/)
| 模块 | 说明 |
|------|------|
| org_orchestrator.py | 组织协同编排 |
| approval_flow.py | 审批流程 |

### 资源层 (portfolio/)
| 模块 | 说明 |
|------|------|
| resource_scheduler.py | 资源组合调度 |
| cost_center.py | 成本核算中心 |

### 模拟层 (simulation/)
| 模块 | 说明 |
|------|------|
| decision_lab.py | 决策模拟实验室 |
| scenario_runner.py | 场景运行器 |

### 可靠性层 (reliability/)
| 模块 | 说明 |
|------|------|
| resilience_center.py | 可靠性中心 |
| incident_handler.py | 事件处理器 |

### 合规层 (compliance/)
| 模块 | 说明 |
|------|------|
| trust_center.py | 合规信任中心 |
| audit_logger.py | 审计日志 |

### 开放层 (openapi/)
| 模块 | 说明 |
|------|------|
| integration_contract.py | 开放接入契约 |
| api_versioning.py | API版本管理 |

### 生态层 (ecosystem/)
| 模块 | 说明 |
|------|------|
| partner_manager.py | 伙伴生态管理 |
| marketplace.py | 技能市场 |

### 标准层 (standards/)
| 模块 | 说明 |
|------|------|
| asset_registry.py | 标准资产注册 |
| template_library.py | 模板库 |

### 战略层 (strategy/)
| 模块 | 说明 |
|------|------|
| goal_engine.py | 战略目标引擎 |

### 自治层 (autonomy/)
| 模块 | 说明 |
|------|------|
| bounded_governor.py | 受控自治治理器 |

### 协作层 (collaboration/)
| 模块 | 说明 |
|------|------|
| org_orchestrator.py | 组织协同编排 |

### 资源层 (portfolio/)
| 模块 | 说明 |
|------|------|
| resource_scheduler.py | 资源组合调度 |

### 模拟层 (simulation/)
| 模块 | 说明 |
|------|------|
| decision_lab.py | 决策模拟实验室 |

### 可靠性层 (reliability/)
| 模块 | 说明 |
|------|------|
| resilience_center.py | 可靠性中心 |

### 合规层 (compliance/)
| 模块 | 说明 |
|------|------|
| trust_center.py | 合规信任中心 |

### 开放层 (openapi/)
| 模块 | 说明 |
|------|------|
| integration_contract.py | 开放接入契约 |

### 生态层 (ecosystem/)
| 模块 | 说明 |
|------|------|
| partner_manager.py | 伙伴生态管理 |

### 产品层 (product/)
| 模块 | 说明 |
|------|------|
| surface_manager.py | 产品封装管理 |

### 租户层 (tenant/)
| 模块 | 说明 |
|------|------|
| workspace_manager.py | 多租户工作空间 |

### 交付层 (delivery/)
| 模块 | 说明 |
|------|------|
| multi_surface_hub.py | 多端交付中心 |

### 成本层 (billing/)
| 模块 | 说明 |
|------|------|
| cost_center.py | 成本核算中心 |

### 已归档 (business/)
| 模块 | 说明 |
|------|------|
| packaging_manager.py | 商业封装管理 |

### 发布层 (release/)
| 模块 | 说明 |
|------|------|
| release_manager.py | 版本发布管理 |

### 已归档 (ops/)
| 模块 | 说明 |
|------|------|
| dashboard.py | 运维监控面板 |

### 已归档 (extension/)
| 模块 | 说明 |
|------|------|
| contract_manager.py | 扩展协议管理 |

### 模板层 (templates/)
| 模块 | 说明 |
|------|------|
| replication_engine.py | 模板复制引擎 |

### 引导层 (guide/)
| 模块 | 说明 |
|------|------|
| assistant_guide.py | 完整引导模块 |
| bootstrap.py | 启动脚本 |
| guide_config.json | 配置文件 |

---

💡 **提示**: 70+模块协同工作，自动完成复杂任务！"""
    
    def get_usage_guide(self) -> str:
        return """## 📖 完整使用引导

### 🚀 快速开始

#### 第一步：了解能力
```
说: "帮助" → 查看能力列表
说: "全部功能" → 查看功能大全
说: "所有技能" → 查看技能列表(175个)
说: "所有模块" → 查看模块列表(50+)
```

#### 第二步：尝试基础功能
```
说: "搜索电商趋势" → 网页搜索
说: "生成一份报告" → 文档生成
说: "分析这份数据" → 数据分析
说: "每天9点提醒我" → 定时任务
```

#### 第三步：使用工作流
```
说: "电商选品分析" → 完整选品分析流程
说: "工厂筛选比价" → 供应商对比流程
说: "市场分析报告" → 市场调研流程
```

### 🎯 按场景使用

#### 电商运营场景
```
1. 说: "电商选品分析" → 分析产品趋势
2. 说: "搜索竞品xxx" → 竞品分析
3. 说: "生成选品报告" → 输出报告
```

#### 数据分析场景
```
1. 说: "分析这份数据" → 数据分析
2. 说: "做个趋势图表" → 可视化
3. 说: "生成分析报告" → 输出报告
```

#### 内容创作场景
```
1. 说: "写一篇关于xxx的文章" → 文章生成
2. 说: "为这个产品写文案" → 文案创作
3. 说: "生成PPT介绍" → 演示文稿
```

#### 自动化办公场景
```
1. 说: "每天早上9点提醒我" → 定时提醒
2. 说: "每周一发送周报" → 周期任务
3. 说: "自动监控xxx" → 自动监控
```

### 🔧 高级使用

#### 技能组合
```
说: "搜索电商趋势并生成报告"
→ 自动调用: xiaoyi-web-search + docx

说: "分析数据并制作PPT"
→ 自动调用: data-analysis + pptx
```

#### 记忆功能
```
说: "记住我的店铺名称是xxx" → 保存信息
说: "我之前说过什么" → 回忆信息
```

#### 决策支持
```
说: "对比方案A和方案B" → 方案对比
说: "预估这个决策的风险" → 风险评估
```

### 📱 手机操作
```
说: "在淘宝上搜索蓝牙耳机" → 自动操作淘宝
说: "在小红书发布笔记" → 自动发布
```

### 🖼️ 图片处理
```
发送图片后说: "识别图片内容" → 图片理解
说: "生成一张咖啡店宣传图" → AI生成图片
```

### 📊 数据处理
```
发送Excel后说: "分析这个Excel" → 数据分析
说: "查询用户表数据" → SQL查询
```

### 🆘 获取帮助
```
说: "帮助" → 快速参考
说: "新手引导" → 完整教程
说: "xxx功能怎么用" → 功能说明
```

---

## 💡 使用技巧

1. **自然语言**: 直接说出需求，无需记忆命令
2. **多步骤任务**: 我会自动拆解复杂任务
3. **记忆功能**: 重要信息说"记住xxx"
4. **工作流**: 预设工作流快速完成复杂任务
5. **技能组合**: 多个技能可以组合使用

---

💡 **提示**: 遇到任何问题，说"帮助"获取引导！"""
    
    def detect_intent(self, user_input: str) -> Dict[str, Any]:
        user_input_lower = user_input.lower()
        intents = {
            "help": any(w in user_input_lower for w in ["帮助", "help", "怎么用"]),
            "search": any(w in user_input_lower for w in ["搜索", "查找", "查一下"]),
            "document": any(w in user_input_lower for w in ["文档", "报告", "生成"]),
            "data": any(w in user_input_lower for w in ["数据", "分析", "统计"]),
            "automation": any(w in user_input_lower for w in ["定时", "自动", "提醒"]),
            "memory": any(w in user_input_lower for w in ["记住", "记忆", "保存"]),
            "workflow": any(w in user_input_lower for w in ["工作流", "流程"]),
            "skill": any(w in user_input_lower for w in ["技能", "工具"]) and "所有技能" not in user_input_lower and "全部技能" not in user_input_lower,
            "commands": any(w in user_input_lower for w in ["命令", "指令"]),
            "code": any(w in user_input_lower for w in ["代码", "示例"]),
            "tips": any(w in user_input_lower for w in ["技巧", "提示"]),
            "tutorial": any(w in user_input_lower for w in ["新手", "教程", "入门"]),
            "architecture": any(w in user_input_lower for w in ["架构", "系统架构", "六层架构"]),
            "new_features": any(w in user_input_lower for w in ["新增功能", "新功能", "最新功能", "更新内容"]),
            "all_features": any(w in user_input_lower for w in ["全部功能", "所有功能", "功能大全", "功能列表"]),
            "all_skills": any(w in user_input_lower for w in ["所有技能", "全部技能", "技能列表", "技能大全"]),
            "all_modules": any(w in user_input_lower for w in ["所有模块", "全部模块", "模块列表", "模块介绍"]),
            "usage_guide": any(w in user_input_lower for w in ["使用引导", "使用指南", "怎么使用", "如何使用", "使用教程"]),
        }
        matched = [k for k, v in intents.items() if v]
        return {"intents": matched, "primary_intent": matched[0] if matched else "unknown"}
    
    def get_contextual_guide(self, user_input: str) -> str:
        intent_info = self.detect_intent(user_input)
        primary = intent_info["primary_intent"]
        response_map = {
            "help": self.get_quick_reference(),
            "search": "## 🔍 搜索功能\n\n说'搜索xxx'或'查一下xxx'",
            "document": "## 📝 文档功能\n\n说'生成报告'或'制作PPT'",
            "data": "## 📊 数据分析\n\n说'分析数据'或'做个图表'",
            "automation": "## ⏰ 自动化\n\n说'每天提醒我'设置定时任务",
            "memory": "## 🧠 记忆功能\n\n说'记住xxx'保存信息",
            "workflow": "## 🔄 工作流\n\n电商选品分析、工厂筛选比价、市场分析报告",
            "skill": "## 🛠️ 技能\n\n说'所有技能'查看175个技能列表",
            "commands": "## 📋 命令\n\n帮助、架构、新增功能、全部功能、所有技能、所有模块、使用引导",
            "code": "## 💻 代码模板\n\nWord文档、数据分析、定时任务、图片识别、Excel处理",
            "tips": "## 💡 技巧\n\n多步骤任务自动拆解、自然语言交互、记忆功能、工作流预设",
            "tutorial": self.get_quick_reference(),
            "architecture": self.get_architecture_guide(),
            "new_features": self.get_new_features_guide(),
            "all_features": self.get_all_features_guide(),
            "all_skills": self.get_all_skills_guide(),
            "all_modules": self.get_all_modules_guide(),
            "usage_guide": self.get_usage_guide(),
        }
        return response_map.get(primary, self.get_quick_reference())
    
    def get_smart_response(self, user_input: str) -> str:
        intent_info = self.detect_intent(user_input)
        if intent_info["intents"]:
            return self.get_contextual_guide(user_input)
        return self.get_quick_reference()


# 全局实例
_complete_guide = None

def get_guide() -> CompleteGuide:
    global _complete_guide
    if _complete_guide is None:
        _complete_guide = CompleteGuide()
    return _complete_guide
