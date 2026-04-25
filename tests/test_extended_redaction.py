"""
测试扩展脱敏规则
"""

import pytest
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRedactValue:
    """测试值脱敏"""
    
    def test_redact_phone_number(self):
        """测试手机号脱敏"""
        from scripts.invocation_audit_cli import redact_value
        
        result = redact_value("13800138000")
        assert result == "138****8000"
    
    def test_redact_short_phone(self):
        """测试短号码"""
        from scripts.invocation_audit_cli import redact_value
        
        result = redact_value("123")
        assert result == "123"
    
    def test_redact_long_content(self):
        """测试长内容截断"""
        from scripts.invocation_audit_cli import redact_value
        
        result = redact_value("这是一条很长的短信内容用于测试脱敏功能应该会被截断", max_length=20)
        assert "..." in result
    
    def test_redact_short_content(self):
        """测试短内容不截断"""
        from scripts.invocation_audit_cli import redact_value
        
        result = redact_value("短内容", max_length=20)
        assert result == "短内容"


class TestRedactJsonString:
    """测试 JSON 脱敏"""
    
    def test_redact_json_phone(self):
        """测试 JSON 中手机号脱敏"""
        from scripts.invocation_audit_cli import redact_json_string
        
        json_str = json.dumps({"phone_number": "13800138000"})
        result = redact_json_string(json_str, ["phone_number"])
        
        data = json.loads(result)
        assert data["phone_number"] == "138****8000"
    
    def test_redact_json_content(self):
        """测试 JSON 中内容脱敏"""
        from scripts.invocation_audit_cli import redact_json_string
        
        json_str = json.dumps({"content": "这是一条很长的短信内容用于测试脱敏功能应该会被截断"})
        result = redact_json_string(json_str, ["content"])
        
        data = json.loads(result)
        assert "..." in data["content"]
    
    def test_redact_json_nested(self):
        """测试嵌套 JSON 脱敏"""
        from scripts.invocation_audit_cli import redact_json_string
        
        json_str = json.dumps({
            "request": {
                "phone_number": "13800138000"
            }
        })
        result = redact_json_string(json_str, ["phone_number"])
        
        data = json.loads(result)
        assert data["request"]["phone_number"] == "138****8000"
    
    def test_redact_invalid_json(self):
        """测试无效 JSON"""
        from scripts.invocation_audit_cli import redact_json_string
        
        result = redact_json_string("not a json", ["phone_number"])
        assert result == "not a json"


class TestRedactSensitiveExtended:
    """测试扩展脱敏规则"""
    
    def test_redact_request_json(self):
        """测试 request_json 脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "request_json": json.dumps({
                "phone_number": "13800138000",
                "content": "这是一条很长的短信内容用于测试脱敏功能应该会被截断"
            })
        }
        
        result = redact_sensitive(data)
        
        req = json.loads(result["request_json"])
        assert req["phone_number"] == "138****8000"
        assert "..." in req["content"]
    
    def test_redact_raw_result_json(self):
        """测试 raw_result_json 脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "raw_result_json": json.dumps({
                "phone": "13900139000",
                "message": "这是一条很长的消息内容用于测试脱敏功能应该会被截断"
            })
        }
        
        result = redact_sensitive(data)
        
        res = json.loads(result["raw_result_json"])
        assert res["phone"] == "139****9000"
        assert "..." in res["message"]
    
    def test_redact_confirm_note(self):
        """测试 confirm_note 脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "confirm_note": "这是一个非常长的确认备注，用于测试脱敏功能是否正常工作，应该会被截断，这里再加一些内容确保超过五十个字"
        }
        
        result = redact_sensitive(data)
        
        assert len(result["confirm_note"]) <= 53  # 50 + "..."
        assert "..." in result["confirm_note"]
    
    def test_redact_multiple_fields(self):
        """测试多字段脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "phone_number": "13800138000",
            "title": "这是一个很长的标题用于测试脱敏功能是否正常",
            "request_json": json.dumps({"phone": "13900139000"}),
            "raw_result_json": json.dumps({"content": "很长的结果内容用于测试脱敏"}),
            "confirm_note": "很长的确认备注内容用于测试脱敏功能是否正常工作"
        }
        
        result = redact_sensitive(data)
        
        assert result["phone_number"] == "138****8000"
        assert "..." in result["title"]
    
    def test_redact_preserves_other_fields(self):
        """测试保留其他字段"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "id": 123,
            "capability": "MESSAGE_SENDING",
            "normalized_status": "completed",
            "elapsed_ms": 1500,
        }
        
        result = redact_sensitive(data)
        
        assert result["id"] == 123
        assert result["capability"] == "MESSAGE_SENDING"
        assert result["normalized_status"] == "completed"
        assert result["elapsed_ms"] == 1500
    
    def test_redact_empty_data(self):
        """测试空数据"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        assert redact_sensitive(None) is None
        assert redact_sensitive({}) == {}


class TestRedactEdgeCases:
    """测试边界情况"""
    
    def test_redact_non_digit_phone(self):
        """测试非纯数字手机号"""
        from scripts.invocation_audit_cli import redact_value
        
        # 不是纯数字，不会被当作手机号
        result = redact_value("138abc8000")
        assert result == "138abc8000"
    
    def test_redact_exact_max_length(self):
        """测试刚好达到最大长度"""
        from scripts.invocation_audit_cli import redact_value
        
        # 刚好20个字符，不会被截断
        result = redact_value("abcdefghijklmnopqrst", max_length=20)
        assert result == "abcdefghijklmnopqrst"
    
    def test_redact_over_max_length(self):
        """测试超过最大长度"""
        from scripts.invocation_audit_cli import redact_value
        
        # 非纯数字的长字符串会被截断
        result = redact_value("abcdefghij12345678901", max_length=20)
        assert "..." in result
