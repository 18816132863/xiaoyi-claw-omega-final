#!/usr/bin/env python3
"""Celia Podcast API client - auth, request, polling."""

import hashlib
import ssl
import os
import time
import uuid
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 配置路径
def read_xiaoyienv():
    """
    读取 ~/.openclaw/.xiaoyienv 文件并返回键值对字典。
    """
    file_path = os.path.expanduser("~/.openclaw/.xiaoyienv")
    env_dict = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip()

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    return env_dict


def build_request_body(
    url=None,
    content=None,
    action="gen_podcast",
    style="interview",
    scene_type="briefs",
    item_id=None,
    hash_id=None,
    uid=None,
    vocal_enhance=True,
    bg_noise_reduce=True,
):
    """构建请求体。

    gen_podcast 和 sync_audio 使用相同的请求体结构，
    仅 action 不同。轮询时需保持相同的 itemId 和 hashId。

    支持两种输入模式：
    - url: 链接，genMethod=link，refInfos=[{"url": url}]
    - content: 本地文件内容，genMethod=collection，refItemIds 引用 content item
    """
    if not url and not content:
        raise ValueError("必须提供 url 或 content")

    if item_id is None:
        unique_id = uuid.uuid4().hex[:16]
        item_id = f"CeliaColl_{unique_id}"
    if hash_id is None:
        hash_id = str(uuid.uuid4())

    # 根据 url/content 决定 genMethod 和请求结构
    if content:
        # 本地文件内容模式：collection + refItemIds + 额外 content item
        gen_method = "collection"
        content_item_id = "1"
        main_item = {
            "itemId": item_id,
            "type": 5,
            "aigcAudioInfo": {
                "refItemIds": [content_item_id],
                "genMethod": gen_method,
                "aigcParam": {
                    "adapter": {
                        "balance": True,
                        "headroom": 1,
                        "speed": 1,
                    },
                    "bgNoiseReduce": bg_noise_reduce,
                    "hashId": hash_id,
                    "modelType": "celia-tts",
                    "peopleNo": "double",
                    "sceneType": scene_type,
                    "style": style,
                    "vocalEnhance": vocal_enhance,
                    "voiceType": ["blog_female", "huxiu"],
                },
            },
        }
        content_item = {
            "itemId": content_item_id,
            "type": 3,
            "content": content,
        }
        item_infos = [main_item, content_item]
    elif url:
        gen_method = "link"
        ref_infos = [{"url": url}]
        item_infos = [
            {
                "itemId": item_id,
                "type": 5,
                "aigcAudioInfo": {
                    "genMethod": gen_method,
                    "refInfos": ref_infos,
                    "aigcParam": {
                        "adapter": {
                            "balance": True,
                            "headroom": 1,
                            "speed": 1,
                        },
                        "bgNoiseReduce": bg_noise_reduce,
                        "hashId": hash_id,
                        "modelType": "celia-tts",
                        "peopleNo": "double",
                        "sceneType": scene_type,
                        "style": style,
                        "vocalEnhance": vocal_enhance,
                        "voiceType": ["blog_female", "huxiu"],
                    },
                },
            }
        ]
    else:
        raise ValueError("必须提供 url 或 content")

    body = {
        "logId": item_id.replace("CeliaColl_", "gen_podcast_"),
        "deviceInfo": {
            "appVersion": "11.3.8.200",
            "deviceType": "openclaw",
            "deviceId": uid,
            "packageName": "com.huawei.hmos.vassistant",
            "deviceName": "ADY",
        },
        "userInfo": {
            "uid": uid,
        },
        "apiName": "gen_aigc",
        "mediaId": "celia_collect",
        "genAigc": {
            "itemInfos": item_infos,
            "action": action,
        },
    }

    return body


def submit_podcast(url=None, content=None, **kwargs):
    """提交播客生成任务，返回 (响应JSON, itemId, hashId)。

    itemId 和 hashId 需要保存，后续 sync_audio 轮询要用相同的值。
    支持 url(链接) 或 content(本地文件内容) 两种输入，二选一。
    """
    # 读取环境变量
    config = read_xiaoyienv()
    
    required_keys = ['PERSONAL-API-KEY', 'PERSONAL-UID']
    for key in required_keys:
        if key not in config:
            raise RuntimeError(f"缺少环境变量 {key}。请在 ~/.openclaw/.xiaoyienv 中配置")
    
    base_url = config.get('SERVICE_URL', '')
    api_key = config['PERSONAL-API-KEY']
    uid = config['PERSONAL-UID']
    trace_id = f"{hashlib.sha256(uid.encode('utf-8')).hexdigest()[:32]}-{datetime.now().strftime("20260328%H%M%S")}"

    # 公共请求头
    headers = {
        'Content-Type': 'application/json',
        'x-uid': uid,
        'x-api-key': api_key,
        'x-request-from': 'openclaw',
        'x-prd-pkg-name': 'com.huawei.hmos.vassistant',
        'x-skill-id': 'xiaoyi_podcast_gen',
        'x-hag-trace-id': trace_id
    }

    # 生成唯一标识，轮询时复用
    unique_id = uuid.uuid4().hex[:16]
    item_id = f"CeliaColl_{unique_id}"
    hash_id = str(uuid.uuid4())

    body = build_request_body(
        url=url,
        content=content,
        action="gen_podcast",
        item_id=item_id,
        hash_id=hash_id,
        uid=uid,
        **kwargs,
    )

    source = content[:50] + "..." if content else url
    print(f"[Podcast] 提交生成任务: {source}")
    print(f"[Podcast] itemId: {item_id}, hashId: {hash_id}")

    resp = requests.post(
        f"{base_url}/celia-claw/v1/rest-api/skill/execute", 
        headers=headers, 
        json=body, 
        verify=False, 
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()

    code = result.get("code", -1)
    msg = result.get("msg", "unknown")
    print(f"[Podcast] 提交响应: code={code}, msg={msg}")

    if code != 0:
        raise RuntimeError(f"播客提交失败: code={code}, msg={msg}")

    # 打印配额信息
    quota = result.get("genAigc", {}).get("aigcQuotaInfo", {})
    if quota:
        print(f"[Podcast] 配额: 今日处理中={quota.get('todayProcessingPodcastNum', '?')}, "
              f"已完成={quota.get('todaySuccessPodcastNum', '?')}, "
              f"待处理={quota.get('todayTodoPodcastNum', '?')}, "
              f"每日上限={quota.get('maxDailyGenerationNum', '?')}")

    return result, item_id, hash_id


def poll_task(url=None, content=None, item_id=None, hash_id=None, interval=20, timeout=1800, **kwargs):
    """轮询任务状态直到完成或超时。

    gen_podcast 和 sync_audio 使用相同的请求体结构，
    仅 action 从 gen_podcast 改为 sync_audio。
    需保持相同的 itemId 和 hashId。
    """
    # 读取环境变量
    config = read_xiaoyienv()
    
    required_keys = ['PERSONAL-API-KEY', 'PERSONAL-UID']
    for key in required_keys:
        if key not in config:
            raise RuntimeError(f"缺少环境变量 {key}。请在 ~/.openclaw/.xiaoyienv 中配置")
    
    base_url = config.get('SERVICE_URL', '')
    api_key = config['PERSONAL-API-KEY']
    uid = config['PERSONAL-UID']
    trace_id = f"{hashlib.sha256(uid.encode('utf-8')).hexdigest()[:32]}-{datetime.now().strftime("20260328%H%M%S")}"

    # 公共请求头
    headers = {
        'Content-Type': 'application/json',
        'x-uid': uid,
        'x-api-key': api_key,
        'x-request-from': 'openclaw',
        'x-prd-pkg-name': 'com.huawei.hmos.vassistant',
        'x-skill-id': 'xiaoyi_podcast_gen',
        'x-hag-trace-id': trace_id
    }

    start = time.time()
    attempt = 0
    while time.time() - start < timeout:
        attempt += 1
        body = build_request_body(
            url=url,
            content=content,
            action="sync_audio",
            item_id=item_id,
            hash_id=hash_id,
            uid=uid,
            **kwargs,
        )

        try:
            resp = requests.post(
                f"{base_url}/celia-claw/v1/rest-api/skill/execute", 
                headers=headers, 
                json=body, 
                verify=False, 
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            print(f"[Podcast] 轮询第 {attempt} 次出错: {e}")
            time.sleep(interval)
            continue

        code = result.get("code", -1)
        if code != 0:
            print(f"[Podcast] 轮询返回错误: code={code}, msg={result.get('msg', '')}")
            time.sleep(interval)
            continue

        status = extract_audio_status(result)
        print(f"\r[Podcast] 轮询第 {attempt} 次, audioStatus={status}", end="", flush=True)
        if status == "done":
            print()  # 完成时换行

        if status == "done":
            return result
        elif status in ("fail", "error"):
            error = extract_error(result)
            raise RuntimeError(f"播客生成失败: {error}")

        time.sleep(interval)

    raise TimeoutError(f"播客生成超时 ({timeout}s)")


def extract_audio_status(result):
    """从响应中提取 audioStatus。

    路径: genAigc.itemInfos[0].aigcAudioInfo.audioStatus
    值: submit / processing / done / fail
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["audioStatus"]
    except (KeyError, IndexError, TypeError):
        return "unknown"


def extract_audio_url(result):
    """从响应中提取音频下载 URL。

    路径: genAigc.itemInfos[0].aigcAudioInfo.audioUrl
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["audioUrl"]
    except (KeyError, IndexError, TypeError):
        return None


def extract_content_url(result):
    """从响应中提取字幕文件 URL (srt)。

    路径: genAigc.itemInfos[0].aigcAudioInfo.contentUrl
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["contentUrl"]
    except (KeyError, IndexError, TypeError):
        return None


def extract_cover_url(result):
    """从响应中提取封面图 URL。

    路径: genAigc.itemInfos[0].aigcAudioInfo.genCoverUrl
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["genCoverUrl"]
    except (KeyError, IndexError, TypeError):
        return None


def extract_title(result):
    """从响应中提取播客标题。

    路径: genAigc.itemInfos[0].aigcAudioInfo.title
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["title"]
    except (KeyError, IndexError, TypeError):
        return None


def extract_duration(result):
    """从响应中提取播客时长（秒）。

    路径: genAigc.itemInfos[0].aigcAudioInfo.duration
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["duration"]
    except (KeyError, IndexError, TypeError):
        return None


def extract_error(result):
    """从响应中提取错误信息。

    路径: genAigc.itemInfos[0].aigcAudioInfo.error
    """
    try:
        return result["genAigc"]["itemInfos"][0]["aigcAudioInfo"]["error"]
    except (KeyError, IndexError, TypeError):
        return result.get("msg", "unknown error")


# 创建兼容旧SSL的适配器（只需要定义一次）
class OldSSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def download_file(url, output_path):
    """下载文件到本地。"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 优先用 curl，回退到 requests
    if shutil.which("curl"):
        cmd = ["curl", "-sL", "-k", "-o", str(output_path), url]
        result = subprocess.run(cmd, timeout=120)
        if result.returncode != 0:
            print(f"[Podcast] curl 下载失败（返回码 {result.returncode}），回退到 requests")
            _download_with_requests(url, output_path)
    else:
        _download_with_requests(url, output_path)

    size = output_path.stat().st_size
    print(f"[Podcast] 下载完成: {output_path} ({size:,} bytes)")
    return str(output_path)


def _download_with_requests(url, output_path):
    """用 requests 下载文件，兼容旧 SSL。"""
    session = requests.Session()
    session.mount("https://", OldSSLAdapter())
    resp = session.get(url, verify=False, timeout=120, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)