#!/usr/bin/env python3
"""
LLM Client - LLM 客户端封装
支持用户自定义 LLM 提供商
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.openclaw/workspace/skills/llm-memory-integration/config/llm_config.json")

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"配置文件加载失败: {e}")
    return {}

class LLMClient:
    """LLM 客户端 - 支持多种提供商"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 LLM 客户端
        
        Args:
            config: 配置字典，如果为 None 则从配置文件加载
        """
        if config is None:
            config = load_config()
        
        llm_config = config.get("llm", {})
        
        # 从配置读取，如果没有则使用环境变量
        self.base_url = llm_config.get("base_url") or os.environ.get("LLM_BASE_URL", "")
        self.api_key = llm_config.get("api_key") or os.environ.get("LLM_API_KEY", "")
        self.model = llm_config.get("model") or os.environ.get("LLM_MODEL", "gpt-4")
        self.max_tokens = llm_config.get("max_tokens", 150)
        self.temperature = llm_config.get("temperature", 0.5)
        self.provider = llm_config.get("provider", "openai-compatible")
        
        # 输入验证
        if self.base_url and len(self.base_url) > 2048:
            raise ValueError("base_url 过长")
        if self.api_key and len(self.api_key) > 256:
            raise ValueError("api_key 过长")
        if self.model and len(self.model) > 100:
            raise ValueError("model 名称过长")
        
        if not self.api_key:
            print("警告: 未配置 LLM API 密钥，请设置配置文件或环境变量 LLM_API_KEY")
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Optional[str]:
        """
        调用 LLM 进行对话
        
        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
            max_tokens: 最大输出 token 数
            temperature: 温度参数
        
        Returns:
            模型回复文本，失败返回 None
        """
        if not self.api_key:
            return None
        
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0].get('message', {}).get('content', '')
                return None
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP 错误: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL 错误: {e.reason}")
            return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def analyze_conversation(self, conversation: str, task: str = "extract_preferences") -> Dict[str, Any]:
        """
        分析对话内容
        
        Args:
            conversation: 对话文本
            task: 分析任务类型
        
        Returns:
            分析结果字典
        """
        prompts = {
            "extract_preferences": """请分析以下对话，提取用户的偏好、习惯和特征。

对话内容:
{conversation}

请以 JSON 格式返回结果，包含以下字段:
{{
    "preferences": ["偏好1", "偏好2", ...],
    "habits": ["习惯1", "习惯2", ...],
    "characteristics": ["特征1", "特征2", ...],
    "summary": "一句话总结"
}}

只返回 JSON，不要其他内容。""",

            "extract_scene": """请分析以下对话，识别场景边界和主题。

对话内容:
{conversation}

请以 JSON 格式返回结果，包含以下字段:
{{
    "scene_name": "场景名称",
    "scene_type": "配置/任务/讨论/其他",
    "key_points": ["要点1", "要点2", ...],
    "participants": ["参与者1", "参与者2", ...],
    "outcome": "结果描述"
}}

只返回 JSON，不要其他内容。""",

            "summarize": """请总结以下对话内容。

对话内容:
{conversation}

请以 JSON 格式返回结果，包含以下字段:
{{
    "summary": "一句话总结",
    "key_topics": ["主题1", "主题2", ...],
    "decisions": ["决策1", "决策2", ...],
    "action_items": ["待办1", "待办2", ...]
}}

只返回 JSON，不要其他内容。"""
        }
        
        prompt = prompts.get(task, prompts["summarize"]).format(conversation=conversation)
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, max_tokens=1000, temperature=0.3)
        
        if response:
            try:
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                return json.loads(response)
            except json.JSONDecodeError as e:
                return {"raw_response": response, "error": f"JSON 解析失败: {e}"}
        else:
            return {"error": "API 调用失败或未配置"}


# 兼容旧代码
GLM5Client = LLMClient


def main():
    """测试函数"""
    client = LLMClient()
    
    if not client.api_key:
        print("请先配置 LLM API 密钥:")
        print(f"1. 复制配置示例: cp ~/.openclaw/workspace/skills/llm-memory-integration/config/llm_config.example.json {CONFIG_PATH}")
        print("2. 编辑配置文件，填入您的 API 密钥")
        return
    
    print("=== 测试基本对话 ===")
    response = client.chat([{"role": "user", "content": "你好，请用一句话介绍自己"}])
    print(f"回复: {response}")


if __name__ == "__main__":
    main()
