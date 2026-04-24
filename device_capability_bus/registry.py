"""设备能力注册表"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class CapabilityCategory(Enum):
    """能力分类"""
    COMMUNICATION = "communication"
    SCHEDULE = "schedule"
    STORAGE = "storage"
    NOTIFICATION = "notification"
    APP_CONTROL = "app_control"
    SCREEN_VISION = "screen_vision"
    INPUT_CONTROL = "input_control"


class RiskLevel(Enum):
    """风险等级"""
    L0 = "L0"  # 查询、总结、解释 - 自动执行
    L1 = "L1"  # 轻写入 - 自动执行
    L2 = "L2"  # 短信、通知、批量 - 策略控制
    L3 = "L3"  # 删除、拨电话、重要修改 - 默认确认
    L4 = "L4"  # 支付、金融、账号、隐私 - 强确认
    BLOCKED = "BLOCKED"  # 违法、盗号、绕过反作弊 - 拒绝


@dataclass
class CapabilityDefinition:
    """能力定义"""
    capability_id: str
    name: str
    category: CapabilityCategory
    description: str
    risk_level: RiskLevel
    side_effecting: bool = False
    requires_auth: bool = False
    requires_confirmation: bool = False
    can_auto_run: bool = True
    can_dry_run: bool = True
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


class CapabilityRegistry:
    """能力注册表"""
    
    def __init__(self):
        self._capabilities: Dict[str, CapabilityDefinition] = {}
        self._register_builtin_capabilities()
    
    def _register_builtin_capabilities(self):
        """注册内置能力"""
        # Communication
        self.register(CapabilityDefinition(
            capability_id="communication.send_message",
            name="发送短信",
            category=CapabilityCategory.COMMUNICATION,
            description="发送短信到指定号码",
            risk_level=RiskLevel.L2,
            side_effecting=True,
            requires_auth=True,
            requires_confirmation=False,
        ))
        self.register(CapabilityDefinition(
            capability_id="communication.call_phone",
            name="拨打电话",
            category=CapabilityCategory.COMMUNICATION,
            description="拨打指定号码",
            risk_level=RiskLevel.L3,
            side_effecting=True,
            requires_auth=True,
            requires_confirmation=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="communication.contact_lookup",
            name="查询联系人",
            category=CapabilityCategory.COMMUNICATION,
            description="查询联系人信息",
            risk_level=RiskLevel.L0,
            side_effecting=False,
        ))
        
        # Schedule
        self.register(CapabilityDefinition(
            capability_id="schedule.create_calendar_event",
            name="创建日程",
            category=CapabilityCategory.SCHEDULE,
            description="创建日历事件",
            risk_level=RiskLevel.L1,
            side_effecting=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="schedule.update_calendar_event",
            name="更新日程",
            category=CapabilityCategory.SCHEDULE,
            description="更新日历事件",
            risk_level=RiskLevel.L1,
            side_effecting=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="schedule.delete_calendar_event",
            name="删除日程",
            category=CapabilityCategory.SCHEDULE,
            description="删除日历事件",
            risk_level=RiskLevel.L3,
            side_effecting=True,
            requires_confirmation=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="schedule.create_alarm",
            name="创建闹钟",
            category=CapabilityCategory.SCHEDULE,
            description="创建闹钟",
            risk_level=RiskLevel.L1,
            side_effecting=True,
        ))
        
        # Storage
        self.register(CapabilityDefinition(
            capability_id="storage.create_note",
            name="创建备忘录",
            category=CapabilityCategory.STORAGE,
            description="创建备忘录",
            risk_level=RiskLevel.L1,
            side_effecting=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="storage.update_note",
            name="更新备忘录",
            category=CapabilityCategory.STORAGE,
            description="更新备忘录",
            risk_level=RiskLevel.L1,
            side_effecting=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="storage.delete_note",
            name="删除备忘录",
            category=CapabilityCategory.STORAGE,
            description="删除备忘录",
            risk_level=RiskLevel.L3,
            side_effecting=True,
            requires_confirmation=True,
        ))
        
        # Notification
        self.register(CapabilityDefinition(
            capability_id="notification.push",
            name="推送通知",
            category=CapabilityCategory.NOTIFICATION,
            description="推送通知到负一屏",
            risk_level=RiskLevel.L2,
            side_effecting=True,
        ))
        
        # App Control
        self.register(CapabilityDefinition(
            capability_id="app_control.open_app",
            name="打开应用",
            category=CapabilityCategory.APP_CONTROL,
            description="打开指定应用",
            risk_level=RiskLevel.L1,
            side_effecting=True,
        ))
        
        # Screen Vision
        self.register(CapabilityDefinition(
            capability_id="screen_vision.screenshot",
            name="截屏",
            category=CapabilityCategory.SCREEN_VISION,
            description="截取屏幕",
            risk_level=RiskLevel.L0,
            side_effecting=False,
        ))
        self.register(CapabilityDefinition(
            capability_id="screen_vision.read_screen",
            name="读屏",
            category=CapabilityCategory.SCREEN_VISION,
            description="读取屏幕内容",
            risk_level=RiskLevel.L0,
            side_effecting=False,
        ))
        
        # Input Control
        self.register(CapabilityDefinition(
            capability_id="input_control.tap",
            name="点击",
            category=CapabilityCategory.INPUT_CONTROL,
            description="点击屏幕指定位置",
            risk_level=RiskLevel.L2,
            side_effecting=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="input_control.swipe",
            name="滑动",
            category=CapabilityCategory.INPUT_CONTROL,
            description="滑动屏幕",
            risk_level=RiskLevel.L2,
            side_effecting=True,
        ))
        self.register(CapabilityDefinition(
            capability_id="input_control.type_text",
            name="输入文本",
            category=CapabilityCategory.INPUT_CONTROL,
            description="输入文本",
            risk_level=RiskLevel.L2,
            side_effecting=True,
        ))
    
    def register(self, capability: CapabilityDefinition):
        """注册能力"""
        self._capabilities[capability.capability_id] = capability
    
    def get(self, capability_id: str) -> Optional[CapabilityDefinition]:
        """获取能力定义"""
        return self._capabilities.get(capability_id)
    
    def list_all(self) -> List[CapabilityDefinition]:
        """列出所有能力"""
        return list(self._capabilities.values())
    
    def list_by_category(self, category: CapabilityCategory) -> List[CapabilityDefinition]:
        """按分类列出能力"""
        return [c for c in self._capabilities.values() if c.category == category]
    
    def list_by_risk_level(self, risk_level: RiskLevel) -> List[CapabilityDefinition]:
        """按风险等级列出能力"""
        return [c for c in self._capabilities.values() if c.risk_level == risk_level]
