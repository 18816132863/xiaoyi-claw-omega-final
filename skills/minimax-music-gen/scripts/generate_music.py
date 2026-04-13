import os
import requests
import urllib3
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
import random
import string
import uuid

urllib3.disable_warnings()


DEFAULT_SAMPLE_RATE = 44100     # 16000, 24000, 32000, 44100
DEFAULT_BITRATE = 256000        # 32000, 64000, 128000, 256000
DEFAULT_AUDIO_FORMAT = "mp3"    # mp3, wav, pcm


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


def download_audio_file(url, output_path: str):
    """
    下载音频文件到本地目录
    
    Args:
        url (str): 音频文件的URL
        output_path (str): 输出目录，默认为 workspace/generated-musics/
    
    Returns:
        str: 下载的文件路径
    """
    # 确保输出目录存在
    output_path = os.path.expanduser(output_path)
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # 构建输出文件路径
    now_time = datetime.now()
    ms = now_time.strftime('%f')[:3]
    base_time = now_time.strftime('%Y%m%d_%H%M%S')

    # 2 位随机字符
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=2))

    timestamp = f"{base_time}_{ms}_{random_chars}"
    music_filename = f"{timestamp}_generated.mp3"
    
    # 完整的文件路径
    file_path = os.path.join(output_path, music_filename)
    
    try: 
        # 发送GET请求下载文件
        response = requests.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        
        # 获取文件大小（如果服务器提供）
        total_size = int(response.headers.get('content-length', 0))
        
        # 写入文件
        with open(file_path, 'wb') as f:
            if total_size == 0:
                # 服务器未提供文件大小
                f.write(response.content)
                print("下载完成")
            else:
                # 显示下载进度
                downloaded = 0
                chunk_size = 8192
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 显示进度
                        progress = (downloaded / total_size) * 100
                        print(f"\r下载进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
                print()  # 换行
        
        print(f"文件已保存: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"下载失败: {e}")
        # 如果下载失败，删除可能已创建的部分文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise


def generate_music(prompt, lyrics=None, aigc_watermark=True, lyrics_optimizer=False, is_instrumental=False):
    """
    使用MiniMax API生成音乐（SSE流式接口）
    
    Args:
        prompt (str): 音乐风格提示词，例如："Mandopop, Festive, Upbeat, Celebration, New Year"
        lyrics (str): 完整的歌词内容，可以包含[Intro]、[Verse]、[Chorus]等标签
        bitrate (int): 比特率，默认为256000
        audio_format (str): 音频格式，默认为"mp3"
        aigc_watermark (bool): 是否添加AIGC水印，默认为True
        lyrics_optimizer (bool): 是否根据prompt自动生成歌词，默认False
        is_instrumental (bool): 是否生成纯音乐（无人声），默认False
    
    Returns:
        dict: API响应结果，包含音乐URL等信息
    """
    
    # Check environment variables
    required_env = ['PERSONAL-API-KEY', 'PERSONAL-UID', 'SERVICE_URL']

    # 从环境文件中获取API密钥
    env_dict = read_xiaoyienv()
    SERVICE_URL = env_dict.get('SERVICE_URL', '')
    UID = env_dict.get('PERSONAL-UID', '')
    API_KEY = env_dict.get('PERSONAL-API-KEY', '')

    missing = [k for k in required_env if not env_dict.get(k)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    # Configuration
    trace_id = str(uuid.uuid4())
    api_url = f'{SERVICE_URL}/celia-claw/v1/sse-api/skill/execute'
    
    # Build request
    headers = {
        'Content-Type': 'application/json',
        'x-skill-id': 'minimax_music_gen',
        'x-hag-trace-id': trace_id,
        'x-uid': UID,
        'x-api-key': API_KEY,
        'x-request-from': 'openclaw',
    }
    
    # 定义 content 字段
    content = {
        "prompt": prompt,
        "audio_setting": {
            "sample_rate": DEFAULT_SAMPLE_RATE,
            "bitrate": DEFAULT_BITRATE,
            "format": DEFAULT_AUDIO_FORMAT
        },
        "aigc_watermark": aigc_watermark,
        "lyrics_optimizer": lyrics_optimizer,
        "is_instrumental": is_instrumental
    }

    # 只有当lyrics不为空时才添加到请求体
    if lyrics:
        content["lyrics"] = lyrics

    payload = {
        "actions": [
            {
                "actionExecutorTask": {
                    "actionName": "musicGeneration",
                    "content": content,
                    "replyCard": False
                },
                "actionSn": "81ef5ac1b5e74e85b90832503ea34a07"
            }
        ],
        "endpoint": {
            "countryCode": "",
            "device": {
                "deviceId": "5682d99dbb90973b775b7e9bf774ff9f",
                "phoneType": "2in1",
                "prdVer": "11.6.2.202"
            }
        },
        "session": {
            "interactionId": "0",
            "isNew": False,
            "sessionId": "xxx"
        },
        "utterance": {
            "original": "",
            "type": "text"
        },
        "version": "1.0"
    }
    
    # 发送POST请求 - 使用SSE流式接口
    print("正在生成音乐，请耐心等待...")
    response = requests.post(api_url, headers=headers, json=payload, timeout=300, verify=False, stream=True)
    response.raise_for_status()
    
    # 解析SSE流式响应
    final_result = None
    
    for line in response.iter_lines():
        if not line:
            continue
            
        line_str = line.decode('utf-8')
        
        # 跳过非数据行 (如 id: lines)
        if line_str.startswith('id:'):
            continue
            
        # 解析SSE格式: "data: {...}"
        if line_str.startswith('data:'):
            json_str = line_str[5:].strip()  # 去掉 "data:" 前缀
            
            try:
                result = json.loads(json_str)
                
                # 获取 abilityInfos
                ability_infos = result.get('abilityInfos', [])
                if not ability_infos:
                    continue
                
                action_executor_result = ability_infos[0].get('actionExecutorResult', {})
                
                # 检查响应码 (code为"0"表示成功)
                result_code = action_executor_result.get('code', '')
                if result_code != '0':
                    error_desc = action_executor_result.get('desc', 'Unknown error')
                    print(f"API Error: {error_desc}")
                    continue
                
                # 获取流信息
                reply = action_executor_result.get('reply', {})
                stream_info = reply.get('streamInfo', {})
                stream_type = stream_info.get('streamType', '')
                
                # 如果是最终结果，从 content 字段获取音乐数据
                if stream_type == 'final':
                    content = reply.get('content', {})
                    if content and content.get('data', {}).get('audio'):
                        final_result = content
                        break
                        
            except json.JSONDecodeError:
                # 跳过无法解析的行
                continue
    
    if final_result is None:
        raise Exception("未能从流式响应中获取有效的音乐数据")
    
    return final_result


def main():
    """
    主函数：从命令行获取prompt和lyrics，生成音乐并输出
    """
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='使用MiniMax API生成音乐')
    parser.add_argument('--prompt', type=str, help='音乐风格提示词')
    parser.add_argument('--lyrics', type=str, nargs='?', default='', help='歌词内容（可以是文件路径或直接传入歌词），不传则使用lyrics_optimizer自动生成或生成纯音乐')
    parser.add_argument('--output', type=str, default="~/.openclaw/workspace/generated-musics", help='输出目录')
    parser.add_argument('--lyrics-optimizer', action='store_true', help='根据prompt自动生成歌词（当lyrics为空时生效）')
    parser.add_argument('--instrumental', action='store_true', help='生成纯音乐（无人声），此时lyrics字段非必填')
    
    # 解析命令行参数
    args = parser.parse_args()
    prompt = args.prompt
    lyrics = args.lyrics
    
    # 处理歌词参数
    lyrics_content = None
    
    if lyrics:
        # 检查lyrics参数是文件路径还是直接传入的歌词
        if os.path.exists(lyrics):
            # 检查文件扩展名
            if lyrics.endswith('.json'):
                # 读取JSON格式歌词文件
                with open(lyrics, 'r', encoding='utf-8') as f:
                    lyrics_data = json.load(f)
                    lyrics_content = lyrics_data.get('lyrics', '')
                    print(f"已从JSON文件读取歌词: {lyrics}")
            else:
                # 读取纯文本歌词文件
                with open(lyrics, 'r', encoding='utf-8') as f:
                    lyrics_content = f.read()
                    print(f"已从文本文件读取歌词: {lyrics}")
        else:
            lyrics_content = lyrics
            print(f"使用命令行传入的歌词")
    else:
        # lyrics为空
        if args.instrumental:
            print("已启用instrumental模式，将生成纯音乐（无人声）")
        elif not args.lyrics_optimizer:
            print("错误: 未提供歌词内容。请提供歌词、添加 --lyrics-optimizer 参数自动生成歌词，或添加 --instrumental 生成纯音乐")
            print("用法示例:")
            print(f'  python scripts/generate_music.py --prompt "Mandopop, Festive" --lyrics "歌词内容"')
            print(f'  python scripts/generate_music.py --prompt "Mandopop, Festive" --lyrics-optimizer')
            print(f'  python scripts/generate_music.py --prompt "Mandopop, Festive" --instrumental')
            print(f'  python scripts/generate_music.py --prompt "Mandopop, Festive" --lyrics /path/to/lyrics.json')
            exit(1)
        else:
            print("已启用lyrics_optimizer，将根据prompt自动生成歌词")
    
    try:
        # 生成音乐
        result = generate_music(prompt, lyrics_content, 
                               lyrics_optimizer=args.lyrics_optimizer, 
                               is_instrumental=args.instrumental)
        
        # 检查响应是否成功
        if result.get('base_resp', {}).get('status_code') != 0:
            error_msg = result.get('base_resp', {}).get('status_msg', '未知错误')
            raise Exception(f"生成音乐失败: {error_msg}")
        
        # 显示音频URL并下载 (音频URL在 result.data.audio 中)
        audio_url = result.get('data', {}).get('audio', '')
        if audio_url:
            music_path = download_audio_file(audio_url, args.output)
            print("\n" + "=" * 50)
            print("生成音乐成功!")
            print("=" * 50)
            print(f"提示词: {prompt}")
            if args.instrumental:
                print("类型: 纯音乐（无人声）")
            elif lyrics_content:
                print(f"歌词长度: {len(lyrics_content)} 字符")
            else:
                print("歌词: 自动生成")
            print(f"保存路径: {music_path}")
        else:
            print("\n未获取到音频链接")
        
    except Exception as e:
        print(f"生成音乐时发生错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()