#!/usr/bin/env python3
"""
引导模块启动脚本
每次会话启动时自动调用
"""

from guide.assistant_guide import get_guide

def show_welcome():
    """显示欢迎消息（每次对话调用）"""
    guide = get_guide()
    return guide._get_welcome()

def show_quick_reference():
    """显示快速参考（每次对话调用）"""
    guide = get_guide()
    return guide.get_quick_reference()

def show_full_guide():
    """显示完整引导"""
    guide = get_guide()
    return guide.get_full_guide()

def show_help():
    """显示帮助"""
    return show_quick_reference()

def show_capabilities():
    """显示能力"""
    guide = get_guide()
    return guide._get_capabilities()

def show_skills():
    """显示技能"""
    guide = get_guide()
    return guide._get_skills_overview()

def show_workflows():
    """显示工作流"""
    guide = get_guide()
    return guide._get_workflows()

def show_commands():
    """显示命令"""
    guide = get_guide()
    return guide._get_commands()

def show_quick_codes():
    """显示快速代码"""
    guide = get_guide()
    return guide._get_quick_codes()

def show_tips():
    """显示技巧"""
    guide = get_guide()
    return guide._get_tips()

def show_recommendations():
    """显示推荐"""
    guide = get_guide()
    return guide._get_recommendations()

def get_skill_detail(skill_name: str):
    """获取技能详情"""
    guide = get_guide()
    return guide.get_skill_detail(skill_name)

def get_workflow_detail(workflow_name: str):
    """获取工作流详情"""
    guide = get_guide()
    return guide.get_workflow_detail(workflow_name)

def search_skills(keyword: str):
    """搜索技能"""
    guide = get_guide()
    return guide.search_skills(keyword)

def get_conversation_guide():
    """获取每次对话的引导内容"""
    guide = get_guide()
    return f"""{guide._get_welcome()}

{guide.get_quick_reference()}"""

# 启动时自动显示
if __name__ == "__main__":
    print(get_conversation_guide())

def get_smart_guide(user_input: str):
    """智能引导 - 根据用户输入自动匹配"""
    guide = get_guide()
    return guide.get_smart_response(user_input)

def detect_user_intent(user_input: str):
    """检测用户意图"""
    guide = get_guide()
    return guide.detect_intent(user_input)

def get_contextual_guide(user_input: str):
    """上下文相关引导"""
    guide = get_guide()
    return guide.get_contextual_guide(user_input)

def show_architecture():
    """显示架构完整功能"""
    guide = get_guide()
    return guide.get_architecture_guide()
