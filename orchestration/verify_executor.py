#!/usr/bin/env python3
"""真实验证器 - V1.0.0

不再占位成功，必须有证据才能通过。
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # orchestration/ 的父目录


@dataclass
class VerifyResult:
    """验证结果"""
    status: str  # success / failed
    completed_items: List[str]
    failed_items: List[str]
    evidence: Dict[str, Any]
    raw_result: Dict[str, Any]


class VerifyExecutor:
    """真实验证器"""
    
    def __init__(self):
        self.project_root = Path(str(PROJECT_ROOT))
    
    def verify(self, execution_results: Dict[str, Any], task_type: str) -> VerifyResult:
        """
        验证执行结果
        
        Args:
            execution_results: 执行结果字典
            task_type: 任务类型 (file / db / message / tool_call)
        
        Returns:
            VerifyResult
        """
        completed_items = []
        failed_items = []
        evidence = {
            "files": [],
            "db_records": [],
            "messages": [],
            "tool_calls": [],
            "extra": {}
        }
        
        for task_id, result in execution_results.items():
            if not isinstance(result, dict):
                failed_items.append(f"{task_id}: 结果格式错误")
                continue
            
            # 检查是否成功
            success = result.get("success", False)
            
            if not success:
                error = result.get("error", {})
                if isinstance(error, dict):
                    failed_items.append(f"{task_id}: {error.get('message', '执行失败')}")
                else:
                    failed_items.append(f"{task_id}: {str(error)}")
                continue
            
            # 提取证据
            result_evidence = result.get("evidence", {})
            
            # 文件证据
            files = result_evidence.get("files", [])
            if not files:
                # 尝试从 result 直接提取
                if "file_path" in result:
                    files = [{"path": result["file_path"], "exists": False}]
                elif "output_file" in result:
                    files = [{"path": result["output_file"], "exists": False}]
            
            # 验证文件是否存在
            for file_info in files:
                if isinstance(file_info, dict):
                    path = file_info.get("path", "")
                else:
                    path = str(file_info)
                
                exists = os.path.exists(path) if path else False
                evidence["files"].append({
                    "path": path,
                    "exists": exists,
                    "verified": exists
                })
                
                if exists:
                    completed_items.append(f"文件已生成: {path}")
                else:
                    failed_items.append(f"文件不存在: {path}")
            
            # 数据库记录证据
            db_records = result_evidence.get("db_records", [])
            if not db_records:
                if "record_id" in result:
                    db_records = [{"id": result["record_id"], "table": result.get("table", "unknown")}]
                elif "task_id" in result and "tasks" in task_id:
                    db_records = [{"id": result["task_id"], "table": "tasks"}]
            
            for record in db_records:
                if isinstance(record, dict):
                    record_id = record.get("id", "")
                    table = record.get("table", "unknown")
                else:
                    record_id = str(record)
                    table = "unknown"
                
                evidence["db_records"].append({
                    "id": record_id,
                    "table": table,
                    "verified": bool(record_id)
                })
                
                if record_id:
                    completed_items.append(f"记录已写入: {table}.{record_id}")
            
            # 消息证据
            messages = result_evidence.get("messages", [])
            if not messages and "message_id" in result:
                messages = [{"id": result["message_id"], "channel": result.get("channel", "unknown")}]
            
            for msg in messages:
                if isinstance(msg, dict):
                    msg_id = msg.get("id", "")
                    channel = msg.get("channel", "unknown")
                else:
                    msg_id = str(msg)
                    channel = "unknown"
                
                evidence["messages"].append({
                    "id": msg_id,
                    "channel": channel,
                    "verified": bool(msg_id)
                })
                
                if msg_id:
                    completed_items.append(f"消息已发送: {channel}/{msg_id}")
            
            # 工具调用证据
            tool_calls = result_evidence.get("tool_calls", [])
            if not tool_calls and "tool_call_id" in result:
                tool_calls = [{"id": result["tool_call_id"], "tool": result.get("tool", "unknown")}]
            
            for call in tool_calls:
                if isinstance(call, dict):
                    call_id = call.get("id", "")
                    tool = call.get("tool", "unknown")
                else:
                    call_id = str(call)
                    tool = "unknown"
                
                evidence["tool_calls"].append({
                    "id": call_id,
                    "tool": tool,
                    "verified": bool(call_id)
                })
                
                if call_id:
                    completed_items.append(f"工具已调用: {tool}")
            
            # 额外证据
            extra = result_evidence.get("extra", {})
            if extra:
                evidence["extra"].update(extra)
            
            # 如果没有任何证据，标记为失败
            if not any([evidence["files"], evidence["db_records"], evidence["messages"], evidence["tool_calls"]]):
                # 检查是否有内容证据
                content = result.get("content") or result.get("text") or result.get("data", {}).get("content")
                if content:
                    evidence["extra"]["content_length"] = len(content) if isinstance(content, str) else len(str(content))
                    completed_items.append(f"内容已生成: {evidence['extra']['content_length']} 字符")
                else:
                    failed_items.append(f"{task_id}: 无有效证据")
        
        # 判断整体状态
        has_evidence = any([
            evidence["files"],
            evidence["db_records"],
            evidence["messages"],
            evidence["tool_calls"],
            evidence["extra"]
        ])
        
        if failed_items or not has_evidence:
            status = "failed"
        elif completed_items:
            status = "success"
        else:
            status = "failed"
        
        return VerifyResult(
            status=status,
            completed_items=completed_items,
            failed_items=failed_items,
            evidence=evidence,
            raw_result=execution_results
        )
    
    def has_evidence(self, evidence: Dict[str, Any]) -> bool:
        """检查是否有有效证据"""
        return any([
            evidence.get("files"),
            evidence.get("db_records"),
            evidence.get("messages"),
            evidence.get("tool_calls"),
            evidence.get("extra")
        ])


# 全局实例
_verify_executor: Optional[VerifyExecutor] = None

def get_verify_executor() -> VerifyExecutor:
    """获取全局验证器"""
    global _verify_executor
    if _verify_executor is None:
        _verify_executor = VerifyExecutor()
    return _verify_executor

def verify_execution(results: Dict[str, Any], task_type: str = "general") -> VerifyResult:
    """验证执行结果（便捷函数）"""
    return get_verify_executor().verify(results, task_type)
