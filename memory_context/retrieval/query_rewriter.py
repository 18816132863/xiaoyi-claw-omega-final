"""
Query Rewriter - 查询重写器
负责优化和扩展检索查询
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


@dataclass
class RewriteResult:
    """重写结果"""
    original_query: str
    rewritten_query: str
    rewrite_type: str
    reason: str
    expansions: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_query": self.original_query,
            "rewritten_query": self.rewritten_query,
            "rewrite_type": self.rewrite_type,
            "reason": self.reason,
            "expansions": self.expansions,
            "synonyms": self.synonyms,
            "timestamp": self.timestamp
        }


class QueryRewriter:
    """
    查询重写器

    职责：
    - 扩展查询词
    - 添加同义词
    - 优化查询结构
    - 处理模糊匹配
    """

    def __init__(self):
        self._synonym_map: Dict[str, List[str]] = {
            "架构": ["architecture", "结构", "设计"],
            "检查": ["check", "验证", "审查", "检测"],
            "完整性": ["integrity", "完整", "一致"],
            "代码": ["code", "源码", "程序"],
            "测试": ["test", "测试用例", "单元测试"],
            "文档": ["document", "文档", "说明"],
            "配置": ["config", "配置", "设置"],
            "错误": ["error", "异常", "bug", "问题"],
            "性能": ["performance", "效率", "速度"],
            "安全": ["security", "安全", "漏洞"],
        }

        self._expansion_rules: List[Dict[str, Any]] = [
            {
                "pattern": r"检查(.*)完整性",
                "expansions": ["{0}架构", "{0}结构", "{0}设计"],
                "type": "integrity_check"
            },
            {
                "pattern": r"分析(.*)",
                "expansions": ["{0}报告", "{0}统计", "{0}趋势"],
                "type": "analysis"
            }
        ]

    def rewrite(
        self,
        query: str,
        context: Dict[str, Any] = None,
        profile: str = "default"
    ) -> RewriteResult:
        """
        重写查询

        Args:
            query: 原始查询
            context: 上下文信息
            profile: 执行配置

        Returns:
            RewriteResult
        """
        original = query
        expansions = []
        synonyms = []
        rewrite_type = "none"
        reason = "No rewrite needed"

        # 1. 同义词扩展
        rewritten, found_synonyms = self._expand_synonyms(query)
        if found_synonyms:
            synonyms = found_synonyms
            rewrite_type = "synonym_expansion"
            reason = f"Added {len(synonyms)} synonyms"

        # 2. 模式扩展
        pattern_expansions = self._apply_expansion_rules(query)
        if pattern_expansions:
            expansions.extend(pattern_expansions)
            rewrite_type = "pattern_expansion"
            reason = f"Applied pattern expansion"

        # 3. 上下文增强
        if context:
            context_terms = self._extract_context_terms(context)
            if context_terms:
                expansions.extend(context_terms)
                if rewrite_type == "none":
                    rewrite_type = "context_enhancement"
                    reason = "Added context terms"

        # 4. 构建最终查询
        if expansions:
            rewritten = f"{rewritten} {' '.join(expansions[:3])}"

        return RewriteResult(
            original_query=original,
            rewritten_query=rewritten,
            rewrite_type=rewrite_type,
            reason=reason,
            expansions=expansions,
            synonyms=synonyms
        )

    def _expand_synonyms(self, query: str) -> tuple[str, List[str]]:
        """扩展同义词"""
        synonyms = []
        rewritten = query

        for term, syns in self._synonym_map.items():
            if term in query:
                synonyms.extend(syns[:2])  # 每个词最多加 2 个同义词

        return rewritten, synonyms

    def _apply_expansion_rules(self, query: str) -> List[str]:
        """应用扩展规则"""
        expansions = []

        for rule in self._expansion_rules:
            match = re.search(rule["pattern"], query)
            if match:
                captured = match.group(1) if match.groups() else ""
                for exp_template in rule["expansions"]:
                    try:
                        expansion = exp_template.format(captured)
                        expansions.append(expansion)
                    except (IndexError, KeyError):
                        pass

        return expansions

    def _extract_context_terms(self, context: Dict[str, Any]) -> List[str]:
        """从上下文提取关键词"""
        terms = []

        # 从任务元数据提取
        task_meta = context.get("task_meta", {})
        if "intent" in task_meta:
            terms.append(task_meta["intent"])

        # 从历史提取
        history = context.get("history", [])
        for item in history[-3:]:  # 最近 3 条
            if isinstance(item, dict) and "content" in item:
                terms.append(item["content"][:20])

        return terms[:5]  # 最多 5 个

    def add_synonyms(self, term: str, synonyms: List[str]):
        """添加同义词"""
        if term not in self._synonym_map:
            self._synonym_map[term] = []
        self._synonym_map[term].extend(synonyms)

    def add_expansion_rule(self, pattern: str, expansions: List[str], rule_type: str):
        """添加扩展规则"""
        self._expansion_rules.append({
            "pattern": pattern,
            "expansions": expansions,
            "type": rule_type
        })


# 全局单例
_query_rewriter = None


def get_query_rewriter() -> QueryRewriter:
    """获取查询重写器单例"""
    global _query_rewriter
    if _query_rewriter is None:
        _query_rewriter = QueryRewriter()
    return _query_rewriter
