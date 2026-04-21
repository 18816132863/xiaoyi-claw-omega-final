#!/usr/bin/env python3
"""真实总结器 - V1.0.0

不再返回空壳 internal completed，生成真实总结。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SummarizeResult:
    """总结结果"""
    status: str  # success / failed
    message: str  # 给用户看的总结
    completed_items: List[str]
    failed_items: List[str]
    evidence: Dict[str, Any]
    next_action: str


class SummarizeExecutor:
    """真实总结器"""
    
    def summarize(
        self,
        verify_result: Any,
        intent: str,
        execution_trace: List[Dict[str, Any]]
    ) -> SummarizeResult:
        """
        根据验证结果生成真实总结
        
        Args:
            verify_result: VerifyResult 对象
            intent: 任务意图
            execution_trace: 执行轨迹
        
        Returns:
            SummarizeResult
        """
        # 提取验证结果
        status = getattr(verify_result, "status", "failed")
        completed_items = getattr(verify_result, "completed_items", [])
        failed_items = getattr(verify_result, "failed_items", [])
        evidence = getattr(verify_result, "evidence", {})
        
        # 生成消息
        message = self._generate_message(status, intent, completed_items, failed_items, evidence)
        
        # 生成下一步
        next_action = self._suggest_next_action(status, intent, failed_items)
        
        return SummarizeResult(
            status=status,
            message=message,
            completed_items=completed_items,
            failed_items=failed_items,
            evidence=evidence,
            next_action=next_action
        )
    
    def _generate_message(
        self,
        status: str,
        intent: str,
        completed_items: List[str],
        failed_items: List[str],
        evidence: Dict[str, Any]
    ) -> str:
        """生成给用户看的完整消息"""
        lines = []
        
        # 执行结果
        if status == "success":
            lines.append(f"【执行结果】")
            lines.append(f"✅ {intent} 成功")
        else:
            lines.append(f"【执行结果】")
            lines.append(f"❌ {intent} 失败")
        
        # 完成项
        if completed_items:
            lines.append(f"\n【完成项】")
            for item in completed_items:
                lines.append(f"- {item}")
        
        # 未完成项
        if failed_items:
            lines.append(f"\n【未完成项】")
            for item in failed_items:
                lines.append(f"- {item}")
        
        # 证据
        verified_evidence = self._get_verified_evidence(evidence)
        if verified_evidence:
            lines.append(f"\n【证据】")
            for e in verified_evidence:
                lines.append(f"- {e}")
        
        return "\n".join(lines)
    
    def _get_verified_evidence(self, evidence: Dict[str, Any]) -> List[str]:
        """提取已验证的证据"""
        result = []
        
        # 文件证据
        for f in evidence.get("files", []):
            if f.get("verified") or f.get("exists"):
                result.append(f"文件: {f.get('path', 'unknown')}")
        
        # 数据库记录证据
        for r in evidence.get("db_records", []):
            if r.get("verified"):
                result.append(f"数据记录: {r.get('table', 'unknown')}.{r.get('id', 'unknown')}")
        
        # 消息证据
        for m in evidence.get("messages", []):
            if m.get("verified"):
                result.append(f"消息: {m.get('channel', 'unknown')}/{m.get('id', 'unknown')}")
        
        # 工具调用证据
        for t in evidence.get("tool_calls", []):
            if t.get("verified"):
                result.append(f"工具调用: {t.get('tool', 'unknown')}")
        
        # 额外证据
        extra = evidence.get("extra", {})
        if extra.get("content_length"):
            result.append(f"生成内容: {extra['content_length']} 字符")
        
        return result
    
    def _suggest_next_action(
        self,
        status: str,
        intent: str,
        failed_items: List[str]
    ) -> str:
        """建议下一步"""
        if status == "success":
            return "任务已完成，可以进行下一步操作"
        
        if not failed_items:
            return "请检查任务配置后重试"
        
        # 根据失败项建议
        for item in failed_items:
            if "文件不存在" in item:
                return "请检查文件路径是否正确"
            if "无有效证据" in item:
                return "请确认操作是否真正执行"
            if "执行失败" in item:
                return "请检查错误信息后重试"
        
        return "请检查失败项后重试"


# 全局实例
_summarize_executor: Optional[SummarizeExecutor] = None

def get_summarize_executor() -> SummarizeExecutor:
    """获取全局总结器"""
    global _summarize_executor
    if _summarize_executor is None:
        _summarize_executor = SummarizeExecutor()
    return _summarize_executor

def summarize_execution(verify_result: Any, intent: str, execution_trace: List[Dict] = None) -> SummarizeResult:
    """总结执行结果（便捷函数）"""
    return get_summarize_executor().summarize(verify_result, intent, execution_trace or [])
