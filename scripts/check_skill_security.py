#!/usr/bin/env python3
"""
技能安全识别器 - V1.0.0

检测和识别高危 Skill，防止安装恶意或高风险的技能

基于 @傅盛 的安全分析，识别 8 类高危 Skill：
1. 密钥收割型 - 索取 API Key / 云服务密钥
2. 挖矿注入型 - 后台偷跑挖矿程序
3. 动态拉取型 - 运行时从外部服务器拉取恶意逻辑
4. 越权访问型 - 权限申请与功能不匹配
5. 仿冒官方型 - 名字模仿官方或知名 Skill
6. 无作者溯源型 - 无 GitHub、无作者信息、无 README
7. 第三方内容抓取型 - 抓取不可信网页内容
8. 无维护型 - 零评论、零 star、几个月没更新
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# 高危类型定义
HIGH_RISK_TYPES = {
    "key_harvester": {
        "id": 1,
        "name": "密钥收割型",
        "description": "要求填入 API Key / 云服务密钥，可能偷偷发往攻击者服务器",
        "indicators": [
            "要求 API Key",
            "要求云服务密钥",
            "要求 SSH 私钥",
            "要求数据库密码",
            "功能简单但索取密钥权限"
        ],
        "severity": "critical"
    },
    "crypto_miner": {
        "id": 2,
        "name": "挖矿注入型",
        "description": "在后台偷跑挖矿程序，吃掉 CPU 和电费",
        "indicators": [
            "安装后系统变慢",
            "CPU 异常飙高",
            "包含挖矿相关代码",
            "后台持续运行"
        ],
        "severity": "critical"
    },
    "dynamic_fetcher": {
        "id": 3,
        "name": "动态拉取型",
        "description": "安装时代码干净，运行时从外部服务器动态拉取恶意逻辑",
        "indicators": [
            "运行时从外部服务器拉取代码",
            "包含 eval() 或 exec() 动态执行",
            "从远程 URL 加载脚本",
            "统计数据: 2.9% 的 ClawHub Skill 有此行为"
        ],
        "severity": "high"
    },
    "permission_abuser": {
        "id": 4,
        "name": "越权访问型",
        "description": "权限申请与功能明显不匹配",
        "indicators": [
            "天气查询却要读取 SSH 私钥",
            "简单功能却要文件系统访问",
            "功能与权限不匹配"
        ],
        "severity": "high"
    },
    "fake_official": {
        "id": 5,
        "name": "仿冒官方型",
        "description": "名字高度模仿官方或知名 Skill",
        "indicators": [
            "名字包含 browser-pro、memory-plus 等",
            "下载量极低",
            "发布时间极短",
            "模仿知名 Skill 名称"
        ],
        "severity": "medium"
    },
    "no_author": {
        "id": 6,
        "name": "无作者溯源型",
        "description": "没有 GitHub 主页、没有作者信息、没有 README",
        "indicators": [
            "无 GitHub 主页",
            "无作者信息",
            "无 README 文件",
            "连作者是谁都不知道"
        ],
        "severity": "medium"
    },
    "content_fetcher": {
        "id": 7,
        "name": "第三方内容抓取型",
        "description": "主动抓取不可信网页内容，可能引入提示词注入攻击",
        "indicators": [
            "抓取不可信网页内容",
            "可能引入提示词注入攻击",
            "统计数据: 17.7% 的 ClawHub Skill 有此行为"
        ],
        "severity": "medium"
    },
    "unmaintained": {
        "id": 8,
        "name": "无维护型",
        "description": "零评论、零 star、几个月没更新，发布即跑路",
        "indicators": [
            "无评分",
            "零评论、零 star",
            "几个月没更新",
            "发布即跑路，出了事没人管"
        ],
        "severity": "low"
    }
}


def check_skill_security(skill_path: Path) -> Dict:
    """检查单个技能的安全性"""
    result = {
        "skill_path": str(skill_path),
        "skill_name": skill_path.name,
        "risks": [],
        "risk_count": 0,
        "max_severity": "none",
        "passed": True
    }
    
    if not skill_path.exists():
        result["error"] = "技能目录不存在"
        return result
    
    # 1. 检查密钥收割型
    risk = check_key_harvester(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 2. 检查挖矿注入型
    risk = check_crypto_miner(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 3. 检查动态拉取型
    risk = check_dynamic_fetcher(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 4. 检查越权访问型
    risk = check_permission_abuser(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 5. 检查仿冒官方型
    risk = check_fake_official(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 6. 检查无作者溯源型
    risk = check_no_author(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 7. 检查第三方内容抓取型
    risk = check_content_fetcher(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 8. 检查无维护型
    risk = check_unmaintained(skill_path)
    if risk:
        result["risks"].append(risk)
    
    # 汇总结果
    result["risk_count"] = len(result["risks"])
    
    if result["risks"]:
        severities = [r["severity"] for r in result["risks"]]
        if "critical" in severities:
            result["max_severity"] = "critical"
            result["passed"] = False
        elif "high" in severities:
            result["max_severity"] = "high"
            result["passed"] = False
        elif "medium" in severities:
            result["max_severity"] = "medium"
        else:
            result["max_severity"] = "low"
    
    return result


def check_key_harvester(skill_path: Path) -> Dict:
    """检查密钥收割型"""
    indicators = []
    
    # 检查 SKILL.md 或配置文件中是否要求密钥
    for file_name in ["SKILL.md", "skill.json", "config.json", "README.md"]:
        file_path = skill_path / file_name
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
            if any(kw in content for kw in ["api key", "api_key", "secret key", "ssh", "password", "token"]):
                indicators.append(f"{file_name} 中包含密钥相关关键词")
    
    if indicators:
        return {
            "type": "key_harvester",
            "name": "密钥收割型",
            "severity": "critical",
            "indicators": indicators
        }
    return None


def check_crypto_miner(skill_path: Path) -> Dict:
    """检查挖矿注入型"""
    indicators = []
    
    # 检查 Python 文件中是否包含挖矿相关代码
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore').lower()
            if any(kw in content for kw in ["crypto", "mining", "miner", "stratum", "pool"]):
                indicators.append(f"{py_file.name} 中包含挖矿相关关键词")
        except:
            pass
    
    if indicators:
        return {
            "type": "crypto_miner",
            "name": "挖矿注入型",
            "severity": "critical",
            "indicators": indicators
        }
    return None


def check_dynamic_fetcher(skill_path: Path) -> Dict:
    """检查动态拉取型"""
    indicators = []
    
    # 检查是否包含动态执行代码
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if "eval(" in content or "exec(" in content:
                indicators.append(f"{py_file.name} 中包含 eval/exec")
            if "requests.get" in content or "urllib" in content:
                if "import" in content:
                    indicators.append(f"{py_file.name} 中包含远程请求")
        except:
            pass
    
    if indicators:
        return {
            "type": "dynamic_fetcher",
            "name": "动态拉取型",
            "severity": "high",
            "indicators": indicators
        }
    return None


def check_permission_abuser(skill_path: Path) -> Dict:
    """检查越权访问型"""
    indicators = []
    
    # 检查 _meta.json 中的权限声明
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.load(open(meta_file, encoding='utf-8'))
            permissions = meta.get("permissions", [])
            if "file_system" in permissions or "ssh" in permissions:
                # 检查技能名称是否与权限匹配
                skill_name = skill_path.name.lower()
                if "weather" in skill_name or "time" in skill_name or "note" in skill_name:
                    indicators.append(f"技能 {skill_path.name} 申请了文件系统/SSH 权限但功能可能不需要")
        except:
            pass
    
    if indicators:
        return {
            "type": "permission_abuser",
            "name": "越权访问型",
            "severity": "high",
            "indicators": indicators
        }
    return None


def check_fake_official(skill_path: Path) -> Dict:
    """检查仿冒官方型"""
    indicators = []
    
    skill_name = skill_path.name.lower()
    
    # 检查是否模仿知名技能
    official_patterns = ["browser", "memory", "file", "git", "docker", "pdf", "docx"]
    for pattern in official_patterns:
        if f"{pattern}-pro" in skill_name or f"{pattern}-plus" in skill_name:
            indicators.append(f"技能名称 {skill_path.name} 可能模仿官方技能")
    
    if indicators:
        return {
            "type": "fake_official",
            "name": "仿冒官方型",
            "severity": "medium",
            "indicators": indicators
        }
    return None


def check_no_author(skill_path: Dict) -> Dict:
    """检查无作者溯源型"""
    indicators = []
    
    # 检查是否有 README
    readme_exists = any((skill_path / f).exists() for f in ["README.md", "readme.md", "README.txt"])
    if not readme_exists:
        indicators.append("缺少 README 文件")
    
    # 检查 _meta.json 中是否有作者信息
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.load(open(meta_file, encoding='utf-8'))
            if not meta.get("author") and not meta.get("github"):
                indicators.append("_meta.json 中缺少作者信息")
        except:
            indicators.append("_meta.json 解析失败")
    
    if indicators:
        return {
            "type": "no_author",
            "name": "无作者溯源型",
            "severity": "medium",
            "indicators": indicators
        }
    return None


def check_content_fetcher(skill_path: Path) -> Dict:
    """检查第三方内容抓取型"""
    indicators = []
    
    # 检查是否包含网页抓取代码
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if "beautifulsoup" in content.lower() or "selenium" in content.lower():
                indicators.append(f"{py_file.name} 中包含网页抓取库")
            if "web_fetch" in content or "fetch_url" in content:
                indicators.append(f"{py_file.name} 中包含 URL 抓取函数")
        except:
            pass
    
    if indicators:
        return {
            "type": "content_fetcher",
            "name": "第三方内容抓取型",
            "severity": "medium",
            "indicators": indicators
        }
    return None


def check_unmaintained(skill_path: Path) -> Dict:
    """检查无维护型"""
    indicators = []
    
    # 检查 _meta.json 中的更新时间
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.load(open(meta_file, encoding='utf-8'))
            updated = meta.get("updated", meta.get("created", ""))
            if updated:
                # 检查是否超过 6 个月未更新
                try:
                    update_time = datetime.strptime(updated[:10], "%Y-%m-%d")
                    days = (datetime.now() - update_time).days
                    if days > 180:
                        indicators.append(f"已 {days} 天未更新")
                except:
                    pass
        except:
            pass
    
    if indicators:
        return {
            "type": "unmaintained",
            "name": "无维护型",
            "severity": "low",
            "indicators": indicators
        }
    return None


def scan_all_skills() -> Dict:
    """扫描所有技能"""
    root = get_project_root()
    skills_dir = root / "skills"
    
    if not skills_dir.exists():
        return {
            "error": "skills 目录不存在",
            "scanned": 0,
            "results": []
        }
    
    results = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            result = check_skill_security(skill_dir)
            results.append(result)
    
    # 汇总
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    
    critical = sum(1 for r in results if r["max_severity"] == "critical")
    high = sum(1 for r in results if r["max_severity"] == "high")
    medium = sum(1 for r in results if r["max_severity"] == "medium")
    low = sum(1 for r in results if r["max_severity"] == "low")
    
    return {
        "scanned": total,
        "passed": passed,
        "failed": failed,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "results": results,
        "generated_at": datetime.now().isoformat()
    }


def print_report(report: Dict):
    """打印报告"""
    print("╔══════════════════════════════════════════════════╗")
    print("║          技能安全识别报告 V1.0.0               ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print(f"扫描技能数: {report['scanned']}")
    print(f"通过: {report['passed']}")
    print(f"风险: {report['failed']}")
    print()
    
    print("【风险分布】")
    print(f"  🔴 Critical: {report['critical']}")
    print(f"  🟠 High: {report['high']}")
    print(f"  🟡 Medium: {report['medium']}")
    print(f"  🟢 Low: {report['low']}")
    print()
    
    # 显示高风险技能
    critical_skills = [r for r in report['results'] if r['max_severity'] == 'critical']
    if critical_skills:
        print("【Critical 风险技能】")
        for skill in critical_skills:
            print(f"  ❌ {skill['skill_name']}")
            for risk in skill['risks']:
                if risk['severity'] == 'critical':
                    print(f"     - {risk['name']}: {', '.join(risk['indicators'][:2])}")
        print()
    
    high_skills = [r for r in report['results'] if r['max_severity'] == 'high']
    if high_skills:
        print("【High 风险技能】")
        for skill in high_skills[:5]:
            print(f"  ⚠️ {skill['skill_name']}")
            for risk in skill['risks']:
                if risk['severity'] == 'high':
                    print(f"     - {risk['name']}")
        if len(high_skills) > 5:
            print(f"  ... 还有 {len(high_skills) - 5} 个")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="技能安全识别器 V1.0.0")
    parser.add_argument("--scan-all", action="store_true", help="扫描所有技能")
    parser.add_argument("--skill", help="扫描指定技能目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--save", action="store_true", help="保存报告到文件")
    args = parser.parse_args()
    
    if args.skill:
        skill_path = Path(args.skill)
        result = check_skill_security(skill_path)
        report = {"results": [result], "scanned": 1}
    elif args.scan_all:
        report = scan_all_skills()
    else:
        print("请指定 --scan-all 或 --skill <path>")
        return 1
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    
    if args.save:
        root = get_project_root()
        report_path = root / "reports/ops/skill_security_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存: {report_path}")
    
    return 0 if report.get('failed', 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
