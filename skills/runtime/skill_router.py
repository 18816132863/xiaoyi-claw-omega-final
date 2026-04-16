"""Skill router - routes skill execution requests."""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
import importlib
import os


@dataclass
class SkillExecutionContext:
    """Context for skill execution."""
    skill_id: str
    input_data: Dict
    profile: str = "default"
    timeout_seconds: int = 60
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SkillExecutionResult:
    """Result of skill execution."""
    skill_id: str
    success: bool
    output: Dict
    error: Optional[str] = None
    duration_ms: int = 0
    executed_at: datetime = None
    
    def __post_init__(self):
        if self.executed_at is None:
            self.executed_at = datetime.now()


class SkillRouter:
    """
    Routes skill execution requests to appropriate executors.
    
    Responsibilities:
    - Skill discovery and matching
    - Executor selection
    - Input validation
    - Output validation
    - Error handling
    """
    
    def __init__(self, registry=None, governance=None):
        self.registry = registry
        self.governance = governance
        self._executors: Dict[str, Any] = {}
        self._loaders: Dict[str, Any] = {}
    
    def register_executor(self, executor_type: str, executor):
        """Register an executor for a skill type."""
        self._executors[executor_type] = executor
    
    def register_loader(self, loader_type: str, loader):
        """Register a skill loader."""
        self._loaders[loader_type] = loader
    
    def route(self, skill_id: str, input_data: Dict, context: Dict = None) -> SkillExecutionResult:
        """
        Route a skill execution request.
        
        Args:
            skill_id: Skill to execute
            input_data: Input data for the skill
            context: Additional execution context
        
        Returns:
            SkillExecutionResult with output or error
        """
        start_time = datetime.now()
        
        # Get skill manifest
        manifest = self._get_manifest(skill_id)
        if not manifest:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=f"Skill not found: {skill_id}"
            )
        
        # Check governance
        if self.governance:
            allowed, reason = self.governance.check_skill_allowed(manifest, context)
            if not allowed:
                return SkillExecutionResult(
                    skill_id=skill_id,
                    success=False,
                    output={},
                    error=f"Skill not allowed: {reason}"
                )
        
        # Validate input
        validation_error = self._validate_input(manifest, input_data)
        if validation_error:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=f"Input validation failed: {validation_error}"
            )
        
        # Get executor
        executor = self._get_executor(manifest.executor_type)
        if not executor:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=f"No executor for type: {manifest.executor_type}"
            )
        
        # Execute
        try:
            output = executor.execute(manifest, input_data, context)
            
            # Validate output
            output_error = self._validate_output(manifest, output)
            if output_error:
                return SkillExecutionResult(
                    skill_id=skill_id,
                    success=False,
                    output=output,
                    error=f"Output validation failed: {output_error}"
                )
            
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return SkillExecutionResult(
                skill_id=skill_id,
                success=True,
                output=output,
                duration_ms=duration
            )
            
        except Exception as e:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=str(e)
            )
    
    def execute(self, skill_id: str, input_data: Dict, context: Dict = None) -> Dict:
        """
        Execute a skill and return output.
        
        Convenience method that raises on failure.
        """
        result = self.route(skill_id, input_data, context)
        if not result.success:
            raise RuntimeError(result.error)
        return result.output
    
    def discover(self, query: str, context: Dict = None) -> List[str]:
        """
        Discover skills matching a query.
        
        Returns:
            List of matching skill IDs
        """
        if not self.registry:
            return []
        
        # Search by name, description, tags
        matches = self.registry.search(query=query)
        
        # Filter by governance
        if self.governance:
            allowed = []
            for manifest in matches:
                ok, _ = self.governance.check_skill_allowed(manifest, context)
                if ok:
                    allowed.append(manifest.skill_id)
            return allowed
        
        return [m.skill_id for m in matches]
    
    def _get_manifest(self, skill_id: str):
        """Get skill manifest from registry."""
        if not self.registry:
            return None
        return self.registry.get(skill_id)
    
    def _get_executor(self, executor_type: str):
        """Get executor for a type."""
        return self._executors.get(executor_type)
    
    def _validate_input(self, manifest, input_data: Dict) -> Optional[str]:
        """Validate input against contract."""
        # TODO: Implement JSON schema validation
        return None
    
    def _validate_output(self, manifest, output: Dict) -> Optional[str]:
        """Validate output against contract."""
        # TODO: Implement JSON schema validation
        return None


class SkillExecutor:
    """Base class for skill executors."""
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """Execute a skill."""
        raise NotImplementedError


class SkillMdExecutor(SkillExecutor):
    """Executor for SKILL.md based skills."""
    
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """Execute a SKILL.md skill."""
        skill_path = manifest.entry_point or os.path.join(self.skills_dir, manifest.skill_id, "SKILL.md")
        
        if not os.path.exists(skill_path):
            raise FileNotFoundError(f"Skill file not found: {skill_path}")
        
        # Read skill content
        with open(skill_path, 'r') as f:
            content = f.read()
        
        # Return skill content for processing
        return {
            "skill_content": content,
            "input": input_data,
            "context": context
        }


class PythonExecutor(SkillExecutor):
    """Executor for Python-based skills."""
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """Execute a Python skill."""
        entry_point = manifest.entry_point
        
        if not entry_point:
            raise ValueError("No entry point specified")
        
        # Import and execute
        module_path, func_name = entry_point.rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        
        return func(input_data, context)
