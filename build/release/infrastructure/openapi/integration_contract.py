#!/usr/bin/env python3
"""
开放接入契约中心 - V2.8.0

规范：
- 外部工具接入规范
- 第三方工作流接入规范
- 插件 / 技能 SDK 规范
- 输入输出契约
- 认证与授权规范
- 回调与事件规范
- 错误码规范
- 版本兼容规范
"""

import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class IntegrationType(Enum):
    TOOL = "tool"               # 外部工具
    WORKFLOW = "workflow"       # 第三方工作流
    PLUGIN = "plugin"           # 插件
    SDK = "sdk"                 # SDK

class ContractStatus(Enum):
    DRAFT = "draft"             # 草稿
    ACTIVE = "active"           # 激活
    DEPRECATED = "deprecated"   # 废弃
    REVOKED = "revoked"         # 撤销

class AuthMethod(Enum):
    API_KEY = "api_key"         # API密钥
    OAUTH2 = "oauth2"           # OAuth2
    JWT = "jwt"                 # JWT
    CERTIFICATE = "certificate" # 证书

@dataclass
class InputContract:
    """输入契约"""
    field_name: str
    field_type: str             # string, number, boolean, object, array
    required: bool
    default: Any
    validation: Dict            # 验证规则
    description: str

@dataclass
class OutputContract:
    """输出契约"""
    field_name: str
    field_type: str
    required: bool
    description: str

@dataclass
class ErrorContract:
    """错误契约"""
    error_code: str
    error_message: str
    http_status: int
    retryable: bool

@dataclass
class EventContract:
    """事件契约"""
    event_name: str
    event_type: str             # sync / async
    payload_schema: Dict
    callback_required: bool

@dataclass
class IntegrationContract:
    """集成契约"""
    contract_id: str
    name: str
    version: str
    integration_type: str
    status: str
    description: str
    inputs: List[Dict]          # InputContract 列表
    outputs: List[Dict]         # OutputContract 列表
    errors: List[Dict]          # ErrorContract 列表
    events: List[Dict]          # EventContract 列表
    auth_method: str
    auth_config: Dict
    rate_limit: Dict
    timeout_seconds: int
    retry_policy: Dict
    version_compatibility: List[str]
    created_at: str
    updated_at: str

@dataclass
class IntegrationInstance:
    """集成实例"""
    instance_id: str
    contract_id: str
    integrator: str             # 集成方
    tenant_id: str
    config: Dict
    status: str
    created_at: str
    last_used: Optional[str]

class OpenIntegrationContractHub:
    """开放接入契约中心"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.openapi_path = self.project_root / 'openapi'
        self.config_path = self.openapi_path / 'contracts.json'
        
        # 契约定义
        self.contracts: Dict[str, IntegrationContract] = {}
        
        # 集成实例
        self.instances: List[IntegrationInstance] = []
        
        # 错误码规范
        self.error_codes = self._init_error_codes()
        
        # 版本兼容规范
        self.version_rules = self._init_version_rules()
        
        self._init_default_contracts()
        self._load()
    
    def _init_error_codes(self) -> Dict[str, Dict]:
        """初始化错误码规范"""
        return {
            # 1xxx: 客户端错误
            "1000": {"message": "请求格式错误", "http_status": 400, "retryable": False},
            "1001": {"message": "缺少必需参数", "http_status": 400, "retryable": False},
            "1002": {"message": "参数类型错误", "http_status": 400, "retryable": False},
            "1003": {"message": "参数验证失败", "http_status": 400, "retryable": False},
            
            # 2xxx: 认证授权错误
            "2000": {"message": "认证失败", "http_status": 401, "retryable": False},
            "2001": {"message": "令牌过期", "http_status": 401, "retryable": True},
            "2002": {"message": "权限不足", "http_status": 403, "retryable": False},
            "2003": {"message": "访问被拒绝", "http_status": 403, "retryable": False},
            
            # 3xxx: 资源错误
            "3000": {"message": "资源不存在", "http_status": 404, "retryable": False},
            "3001": {"message": "资源已存在", "http_status": 409, "retryable": False},
            "3002": {"message": "资源已锁定", "http_status": 423, "retryable": True},
            
            # 4xxx: 业务错误
            "4000": {"message": "业务处理失败", "http_status": 422, "retryable": False},
            "4001": {"message": "工作流执行失败", "http_status": 422, "retryable": True},
            "4002": {"message": "任务超时", "http_status": 408, "retryable": True},
            
            # 5xxx: 系统错误
            "5000": {"message": "系统内部错误", "http_status": 500, "retryable": True},
            "5001": {"message": "服务不可用", "http_status": 503, "retryable": True},
            "5002": {"message": "网关超时", "http_status": 504, "retryable": True},
        }
    
    def _init_version_rules(self) -> Dict:
        """初始化版本兼容规范"""
        return {
            "compatibility_policy": "semantic_versioning",
            "breaking_change_rules": [
                "删除必需字段",
                "更改字段类型",
                "更改必需字段为可选",
                "更改错误码含义"
            ],
            "non_breaking_changes": [
                "添加可选字段",
                "添加新的错误码",
                "添加新的事件",
                "扩展枚举值"
            ],
            "deprecation_policy": {
                "notice_period_days": 90,
                "support_period_days": 180
            }
        }
    
    def _init_default_contracts(self):
        """初始化默认契约"""
        # 工具接入契约
        tool_contract = IntegrationContract(
            contract_id="contract_tool_v1",
            name="外部工具接入契约",
            version="1.0.0",
            integration_type=IntegrationType.TOOL.value,
            status=ContractStatus.ACTIVE.value,
            description="外部工具接入标准契约",
            inputs=[
                {"field_name": "action", "field_type": "string", "required": True, "default": None, "validation": {"min_length": 1}, "description": "操作类型"},
                {"field_name": "params", "field_type": "object", "required": False, "default": {}, "validation": {}, "description": "参数"},
            ],
            outputs=[
                {"field_name": "success", "field_type": "boolean", "required": True, "description": "是否成功"},
                {"field_name": "result", "field_type": "object", "required": False, "description": "结果"},
                {"field_name": "error", "field_type": "string", "required": False, "description": "错误信息"},
            ],
            errors=[
                {"error_code": "1000", "error_message": "请求格式错误", "http_status": 400, "retryable": False},
                {"error_code": "2000", "error_message": "认证失败", "http_status": 401, "retryable": False},
            ],
            events=[
                {"event_name": "on_complete", "event_type": "async", "payload_schema": {}, "callback_required": False},
                {"event_name": "on_error", "event_type": "async", "payload_schema": {}, "callback_required": True},
            ],
            auth_method=AuthMethod.API_KEY.value,
            auth_config={"header_name": "X-API-Key", "key_format": "prefix_random"},
            rate_limit={"requests_per_minute": 100, "burst": 20},
            timeout_seconds=30,
            retry_policy={"max_retries": 3, "backoff": "exponential", "base_delay_ms": 100},
            version_compatibility=["1.0.x"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # 工作流接入契约
        workflow_contract = IntegrationContract(
            contract_id="contract_workflow_v1",
            name="第三方工作流接入契约",
            version="1.0.0",
            integration_type=IntegrationType.WORKFLOW.value,
            status=ContractStatus.ACTIVE.value,
            description="第三方工作流接入标准契约",
            inputs=[
                {"field_name": "workflow_id", "field_type": "string", "required": True, "default": None, "validation": {}, "description": "工作流ID"},
                {"field_name": "inputs", "field_type": "object", "required": True, "default": None, "validation": {}, "description": "输入参数"},
            ],
            outputs=[
                {"field_name": "execution_id", "field_type": "string", "required": True, "description": "执行ID"},
                {"field_name": "status", "field_type": "string", "required": True, "description": "执行状态"},
                {"field_name": "outputs", "field_type": "object", "required": False, "description": "输出结果"},
            ],
            errors=[
                {"error_code": "4001", "error_message": "工作流执行失败", "http_status": 422, "retryable": True},
            ],
            events=[
                {"event_name": "on_start", "event_type": "sync", "payload_schema": {}, "callback_required": False},
                {"event_name": "on_step_complete", "event_type": "async", "payload_schema": {}, "callback_required": False},
                {"event_name": "on_complete", "event_type": "async", "payload_schema": {}, "callback_required": True},
            ],
            auth_method=AuthMethod.JWT.value,
            auth_config={"algorithm": "RS256", "issuer": "platform", "audience": "workflow"},
            rate_limit={"requests_per_minute": 50, "burst": 10},
            timeout_seconds=300,
            retry_policy={"max_retries": 2, "backoff": "linear", "base_delay_ms": 1000},
            version_compatibility=["1.0.x"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # 插件接入契约
        plugin_contract = IntegrationContract(
            contract_id="contract_plugin_v1",
            name="插件接入契约",
            version="1.0.0",
            integration_type=IntegrationType.PLUGIN.value,
            status=ContractStatus.ACTIVE.value,
            description="插件接入标准契约",
            inputs=[
                {"field_name": "plugin_id", "field_type": "string", "required": True, "default": None, "validation": {}, "description": "插件ID"},
                {"field_name": "action", "field_type": "string", "required": True, "default": None, "validation": {}, "description": "动作"},
                {"field_name": "args", "field_type": "object", "required": False, "default": {}, "validation": {}, "description": "参数"},
            ],
            outputs=[
                {"field_name": "result", "field_type": "string", "required": True, "description": "结果"},
            ],
            errors=[
                {"error_code": "1000", "error_message": "请求格式错误", "http_status": 400, "retryable": False},
            ],
            events=[
                {"event_name": "on_invoke", "event_type": "sync", "payload_schema": {}, "callback_required": False},
            ],
            auth_method=AuthMethod.API_KEY.value,
            auth_config={"header_name": "X-Plugin-Key", "key_format": "uuid"},
            rate_limit={"requests_per_minute": 200, "burst": 50},
            timeout_seconds=60,
            retry_policy={"max_retries": 1, "backoff": "none", "base_delay_ms": 0},
            version_compatibility=["1.0.x"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.contracts[tool_contract.contract_id] = tool_contract
        self.contracts[workflow_contract.contract_id] = workflow_contract
        self.contracts[plugin_contract.contract_id] = plugin_contract
    
    def _load(self):
        """加载契约"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for cid, contract in data.get("contracts", {}).items():
                self.contracts[cid] = IntegrationContract(**contract)
            
            self.instances = [IntegrationInstance(**i) for i in data.get("instances", [])]
    
    def _save(self):
        """保存契约"""
        self.openapi_path.mkdir(parents=True, exist_ok=True)
        data = {
            "contracts": {cid: asdict(c) for cid, c in self.contracts.items()},
            "instances": [asdict(i) for i in self.instances],
            "error_codes": self.error_codes,
            "version_rules": self.version_rules,
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def get_contract(self, contract_id: str) -> Optional[IntegrationContract]:
        """获取契约"""
        return self.contracts.get(contract_id)
    
    def list_contracts(self, integration_type: str = None,
                       status: str = None) -> List[IntegrationContract]:
        """列出契约"""
        contracts = list(self.contracts.values())
        
        if integration_type:
            contracts = [c for c in contracts if c.integration_type == integration_type]
        if status:
            contracts = [c for c in contracts if c.status == status]
        
        return contracts
    
    def create_contract(self, name: str, integration_type: str,
                        description: str, inputs: List[Dict],
                        outputs: List[Dict], errors: List[Dict] = None,
                        events: List[Dict] = None, auth_method: str = "api_key",
                        timeout_seconds: int = 30) -> IntegrationContract:
        """创建契约"""
        contract_id = f"contract_{integration_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        contract = IntegrationContract(
            contract_id=contract_id,
            name=name,
            version="1.0.0",
            integration_type=integration_type,
            status=ContractStatus.DRAFT.value,
            description=description,
            inputs=inputs,
            outputs=outputs,
            errors=errors or [],
            events=events or [],
            auth_method=auth_method,
            auth_config={},
            rate_limit={"requests_per_minute": 100},
            timeout_seconds=timeout_seconds,
            retry_policy={"max_retries": 3},
            version_compatibility=["1.0.x"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.contracts[contract_id] = contract
        self._save()
        
        return contract
    
    def validate_input(self, contract_id: str, input_data: Dict) -> tuple:
        """验证输入"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False, "契约不存在"
        
        # 检查必需字段
        for input_def in contract.inputs:
            if input_def.get("required", False):
                field_name = input_def["field_name"]
                if field_name not in input_data or input_data[field_name] is None:
                    return False, f"缺少必需字段: {field_name}"
        
        return True, "验证通过"
    
    def validate_output(self, contract_id: str, output_data: Dict) -> tuple:
        """验证输出"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False, "契约不存在"
        
        # 检查必需字段
        for output_def in contract.outputs:
            if output_def.get("required", False):
                field_name = output_def["field_name"]
                if field_name not in output_data:
                    return False, f"输出缺少必需字段: {field_name}"
        
        return True, "验证通过"
    
    def register_instance(self, contract_id: str, integrator: str,
                          tenant_id: str, config: Dict) -> IntegrationInstance:
        """注册集成实例"""
        instance = IntegrationInstance(
            instance_id=f"inst_{contract_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            contract_id=contract_id,
            integrator=integrator,
            tenant_id=tenant_id,
            config=config,
            status="active",
            created_at=datetime.now().isoformat(),
            last_used=None
        )
        
        self.instances.append(instance)
        self._save()
        
        return instance
    
    def get_error_info(self, error_code: str) -> Optional[Dict]:
        """获取错误信息"""
        return self.error_codes.get(error_code)
    
    def check_version_compatibility(self, contract_id: str, version: str) -> tuple:
        """检查版本兼容性"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False, "契约不存在"
        
        # 简化实现：检查主版本号
        contract_major = contract.version.split('.')[0]
        request_major = version.split('.')[0]
        
        if contract_major != request_major:
            return False, f"主版本不兼容: {version} vs {contract.version}"
        
        return True, "版本兼容"
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 开放接入契约报告",
            "",
            "## 契约列表",
            ""
        ]
        
        for contract in self.contracts.values():
            status = "✅" if contract.status == ContractStatus.ACTIVE.value else "📝"
            lines.append(f"### {status} {contract.name} (v{contract.version})")
            lines.append(f"- 类型: {contract.integration_type}")
            lines.append(f"- 认证: {contract.auth_method}")
            lines.append(f"- 超时: {contract.timeout_seconds}s")
            lines.append(f"- 输入字段: {len(contract.inputs)}")
            lines.append(f"- 输出字段: {len(contract.outputs)}")
            lines.append("")
        
        lines.extend([
            "## 集成实例",
            ""
        ])
        
        for instance in self.instances[-10:]:
            lines.append(f"- [{instance.contract_id}] {instance.integrator} ({instance.status})")
        
        return "\n".join(lines)

# 全局实例
_contract_hub = None

def get_contract_hub() -> OpenIntegrationContractHub:
    global _contract_hub
    if _contract_hub is None:
        _contract_hub = OpenIntegrationContractHub()
    return _contract_hub
