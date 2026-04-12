#!/usr/bin/env python3
"""
飞书长连接客户端 - V1.0.8

使用飞书官方 SDK 建立长连接，接收消息事件并回复
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 飞书 SDK
try:
    import lark_oapi as lark
    from lark_oapi.ws import Client as WsClient
    from lark_oapi.event.dispatcher_handler import EventDispatcherHandlerBuilder
    from lark_oapi.api.im.v1 import (
        CreateMessageRequest,
        CreateMessageRequestBody,
        CreateMessageRequestBodyBuilder
    )
except ImportError:
    print("请先安装飞书 SDK: pip install lark-oapi")
    sys.exit(1)

class FeishuLongPollClient:
    """飞书长连接客户端"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.ws_client = None
        self.api_client = None
    
    def init_api_client(self):
        """初始化 API 客户端"""
        self.api_client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.ERROR) \
            .build()
    
    def handle_message(self, event):
        """处理接收到的消息"""
        try:
            event_data = event.event if hasattr(event, 'event') else event.get("event", {})
            message = event_data.message if hasattr(event_data, 'message') else event_data.get("message", {})
            sender = event_data.sender if hasattr(event_data, 'sender') else event_data.get("sender", {})
            
            msg_type = message.message_type if hasattr(message, 'message_type') else message.get("message_type", "unknown")
            content = message.content if hasattr(message, 'content') else message.get("content", "")
            chat_id = message.chat_id if hasattr(message, 'chat_id') else message.get("chat_id", "")
            msg_id = message.message_id if hasattr(message, 'message_id') else message.get("message_id", "")
            
            sender_id_obj = sender.sender_id if hasattr(sender, 'sender_id') else sender.get("sender_id", {})
            sender_id = sender_id_obj.user_id if hasattr(sender_id_obj, 'user_id') else sender_id_obj.get("user_id", "unknown")
            
            print(f"\n📨 收到消息:")
            print(f"   类型: {msg_type}")
            print(f"   发送者: {sender_id}")
            print(f"   聊天ID: {chat_id}")
            print(f"   内容: {content[:100] if content else 'empty'}")
            
            self.save_message({
                "timestamp": datetime.now().isoformat(),
                "msg_id": msg_id,
                "msg_type": msg_type,
                "content": content,
                "chat_id": chat_id,
                "sender_id": sender_id
            })
            
            if msg_type == "text":
                self.reply_text(chat_id, "收到你的消息了！")
            
        except Exception as e:
            print(f"❌ 处理消息失败: {e}")
            import traceback
            traceback.print_exc()
    
    def save_message(self, msg: dict):
        """保存消息"""
        msg_file = Path.home() / ".openclaw" / "feishu_messages.json"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        
        messages = []
        if msg_file.exists():
            try:
                messages = json.load(open(msg_file, encoding='utf-8'))
            except:
                pass
        
        messages.append(msg)
        messages = messages[-100:]
        
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    def reply_text(self, chat_id: str, text: str):
        """回复文本消息"""
        try:
            req = CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type("text")
                    .content(json.dumps({"text": text}))
                    .build()) \
                .build()
            
            resp = self.api_client.im.v1.message.create(req)
            
            if resp.code == 0:
                print(f"✅ 已回复: {text}")
            else:
                print(f"❌ 回复失败: code={resp.code}, msg={resp.msg}")
                
        except Exception as e:
            print(f"❌ 回复消息异常: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """启动长连接"""
        print("🚀 启动飞书长连接服务...")
        print(f"   App ID: {self.app_id}")
        
        self.init_api_client()
        print("✅ API 客户端已初始化")
        
        def on_message(event):
            self.handle_message(event)
        
        event_handler = EventDispatcherHandlerBuilder(
            encrypt_key="",
            verification_token=""
        ).register_p2_im_message_receive_v1(on_message).build()
        
        self.ws_client = WsClient(
            app_id=self.app_id,
            app_secret=self.app_secret,
            event_handler=event_handler,
            log_level=lark.LogLevel.INFO
        )
        
        print("✅ 长连接服务已启动")
        print("   等待消息中... (按 Ctrl+C 停止)")
        
        try:
            self.ws_client.start()
        except KeyboardInterrupt:
            print("\n⏹️ 停止长连接服务")
            self.stop()
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        return 0
    
    def stop(self):
        """停止长连接"""
        if self.ws_client:
            try:
                self.ws_client.stop()
            except:
                pass
        print("⏹️ 长连接服务已停止")

def load_config() -> dict:
    """加载配置"""
    config_file = Path.home() / ".openclaw" / "channels" / "feishu.json"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return None
    
    try:
        return json.load(open(config_file, encoding='utf-8'))
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return None

def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║              飞书长连接服务 V1.0.8              ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    config = load_config()
    if not config:
        return 1
    
    app_id = config.get("appId")
    app_secret = config.get("appSecret")
    
    if not app_id or not app_secret:
        print("❌ 配置缺少 appId 或 appSecret")
        return 1
    
    client = FeishuLongPollClient(app_id, app_secret)
    return client.start()

if __name__ == "__main__":
    sys.exit(main())
