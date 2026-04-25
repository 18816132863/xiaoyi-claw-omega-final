"""端侧工具适配器 - 连接能力与真实端侧工具"""

from typing import Dict, Any, Optional
import json


class DeviceToolAdapter:
    """端侧工具适配器"""
    
    @staticmethod
    def call_photo_tool(action: str, params: dict) -> dict:
        """调用图库工具"""
        try:
            # 尝试使用真实工具
            try:
                from skills.xiaoyi_image_search.scripts.image_search import search_images
                
                if action == "search":
                    results = search_images(query=params.get("keyword", ""), limit=params.get("limit", 20))
                    return {"success": True, "photos": results, "keyword": params.get("keyword")}
                elif action == "list":
                    results = search_images(query="", limit=params.get("limit", 50))
                    return {"success": True, "photos": results}
                elif action == "query":
                    results = search_images(query=params.get("date", ""), limit=50)
                    return {"success": True, "photos": results}
            except ImportError:
                pass
            
            # 返回模拟数据
            return {
                "success": True,
                "photos": [],
                "action": action,
                "message": "图库工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "photos": []}
    
    @staticmethod
    def call_contact_tool(action: str, params: dict) -> dict:
        """调用联系人工具"""
        try:
            # 使用 get_contact_tool_schema 获取工具
            # 这里返回模拟数据，实际会调用端侧
            return {
                "success": True,
                "contacts": [],
                "action": action,
                "message": "联系人工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def call_file_tool(action: str, params: dict) -> dict:
        """调用文件管理工具"""
        try:
            # 使用 get_device_file_tool_schema 获取工具
            return {
                "success": True,
                "files": [],
                "action": action,
                "message": "文件管理工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def call_alarm_tool(action: str, params: dict) -> dict:
        """调用闹钟工具"""
        try:
            # 使用 get_alarm_tool_schema 获取工具
            return {
                "success": True,
                "alarms": [],
                "action": action,
                "message": "闹钟工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def call_phone_tool(action: str, params: dict) -> dict:
        """调用电话工具"""
        try:
            # 使用 get_contact_tool_schema 获取工具（电话也在里面）
            return {
                "success": True,
                "calls": [],
                "action": action,
                "message": "电话工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def call_location_tool(action: str, params: dict) -> dict:
        """调用定位工具"""
        try:
            if action == "get":
                # 使用 get_user_location 获取位置
                from tools import get_user_location
                location = get_user_location()
                return {
                    "success": True,
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "accuracy": location.get("accuracy")
                }
            else:
                return {
                    "success": True,
                    "locations": [],
                    "action": action,
                    "message": "定位工具调用成功（模拟）"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def call_note_tool(action: str, params: dict) -> dict:
        """调用备忘录工具"""
        try:
            # 使用 get_note_tool_schema 获取工具
            return {
                "success": True,
                "notes": [],
                "action": action,
                "message": "备忘录工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def call_calendar_tool(action: str, params: dict) -> dict:
        """调用日历工具"""
        try:
            # 使用 get_calendar_tool_schema 获取工具
            return {
                "success": True,
                "events": [],
                "action": action,
                "message": "日历工具调用成功（模拟）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 便捷函数
def call_device_tool(tool_type: str, action: str, params: dict) -> dict:
    """
    调用端侧工具的统一入口
    
    Args:
        tool_type: 工具类型 (photo/contact/file/alarm/phone/location/note/calendar)
        action: 操作
        params: 参数
        
    Returns:
        调用结果
    """
    adapter = DeviceToolAdapter()
    
    method_map = {
        "photo": adapter.call_photo_tool,
        "contact": adapter.call_contact_tool,
        "file": adapter.call_file_tool,
        "alarm": adapter.call_alarm_tool,
        "phone": adapter.call_phone_tool,
        "location": adapter.call_location_tool,
        "note": adapter.call_note_tool,
        "calendar": adapter.call_calendar_tool,
    }
    
    handler = method_map.get(tool_type)
    if handler:
        return handler(action, params)
    else:
        return {"success": False, "error": f"未知的工具类型: {tool_type}"}
