#!/usr/bin/env python3
"""
腾讯混元图像 3.0 (Hunyuan-Image) 图像生成脚本
腾讯自研的文生图大模型
"""

import sys
import os
import json
import time
import argparse
import requests
import base64
import hashlib
import hmac
import mimetypes
from datetime import datetime

# API 配置
BASE_URL = "hunyuan.tencentcloudapi.com"
SERVICE = "hunyuan"
REGION = "ap-guangzhou"
VERSION = "2023-09-01"


def get_credentials():
    """获取腾讯云凭证"""
    secret_id = os.environ.get("TENCENT_SECRET_ID")
    secret_key = os.environ.get("TENCENT_SECRET_KEY")
    
    if not secret_id or not secret_key:
        print("❌ 错误: 腾讯云凭证未配置", file=sys.stderr)
        print("请先配置凭证:", file=sys.stderr)
        print("  1. 访问 https://cloud.tencent.com 注册账号", file=sys.stderr)
        print("  2. 开通混元大模型服务", file=sys.stderr)
        print("  3. 在访问管理 > API密钥管理中创建密钥", file=sys.stderr)
        print("  4. 设置环境变量:", file=sys.stderr)
        print("     export TENCENT_SECRET_ID='your_id'", file=sys.stderr)
        print("     export TENCENT_SECRET_KEY='your_key'", file=sys.stderr)
        sys.exit(1)
    
    return secret_id, secret_key


def sign_request(secret_id, secret_key, action, params):
    """生成腾讯云 API 签名"""
    # 时间戳
    timestamp = int(time.time())
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    
    # 步骤1：拼接规范请求串
    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json; charset=utf-8"
    canonical_headers = f"content-type:{ct}\nhost:{BASE_URL}\n"
    signed_headers = "content-type;host"
    
    payload = json.dumps(params)
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
    canonical_request = (
        f"{http_request_method}\n"
        f"{canonical_uri}\n"
        f"{canonical_querystring}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{hashed_request_payload}"
    )
    
    # 步骤2：拼接待签名字符串
    algorithm = "TC3-HMAC-SHA256"
    credential_scope = f"{date}/{SERVICE}/tc3_request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    
    string_to_sign = (
        f"{algorithm}\n"
        f"{timestamp}\n"
        f"{credential_scope}\n"
        f"{hashed_canonical_request}"
    )
    
    # 步骤3：计算签名
    def hmac_sha256(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
    
    secret_date = hmac_sha256(("TC3" + secret_key).encode("utf-8"), date)
    secret_service = hmac_sha256(secret_date, SERVICE)
    secret_signing = hmac_sha256(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    
    # 步骤4：拼接 Authorization
    authorization = (
        f"{algorithm} "
        f"Credential={secret_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    
    headers = {
        "Authorization": authorization,
        "Content-Type": ct,
        "Host": BASE_URL,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Version": VERSION,
        "X-TC-Region": REGION,
    }
    
    return headers, payload


def text2image(args):
    """文生图"""
    secret_id, secret_key = get_credentials()
    
    # 构建请求参数
    params = {
        "Prompt": args.prompt,
        "NegativePrompt": getattr(args, 'negative_prompt', ""),
        "Style": args.style,
        "Size": args.size.replace("x", "*"),
        "Num": args.quantity,
    }
    
    if args.seed:
        params["Seed"] = args.seed
    
    headers, payload = sign_request(secret_id, secret_key, "TextToImage", params)
    
    print("🎨 [text2image] 生成图像...")
    print(f"  描述    : {args.prompt}")
    print(f"  风格    : {args.style}")
    print(f"  尺寸    : {args.size}")
    print(f"  数量    : {args.quantity}")
    
    try:
        url = f"https://{BASE_URL}"
        resp = requests.post(url, headers=headers, data=payload, timeout=120)
        result = resp.json()
        
        if "Response" in result:
            response = result["Response"]
            if "Error" in response:
                print(f"❌ 错误: {response['Error'].get('Message', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
            
            images = response.get("ResultImage", [])
            
            print(f"\n✅ 生成完成! 共 {len(images)} 张图像")
            
            # 保存图像
            output_dir = os.path.expanduser("~/.openclaw/workspace/generated-images")
            os.makedirs(output_dir, exist_ok=True)
            
            for i, img_data in enumerate(images, 1):
                if img_data.startswith("data:"):
                    # base64 数据
                    img_bytes = base64.b64decode(img_data.split(",", 1)[1])
                else:
                    # URL
                    img_resp = requests.get(img_data, timeout=30)
                    img_bytes = img_resp.content
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(output_dir, f"hunyuan_{timestamp}_{i}.png")
                
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                
                print(f"  [{i}] {output_path}")
            
            return images
        else:
            print(f"❌ 错误: {result}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def encode_local_image(path):
    """将本地图片编码为 base64"""
    if path.startswith(("http://", "https://", "data:")):
        return path
    
    abs_path = os.path.expanduser(path)
    if not os.path.isfile(abs_path):
        print(f"❌ 错误: 文件不存在: {abs_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(abs_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    
    print(f"  [base64] 已编码本地文件: {abs_path}")
    return f"data:image/png;base64,{b64}"


def image_edit(args):
    """图像编辑"""
    secret_id, secret_key = get_credentials()
    
    image_data = encode_local_image(args.image)
    
    params = {
        "Prompt": args.prompt,
        "InputImage": image_data,
        "Strength": args.strength,
    }
    
    headers, payload = sign_request(secret_id, secret_key, "ImageEdit", params)
    
    print("🎨 [image-edit] 编辑图像...")
    print(f"  指令    : {args.prompt}")
    print(f"  图片    : {args.image}")
    print(f"  强度    : {args.strength}")
    
    try:
        url = f"https://{BASE_URL}"
        resp = requests.post(url, headers=headers, data=payload, timeout=120)
        result = resp.json()
        
        if "Response" in result:
            response = result["Response"]
            if "Error" in response:
                print(f"❌ 错误: {response['Error'].get('Message', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
            
            image = response.get("ResultImage", "")
            
            print(f"\n✅ 编辑完成!")
            
            # 保存图像
            output_dir = os.path.expanduser("~/.openclaw/workspace/generated-images")
            os.makedirs(output_dir, exist_ok=True)
            
            if image.startswith("data:"):
                img_bytes = base64.b64decode(image.split(",", 1)[1])
            else:
                img_resp = requests.get(image, timeout=30)
                img_bytes = img_resp.content
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"hunyuan_edit_{timestamp}.png")
            
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            
            print(f"  {output_path}")
            
            return image
        else:
            print(f"❌ 错误: {result}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def super_resolution(args):
    """图像超分"""
    secret_id, secret_key = get_credentials()
    
    image_data = encode_local_image(args.image)
    
    params = {
        "InputImage": image_data,
        "Scale": args.scale,
    }
    
    headers, payload = sign_request(secret_id, secret_key, "ImageSuperResolution", params)
    
    print("🎨 [super-resolution] 图像超分...")
    print(f"  图片    : {args.image}")
    print(f"  放大倍数: {args.scale}x")
    
    try:
        url = f"https://{BASE_URL}"
        resp = requests.post(url, headers=headers, data=payload, timeout=120)
        result = resp.json()
        
        if "Response" in result:
            response = result["Response"]
            if "Error" in response:
                print(f"❌ 错误: {response['Error'].get('Message', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
            
            image = response.get("ResultImage", "")
            
            print(f"\n✅ 超分完成!")
            
            # 保存图像
            output_dir = os.path.expanduser("~/.openclaw/workspace/generated-images")
            os.makedirs(output_dir, exist_ok=True)
            
            if image.startswith("data:"):
                img_bytes = base64.b64decode(image.split(",", 1)[1])
            else:
                img_resp = requests.get(image, timeout=30)
                img_bytes = img_resp.content
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"hunyuan_sr_{args.scale}x_{timestamp}.png")
            
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            
            print(f"  {output_path}")
            
            return image
        else:
            print(f"❌ 错误: {result}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="腾讯混元图像 3.0")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # text2image
    t2i_parser = subparsers.add_parser("text2image", help="文生图")
    t2i_parser.add_argument("--prompt", required=True, help="图像描述")
    t2i_parser.add_argument("--negative-prompt", default="", help="负面提示词")
    t2i_parser.add_argument("--style", default="realistic", help="风格")
    t2i_parser.add_argument("--size", default="1024x1024", help="尺寸")
    t2i_parser.add_argument("--quantity", type=int, default=1, help="数量")
    t2i_parser.add_argument("--seed", type=int, help="随机种子")
    
    # image-edit
    ie_parser = subparsers.add_parser("image-edit", help="图像编辑")
    ie_parser.add_argument("--prompt", required=True, help="编辑指令")
    ie_parser.add_argument("--image", required=True, help="图片路径或URL")
    ie_parser.add_argument("--strength", type=float, default=0.8, help="编辑强度")
    
    # super-resolution
    sr_parser = subparsers.add_parser("super-resolution", help="图像超分")
    sr_parser.add_argument("--image", required=True, help="图片路径或URL")
    sr_parser.add_argument("--scale", type=int, default=4, choices=[2, 4], help="放大倍数")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "text2image":
        text2image(args)
    elif args.command == "image-edit":
        image_edit(args)
    elif args.command == "super-resolution":
        super_resolution(args)


if __name__ == "__main__":
    main()
