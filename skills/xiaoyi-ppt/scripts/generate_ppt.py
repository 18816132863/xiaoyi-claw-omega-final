"""
generate_ppt.py - 通过 OSMS {SERVICE_URL}/celia-claw/v1/sse-api/skill/execute SSE 接口生成 PPT

用法：
  python generate_ppt.py <query>
"""

import argparse
import json
import logging
import os
import sys
import threading
import uuid
import urllib3
from pathlib import Path
from posixpath import basename as url_basename
from typing import Optional

import requests

from config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SKILL_EXECUTE_PATH = "/celia-claw/v1/sse-api/skill/execute"
SKILL_ID = "xiaoyi_office"

OFFICE_EXTENSIONS = {
    ".pptx", ".ppt", ".docx", ".doc", ".xlsx", ".xls",
    ".pdf", ".pptm", ".docm", ".xlsm",
}

logger = logging.getLogger("generate_ppt")
logger.addHandler(logging.NullHandler())


def _setup_logger(log_path: Path) -> None:
    """初始化 logger，输出到指定文件。"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(handler)


# ============================================================
# Event Handlers
# ============================================================

def handle_step_info(data: dict):
    content = data.get("content", "").rstrip("\n")
    if content:
        logger.info("[进度] %s", content)


def handle_data(data: dict) -> str:
    reasoning = data.get("reasoning_content", "")
    if reasoning:
        logger.debug("[思考] %s", reasoning)
    content = data.get("content", "")
    if content:
        logger.debug("[data] %s", content)
    return content


OFFICE_EXTENSIONS = {
    ".pptx", ".ppt", ".docx", ".doc", ".xlsx", ".xls",
    ".pdf", ".pptm", ".docm", ".xlsm",
}


def handle_generate_doc(data: dict, output_dir: Path) -> Optional[str]:
    doc = data.get("doc", {})
    name = doc.get("name") or doc.get("path", "")
    url = doc.get("url", "")
    if not url:
        return None
    logger.info("[生成文件] %s: %s", name, url)

    # 仅下载 Office 格式的文档，跳过 zip 等中间文件
    suffix = Path(name).suffix.lower() if name else ""
    if suffix and suffix not in OFFICE_EXTENSIONS:
        logger.info("[跳过下载] %s (非Office格式: %s)", name, suffix)
        return None

    # 下载文件到 output_dir
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        local_path = output_dir / (name or "output")
        resp = requests.get(url, timeout=300, verify=False)
        resp.raise_for_status()
        local_path.write_bytes(resp.content)
        abs_path = str(local_path.resolve())
        logger.info("[文件已保存] %s -> %s", name, abs_path)
        return abs_path
    except Exception as e:
        logger.error("[下载失败] %s: %s", name, e)
        return None


def handle_tool(data: dict):
    tool_name = data.get("tool_name", "")
    if tool_name:
        logger.info("[调用工具] %s", tool_name)


def handle_tool_result(data: dict):
    tool_name = data.get("tool_name", "")
    result = str(data.get("tool_result", ""))
    if len(result) > 200:
        result = result[:200] + "..."
    if tool_name:
        logger.info("[%s 结果] %s", tool_name, result)


def handle_command(data: dict):
    content_str = data.get("content", "")
    try:
        content = json.loads(content_str) if isinstance(content_str, str) else content_str
    except json.JSONDecodeError:
        return
    steps = content.get("payload", {}).get("cardParams", {}).get("taskStepInfo", [])
    running = [s["stepName"] for s in steps if s.get("stepStatus") == "running"]
    if running:
        logger.info("[进行中] %s", ", ".join(running))


def handle_finish(data: dict):
    finish_type = data.get("type", "normal")
    # logger.info("[完成] type=%s", finish_type)


def _heartbeat_worker(stop_event: threading.Event, interval: int = 10) -> None:
    """每隔 interval 秒向日志写入心跳，直到 stop_event 被设置。"""
    while not stop_event.wait(interval):
        logger.info("[进行中] PPT生成中，请耐心等待")


# ============================================================
# SSE parsing
# ============================================================

def process_event(event_data: str, response_text: list[str], output_dir: Path) -> bool:
    """处理一个 SSE 事件的 data 内容。返回 True 表示收到 finish 应终止。"""
    try:
        data = json.loads(event_data)
    except json.JSONDecodeError:
        logger.warning("无法解析: %s", event_data[:200])
        return False

    event_type = data.get("event", "")

    if event_type == "stepInfo":
        handle_step_info(data)
    elif event_type == "data":
        text = handle_data(data)
        if text:
            response_text.append(text)
    elif event_type == "generateDoc":
        handle_generate_doc(data, output_dir)
    elif event_type == "tool":
        handle_tool(data)
    elif event_type == "tool_result":
        handle_tool_result(data)
    elif event_type == "command":
        handle_command(data)
    elif event_type == "heartbeat":
        pass
    elif event_type == "finish":
        handle_finish(data)
        return True

    return False


# ============================================================
# Core: build request + streaming SSE response
# ============================================================

def build_request(
    cfg: Config,
    session_id: str,
    interaction_id: int,
    query: str,
    attachments: list[dict] = None,
) -> dict:
    sn = session_id + str(interaction_id)
    req = {
        "sn": sn,
        "sessionid": session_id,
        "interactionid": str(interaction_id),
        "query": query,
        "from": cfg.request_from,
        "device": cfg.device.to_dict(trace_id=sn),
        "client_context": {"appExtraInfo": {"customAgent": {"name": "acp_ppt_with_outline"}}},
    }

    if attachments:
        req["attachment"] = attachments

    if cfg.personal_uid:
        req["user"] = {"uid": cfg.personal_uid}

    if cfg.request_from:
        req["agentInfo"] = {"agentId": cfg.request_from}

    return req


def prompt(cfg: Config, query: str, attachments: list[dict] = None) -> str:
    """
    发送 prompt 到 OSMS skill/execute SSE 接口，返回完整的响应文本。

    Args:
        cfg: 配置
        query: 用户查询文本
        attachments: 可选的附件列表

    Returns:
        完整的响应文本
    """
    ppt_session_id = os.getenv("PPT_SESSION_ID", "") or str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    interaction_id = 1
    output_dir = Path("/tmp/xiaoyi_ppt") / ppt_session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    _setup_logger(output_dir / "generate.log")
    req_body = build_request(cfg, session_id, interaction_id, query, attachments)

    headers = {
        "Content-Type": "application/json",
        "x-skill-id": SKILL_ID,
        "x-hag-trace-id": req_body["sn"],
        **cfg.auth_headers(),
    }

    url = cfg.service_url.rstrip("/") + SKILL_EXECUTE_PATH
    response_text = []

    logger.info("发送请求 url=%s sn=%s", url, req_body["sn"])

    _stop_heartbeat = threading.Event()
    _heartbeat = threading.Thread(
        target=_heartbeat_worker, args=(_stop_heartbeat, 15), daemon=True
    )
    _heartbeat.start()

    try:
        with requests.post(
            url,
            json=req_body,
            headers=headers,
            stream=True,
            timeout=cfg.request_timeout,
            verify=not cfg.tls_skip_verify,
        ) as resp:
            if resp.status_code != 200:
                error_body = resp.text
                logger.error("HTTP %d: %s", resp.status_code, error_body)
                raise RuntimeError(f"HTTP {resp.status_code}: {error_body}")

            pending_data = ""
            has_pending = False

            for raw_line in resp.iter_lines(decode_unicode=True):
                if raw_line is None:
                    continue
                line = raw_line.strip()

                if not line:
                    if has_pending and pending_data:
                        if process_event(pending_data, response_text, output_dir):
                            break
                    pending_data = ""
                    has_pending = False
                    continue

                if line.startswith("data:"):
                    data_part = line[5:].strip()
                    if has_pending:
                        pending_data += "\n" + data_part
                    else:
                        pending_data = data_part
                        has_pending = True

            if has_pending and pending_data:
                process_event(pending_data, response_text, output_dir)

    except requests.exceptions.RequestException as e:
        logger.error("[ERROR] 请求失败: %s", e)
        raise
    finally:
        _stop_heartbeat.set()
        _heartbeat.join(timeout=1)

    logger.info("[DONE] output_dir=%s", output_dir)
    return "".join(response_text)


# ============================================================
# CLI 入口
# ============================================================

def parse_files_to_attachments(files_json: str) -> list[dict]:
    """将 --files JSON 数组转换为 attachment 列表"""
    urls = json.loads(files_json)
    attachments = []
    for url in urls:
        # 从 URL 中提取文件名（取最后一段路径）
        file_name = url_basename(url.split("?")[0]) or "file"
        attachments.append({
            "fileId": str(uuid.uuid4()),
            "fileName": file_name,
            "fileDownloadUrl": url,
        })
    return attachments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="用户查询文本")
    parser.add_argument("--files", default=None, help='附件 URL JSON 数组，如 \'["http://host/a.md"]\'')
    args = parser.parse_args()

    try:
        cfg = Config.load()
    except ValueError as e:
        logger.error("配置错误: %s", e)
        sys.exit(1)

    attachments = None
    if args.files:
        try:
            attachments = parse_files_to_attachments(args.files)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error("--files 参数解析失败: %s", e)
            sys.exit(1)

    try:
        prompt(cfg, args.query, attachments)
    except Exception as e:
        logger.error("[ERROR] %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
