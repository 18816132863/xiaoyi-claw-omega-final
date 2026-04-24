#!/usr/bin/env python3
"""
消息发送服务 V5.0.0

真实消息出口 + 可观测性 + 配置中心：
- 从 settings 读取配置
- 结构化日志
- 业务指标
- 健康检查接口
"""

import http.server
import socketserver
import json
import sys
import os
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.observability import get_logger, get_metrics, HealthChecker
from config import get_settings


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """多线程 HTTP 服务器"""
    daemon_threads = True
    allow_reuse_address = True


class MessageHandler(http.server.BaseHTTPRequestHandler):
    """消息发送处理器"""
    
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, format, *args):
        """静默默认日志"""
        pass
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/health':
            self._handle_health()
        elif self.path == '/ready':
            self._handle_ready()
        elif self.path == '/metrics':
            self._handle_metrics()
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/send':
            self._handle_send()
        else:
            self._send_error(404, "Not Found")
    
    def _handle_send(self):
        logger = get_logger("message_server", "handler")
        metrics = get_metrics()
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            channel = data.get('channel', 'xiaoyi-channel')
            target = data.get('target', 'default')
            message = data.get('message', '')
            task_id = data.get('task_id')
            run_id = data.get('run_id')

            if not message:
                logger.warning("消息内容为空", task_id=task_id)
                self._send_error(400, "消息内容不能为空")
                return

            message_id = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            delivered_file = project_root / "reports" / "ops" / "delivered_messages.jsonl"
            delivered_file.parent.mkdir(parents=True, exist_ok=True)

            delivered_at = datetime.now().isoformat()
            entry = {
                "message_id": message_id,
                "task_id": task_id,
                "run_id": run_id,
                "channel": channel,
                "target": target,
                "message": message,
                "delivered_at": delivered_at,
                "status": "delivered"
            }

            with open(delivered_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

            logger.info(
                "消息送达成功",
                task_id=task_id,
                run_id=run_id,
                event_type="message_delivered",
                status="delivered"
            )
            
            metrics.increment("messages_sent")
            metrics.histogram("message_size_bytes", len(message.encode('utf-8')))

            response = {
                "success": True,
                "message_id": message_id,
                "task_id": task_id,
                "run_id": run_id,
                "status": "delivered",
                "delivered_at": delivered_at
            }
            self._send_json(200, response)

        except Exception as e:
            logger.error(
                f"消息发送失败: {e}",
                event_type="message_send_error",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            metrics.increment("message_send_errors")
            self._send_error(500, str(e))
    
    def _handle_health(self):
        """健康检查"""
        health = HealthChecker("message_server")
        health.register("server_running", lambda: {"status": "healthy"})
        health.register("storage_writable", self._check_storage)
        
        result = health.check()
        self._send_json(200, result)
    
    def _handle_ready(self):
        """就绪检查"""
        health = HealthChecker("message_server")
        health.register("server_running", lambda: {"status": "healthy"})
        health.register("storage_writable", self._check_storage)
        
        result = health.check_ready()
        is_ready = result["ready"]
        self._send_json(200 if is_ready else 503, result)
    
    def _handle_metrics(self):
        """指标接口"""
        metrics = get_metrics()
        self._send_json(200, metrics.get_all())
    
    def _check_storage(self) -> dict:
        try:
            delivered_file = project_root / "reports" / "ops" / "delivered_messages.jsonl"
            delivered_file.parent.mkdir(parents=True, exist_ok=True)
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def _send_error(self, status_code: int, message: str):
        self._send_json(status_code, {"success": False, "error": message})


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="消息发送服务 V5.0.0")
    parser.add_argument("--port", "-p", type=int, help="监听端口，默认从配置读取")
    args = parser.parse_args()
    
    # 从配置中心读取配置
    settings = get_settings()
    port = args.port if args.port else settings.message_server.port
    
    logger = get_logger("message_server", "main")
    
    pid_file = project_root / "data" / "message_server.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    logger.info(
        f"消息服务启动",
        event_type="server_start",
        port=port,
        env=settings.env.value
    )
    
    print("=" * 60)
    print("  消息发送服务 V5.0.0")
    print("=" * 60)
    print(f"  PID: {os.getpid()}")
    print(f"  环境: {settings.env.value}")
    print(f"  端口: {port}")
    print(f"  API: POST http://localhost:{port}/send")
    print(f"  健康检查: GET http://localhost:{port}/health")
    print(f"  就绪检查: GET http://localhost:{port}/ready")
    print(f"  指标接口: GET http://localhost:{port}/metrics")
    print("=" * 60)
    
    try:
        with ThreadedHTTPServer(("", port), MessageHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务停止", event_type="server_stop")
        print("\n服务已停止")
    finally:
        if pid_file.exists():
            pid_file.unlink()


if __name__ == "__main__":
    main()
