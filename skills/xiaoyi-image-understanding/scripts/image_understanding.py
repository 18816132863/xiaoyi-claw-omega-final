#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小艺图像理解 - 小艺 AI 图像理解 API
根据 SKILL.md 说明实现

用法:
  python image_understanding.py "图片URL"
  python image_understanding.py "图片URL" "描述图中讲了什么"
"""

import uuid
import json
import sys
import os
import requests


def read_xiaoyienv(file_path):
    """
    读取 .xiaoyienv 文件并解析为键值对象

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


def image_understanding(image_url, text="图中讲了什么", debug=False):
    """
    执行图像理解

    Args:
        image_url: 图片 URL
        text: 提示文本（默认"图中讲了什么"）
        debug: 是否打印调试信息

    Returns:
        dict: {"caption": "图像描述文本"} 或 None
    """
    try:
        # 固定的服务 URL
        api_url = "https://hag-drcn.op.dbankcloud.com/celia-claw/v1/sse-api/skill/execute"

        # 读取并校验配置
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

        print(f'✅ 请求 URL：{api_url}')

        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'x-hag-trace-id': str(uuid.uuid4()),
            'x-api-key': config['PERSONAL-API-KEY'],
            'x-request-from': 'openclaw',
            'x-uid': config['PERSONAL-UID'],
            'x-skill-id': 'image_comprehension',
            'x-prd-pkg-name': 'com.huawei.hag'
        }

        # 构建请求体
        payload = {
            "version": "1.0",
            "session": {
                "isNew": False,
                "sessionId": "wangyu202410241921",
                "interactionId": 0
            },
            "endpoint": {
                "device": {
                    "sid": "3df83a4a8124d7600f66206f96ea1e7e4e21c593adc4246bd20d450d8404cbf3",
                    "deviceId": "3f35019f-ba4c-4ed5-80c0-6ddcef741200",
                    "prdVer": "99.0.64.303",
                    "phoneType": "WLZ-AL10",
                    "sysVer": "HarmonyOS_2.0.0",
                    "deviceType": 0,
                    "timezone": "GMT+08:00"
                },
                "locale": "zh-CN",
                "sysLocale": "zh",
                "countryCode": "CN"
            },
            "utterance": {
                "type": "text",
                "original": text
            },
            "actions": [
                {
                    "actionSn": str(uuid.uuid4()),
                    "actionExecutorTask": {
                        "pluginId": "aeac4e92c32949c1b7fc02de262615e6",
                        "agentState": "OnShelf",
                        "actionName": "imageUnderStandStream",
                        "content": {
                            "imageUrl": image_url,
                            "text": text
                        }
                    }
                }
            ]
        }

        if debug:
            print(f'\n[DEBUG] Trace ID: {headers["x-hag-trace-id"]}')
            print(f'[DEBUG] Image URL: {image_url}')
            print(f'[DEBUG] Text: {text}')

        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=120
        )

        if debug:
            print(f'[DEBUG] 响应状态码: {response.status_code}')
            print(f'[DEBUG] Content-Type: {response.headers.get("Content-Type")}')

        if response.status_code != 200:
            print(f'❌ 请求失败: {response.status_code}')
            print(f'❌ 响应内容: {response.text}')
            return None

        # 接收 SSE 流式数据
        last_caption = ""
        line_count = 0
        buffer = ""

        if debug:
            print('\n[DEBUG] 开始接收 SSE 流式数据...\n')

        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk is None:
                continue

            buffer += chunk
            lines = buffer.split('\n')
            buffer = lines.pop()

            for line in lines:
                line_count += 1
                line = line.rstrip('\r')

                if not line:
                    continue

                if debug and line_count <= 10:
                    print(f'[DEBUG] 行 {line_count}: {line[:200]}')

                if line.startswith("data:"):
                    data_content = line[5:].strip()
                    if data_content and data_content != "[DONE]":
                        try:
                            data_json = json.loads(data_content)

                            # 提取 streamContent
                            if 'abilityInfos' in data_json:
                                for info in data_json['abilityInfos']:
                                    if 'actionExecutorResult' in info:
                                        result = info['actionExecutorResult']
                                        if 'reply' in result and 'streamInfo' in result['reply']:
                                            stream_info = result['reply']['streamInfo']
                                            stream_content = stream_info.get('streamContent', '')

                                            # 每次直接覆盖，保留最新（最完整）的内容
                                            if stream_content:
                                                last_caption = stream_content
                                                if debug:
                                                    print(f'[DEBUG] 更新内容: {stream_content}')

                        except json.JSONDecodeError as e:
                            if debug:
                                print(f'[DEBUG] JSON 解析失败: {e}')

        if debug:
            print(f'\n[DEBUG] 共接收 {line_count} 行')
            print(f'[DEBUG] 最终 caption: {last_caption}')

        return {"caption": last_caption} if last_caption else None

    except requests.exceptions.Timeout:
        print('❌ 请求超时（服务器处理时间过长）')
        return None
    except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError) as e:
        # 连接提前关闭，但可能已经收到部分数据
        if debug:
            print(f'⚠️ 连接异常: {e}')
            print(f'⚠️ 但已接收 {line_count} 行')
        return {"caption": last_caption} if last_caption else None
    except Exception as e:
        print(f'❌ 请求异常: {e}')
        import traceback
        traceback.print_exc()
        return None


def format_result(result, image_url):
    """
    格式化输出结果

    Args:
        result: 图像理解结果
        image_url: 图片 URL
    """
    if not result or not result.get('caption'):
        print('🔍 图像理解失败：无法获取图像描述')
        return

    print(f'\n🔍 图像理解结果')
    print(f'🖼️  图片: {image_url}')
    print('=' * 80)
    print(f'\n📝 图像描述:')
    print(f'{result["caption"]}')
    print('\n' + '=' * 80)

    # 🔥 重要：单独打印 JSON 格式结果，确保大模型能直接读取
    print(json.dumps(result, ensure_ascii=False))


def main():
    """主程序"""
    if len(sys.argv) < 2:
        print('小艺图像理解 - 小艺 AI 图像理解')
        print('')
        print('用法:')
        print('  python image_understanding.py "图片URL"')
        print('  python image_understanding.py "图片URL" "描述图中讲了什么"')
        print('')
        print('示例:')
        print('  python image_understanding.py "https://example.com/image.jpg"')
        print('  python image_understanding.py "https://example.com/image.jpg" "这张图片展示了什么"')
        sys.exit(0)

    image_url = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "图中讲了什么"
    debug = '--debug' in sys.argv or '-d' in sys.argv

    result = image_understanding(image_url, text, debug=debug)
    format_result(result, image_url)


# 导出函数供外部调用
__all__ = ['image_understanding']

# 如果直接运行则执行主程序
if __name__ == '__main__':
    main()
