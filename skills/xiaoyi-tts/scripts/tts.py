#!/usr/bin/env python3
"""
TTS 请求脚本（支持自定义帧解析，过滤音素数据）
一次性接收 Base64 编码的完整流 → 解码为二进制 → 逐帧解析 → 提取纯音频
"""

import argparse
import base64
import sys
from datetime import datetime

import requests
import uuid
import struct
from pathlib import Path
from io import BytesIO  # 关键：把二进制数据变成可读取的流


def parse_args():
    parser = argparse.ArgumentParser(description="发送 TTS 请求并保存音频文件")
    parser.add_argument("--text", required=True, help="要合成的文本内容")
    parser.add_argument("--language", default="zh-Hans", help="语言代码")
    parser.add_argument("--person", default="zh-Hans-st-1", help="发音人")
    parser.add_argument("--speed", default="5.0", help="语速")
    parser.add_argument("--pitch", default="5.0", help="音调")
    parser.add_argument("--volume", default="5.0", help="音量")
    return parser.parse_args()


def read_exact(stream: BytesIO, length: int) -> bytes:
    """从二进制流中精确读取指定长度字节"""
    data = stream.read(length)
    if len(data) != length:
        raise EOFError(f"期望 {length} 字节，实际收到 {len(data)} 字节")
    return data


class FrameHeader:
    def __init__(self, header_bytes: bytes):
        if len(header_bytes) != 8:
            raise ValueError("帧头必须是 8 字节")

        b0, b1, b2, b3, b4, b5, b6, b7 = struct.unpack("8B", header_bytes)
        self.error_code = (b0 >> 4) & 0xF
        self.reply_type = b0 & 0xF  # 2 = 音素帧，其他 = 音频帧
        self.content_length = ((b1 & 0xFF) << 14) | ((b2 & 0xFF) << 6) | ((b3 & 0xFF) >> 2)
        self.has_more = b3 & 0x3
        self.start_offset = ((b4 & 0xFF) << 8) | (b5 & 0xFF)
        self.text_length = ((b6 & 0xFF) << 8) | (b7 & 0xFF)


def process_frames(base64_str: str, output_path: Path):
    """
    1. Base64 解码 → 二进制流
    2. 逐帧解析 8 字节头
    3. 过滤音素帧（type=2）
    4. 只写入音频数据到 MP3
    """
    # ========== 第一步：Base64 解码成完整二进制 ==========
    try:
        total_binary = base64.b64decode(base64_str)
    except Exception as e:
        print(f"❌ Base64 解码失败: {e}")
        raise

    # ========== 第二步：包装成可读取的流 ==========
    stream = BytesIO(total_binary)

    # ========== 第三步：逐帧解析 ==========
    total_audio_bytes = 0
    frame_count = 0
    audio_frame_count = 0

    # 先清空输出文件
    with open(output_path, "wb") as f:
        pass

    try:
        while True:
            # 1. 读 8 字节头
            header_bytes = read_exact(stream, 8)
            frame = FrameHeader(header_bytes)
            frame_count += 1

            if frame.error_code != 0:
                print(f"⚠️  帧 {frame_count} 错误码: {frame.error_code}")

            # 2. 读对应长度的数据
            data = read_exact(stream, frame.content_length)

            # 3. 过滤音素帧（type=2 丢弃）
            if frame.reply_type == 2:
                print(f"[帧 {frame_count}] 音素数据，已丢弃")
            else:
                audio_frame_count += 1
                total_audio_bytes += len(data)
                print(f"[帧 {frame_count}] 音频数据，大小 {len(data)} 字节")
                # 追加写入文件
                with open(output_path, "ab") as f:
                    f.write(data)

            # 4. 结束判断
            if frame.has_more == 0:
                print("\n✅ 所有帧解析完成")
                break

    except EOFError:
        print("\n✅ 流读取完毕（正常结束）")

    print(f"\n📊 统计：总帧数 {frame_count}，音频帧 {audio_frame_count}，音频总大小 {total_audio_bytes} 字节")
    print(f"✅ 纯音频已保存到：{output_path.absolute()}")


def read_xiaoyienv(file_path):
    """
    读取 .env 文件并解析为键值对象

    Args:
        file_path: 文件路径

    Returns:
        dict: 解析后的属性对象
    """
    result = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 按行分割
        lines = content.split('\n')

        for line in lines:
            # 跳过空行或注释行（以 # 或 ! 开头的行）
            if not line or line.strip() == '' or line.strip().startswith('#') or line.strip().startswith('!'):
                continue

            # 使用等号分割
            if '=' in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()

        print('✅ .xiaoyienv 文件解析成功')
    except Exception as err:
        print(f'❌ 读取或解析 .xiaoyienv 文件失败：{err}')
        return {}

    return result

def main():
    args = parse_args()

    payload = {
        "data": {
            "language": args.language,
            "text": args.text
        },
        "config": {
            "person": args.person,
            "codec": 3,
            "sampleRate": 1,
            "speed": args.speed,
            "pitch": args.pitch,
            "volume": args.volume,
            "type": 0,
            "audioType": "mp3",
            "frameFormat": 0,
            "compressRate": 24
        }
    }

    xiaoyi_path = "/home/sandbox/.openclaw/.xiaoyienv"
    config = read_xiaoyienv(xiaoyi_path)
    required_keys = ['PERSONAL-API-KEY', 'PERSONAL-UID']
    check_result = True

    for key in required_keys:
        if key in config:
            print(f'✅ key "{key}" 存在：{config[key]}')
        else:
            print(f'❌ key "{key}" 不存在：失败...')
            check_result = False

    if not check_result:
        return None

    # 固定的服务 URL
    api_url_prefix = config['SERVICE_URL']
    api_url_suffix = "/celia-claw/v1/rest-api/skill/execute"
    api_url = api_url_prefix + api_url_suffix
    print(f'✅ 请求 URL：{api_url}')

    headers = {
        "Content-Type": "application/json",
        "X-Request-ID": str(uuid.uuid4()),
        "X-Package-Name": "com.example.tts.demo",
        "X-Country-Code": "CN",
        "HMS-APPLICATION-ID": "123456789",
        "X-Mlkit-Version": "1.0.0",
        "x-skill-id": "xiaoyi_tts",
        "x-hag-trace-id": str(uuid.uuid4()),
        'x-api-key': config['PERSONAL-API-KEY'],
        'x-uid': config['PERSONAL-UID'],
        'x-request-from': 'openclaw'
    }

    # 发送请求
    try:
        response = requests.post(api_url, json=payload, headers=headers)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return

    if response.status_code != 200:
        print(f"❌ HTTP 错误 {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        return
    filename = datetime.now().strftime("%Y%m%d%f")[:-3]  # 微秒转毫秒
    output = args.language + "-" + filename + ".mp3"
    # 核心处理
    process_frames(response.text.strip(), Path(output))


if __name__ == "__main__":
    main()