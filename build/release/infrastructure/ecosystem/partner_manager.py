#!/usr/bin/env python3
"""
伙伴生态管理器 - V2.8.0

能力：
- 伙伴身份分层
- 伙伴权限控制
- 伙伴接入审核
- 模板贡献审核
- 外部能力上架审核
- 伙伴测试沙箱
- 伙伴健康度评估
- 伙伴接入风险记录
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class PartnerTier(Enum):
    BRONZE = "bronze"           # 青铜伙伴
    SILVER = "silver"           # 白银伙伴
    GOLD = "gold"               # 黄金伙伴
    PLATINUM = "platinum"       # 铂金伙伴
    STRATEGIC = "strategic"     # 战略伙伴

class PartnerStatus(Enum):
    PENDING = "pending"         # 待审核
    ACTIVE = "active"           # 激活
    SUSPENDED = "suspended"     # 暂停
    TERMINATED = "terminated"   # 终止

class ContributionType(Enum):
    TEMPLATE = "template"       # 模板贡献
    WORKFLOW = "workflow"       # 工作流贡献
    PLUGIN = "plugin"           # 插件贡献
    CAPABILITY = "capability"   # 能力贡献

class ReviewStatus(Enum):
    PENDING = "pending"         # 待审核
    APPROVED = "approved"       # 已批准
    REJECTED = "rejected"       # 已拒绝
    REVISION = "revision"       # 需修改

@dataclass
class Partner:
    """伙伴"""
    partner_id: str
    name: str
    tier: str
    status: str
    contact: str
    api_key: str
    permissions: List[str]
    quotas: Dict[str, int]
    health_score: float
    risk_level: str
    joined_at: str
    last_activity: Optional[str]
    metadata: Dict

@dataclass
class Contribution:
    """贡献"""
    contribution_id: str
    partner_id: str
    contribution_type: str
    name: str
    description: str
    content_ref: str            # 内容引用
    status: str
    reviewer: Optional[str]
    review_notes: List[str]
    submitted_at: str
    reviewed_at: Optional[str]

@dataclass
class Sandbox:
    """测试沙箱"""
    sandbox_id: str
    partner_id: str
    environment: str            # dev / staging
    resources: Dict
    created_at: str
    expires_at: str
    status: str

@dataclass
class RiskRecord:
    """风险记录"""
    record_id: str
    partner_id: str
    risk_type: str
    severity: str               # low / medium / high / critical
    description: str
    action_taken: str
    timestamp: str
    resolved: bool

class PartnerEcosystemManager:
    """伙伴生态管理器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.ecosystem_path = self.project_root / 'ecosystem'
        self.config_path = self.ecosystem_path / 'partners.json'
        
        # 伙伴
        self.partners: Dict[str, Partner] = {}
        
        # 贡献
        self.contributions: List[Contribution] = []
        
        # 沙箱
        self.sandboxes: List[Sandbox] = []
        
        # 风险记录
        self.risk_records: List[RiskRecord] = []
        
        # 层级权限定义
        self.tier_permissions = {
            PartnerTier.BRONZE.value: ["basic_api", "template_use"],
            PartnerTier.SILVER.value: ["basic_api", "template_use", "template_contribute"],
            PartnerTier.GOLD.value: ["basic_api", "template_use", "template_contribute", "workflow_contribute"],
            PartnerTier.PLATINUM.value: ["basic_api", "template_use", "template_contribute", "workflow_contribute", "plugin_contribute"],
            PartnerTier.STRATEGIC.value: ["all"],
        }
        
        # 层级配额定义
        self.tier_quotas = {
            PartnerTier.BRONZE.value: {"api_calls_per_day": 1000, "storage_mb": 100},
            PartnerTier.SILVER.value: {"api_calls_per_day": 5000, "storage_mb": 500},
            PartnerTier.GOLD.value: {"api_calls_per_day": 20000, "storage_mb": 2000},
            PartnerTier.PLATINUM.value: {"api_calls_per_day": 100000, "storage_mb": 10000},
            PartnerTier.STRATEGIC.value: {"api_calls_per_day": -1, "storage_mb": -1},  # 无限制
        }
        
        self._load()
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for pid, partner in data.get("partners", {}).items():
                self.partners[pid] = Partner(**partner)
            
            self.contributions = [Contribution(**c) for c in data.get("contributions", [])]
            self.sandboxes = [Sandbox(**s) for s in data.get("sandboxes", [])]
            self.risk_records = [RiskRecord(**r) for r in data.get("risk_records", [])]
    
    def _save(self):
        """保存配置"""
        self.ecosystem_path.mkdir(parents=True, exist_ok=True)
        data = {
            "partners": {pid: asdict(p) for pid, p in self.partners.items()},
            "contributions": [asdict(c) for c in self.contributions],
            "sandboxes": [asdict(s) for s in self.sandboxes],
            "risk_records": [asdict(r) for r in self.risk_records],
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _generate_api_key(self) -> str:
        """生成 API Key"""
        import secrets
        return f"pk_{secrets.token_hex(16)}"
    
    # === 伙伴管理 ===
    def register_partner(self, name: str, contact: str,
                         tier: str = "bronze") -> Partner:
        """注册伙伴"""
        partner_id = f"partner_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        partner = Partner(
            partner_id=partner_id,
            name=name,
            tier=tier,
            status=PartnerStatus.PENDING.value,
            contact=contact,
            api_key=self._generate_api_key(),
            permissions=self.tier_permissions.get(tier, []),
            quotas=self.tier_quotas.get(tier, {}),
            health_score=100.0,
            risk_level="low",
            joined_at=datetime.now().isoformat(),
            last_activity=None,
            metadata={}
        )
        
        self.partners[partner_id] = partner
        self._save()
        
        return partner
    
    def approve_partner(self, partner_id: str) -> Dict:
        """批准伙伴"""
        if partner_id not in self.partners:
            return {"error": "伙伴不存在"}
        
        partner = self.partners[partner_id]
        partner.status = PartnerStatus.ACTIVE.value
        self._save()
        
        return {"status": "approved", "partner_id": partner_id}
    
    def suspend_partner(self, partner_id: str, reason: str) -> Dict:
        """暂停伙伴"""
        if partner_id not in self.partners:
            return {"error": "伙伴不存在"}
        
        partner = self.partners[partner_id]
        partner.status = PartnerStatus.SUSPENDED.value
        self._save()
        
        # 记录风险
        self._add_risk_record(partner_id, "suspension", "high", reason, "暂停伙伴")
        
        return {"status": "suspended", "partner_id": partner_id}
    
    def upgrade_tier(self, partner_id: str, new_tier: str) -> Dict:
        """升级层级"""
        if partner_id not in self.partners:
            return {"error": "伙伴不存在"}
        
        partner = self.partners[partner_id]
        partner.tier = new_tier
        partner.permissions = self.tier_permissions.get(new_tier, [])
        partner.quotas = self.tier_quotas.get(new_tier, {})
        self._save()
        
        return {"status": "upgraded", "partner_id": partner_id, "new_tier": new_tier}
    
    def get_partner(self, partner_id: str) -> Optional[Partner]:
        """获取伙伴"""
        return self.partners.get(partner_id)
    
    def list_partners(self, tier: str = None, status: str = None) -> List[Partner]:
        """列出伙伴"""
        partners = list(self.partners.values())
        
        if tier:
            partners = [p for p in partners if p.tier == tier]
        if status:
            partners = [p for p in partners if p.status == status]
        
        return partners
    
    # === 权限检查 ===
    def check_permission(self, partner_id: str, permission: str) -> tuple:
        """检查权限"""
        partner = self.get_partner(partner_id)
        if not partner:
            return False, "伙伴不存在"
        
        if partner.status != PartnerStatus.ACTIVE.value:
            return False, "伙伴未激活"
        
        if "all" in partner.permissions or permission in partner.permissions:
            return True, "权限检查通过"
        
        return False, f"无权限: {permission}"
    
    def check_quota(self, partner_id: str, quota_type: str, current_usage: int) -> tuple:
        """检查配额"""
        partner = self.get_partner(partner_id)
        if not partner:
            return False, "伙伴不存在"
        
        quota = partner.quotas.get(quota_type, 0)
        
        if quota == -1:  # 无限制
            return True, "无限制"
        
        if current_usage >= quota:
            return False, f"已达配额上限: {quota}"
        
        return True, f"剩余: {quota - current_usage}"
    
    # === 贡献管理 ===
    def submit_contribution(self, partner_id: str, contribution_type: str,
                            name: str, description: str,
                            content_ref: str) -> Contribution:
        """提交贡献"""
        # 检查权限
        required_permission = f"{contribution_type}_contribute"
        has_perm, msg = self.check_permission(partner_id, required_permission)
        if not has_perm:
            raise ValueError(f"无贡献权限: {msg}")
        
        contribution = Contribution(
            contribution_id=f"contrib_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            partner_id=partner_id,
            contribution_type=contribution_type,
            name=name,
            description=description,
            content_ref=content_ref,
            status=ReviewStatus.PENDING.value,
            reviewer=None,
            review_notes=[],
            submitted_at=datetime.now().isoformat(),
            reviewed_at=None
        )
        
        self.contributions.append(contribution)
        self._save()
        
        return contribution
    
    def review_contribution(self, contribution_id: str, reviewer: str,
                            approved: bool, notes: str = "") -> Dict:
        """审核贡献"""
        for contrib in self.contributions:
            if contrib.contribution_id == contribution_id:
                contrib.status = ReviewStatus.APPROVED.value if approved else ReviewStatus.REJECTED.value
                contrib.reviewer = reviewer
                contrib.review_notes.append(notes)
                contrib.reviewed_at = datetime.now().isoformat()
                self._save()
                return {"status": contrib.status, "contribution_id": contribution_id}
        
        return {"error": "贡献不存在"}
    
    def list_contributions(self, partner_id: str = None,
                           status: str = None) -> List[Contribution]:
        """列出贡献"""
        contributions = self.contributions
        
        if partner_id:
            contributions = [c for c in contributions if c.partner_id == partner_id]
        if status:
            contributions = [c for c in contributions if c.status == status]
        
        return contributions
    
    # === 沙箱管理 ===
    def create_sandbox(self, partner_id: str, environment: str = "dev",
                       expires_days: int = 30) -> Sandbox:
        """创建沙箱"""
        sandbox = Sandbox(
            sandbox_id=f"sandbox_{partner_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            partner_id=partner_id,
            environment=environment,
            resources={"cpu": 1, "memory_mb": 512, "storage_mb": 100},
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=expires_days)).isoformat(),
            status="active"
        )
        
        self.sandboxes.append(sandbox)
        self._save()
        
        return sandbox
    
    def get_partner_sandboxes(self, partner_id: str) -> List[Sandbox]:
        """获取伙伴沙箱"""
        return [s for s in self.sandboxes if s.partner_id == partner_id and s.status == "active"]
    
    # === 健康度评估 ===
    def evaluate_health(self, partner_id: str) -> Dict:
        """评估健康度"""
        partner = self.get_partner(partner_id)
        if not partner:
            return {"error": "伙伴不存在"}
        
        # 计算健康度
        score = 100.0
        
        # 风险记录扣分
        partner_risks = [r for r in self.risk_records if r.partner_id == partner_id and not r.resolved]
        for risk in partner_risks:
            if risk.severity == "critical":
                score -= 30
            elif risk.severity == "high":
                score -= 20
            elif risk.severity == "medium":
                score -= 10
            else:
                score -= 5
        
        # 活跃度加分
        if partner.last_activity:
            last = datetime.fromisoformat(partner.last_activity)
            days_inactive = (datetime.now() - last).days
            if days_inactive > 30:
                score -= 10
            elif days_inactive > 7:
                score -= 5
        
        score = max(0, min(100, score))
        
        # 更新伙伴健康度
        partner.health_score = score
        
        # 更新风险等级
        if score < 50:
            partner.risk_level = "high"
        elif score < 70:
            partner.risk_level = "medium"
        else:
            partner.risk_level = "low"
        
        self._save()
        
        return {
            "partner_id": partner_id,
            "health_score": score,
            "risk_level": partner.risk_level,
            "risk_count": len(partner_risks)
        }
    
    def _add_risk_record(self, partner_id: str, risk_type: str,
                         severity: str, description: str,
                         action_taken: str) -> RiskRecord:
        """添加风险记录"""
        record = RiskRecord(
            record_id=f"risk_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            partner_id=partner_id,
            risk_type=risk_type,
            severity=severity,
            description=description,
            action_taken=action_taken,
            timestamp=datetime.now().isoformat(),
            resolved=False
        )
        
        self.risk_records.append(record)
        self._save()
        
        return record
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 伙伴生态报告",
            "",
            "## 伙伴列表",
            ""
        ]
        
        for partner in self.partners.values():
            status = "✅" if partner.status == PartnerStatus.ACTIVE.value else "⏸️"
            lines.append(f"- {status} **{partner.name}** ({partner.tier})")
            lines.append(f"  - 健康度: {partner.health_score:.0f}")
            lines.append(f"  - 风险等级: {partner.risk_level}")
        
        lines.extend([
            "",
            "## 贡献统计",
            ""
        ])
        
        pending = len([c for c in self.contributions if c.status == ReviewStatus.PENDING.value])
        approved = len([c for c in self.contributions if c.status == ReviewStatus.APPROVED.value])
        lines.append(f"- 待审核: {pending}")
        lines.append(f"- 已批准: {approved}")
        
        return "\n".join(lines)

# 全局实例
_partner_manager = None

def get_partner_manager() -> PartnerEcosystemManager:
    global _partner_manager
    if _partner_manager is None:
        _partner_manager = PartnerEcosystemManager()
    return _partner_manager
