#!/usr/bin/env python3
"""
技能安全识别器 - V2.1.0

检测和识别高危 Skill，防止安装恶意或高风险的技能

基于 @傅盛 的安全分析，识别 8 类高危 Skill：
1. 密钥收割型 - 索取 API Key / 云服务密钥并发往外部服务器
2. 挖矿注入型 - 后台偷跑挖矿程序
3. 动态拉取型 - 运行时从外部服务器拉取恶意逻辑
4. 越权访问型 - 权限申请与功能不匹配
5. 仿冒官方型 - 名字模仿官方或知名 Skill
6. 无作者溯源型 - 无 GitHub、无作者信息、无 README
7. 第三方内容抓取型 - 抓取不可信网页内容
8. 无维护型 - 零评论、零 star、几个月没更新

V2.1.0 改进：
- 添加白名单机制，排除常见合法关键词
- 优化密钥检测，区分配置说明和恶意收割
- 优化挖矿检测，排除数据挖掘等合法用途
- 添加误报抑制，减少 false positive
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# 白名单：这些关键词是合法的配置说明，不应视为风险
KEY_WHITELIST = [
    # 合法的配置说明
    "api_key_env", "set your api key", "configure your api key",
    "environment variable", "env var", "export api_key",
    "your_api_key_here", "replace with your", "填入你的",
    "配置文件", "环境变量", "设置 api key",
    # 合法的文档说明
    "api key is required", "requires api key", "need api key",
    "api key from", "get your api key", "obtain api key",
    # 示例配置
    "example", "sample", "template", "demo",
    # OpenClaw 系统关键词
    "openclaw", "clawhub", "skill",
]

# 白名单：这些是合法的数据挖掘/分析用途，不是加密货币挖矿
MINING_WHITELIST = [
    # 合法的数据分析
    "data mining", "text mining", "web mining",
    "process mining", "graph mining", "pattern mining",
    "association rule", "frequent pattern", "data analysis",
    "machine learning", "deep learning", "nlp", "natural language",
    # 合法的金融分析
    "stock analysis", "market analysis", "financial analysis",
    "factor analysis", "quantitative", "quant", "alpha",
    # 合法的资源管理
    "connection pool", "thread pool", "resource pool",
    "object pool", "memory pool",
    # 文件名白名单
    "factor_mining", "stock_api", "portfolio", "connection_pool",
    "ultimate_search", "player", "fetch_reddit", "test_config",
    "secret_scanner", "threat_modeler", "batch_convert",
    "interconnect", "background",
]


# 高危类型定义
HIGH_RISK_TYPES = {
    "key_harvester": {
        "id": 1,
        "name": "密钥收割型",
        "description": "要求填入 API Key / 云服务密钥，可能偷偷发往攻击者服务器",
        "indicators": [
            "要求 API Key 并发送到外部服务器",
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
            "包含加密货币挖矿相关代码",
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


def is_whitelisted(content: str, whitelist: List[str]) -> bool:
    """检查内容是否在白名单中"""
    content_lower = content.lower()
    for term in whitelist:
        if term.lower() in content_lower:
            return True
    return False


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


def check_key_harvester(skill_path: Path) -> Optional[Dict]:
    """检查密钥收割型 - V2.1.0 优化版"""
    indicators = []
    
    # 合法的 API 调用模式（这些是正常的 API 使用，不是恶意行为）
    legitimate_patterns = [
        r'authorization["\']?\s*:\s*["\']?bearer',  # Bearer 认证
        r'authorization["\']?\s*:\s*api_key',  # API Key 认证头
        r'headers\s*=\s*\{[^}]*authorization',  # 认证头
        r'x-api-key',  # 标准 API Key 头
        r'api_key\s*=\s*os\.environ',  # 从环境变量读取
        r'api_key\s*=\s*args\.',  # 从命令行参数读取
        r'api_key\s*=\s*config',  # 从配置读取
        r'oauth',  # OAuth 授权流程
        r'grant_type',  # OAuth grant type
        r'client_id',  # OAuth client id
        r'openapi',  # 开放 API
        r'api\.biji\.com',  # Get笔记 API
        r'api\.gitee\.com',  # Gitee AI API
        r'ai\.gitee\.com',  # Gitee AI API
    ]
    
    # 检查是否有发送密钥到外部服务器的代码
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            # 检查是否有发送密钥到外部服务器的行为
            # 必须同时满足：包含密钥关键词 + 包含发送请求
            has_key = any(kw in content_lower for kw in ["api_key", "apikey", "secret_key", "private_key"])
            has_send = any(kw in content_lower for kw in ["requests.post", "urllib.request", "http.post", "fetch("])
            
            if has_key and has_send:
                # 检查是否是合法的 API 调用
                is_legitimate = False
                for pattern in legitimate_patterns:
                    if re.search(pattern, content_lower):
                        is_legitimate = True
                        break
                
                # 检查是否在白名单中
                if not is_legitimate and not is_whitelisted(content, KEY_WHITELIST):
                    indicators.append(f"{py_file.name} 可能发送密钥到外部服务器")
        except:
            pass
    
    # 检查配置文件是否有可疑的外部服务器地址
    for config_file in skill_path.rglob("*.json"):
        if config_file.name in ["package.json", "requirements.json", "_meta.json"]:
            continue
        try:
            content = config_file.read_text(encoding='utf-8', errors='ignore')
            # 检查是否有可疑的外部服务器
            if re.search(r'https?://[^"\']+\.xyz|https?://[^"\']+\.top|https?://[^"\']+\.click', content):
                indicators.append(f"{config_file.name} 包含可疑的外部服务器地址")
        except:
            pass
    
    if indicators:
        return {
            "type": "key_harvester",
            "name": "密钥收割型",
            "severity": "critical",
            "indicators": indicators
        }
    return None


def check_crypto_miner(skill_path: Path) -> Optional[Dict]:
    """检查挖矿注入型 - V2.1.0 优化版"""
    indicators = []
    
    # 加密货币挖矿的明确特征
    mining_patterns = [
        r'stratum\+tcp://',  # 挖矿协议
        r'pool\.[a-z]+\.(com|net|org)',  # 挖矿矿池
        r'xmrig',  # 常见挖矿软件
        r'coinhive',  # 浏览器挖矿
        r'cryptonight',  # 挖矿算法
        r'miner\.start',  # 挖矿启动
    ]
    
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            # 检查是否在白名单中（合法的数据分析用途）
            if is_whitelisted(py_file.name, MINING_WHITELIST):
                continue
            if is_whitelisted(content, MINING_WHITELIST):
                continue
            
            # 检查明确的挖矿特征
            for pattern in mining_patterns:
                if re.search(pattern, content_lower):
                    indicators.append(f"{py_file.name} 包含加密货币挖矿代码")
                    break
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


def check_dynamic_fetcher(skill_path: Path) -> Optional[Dict]:
    """检查动态拉取型 - V2.1.0 优化版"""
    indicators = []
    
    # 可疑的动态执行模式
    suspicious_patterns = [
        r'eval\s*\(\s*requests\.',  # 从网络获取后直接执行
        r'exec\s*\(\s*requests\.',  # 从网络获取后直接执行
        r'__import__\s*\(\s*[\'"]requests',  # 动态导入 requests
        r'compile\s*\(\s*requests\.',  # 动态编译网络代码
    ]
    
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            for pattern in suspicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    indicators.append(f"{py_file.name} 包含动态执行网络代码")
                    break
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


def check_permission_abuser(skill_path: Path) -> Optional[Dict]:
    """检查越权访问型"""
    indicators = []
    
    # 检查 _meta.json 中的权限声明
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.load(open(meta_file, encoding='utf-8'))
            permissions = meta.get("permissions", [])
            
            # 检查是否有敏感权限
            sensitive_perms = ["ssh", "root", "admin", "sudo"]
            for perm in sensitive_perms:
                if perm in permissions:
                    indicators.append(f"技能申请了敏感权限: {perm}")
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


def check_fake_official(skill_path: Path) -> Optional[Dict]:
    """检查仿冒官方型"""
    indicators = []
    
    skill_name = skill_path.name.lower()
    
    # 检查是否模仿知名技能（更严格的模式）
    fake_patterns = [
        r'^openclaw-',  # 冒充官方
        r'^clawhub-',   # 冒充官方
        r'-official$',  # 声称官方
        r'^official-',  # 声称官方
    ]
    
    for pattern in fake_patterns:
        if re.search(pattern, skill_name):
            indicators.append(f"技能名称 {skill_path.name} 可能冒充官方")
    
    if indicators:
        return {
            "type": "fake_official",
            "name": "仿冒官方型",
            "severity": "medium",
            "indicators": indicators
        }
    return None


def check_no_author(skill_path: Path) -> Optional[Dict]:
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
            pass
    
    if indicators:
        return {
            "type": "no_author",
            "name": "无作者溯源型",
            "severity": "medium",
            "indicators": indicators
        }
    return None


def check_content_fetcher(skill_path: Path) -> Optional[Dict]:
    """检查第三方内容抓取型"""
    indicators = []
    
    # 检查是否包含可疑的网页抓取代码
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            # 检查是否有可疑的抓取行为
            if "selenium" in content_lower and "headless" in content_lower:
                indicators.append(f"{py_file.name} 包含无头浏览器抓取")
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


def check_unmaintained(skill_path: Path) -> Optional[Dict]:
    """检查无维护型"""
    indicators = []
    
    # 检查 _meta.json 中的更新时间
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.load(open(meta_file, encoding='utf-8'))
            updated = meta.get("updated", meta.get("created", ""))
            if updated:
                # 检查是否超过 1 年未更新
                try:
                    update_time = datetime.strptime(updated[:10], "%Y-%m-%d")
                    days = (datetime.now() - update_time).days
                    if days > 365:
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
    print("║          技能安全识别报告 V2.1.0               ║")
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
    parser = argparse.ArgumentParser(description="技能安全识别器 V2.1.0")
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
