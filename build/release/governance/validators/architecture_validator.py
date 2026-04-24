"""架构一致性验证器 - V4.3.0

检查是否仍然只认六层，是否有旧层级术语重新混入主文档
"""

from typing import Dict, List
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import re

class ArchitectureValidator:
    """架构一致性验证器"""
    
    # 禁止的旧层级术语
    FORBIDDEN_TERMS = [
        "25层", "L10", "L11", "L12",
        "E0-E7", "E1-E7", "扩展层",
        "X0-X7", "商业层",
        "Y1-Y3", "运维层"
    ]
    
    # 允许的六层术语
    ALLOWED_LAYERS = [
        "L1", "L2", "L3", "L4", "L5", "L6",
        "Core", "Memory Context", "Orchestration", "Execution", "Governance", "Infrastructure"
    ]
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.violations: List[Dict] = []
    
    def validate(self) -> Dict:
        """执行验证"""
        self.violations = []
        
        # 检查主文档
        self._check_main_docs()
        
        # 检查引导模块
        self._check_guide()
        
        # 检查路由配置
        self._check_router()
        
        return {
            "valid": len(self.violations) == 0,
            "violations": self.violations,
            "checked_files": len(self.violations) + 10  # 估算
        }
    
    def _check_main_docs(self):
        """检查主文档"""
        main_docs = [
            "AGENTS.md", "README.md", "core/ARCHITECTURE.md"
        ]
        
        for doc in main_docs:
            doc_path = self.workspace / doc
            if doc_path.exists():
                content = doc_path.read_text()
                self._check_forbidden_terms(content, doc)
    
    def _check_guide(self):
        """检查引导模块"""
        guide_path = self.workspace / "guide/assistant_guide.py"
        if guide_path.exists():
            content = guide_path.read_text()
            self._check_forbidden_terms(content, "guide/assistant_guide.py")
    
    def _check_router(self):
        """检查路由配置"""
        router_files = list((self.workspace / "orchestration/router").glob("*.json"))
        for router_file in router_files:
            content = router_file.read_text()
            self._check_forbidden_terms(content, str(router_file.relative_to(self.workspace)))
    
    def _check_forbidden_terms(self, content: str, file_path: str):
        """检查禁止术语"""
        for term in self.FORBIDDEN_TERMS:
            if term in content:
                # 排除归档文件
                if "归档" in content[:500] or "历史兼容" in content[:500]:
                    continue
                
                self.violations.append({
                    "file": file_path,
                    "term": term,
                    "type": "forbidden_term"
                })
