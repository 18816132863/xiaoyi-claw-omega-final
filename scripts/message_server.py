#!/usr/bin/env python3
"""
消息发送服务 V2.0.0

提供 HTTP API 让守护进程可以直接发送消息到聊天界面。
通过调用 OpenClaw Gateway 内部接口实现。

使用方式：
    python scripts/message_server.py --port 18790

API:
    POST /send
    {
        "channel": "xiaoyi-channel",
        "target": "default",
        "message": "消息内容"
    }
    
    GET /health - 健康检查
"""

import http.server
import socketserver
import json
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
import hashlib

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class MessageHandler(http.server.BaseHTTPRequestHandler):
    """消息发送处理器"""
    
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, format, *args):
        """静默日志"""
        pass
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/send':
            self._handle_send()
        else:
            self._send_error(404, "Not Found")
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/health':
            self._handle_health()
        else:
            self._send_error(404, "Not Found")
    
    def _handle_send(self):
        """处理发送消息请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            channel = data.get('channel', 'xiaoyi-channel')
            target = data.get('target', 'default')
            message = data.get('message', '')
            
            if not message:
                self._send_error(400, "消息内容不能为空")
                return
            
            # 写入待发送队列（供 AI 读取）
            pending_file = project_root / "reports" / "ops" / "pending_sends.jsonl"
            pending_file.parent.mkdir(parents=True, exist_ok=True)
            
            idempotency_key = hashlib.sha256(
                f"{channel}:{target}:{message}".encode()
            ).hexdigest()[:32]
            
            entry = {
                "action": "send",
                "channel": channel,
                "target": target,
                "message": message,
                "idempotency_key": idempotency_key,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(pending_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            # 写入通知文件
            notify_file = project_root / "reports" / "ops" / "notify_send.txt"
            with open(notify_file, 'w', encoding='utf-8') as f:
                f.write(f"PENDING_SEND:{message[:50]}...\n")
            
            print(f"[MessageServer] 消息已入队: {message[:30]}...")
            
            self._send_response({
                "success": True,
                "message": "消息已写入发送队列",
                "idempotency_key": idempotency_key
            })
            
        except Exception as e:
            print(f"[MessageServer] 错误: {e}")
            self._send_error(500, str(e))
    
    def _handle_health(self):
        """健康检查"""
        self._send_response({"status": "ok", "timestamp": datetime.now().isoformat()})
    
    def _send_response(self, data):
        """发送 JSON 响应"""
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def _send_error(self, code, message):
        """发送错误响应"""
        body = json.dumps({
            "success": False,
            "error": message
        }, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """多线程 HTTP 服务器"""
    allow_reuse_address = True
    daemon_threads = True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="消息发送服务")
    parser.add_argument("--port", "-p", type=int, default=18790, help="监听端口")
    parser.add_argument("--daemon", "-d", action="store_true", help="以守护进程方式运行")
    
    args = parser.parse_args()
    
    # 写入 PID 文件
    pid_file = project_root / "data" / "message_server.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    
    import os
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    print("=" * 60)
    print("  消息发送服务 V2.0.0")
    print("=" * 60)
    print(f"  PID: {os.getpid()}")
    print(f"  端口: {args.port}")
    print(f"  API: POST http://localhost:{args.port}/send")
    print("=" * 60)
    
    try:
        with ThreadedHTTPServer(("", args.port), MessageHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        if pid_file.exists():
            pid_file.unlink()


if __name__ == "__main__":
    main()
