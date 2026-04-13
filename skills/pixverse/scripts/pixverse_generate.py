#!/usr/bin/env python3
"""
PixVerse V6 视频生成脚本
爱诗科技 AI 视频生成模型
"""

import sys
import os
import json
import time
import argparse
import requests
import base64
import mimetypes

# API 配置
BASE_URL = os.environ.get("PIXVERSE_BASE_URL", "https://api.pixverse.ai")


def get_api_key():
    """获取 API Key"""
    api_key = os.environ.get("PIXVERSE_API_KEY")
    if not api_key:
        print("❌ 错误: PIXVERSE_API_KEY 环境变量未设置", file=sys.stderr)
        print("请先配置 API Key:", file=sys.stderr)
        print("  1. 访问 https://pixverse.ai 注册账号", file=sys.stderr)
        print("  2. 在控制台获取 API Key", file=sys.stderr)
        print("  3. 设置环境变量: export PIXVERSE_API_KEY='your_key'", file=sys.stderr)
        sys.exit(1)
    return api_key


def get_headers(api_key, async_mode=True):
    """构建请求头"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if async_mode:
        headers["X-Async"] = "true"
    return headers


def encode_local_image(path):
    """将本地图片编码为 base64"""
    if path.startswith(("http://", "https://", "data:")):
        return path
    
    abs_path = os.path.expanduser(path)
    if not os.path.isfile(abs_path):
        print(f"❌ 错误: 文件不存在: {abs_path}", file=sys.stderr)
        sys.exit(1)
    
    mime, _ = mimetypes.guess_type(abs_path)
    if mime is None:
        mime = "image/png"
    
    with open(abs_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    
    print(f"  [base64] 已编码本地文件: {abs_path} ({mime})")
    return f"data:{mime};base64,{b64}"


def text2video(args):
    """文生视频"""
    api_key = get_api_key()
    url = f"{BASE_URL}/v1/video/text2video"
    
    payload = {
        "prompt": args.prompt,
        "duration": args.duration,
        "resolution": args.resolution,
        "style": getattr(args, 'style', 'realistic'),
    }
    
    headers = get_headers(api_key)
    
    print("🎬 [text2video] 提交视频生成任务...")
    print(f"  描述    : {args.prompt}")
    print(f"  时长    : {args.duration}秒")
    print(f"  分辨率  : {args.resolution}")
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        result = resp.json()
        
        if "error" in result:
            print(f"❌ 错误: {result.get('error')}", file=sys.stderr)
            sys.exit(1)
        
        task_id = result.get("task_id") or result.get("data", {}).get("task_id")
        
        print(f"\n✅ 任务已提交!")
        print(f"  任务ID : {task_id}")
        print(f"\n查询结果:")
        print(f"  python3 scripts/pixverse_generate.py get-task --task-id {task_id}")
        
        return task_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def image2video(args):
    """图生视频"""
    api_key = get_api_key()
    url = f"{BASE_URL}/v1/video/image2video"
    
    image_data = encode_local_image(args.image)
    
    payload = {
        "prompt": args.prompt,
        "image": image_data,
        "duration": args.duration,
        "motion_level": getattr(args, 'motion_level', 5),
    }
    
    headers = get_headers(api_key)
    
    print("🎬 [image2video] 提交视频生成任务...")
    print(f"  描述    : {args.prompt}")
    print(f"  图片    : {args.image}")
    print(f"  时长    : {args.duration}秒")
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        result = resp.json()
        
        if "error" in result:
            print(f"❌ 错误: {result.get('error')}", file=sys.stderr)
            sys.exit(1)
        
        task_id = result.get("task_id") or result.get("data", {}).get("task_id")
        
        print(f"\n✅ 任务已提交!")
        print(f"  任务ID : {task_id}")
        print(f"\n查询结果:")
        print(f"  python3 scripts/pixverse_generate.py get-task --task-id {task_id}")
        
        return task_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def get_task(args):
    """查询任务状态"""
    api_key = get_api_key()
    url = f"{BASE_URL}/v1/video/task/{args.task_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    print(f"🔍 [get-task] 查询任务: {args.task_id}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        result = resp.json()
        
        if "error" in result:
            print(f"❌ 错误: {result.get('error')}", file=sys.stderr)
            sys.exit(1)
        
        data = result.get("data", result)
        status = data.get("status", "unknown")
        
        print(f"  任务ID : {args.task_id}")
        print(f"  状态   : {status}")
        
        if status == "completed" or status == "succeeded":
            video_url = data.get("video_url") or data.get("output", {}).get("video_url")
            print(f"  视频   : {video_url}")
            
            # 下载视频
            if video_url and args.download:
                download_video(video_url, args.task_id)
                
        elif status == "failed":
            print(f"  错误   : {data.get('error', 'Unknown error')}")
        else:
            print(f"\n任务进行中，请稍后查询:")
            print(f"  python3 scripts/pixverse_generate.py get-task --task-id {args.task_id}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def download_video(url, task_id):
    """下载视频到本地"""
    output_dir = os.path.expanduser("~/.openclaw/workspace/generated-videos")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"pixverse_{task_id}.mp4")
    
    print(f"\n📥 下载视频到: {output_path}")
    
    try:
        resp = requests.get(url, timeout=120, stream=True)
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 下载完成: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ 下载失败: {e}", file=sys.stderr)
        return None


def poll_task(task_id, timeout=300, interval=10):
    """轮询任务直到完成"""
    api_key = get_api_key()
    url = f"{BASE_URL}/v1/video/task/{task_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    print(f"\n⏳ 等待视频生成 (最长 {timeout} 秒)...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            result = resp.json()
            
            data = result.get("data", result)
            status = data.get("status", "unknown")
            
            elapsed = int(time.time() - start_time)
            print(f"  [{elapsed}s] 状态: {status}")
            
            if status in ("completed", "succeeded"):
                video_url = data.get("video_url") or data.get("output", {}).get("video_url")
                print(f"\n✅ 视频生成完成!")
                print(f"  视频: {video_url}")
                return video_url
                
            elif status == "failed":
                print(f"\n❌ 视频生成失败: {data.get('error', 'Unknown error')}")
                return None
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"  查询出错: {e}")
            time.sleep(interval)
    
    print(f"\n⏱️ 超时，请稍后查询:")
    print(f"  python3 scripts/pixverse_generate.py get-task --task-id {task_id}")
    return None


def main():
    parser = argparse.ArgumentParser(description="PixVerse V6 视频生成")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # text2video
    t2v_parser = subparsers.add_parser("text2video", help="文生视频")
    t2v_parser.add_argument("--prompt", required=True, help="视频描述")
    t2v_parser.add_argument("--duration", type=int, default=5, help="视频时长(秒)")
    t2v_parser.add_argument("--resolution", default="1080P", help="分辨率")
    t2v_parser.add_argument("--style", default="realistic", help="风格")
    t2v_parser.add_argument("--wait", action="store_true", help="等待完成")
    
    # image2video
    i2v_parser = subparsers.add_parser("image2video", help="图生视频")
    i2v_parser.add_argument("--prompt", required=True, help="视频描述")
    i2v_parser.add_argument("--image", required=True, help="图片路径或URL")
    i2v_parser.add_argument("--duration", type=int, default=5, help="视频时长(秒)")
    i2v_parser.add_argument("--motion-level", type=int, default=5, help="运动强度")
    i2v_parser.add_argument("--wait", action="store_true", help="等待完成")
    
    # get-task
    gt_parser = subparsers.add_parser("get-task", help="查询任务")
    gt_parser.add_argument("--task-id", required=True, help="任务ID")
    gt_parser.add_argument("--download", action="store_true", help="下载视频")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "text2video":
        task_id = text2video(args)
        if args.wait and task_id:
            poll_task(task_id)
            
    elif args.command == "image2video":
        task_id = image2video(args)
        if args.wait and task_id:
            poll_task(task_id)
            
    elif args.command == "get-task":
        get_task(args)


if __name__ == "__main__":
    main()
