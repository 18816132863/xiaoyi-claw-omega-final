#!/usr/bin/env python3
"""
风险体系统一脚本 V2

将 route_registry.json 从旧口径 (LOW/MEDIUM/HIGH/SYSTEM) 
统一到正式口径 (L0/L1/L2/L3/L4/BLOCKED)
并使用与 safety_governor 一致的策略名
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# 正式风险等级定义 (来自 safety_governor/risk_levels.py)
VALID_RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4", "BLOCKED"}

# 旧风险等级 (需要替换)
LEGACY_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "SYSTEM", "CRITICAL"}

# 正式策略名 (来自 safety_governor/risk_levels.py RiskPolicy)
VALID_POLICIES = {
    "auto_execute",  # 自动执行 (L0, L1)
    "rate_limited",  # 限流执行 (L2)
    "confirm_once",  # 单次确认 (L3)
    "strong_confirm",  # 强确认 (L4)
    "blocked",  # 拒绝执行 (BLOCKED)
}

# L4 场景关键词 (需要强确认)
L4_KEYWORDS = [
    "payment", "purchase", "transfer", "account", "password", "privacy",
    "game", "gacha", "draw", "lottery", "bet", "gambl",
    "auto_click", "auto_play", "bot", "script",
]

# BLOCKED 场景关键词 (拒绝执行)
BLOCKED_KEYWORDS = [
    "bypass_anti_cheat", "cheat", "hack", "crack",
    "account_theft", "steal", "unauthorized",
    "batch_harassment", "spam", "flood",
    "bypass_risk_control", "evade",
    "competitive_cheating", "resource_farming_bot",
]


def map_legacy_to_new(legacy_level: str, capability: str, description: str = "") -> Tuple[str, str, bool]:
    """
    将旧风险等级映射到新风险等级
    
    Returns:
        (new_level, policy, blocked)
    """
    cap_lower = capability.lower()
    desc_lower = description.lower()
    
    # 检查是否 BLOCKED
    for keyword in BLOCKED_KEYWORDS:
        if keyword in cap_lower or keyword in desc_lower:
            return "BLOCKED", "blocked", True
    
    # 检查是否 L4
    for keyword in L4_KEYWORDS:
        if keyword in cap_lower or keyword in desc_lower:
            return "L4", "strong_confirm", False
    
    # 根据旧等级映射
    if legacy_level == "LOW":
        # LOW → L0 或 L1
        # 查询类 → L0
        # 轻写入（备忘录、日程）→ L1
        if any(kw in cap_lower for kw in ["query", "list", "search", "get", "explain", "export"]):
            return "L0", "auto_execute", False
        else:
            return "L1", "auto_execute", False
    
    elif legacy_level == "MEDIUM":
        # MEDIUM → L2
        return "L2", "rate_limited", False
    
    elif legacy_level == "HIGH":
        # HIGH → L3
        return "L3", "confirm_once", False
    
    elif legacy_level == "SYSTEM":
        # SYSTEM → L3 或 L4
        # 系统配置、重启 → L4
        # 其他系统操作 → L3
        if any(kw in cap_lower for kw in ["restart", "reboot", "shutdown", "config", "bootstrap"]):
            return "L4", "strong_confirm", False
        else:
            return "L3", "confirm_once", False
    
    elif legacy_level == "CRITICAL":
        # CRITICAL → L4
        return "L4", "strong_confirm", False
    
    else:
        # 未知等级，默认 L2
        return "L2", "rate_limited", False


def compute_route_fields(risk_level: str, policy: str, blocked: bool) -> Dict[str, Any]:
    """
    根据风险等级计算路由字段
    """
    return {
        "risk_level": risk_level,
        "policy": policy,
        "requires_confirmation": risk_level in ["L2", "L3", "L4"],
        "requires_preview": risk_level in ["L3", "L4"],
        "requires_stepwise_execution": risk_level == "L4",
        "audit_required": risk_level in ["L2", "L3", "L4"],
        "blocked": blocked,
    }


def unify_route_registry(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    统一路由注册表风险等级
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stats = {
        "total": 0,
        "mapped": {
            "L0": 0, "L1": 0, "L2": 0, "L3": 0, "L4": 0, "BLOCKED": 0
        },
        "legacy_found": 0,
        "already_new": 0,
        "changes": [],
    }
    
    routes = data.get("routes", {})
    
    for route_id, route in routes.items():
        stats["total"] += 1
        
        legacy_level = route.get("risk_level", "MEDIUM")
        capability = route.get("capability", route_id.replace("route.", ""))
        description = route.get("metadata", {}).get("description", "")
        
        # 检查是否已经是新口径
        if legacy_level in VALID_RISK_LEVELS:
            stats["already_new"] += 1
            stats["mapped"][legacy_level] = stats["mapped"].get(legacy_level, 0) + 1
            
            # 即使已经是新口径，也需要确保策略名正确
            # 更新策略名为正式名称
            policy_map = {
                "L0": "auto_execute",
                "L1": "auto_execute",
                "L2": "rate_limited",
                "L3": "confirm_once",
                "L4": "strong_confirm",
                "BLOCKED": "blocked",
            }
            if legacy_level in policy_map:
                route["policy"] = policy_map[legacy_level]
            continue
        
        # 检查是否是旧口径
        if legacy_level not in LEGACY_RISK_LEVELS:
            print(f"⚠️ 未知风险等级: {route_id} -> {legacy_level}")
            continue
        
        stats["legacy_found"] += 1
        
        # 映射到新等级
        new_level, policy, blocked = map_legacy_to_new(legacy_level, capability, description)
        
        # 计算新字段
        new_fields = compute_route_fields(new_level, policy, blocked)
        
        # 更新路由
        route["risk_level"] = new_fields["risk_level"]
        route["policy"] = new_fields["policy"]
        route["requires_confirmation"] = new_fields["requires_confirmation"]
        route["requires_preview"] = new_fields["requires_preview"]
        route["requires_stepwise_execution"] = new_fields["requires_stepwise_execution"]
        route["audit_required"] = new_fields["audit_required"]
        route["blocked"] = new_fields["blocked"]
        
        # 记录变更
        stats["changes"].append({
            "route_id": route_id,
            "old_level": legacy_level,
            "new_level": new_level,
            "policy": policy,
        })
        
        stats["mapped"][new_level] = stats["mapped"].get(new_level, 0) + 1
    
    # 更新版本和时间戳
    data["version"] = "2.0.0"
    data["updated"] = datetime.now().isoformat()
    data["risk_system"] = "L0-L4-BLOCKED"
    
    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return stats


def generate_report(stats: Dict[str, Any]) -> str:
    """
    生成报告
    """
    lines = [
        "# Route Registry 风险体系统一报告",
        "",
        f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 统计",
        "",
        f"- 总路由数: {stats['total']}",
        f"- 已是新口径: {stats['already_new']}",
        f"- 需要转换: {stats['legacy_found']}",
        "",
        "## 风险等级分布",
        "",
        "| 等级 | 数量 | 策略 | 说明 |",
        "|------|------|------|------|",
        f"| L0 | {stats['mapped'].get('L0', 0)} | auto_execute | 查询、总结、解释 - 自动执行 |",
        f"| L1 | {stats['mapped'].get('L1', 0)} | auto_execute | 轻写入（备忘录、日程） - 自动执行 |",
        f"| L2 | {stats['mapped'].get('L2', 0)} | rate_limited | 短信、通知、批量操作 - 策略控制 + 限流 |",
        f"| L3 | {stats['mapped'].get('L3', 0)} | confirm_once | 删除、拨电话、重要修改 - 默认确认 |",
        f"| L4 | {stats['mapped'].get('L4', 0)} | strong_confirm | 支付、金融、账号、隐私、游戏自动化 - 强确认 + 分步执行 |",
        f"| BLOCKED | {stats['mapped'].get('BLOCKED', 0)} | blocked | 违法、盗号、绕过反作弊 - 拒绝执行 |",
        "",
        "## 策略说明",
        "",
        "| 策略 | 说明 |",
        "|------|------|",
        "| auto_execute | 自动执行，无需确认 |",
        "| rate_limited | 限流执行，防止滥用 |",
        "| confirm_once | 单次确认，用户同意后执行 |",
        "| strong_confirm | 强确认，双重确认 + 预览 + 分步执行 |",
        "| blocked | 拒绝执行，不执行任何操作 |",
        "",
        "## 变更详情",
        "",
    ]
    
    if stats["changes"]:
        lines.append("| 路由ID | 旧等级 | 新等级 | 策略 |")
        lines.append("|--------|--------|--------|------|")
        for change in stats["changes"][:50]:  # 最多显示 50 条
            lines.append(f"| {change['route_id']} | {change['old_level']} | {change['new_level']} | {change['policy']} |")
        
        if len(stats["changes"]) > 50:
            lines.append(f"| ... | ... | ... | ... |")
            lines.append(f"| 共 {len(stats['changes'])} 条变更 | | | |")
    else:
        lines.append("无需变更。")
    
    lines.extend([
        "",
        "## 与 safety_governor 一致性",
        "",
        "风险等级和策略名称完全匹配 `safety_governor/risk_levels.py` 定义:",
        "",
        "- RiskLevel: L0, L1, L2, L3, L4, BLOCKED",
        "- RiskPolicy: auto_execute, rate_limited, confirm_once, strong_confirm, blocked",
        "",
        "## 验证",
        "",
        "运行以下命令验证:",
        "",
        "```bash",
        "python scripts/check_route_registry.py",
        "python -m pytest tests/test_route_safety_governor_consistency.py -v",
        "```",
        "",
        "---",
        "",
        "**风险体系统一完成** ✅",
    ])
    
    return "\n".join(lines)


def main():
    """主函数"""
    workspace = Path(__file__).parent.parent
    input_path = workspace / "infrastructure" / "route_registry.json"
    output_path = workspace / "infrastructure" / "route_registry.json"
    report_path = workspace / "ROUTE_RISK_POLICY_UNIFICATION_REPORT.txt"
    
    print("=" * 60)
    print("Route Registry 风险体系统一 V2")
    print("=" * 60)
    print()
    
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        return 1
    
    print(f"📂 输入: {input_path}")
    print(f"📂 输出: {output_path}")
    print()
    
    # 执行统一
    stats = unify_route_registry(input_path, output_path)
    
    # 生成报告
    report = generate_report(stats)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📊 统计:")
    print(f"   总路由: {stats['total']}")
    print(f"   已是新口径: {stats['already_new']}")
    print(f"   需要转换: {stats['legacy_found']}")
    print()
    print(f"📈 风险等级分布:")
    for level in ["L0", "L1", "L2", "L3", "L4", "BLOCKED"]:
        count = stats["mapped"].get(level, 0)
        print(f"   {level}: {count}")
    print()
    print(f"📄 报告: {report_path}")
    print()
    print("✅ 完成")
    
    return 0


if __name__ == "__main__":
    exit(main())
