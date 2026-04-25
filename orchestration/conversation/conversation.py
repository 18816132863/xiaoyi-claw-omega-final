#!/usr/bin/env python3
"""
多轮对话模块 (v5.0)
对话历史管理、上下文窗口、会话管理
"""

import numpy as np
from typing import List, Dict, Any, Optional
import time
import hashlib


class Message:
    """
    消息定义
    """
    
    def __init__(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        初始化消息
        
        Args:
            role: 角色（user/assistant/system）
            content: 内容
            metadata: 元数据
        """
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = time.time()
        self.message_id = hashlib.md5(f"{role}{content}{self.timestamp}".encode()).hexdigest()[:16]


class Conversation:
    """
    对话定义
    """
    
    def __init__(
        self,
        conversation_id: Optional[str] = None,
        max_history: int = 20,
        context_window: int = 4096
    ):
        """
        初始化对话
        
        Args:
            conversation_id: 对话 ID
            max_history: 最大历史消息数
            context_window: 上下文窗口大小（token）
        """
        self.conversation_id = conversation_id or hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        self.max_history = max_history
        self.context_window = context_window
        
        # 消息历史
        self.messages: List[Message] = []
        
        # 对话元数据
        self.metadata = {
            'created_at': time.time(),
            'updated_at': time.time(),
            'message_count': 0
        }
        
        print(f"对话初始化: {self.conversation_id}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> Message:
        """
        添加消息
        
        Args:
            role: 角色
            content: 内容
            metadata: 元数据
        
        Returns:
            Message: 消息对象
        """
        message = Message(role, content, metadata)
        self.messages.append(message)
        
        # 限制历史长度
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        
        # 更新元数据
        self.metadata['updated_at'] = time.time()
        self.metadata['message_count'] += 1
        
        return message
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取历史消息
        
        Args:
            limit: 返回数量
        
        Returns:
            List[Dict]: 消息列表
        """
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {
                'role': m.role,
                'content': m.content,
                'timestamp': m.timestamp,
                'message_id': m.message_id
            }
            for m in messages
        ]
    
    def get_context(self, max_tokens: Optional[int] = None) -> str:
        """
        获取上下文（压缩）
        
        Args:
            max_tokens: 最大 token 数
        
        Returns:
            str: 上下文文本
        """
        max_tokens = max_tokens or self.context_window
        
        # 简化实现：拼接所有消息
        # 实际实现应使用 token 计数和压缩
        context_parts = []
        current_tokens = 0
        
        for message in reversed(self.messages):
            # 估算 token 数（简化）
            tokens = len(message.content) // 4
            
            if current_tokens + tokens > max_tokens:
                break
            
            context_parts.insert(0, f"{message.role}: {message.content}")
            current_tokens += tokens
        
        return "\n".join(context_parts)
    
    def clear(self):
        """清空对话"""
        self.messages = []
        self.metadata['updated_at'] = time.time()
        self.metadata['message_count'] = 0


class ConversationManager:
    """
    对话管理器
    """
    
    def __init__(
        self,
        max_conversations: int = 100,
        max_history_per_conversation: int = 20
    ):
        """
        初始化对话管理器
        
        Args:
            max_conversations: 最大对话数
            max_history_per_conversation: 每个对话的最大历史数
        """
        self.max_conversations = max_conversations
        self.max_history = max_history_per_conversation
        
        # 对话存储
        self.conversations: Dict[str, Conversation] = {}
        
        # 用户-对话映射
        self.user_conversations: Dict[str, str] = {}
        
        print(f"对话管理器初始化:")
        print(f"  最大对话数: {max_conversations}")
        print(f"  每对话最大历史: {max_history_per_conversation}")
    
    def create_conversation(
        self,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Conversation:
        """
        创建新对话
        
        Args:
            user_id: 用户 ID
            system_prompt: 系统提示
        
        Returns:
            Conversation: 对话对象
        """
        conversation = Conversation(max_history=self.max_history)
        
        # 添加系统提示
        if system_prompt:
            conversation.add_message('system', system_prompt)
        
        # 存储
        self.conversations[conversation.conversation_id] = conversation
        
        # 用户映射
        if user_id:
            self.user_conversations[user_id] = conversation.conversation_id
        
        # 清理旧对话
        if len(self.conversations) > self.max_conversations:
            self._cleanup_old_conversations()
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        获取对话
        
        Args:
            conversation_id: 对话 ID
        
        Returns:
            Optional[Conversation]: 对话对象
        """
        return self.conversations.get(conversation_id)
    
    def get_user_conversation(self, user_id: str) -> Optional[Conversation]:
        """
        获取用户对话
        
        Args:
            user_id: 用户 ID
        
        Returns:
            Optional[Conversation]: 对话对象
        """
        conversation_id = self.user_conversations.get(user_id)
        if conversation_id:
            return self.conversations.get(conversation_id)
        return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话 ID
        
        Returns:
            bool: 是否成功
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
            # 清理用户映射
            for user_id, conv_id in list(self.user_conversations.items()):
                if conv_id == conversation_id:
                    del self.user_conversations[user_id]
            
            return True
        return False
    
    def _cleanup_old_conversations(self):
        """清理旧对话"""
        # 按更新时间排序
        sorted_convs = sorted(
            self.conversations.items(),
            key=lambda x: x[1].metadata['updated_at']
        )
        
        # 删除最旧的
        for conv_id, _ in sorted_convs[:len(self.conversations) - self.max_conversations]:
            self.delete_conversation(conv_id)
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_messages = sum(
            conv.metadata['message_count']
            for conv in self.conversations.values()
        )
        
        return {
            'total_conversations': len(self.conversations),
            'total_messages': total_messages,
            'active_users': len(self.user_conversations)
        }


class MemoryCompressor:
    """
    记忆压缩器
    压缩对话历史以节省上下文空间
    """
    
    def __init__(self, compression_ratio: float = 0.5):
        """
        初始化记忆压缩器
        
        Args:
            compression_ratio: 压缩比例
        """
        self.compression_ratio = compression_ratio
    
    def compress(self, messages: List[Message]) -> str:
        """
        压缩消息
        
        Args:
            messages: 消息列表
        
        Returns:
            str: 压缩后的摘要
        """
        # 简化实现：提取关键信息
        # 实际实现应使用 LLM 生成摘要
        key_points = []
        
        for msg in messages:
            if msg.role == 'user':
                # 提取用户问题
                key_points.append(f"用户问: {msg.content[:50]}...")
            elif msg.role == 'assistant':
                # 提取回答要点
                key_points.append(f"回答: {msg.content[:50]}...")
        
        return "\n".join(key_points)


if __name__ == "__main__":
    # 测试
    print("=== 多轮对话测试 ===")
    
    manager = ConversationManager()
    
    # 创建对话
    conv = manager.create_conversation(user_id="user_001", system_prompt="你是一个助手")
    
    # 添加消息
    conv.add_message("user", "你好")
    conv.add_message("assistant", "你好！有什么可以帮助你的？")
    conv.add_message("user", "介绍一下向量搜索")
    conv.add_message("assistant", "向量搜索是一种基于语义相似度的搜索方法...")
    
    # 获取历史
    history = conv.get_history()
    print(f"历史消息: {len(history)} 条")
    
    # 获取上下文
    context = conv.get_context(max_tokens=500)
    print(f"上下文长度: {len(context)} 字符")
    
    # 统计
    stats = manager.get_stats()
    print(f"统计: {stats}")
