#!/usr/bin/env python3
"""
基于 Seedance 的视频生成工具（支持首帧和首尾帧图生视频）

使用 Celia Claw API 调用
"""

import os
import sys
import json
import base64
import ssl
import time
import argparse
import re
import shutil
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Optional, Literal
from datetime import datetime, timedelta
from urllib.parse import urlparse
import urllib.request
import random
import string
import warnings
warnings.filterwarnings("ignore")

# 忽略SSL验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
GenerationMode = Literal["t2v", "first_frame", "first_last_frame"]


# ============================================================================
# 环境配置工具函数
# ============================================================================

def read_xiaoyienv():
    """
    读取 ~/.openclaw/.xiaoyienv 文件并返回键值对字典。
    """
    file_path = os.path.expanduser("~/.openclaw/.xiaoyienv")
    env_dict = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 去除行首尾的空白字符和换行符
                line = line.strip()
                # 跳过空行和以 # 开头的注释行
                if not line or line.startswith('#'):
                    continue
                # 确保行中包含等号
                if '=' in line:
                    # 只在第一个等号处分割，防止 value 中包含等号
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip()

    except FileNotFoundError:
        print(f"提示: 未找到文件 {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    return env_dict

def _is_remote_url(value):
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_local_file(value):
    """Check if value is a local file path."""
    try:
        return Path(value).is_file()
    except (OSError, TypeError):
        return False
   

def image_to_base64(image_path: str) -> str:
    """将图片转为base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def calculate_sha256(file_path):
    """计算文件的 SHA256 哈希值"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def upload_file(file_path, object_type="TEMPORARY_MATERIAL_DOC"):
    """
    将本地文件上传到小艺文件存储服务（三阶段上传：prepare → upload → complete）

    Args:
        file_path: 本地文件路径
        object_type: 文件类型（默认 TEMPORARY_MATERIAL_DOC）

    Returns:
        fileUrl
    """
    try:
        # 校验文件存在
        if not os.path.isfile(file_path):
            print(f'❌ 文件不存在：{file_path}')
            return None

        # 读取并校验配置
        config = read_xiaoyienv()

        required_keys = ['PERSONAL-API-KEY', 'PERSONAL-UID']
        check_result = True

        for key in required_keys:
            if key not in config:
                print(f'❌ key "{key}" 不存在：失败...')
                check_result = False

        if not check_result:
            return None

        # 准备文件信息
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_sha256 = calculate_sha256(file_path)
        uid = config['PERSONAL-UID']
        base_url = config.get('SERVICE_URL', '')

        # 公共请求头
        common_headers = {
            'Content-Type': 'application/json',
            'x-uid': uid,
            'x-api-key': config['PERSONAL-API-KEY'],
            'x-request-from': 'openclaw',
        }

        # ── 阶段 1: Prepare ──────────────────────────────────────────────────────
        prepare_url = f'{base_url}/osms/v1/file/manager/prepare'

        prepare_payload = {
            'objectType': object_type,
            'fileName': file_name,
            'fileSha256': file_sha256,
            'fileSize': file_size,
            'fileOwnerInfo': {
                'uid': uid,
                'teamId': uid,
            },
            'useEdge': False,
        }

        prepare_resp = requests.post(
            prepare_url,
            headers=common_headers,
            json=prepare_payload,
            timeout=30,
            verify=False
        )

        if prepare_resp.status_code != 200:
            print(f'❌ Prepare 请求失败: HTTP {prepare_resp.status_code}')
            print(f'❌ 响应内容: {prepare_resp.text}')
            return None

        prepare_data = prepare_resp.json()

        # 部分服务器返回 code 字段，"0" 为成功
        if 'code' in prepare_data and prepare_data['code'] != '0':
            print(f'❌ Prepare 失败: {prepare_data.get("desc", "未知错误")}')
            return None

        object_id = prepare_data.get('objectId')
        draft_id = prepare_data.get('draftId')
        upload_infos = prepare_data.get('uploadInfos', [])

        if not object_id or not draft_id or not upload_infos:
            print(f'❌ Prepare 响应缺少必要字段: objectId={object_id}, draftId={draft_id}')
            return None

        upload_info = upload_infos[0]
        upload_url = upload_info['url']
        upload_method = upload_info.get('method', 'PUT').upper()
        upload_headers = upload_info.get('headers', {'Content-Type': 'application/octet-stream'})

        with open(file_path, 'rb') as f:
            file_data = f.read()

        upload_resp = requests.request(
            method=upload_method,
            url=upload_url,
            headers=upload_headers,
            data=file_data,
            timeout=120,
            verify=False
        )

        if upload_resp.status_code not in (200, 204):
            print(f'❌ 文件上传失败: HTTP {upload_resp.status_code}')
            return None

        # ── 阶段 3: Complete ─────────────────────────────────────────────────────
        complete_url = f'{base_url}/osms/v1/file/manager/completeAndQuery'

        complete_payload = {
            'objectId': object_id,
            'draftId': draft_id,
        }

        complete_resp = requests.post(
            complete_url,
            headers=common_headers,
            json=complete_payload,
            timeout=30,
            verify=False
        )

        if complete_resp.status_code != 200:
            print(f'❌ Complete 请求失败: HTTP {complete_resp.status_code}')
            return None

        complete_data = complete_resp.json()

        # 从 completeAndQuery 响应中直接获取文件下载 URL
        file_url = complete_data.get('fileDetailInfo', {}).get('url', '')

        return file_url

    except requests.exceptions.Timeout:
        print('❌ 请求超时')
        return None
    except requests.exceptions.ConnectionError as e:
        print(f'❌ 连接失败: {e}')
        return None
    except Exception as e:
        print(f'❌ 上传异常: {e}')
        import traceback
        traceback.print_exc()
        return None
    

def download_video(video_url: str, output_path: str):
    """下载视频"""
    print(f"📥 下载视频...")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 优先用 curl（Linux/Windows 通常都自带），失败再回落 Python 下载
    curl = shutil.which("curl")
    if curl:
        import subprocess

        result = subprocess.run(
            [curl, "-L", "-o", output_path, video_url, "--max-time", "10"],
            capture_output=True,
            text=True,
        )

        if (
            result.returncode == 0
            and os.path.exists(output_path)
            and os.path.getsize(output_path) > 0
        ):
            print(f"✅ 下载完成: {output_path}")
            return

        # curl 存在但失败，继续走 Python 下载
        stderr = (result.stderr or "").strip()
        if stderr:
            print(
                f"⚠️  curl 下载失败，将回退到 Python 下载。curl stderr: {stderr[:200]}"
            )
        else:
            print("⚠️  curl 下载失败，将回退到 Python 下载。")

    try:
        with urllib.request.urlopen(
            video_url, context=ssl_context, timeout=60
        ) as resp, open(output_path, "wb") as f:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ 下载完成: {output_path}")
        else:
            print(f"⚠️  下载失败（文件为空），请手动下载: {video_url}")
    except Exception as e:
        print(f"⚠️  下载失败，请手动下载: {video_url}")
        print(f"   错误: {e}")


# ============================================================================
# 核心视频生成函数
# ============================================================================

def create_video_generation_task(
    prompt: str,
    first_frame_path: str = None,
    last_frame_path: str = None,
    duration: int = 5,
    ratio: str = "9:16",
    resolution: str = "480p",
    framespersecond: Optional[int] = None,
    seed: Optional[int] = None,
    camera_fixed: Optional[bool] = None,
    watermark: bool = True,
    generate_audio: bool = False,
) -> str:
    """
    创建视频生成任务，返回任务ID

    Args:
        prompt: 文本提示词
        first_frame_path: 首帧参考图片路径
        last_frame_path: 尾帧参考图片路径（用于"首尾帧图生视频"）
        duration: 视频时长（秒）
        ratio: 视频比例
        resolution: 视频分辨率
        framespersecond: 帧率
        seed: 随机种子
        camera_fixed: 是否固定镜头
        watermark: 是否添加水印
        generate_audio: 是否生成同步音频

    Returns:
        任务ID (str)

    生成模式自动推断规则：
        - 仅传 first_frame_path（无 last_frame_path）→ 首帧图生视频 (first_frame)
        - 传 first_frame_path + last_frame_path → 首尾帧图生视频 (first_last_frame)
        - 均不传 → 文生视频 (t2v)
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

    # 参数校验 & 模式自动推断
    has_first_frame = first_frame_path is not None
    has_last_frame = last_frame_path is not None

    # --- 文件存在性校验（仅针对本地文件）---
    def validate_input(path: str, label: str) -> str:
        """验证输入路径，支持本地文件和远程URL"""
        if _is_remote_url(path):
            # 远程URL，直接返回
            return path
        elif _is_local_file(path):
            # 本地文件，返回路径
            return path
        else:
            raise FileNotFoundError(f"❌ 输入无效：{label} 既不是有效的本地文件路径也不是有效的HTTP(S) URL → {path}")

    if has_first_frame:
        first_frame_path = validate_input(first_frame_path, "first_frame_path")
    if has_last_frame:
        last_frame_path = validate_input(last_frame_path, "last_frame_path")

    # --- 自动推断 mode ---
    inferred_mode: GenerationMode
    if has_first_frame and has_last_frame:
        inferred_mode = "first_last_frame"
    elif has_first_frame:
        inferred_mode = "first_frame"
    else:
        inferred_mode = "t2v"

    if inferred_mode == "first_frame":
        print(f"🎬 模式: 首帧图生视频: {first_frame_path}")
    elif inferred_mode == "first_last_frame":
        print(
            f"🎬 模式: 首尾帧图生视频 (first_frame={first_frame_path}, last_frame={last_frame_path})"
        )
    else:
        print("🎬 模式: 文生视频 (text-to-video)")
    
    # 构建content数组 - 包含图片和文本
    content_list = []
    
    # 添加图片输入（根据模式）
    if inferred_mode == "first_frame":
        # 首帧图生视频
        if _is_local_file(first_frame_path):
            first_frame_uri = upload_file(first_frame_path, object_type="TEMPORARY_MATERIAL_DOC")
            if not first_frame_uri:
                raise RuntimeError(f"首帧图片上传失败: {first_frame_path}")
        else:
            # 远程URL - 直接使用
            first_frame_uri = first_frame_path
        
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": first_frame_uri
            },
            "role": "first_frame"
        })
        
    elif inferred_mode == "first_last_frame":
        # 首尾帧图生视频
        # 处理首帧
        if _is_local_file(first_frame_path):
            first_frame_uri = upload_file(first_frame_path, object_type="TEMPORARY_MATERIAL_DOC")
            if not first_frame_uri:
                raise RuntimeError(f"首帧图片上传失败: {first_frame_path}")
        else:
            # 远程URL - 直接使用
            first_frame_uri = first_frame_path
        
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": first_frame_uri
            },
            "role": "first_frame"
        })
        
        # 处理尾帧
        if _is_local_file(last_frame_path):
            last_frame_uri = upload_file(last_frame_path, object_type="TEMPORARY_MATERIAL_DOC")
            if not last_frame_uri:
                raise RuntimeError(f"尾帧图片上传失败: {last_frame_path}")
        else:
            # 远程URL - 直接使用
            last_frame_uri = last_frame_path
        
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": last_frame_uri
            },
            "role": "last_frame"
        })
    
    # 添加文本提示词
    content_list.append({
        "type": "text",
        "text": prompt
    })
    
    # 构建content_data对象，包含content列表和其他参数
    content_data = {
        "actionName": "seedance15proTask",
        "content": content_list,
        "duration": duration,
        "ratio": ratio,
        "resolution": resolution,
        "generate_audio": generate_audio,
        "watermark": watermark
    }
    
    # 添加可选参数
    if seed is not None:
        content_data["seed"] = seed
    if camera_fixed is not None:
        content_data["camera_fixed"] = camera_fixed
    if framespersecond is not None:
        content_data["framespersecond"] = framespersecond

    # 构建完整的请求体
    payload = {
        "endpoint": {
            "device": {
                "prdVer": "13.0.12.100",
                "phoneType": "CDY-AN00",
                "sysVer": "HarmonyOS_3.0.0",
                "deviceType": 0,
                "timezone": "GMT+08:00",
            },
            "privacyOption": {
                "personalizedRecommend": 1
            },
            "locale": "zh-CN",
            "sysLocale": "zh-CN",
            "countryCode": "CN"
        },
        "actions": [
            {
                "actionSn": "1",
                "actionExecutorTask": {
                    "actionName": "seedance15proTask",
                    "pluginId": "2c6c2cf21cb34a87bf114929c0d9c1f8",
                    "content": content_data, 
                }
            }
        ],
        "utterance": {
            "type": "string",
            "original": "string"
        },
        "version": "1.0",
        "session": {
            "isNew": True,
            "sessionId": "string",
            "attributes": "string"
        }
    }
    
    # 公共请求头
    headers = {
        'Content-Type': 'application/json',
        'x-uid': uid,
        'x-api-key': api_key,
        'x-request-from': 'openclaw',
        'x-prd-pkg-name': 'com.huawei.hmos.vassistant',
        'x-skill-id': 'seedance15pro',
        'x-hag-trace-id': trace_id
    }

    # ──────────────────────────────────────────────
    # 发起请求创建任务
    # ──────────────────────────────────────────────

    print(f"🎬 创建视频生成任务...")

    try:
        resp = requests.post(
            f"{base_url}/celia-claw/v1/rest-api/skill/execute",
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )
        
        if resp.status_code != 200:
            raise RuntimeError(f"创建任务失败: HTTP {resp.status_code}: {resp.text}")
        
        result = resp.json()
            
    except requests.exceptions.Timeout:
        raise RuntimeError("创建任务失败: 请求超时")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"创建任务失败: HTTP错误: {e}")
    except Exception as e:
        raise RuntimeError(f"创建任务失败: {e}") from e

    # 检查actionExecutorResult中的code字段（业务层，"0"表示成功）
    ability_infos = result.get('abilityInfos', [])
    if ability_infos:
        action_executor_result = ability_infos[0].get('actionExecutorResult', {})
        if action_executor_result:
            business_code = action_executor_result.get('code')
            if business_code and business_code != '0':
                # 业务逻辑失败，如用户权益校验失败等
                error_msg = action_executor_result.get('desc', '未知错误')
                print(f"❌ 创建任务失败: {error_msg}")
                print(f"   业务错误码: {business_code}")
                raise RuntimeError(f"创建任务失败: {error_msg}")

    # 从响应中提取任务ID
    task_id = None
    try:
        if ability_infos:
            action_executor_result = ability_infos[0].get('actionExecutorResult', {})
            reply = action_executor_result.get('reply', {})
            items = reply.get('items', [])
            if items:
                # 响应中字段名为 'id' 而不是 'taskId'
                task_id = items[0].get('id')
    except Exception as e:
        print(f"⚠️  解析任务ID时出现警告: {e}")
    
    if not task_id:
        raise RuntimeError(f"创建任务失败: 未返回任务ID。响应: {result}")

    print(f"✅ 任务创建成功，任务ID: {task_id}")
    return task_id


def query_video_generation_task(
    task_id: str,
    output_file: str = None,
    poll_interval_s: int = 10,
    timeout_s: int = 60 * 20,
) -> dict:
    """
    查询视频生成任务状态，完成后下载视频

    Args:
        task_id: 任务ID
        output_file: 输出文件路径（可选）
        poll_interval_s: 轮询间隔（秒）
        timeout_s: 超时时间（秒）

    Returns:
        {
            "video_path": "视频路径",
            "task_id": "任务ID"
        }
    """
    # 读取环境变量
    config = read_xiaoyienv()
    
    base_url = config.get('SERVICE_URL', '')
    api_key = config.get('PERSONAL-API-KEY', '')
    uid = config.get('PERSONAL-UID', '')
    trace_id = f"{hashlib.sha256(uid.encode('utf-8')).hexdigest()[:32]}-{datetime.now().strftime("20260328%H%M%S")}"
    
    if not api_key or not uid:
        raise RuntimeError("缺少环境变量 PERSONAL-API-KEY 或 PERSONAL-UID")
    
    # 确保输出目录存在
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        timestamp = int(time.time())
        output_file = Path.home() / ".openclaw/workspace/generated-videos" / f"scene_{timestamp}.mp4"
    
    # 公共请求头
    headers = {
        'Content-Type': 'application/json',
        'x-uid': uid,
        'x-api-key': api_key,
        'x-request-from': 'openclaw',
        'x-prd-pkg-name': 'com.huawei.hmos.vassistant',
        'x-skill-id': 'seedance15pro',
        'x-hag-trace-id': trace_id
    }

    # ──────────────────────────────────────────────
    # 轮询查询任务状态
    # ──────────────────────────────────────────────

    print(f"\n⏳ 等待视频生成[{task_id}]...")
    started = time.time()
    last_status = None
    
    query_payload = {
        "endpoint": {
            "device": {
                "prdVer": "13.0.12.100",
                "phoneType": "CDY-AN00",
                "sysVer": "HarmonyOS_3.0.0",
                "deviceType": 0,
                "timezone": "GMT+08:00",
            },
            "privacyOption": {
                "personalizedRecommend": 1
            },
            "locale": "zh-CN",
            "sysLocale": "zh-CN",
            "countryCode": "CN"
        },
        "actions": [
            {
                "actionSn": "1",
                "actionExecutorTask": {
                    "actionName": "seedance15proTaskQuery",
                    "pluginId": "2c6c2cf21cb34a87bf114929c0d9c1f8",
                    "content": {
                        "id": task_id,
                        "actionName": "seedance15proTaskQuery"
                    }
                }
            }
        ],
        "utterance": {
            "type": "string",
            "original": "string"
        },
        "version": "1.0",
        "session": {
            "isNew": True,
            "sessionId": "string",
            "attributes": "string"
        }
    }
    
    video_url=None
    while True:
        if time.time() - started > timeout_s:
            print(f"❌ 任务超时({timeout_s}s): {task_id}")
            return {}

        time.sleep(max(1, poll_interval_s))
        
        # 查询任务状态
        try:
            query_resp = requests.post(
                f"{base_url}/celia-claw/v1/rest-api/skill/execute",
                headers=headers,
                json=query_payload,
                timeout=30,
                verify=False
            )
            
            query_result = query_resp.json()
            
            # 检查actionExecutorResult中的code字段（业务层，"0"表示成功）
            ability_infos = query_result.get('abilityInfos', [])
            if ability_infos:
                action_executor_result = ability_infos[0].get('actionExecutorResult', {})
                if action_executor_result:
                    business_code = action_executor_result.get('code')
                    if business_code and business_code != '0':
                        # 业务逻辑失败，如用户权益校验失败等
                        error_msg = action_executor_result.get('desc', '未知错误')
                        print(f"❌ 查询任务失败: {error_msg}")
                        print(f"   业务错误码: {business_code}")
                        raise RuntimeError(f"查询任务失败: {error_msg}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️  查询任务超时")
            time.sleep(poll_interval_s)
            continue
        except requests.exceptions.HTTPError as e:
            print(f"⚠️  查询任务失败: HTTP错误: {e}")
            time.sleep(poll_interval_s)
            continue
        except Exception as e:
            print(f"⚠️  查询任务异常: {e}")
            time.sleep(poll_interval_s)
            continue
        
        # 解析查询结果
        try:
            ability_infos = query_result.get('abilityInfos', [])
            if not ability_infos:
                print(f"⚠️  查询响应格式异常: {query_result}")
                time.sleep(poll_interval_s)
                continue
            
            action_executor_result = ability_infos[0].get('actionExecutorResult', {})
            reply = action_executor_result.get('reply', {})
            items = reply.get('items', [])
            
            if not items:
                print(f"⚠️  未找到任务结果")
                time.sleep(poll_interval_s)
                continue
            
            task_info = items[0]
            status = task_info.get('status', '')
            
            # 根据实际API返回，status字段判断任务状态
            if status == 'succeeded':
                # 任务成功
                content = task_info.get('content', {})
                video_url = content.get('video_url', '')
                
                if not video_url:
                    print(f"❌ 任务成功但未返回视频URL: {task_info}")
                    return {}
                print(f"✅ 任务完成，视频URL: {video_url}")
                break
                  
            elif status == 'running':
                # 任务进行中
                if status != last_status:
                    print(f"   状态: {status}... (任务进行中)")
                    last_status = status
            else:
                # 任务失败或其他异常状态
                error_msg = task_info.get('message', '') or task_info.get('desc', status)
                print(f"❌ 视频生成失败: {error_msg}")
                return {}
                    
        except Exception as e:
            print(f"⚠️  解析查询结果时出现错误: {e}")
            time.sleep(poll_interval_s)
            continue
   
    # 下载视频
    try:
        download_video(video_url, str(output_file))
    except Exception as e:
        print(f"❌ 下载视频失败: {e}")
        return {}
                
    return {
        "video_path": str(output_file),
        "task_id": task_id
    }


# ============================================================================
# 任务管理工具函数
# ============================================================================


def sanitize_filename(name: str) -> str:
    """清理文件名，移除非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip()
    return name


def create_task_folder(base_dir: str, task_name: str = None) -> Path:
    """
    为每次任务创建独立的文件夹

    Args:
        base_dir: 基础输出目录
        task_name: 任务名称（可选）

    Returns:
        任务文件夹路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if task_name:
        folder_name = f"{timestamp}_{sanitize_filename(task_name)}"
    else:
        folder_name = f"video_{timestamp}"

    task_folder = Path(base_dir).expanduser() / folder_name
    task_folder.mkdir(parents=True, exist_ok=True)

    print(f"📁 创建任务文件夹: {task_folder}")
    return task_folder


def check_recent_tasks(base_dir: str, minutes: int = 5) -> Optional[Path]:
    """
    检查指定分钟内是否创建过任务文件夹
    
    Args:
        base_dir: 基础输出目录
        minutes: 检查的分钟数（默认5分钟）
    
    Returns:
        如果5分钟内创建过任务，返回最新的任务文件夹路径；否则返回None
    """
    base_dir = Path(base_dir).expanduser()
    
    if not base_dir.exists():
        return None
    
    # 获取截止时间（5分钟前）
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    
    # 遍历所有匹配的视频任务文件夹
    task_folders = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.startswith("video_"):
            # 解析时间戳：video_YYYYMMDD_HHMMSS
            try:
                timestamp_str = item.name.split('_', 1)[0]  # 取时间戳部分
                folder_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                # 检查是否在5分钟内
                if folder_time >= cutoff_time:
                    task_folders.append((folder_time, item))
            except (ValueError, IndexError):
                continue
    
    # 按时间排序，返回最新的一个
    if task_folders:
        task_folders.sort(reverse=True)
        latest_folder = task_folders[0][1]
        
        elapsed = datetime.now() - task_folders[0][0]
        print(f"⚠️  检测到 {elapsed.seconds//60} 分钟前创建过任务文件夹: {latest_folder}")
        print(f"🛑 跳过本次视频生成")
        return latest_folder
    
    return None


def generate_script_videos(
    script_file: str,
    first_frame_path: Optional[str] = None,
    last_frame_path: Optional[str] = None,
    output_dir: str = "~/.openclaw/workspace/generated-videos",
    watermark: bool = True,
    framespersecond: Optional[int] = None,
    seed: Optional[int] = None,
    camera_fixed: Optional[bool] = None,
    poll_interval_s: int = 10,
    timeout_s: int = 60 * 20,
) -> List[Dict]:
    """
    根据脚本生成视频（简化版：单场景）

    Args:
        script_file: JSON 脚本文件路径
        first_frame_path: 首帧图片路径
        last_frame_path: 尾帧图片路径（用于首尾帧图生视频）
        output_dir: 输出目录

    Returns:
        生成的视频信息列表 [{"video_path": ...}]
    """
    # 检查5分钟内是否创建过任务
    recent_task = check_recent_tasks(output_dir)
    if recent_task:
        return []
    
    # 读取脚本
    with open(script_file, "r", encoding="utf-8") as f:
        script = json.load(f)

    # 新格式：直接从顶层获取字段
    prompt = script.get("prompt")
    duration = script.get("duration", 5)
    ratio = script.get("ratio", "9:16")
    # resolution = script.get("resolution", "720p")
    resolution = "720p"
    has_audio = script.get("has_audio", False)

    if not prompt:
        raise ValueError("❌ 脚本中没有 prompt 字段")
    
    if duration < 4 or duration > 12:
        raise ValueError(f"⚠️  视频时长 {duration} 秒超出限制 (4-12秒)，暂时不支持")

    print(f"\n{'='*60}")
    print(f"开始生成视频")
    print(f"{'='*60}")
    print(f"提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"时长: {duration}秒")
    print(f"比例: {ratio}")
    print(f"分辨率: {resolution}")
    print(f"音频: {'是' if has_audio else '否'}")

    if first_frame_path:
        print(f"首帧图: {first_frame_path}")
    if last_frame_path:
        print(f"尾帧图: {last_frame_path}")
    print()

    # 创建任务文件夹
    task_folder = create_task_folder(output_dir)

    # 保存脚本副本到任务文件夹
    script_copy_path = task_folder / "script.json"
    with open(script_copy_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    # 生成视频
    video_results = []
    try:
        # 构建输出文件路径
        now_time = datetime.now()
        ms = now_time.strftime('%f')[:3]
        base_time = now_time.strftime('%Y%m%d_%H%M%S')

        # 2 位随机字符
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=2))

        timestamp = f"{base_time}_{ms}_{random_chars}"
        scene_filename = f"{timestamp}_generated.mp4"

        output_file = str(task_folder / scene_filename)

        print(f"\n{'='*60}")
        print(f"🎬 生成视频")
        print(f"{'='*60}")

        task_id = create_video_generation_task(
            prompt=prompt,
            first_frame_path=first_frame_path,
            last_frame_path=last_frame_path,
            duration=duration,
            ratio=ratio,
            resolution=resolution,
            framespersecond=framespersecond,
            seed=seed,
            camera_fixed=camera_fixed,
            watermark=watermark,
            generate_audio=has_audio,
        )
        
        # 查询任务并等待完成
        result = query_video_generation_task(
            task_id=task_id,
            output_file=output_file,
            poll_interval_s=poll_interval_s,
            timeout_s=timeout_s,
        )

        video_results.append(result)

    except Exception as e:
        print(f"❌ 视频生成失败: {e}")
        import traceback
        traceback.print_exc()
        raise

    # 生成摘要
    success_count = len(video_results)

    print(f"\n{'='*60}")
    print(f"{'✅' if success_count == 1 else '❌'}  视频生成完成!")
    print(f"{'='*60}")
    print(f"📁 任务文件夹: {task_folder}")

    if video_results:
        print(f"\n📋 生成结果:")
        for i, r in enumerate(video_results):
            print(f"   [{i+1}] {r.get('video_path', 'N/A')}")

    return video_results


def main():
    parser = argparse.ArgumentParser(
        description="基于 Seedance 的视频生成工具（支持首帧和首尾帧图生视频）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 纯文生视频（无图片输入）
  python3 generate_video.py --script script.json

  # 首帧图生视频（指定首帧，role填写first_frame）
  python3 generate_video.py --script script.json --first-frame first.png

  # 首尾帧图生视频（指定首尾帧，role必须填写）
  python3 generate_video.py --script script.json --first-frame first.png --last-frame last.png

注意:
  首帧图生视频：role 填写 first_frame
  首尾帧图生视频：role 必须填写（first_frame 和 last_frame）
  5分钟内创建过任务则跳过本次生成
        """,
    )

    parser.add_argument(
        "--script",
        required=True,
        help="JSON 脚本文件路径",
    )
    parser.add_argument(
        "--first-frame",
        default=None,
        help="首帧图片路径，用于首帧图生视频模式（role填写first_frame）",
    )
    parser.add_argument(
        "--last-frame",
        default=None,
        help="尾帧图片路径，用于首尾帧图生视频模式（role必须为last_frame）",
    )
    parser.add_argument(
        "--output",
        default="~/.openclaw/workspace/generated-videos",
        help="输出目录（绝对路径，支持 ~ 展开）",
    )
    parser.add_argument("--watermark", action=argparse.BooleanOptionalAction, default=True,
        help="Add watermark to generated video (default: True)")

    args = parser.parse_args()

    # 校验脚本文件（必须是本地文件）
    if not os.path.exists(args.script):
        print(f"❌ 脚本文件不存在: {args.script}", file=sys.stderr)
        sys.exit(1)

    # 校验首帧图片（支持本地文件或远程URL）
    if args.first_frame:
        if _is_remote_url(args.first_frame):
            # 远程URL，直接通过
            pass
        elif _is_local_file(args.first_frame):
            # 本地文件，通过
            pass
        else:
            print(f"❌ 首帧图片无效: {args.first_frame}", file=sys.stderr)
            sys.exit(1)

    # 校验尾帧图片（支持本地文件或远程URL）
    if args.last_frame:
        if _is_remote_url(args.last_frame):
            # 远程URL，直接通过
            pass
        elif _is_local_file(args.last_frame):
            # 本地文件，通过
            pass
        else:
            print(f"❌ 尾帧图片无效: {args.last_frame}", file=sys.stderr)
            sys.exit(1)

    # 校验首尾帧组合
    if args.last_frame and not args.first_frame:
        print(
            f"❌ 参数错误：传入了 --last-frame 但未传入 --first-frame。\n"
            f"首尾帧图生视频需要同时提供首帧和尾帧图片。",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        video_results = generate_script_videos(
            script_file=args.script,
            first_frame_path=args.first_frame,
            last_frame_path=args.last_frame,
            output_dir=args.output,
            watermark=args.watermark
        )
        if video_results:
            print(f"\n🎉 全部完成! 共生成 {len(video_results)} 个视频")
        else:
            print(f"\n⚠️  5分钟内创建过视频生成任务，跳过当前视频生成任务")

    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()