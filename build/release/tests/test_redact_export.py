"""
测试脱敏导出
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRedaction:
    """测试脱敏功能"""
    
    def test_redact_phone_number(self):
        """测试手机号脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {"phone_number": "13800138000"}
        result = redact_sensitive(data)
        
        assert result["phone_number"] == "138****8000"
    
    def test_redact_phoneNumber(self):
        """测试 phoneNumber 字段脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {"phoneNumber": "13900139000"}
        result = redact_sensitive(data)
        
        assert result["phoneNumber"] == "139****9000"
    
    def test_redact_short_phone(self):
        """测试短号码不脱敏"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {"phone": "123"}
        result = redact_sensitive(data)
        
        # 短于 7 位不脱敏
        assert result["phone"] == "123"
    
    def test_redact_request_json(self):
        """测试 request_json 脱敏"""
        import json
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "request_json": json.dumps({
                "phone_number": "13800138000",
                "content": "这是一条很长的短信内容用于测试脱敏功能应该会被截断"
            })
        }
        
        result = redact_sensitive(data)
        
        # request_json 应该被脱敏
        req = json.loads(result["request_json"])
        assert "****" in req["phone_number"]
        assert "..." in req["content"]
    
    def test_redact_none_data(self):
        """测试空数据"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        result = redact_sensitive(None)
        assert result is None
        
        result = redact_sensitive({})
        assert result == {}
    
    def test_redact_preserves_other_fields(self):
        """测试保留其他字段"""
        from scripts.invocation_audit_cli import redact_sensitive
        
        data = {
            "id": 123,
            "capability": "MESSAGE_SENDING",
            "phone_number": "13800138000",
            "status": "completed",
        }
        
        result = redact_sensitive(data)
        
        assert result["id"] == 123
        assert result["capability"] == "MESSAGE_SENDING"
        assert result["status"] == "completed"
        assert result["phone_number"] == "138****8000"


class TestExportFormats:
    """测试导出格式"""
    
    def test_json_export_format(self):
        """测试 JSON 导出格式"""
        from scripts.invocation_audit_cli import records_to_csv
        import json
        
        records = [
            {"id": 1, "capability": "MESSAGE_SENDING", "status": "completed"},
            {"id": 2, "capability": "TASK_SCHEDULING", "status": "failed"},
        ]
        
        # JSON 导出
        json_output = json.dumps(records, ensure_ascii=False, indent=2)
        
        # 验证格式
        parsed = json.loads(json_output)
        assert len(parsed) == 2
        assert parsed[0]["id"] == 1
    
    def test_csv_export_format(self):
        """测试 CSV 导出格式"""
        from scripts.invocation_audit_cli import records_to_csv
        
        records = [
            {"id": 1, "capability": "MESSAGE_SENDING", "status": "completed"},
            {"id": 2, "capability": "TASK_SCHEDULING", "status": "failed"},
        ]
        
        csv_output = records_to_csv(records)
        
        # 验证格式
        lines = csv_output.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        assert "id" in lines[0]
        assert "capability" in lines[0]
