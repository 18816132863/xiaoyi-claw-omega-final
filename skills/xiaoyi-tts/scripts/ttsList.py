import uuid

import requests
import json

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

        lines = content.split('\n')

        for line in lines:
            if not line or line.strip() == '' or line.strip().startswith('#') or line.strip().startswith('!'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()

        print('✅ .xiaoyienv 文件解析成功')
    except Exception as err:
        print(f'❌ 读取或解析 .xiaoyienv 文件失败：{err}')
        return {}

    return result

def call_tts_list_api():
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

    # 请求头（严格对应 Java 接口的 @RequestHeader）
    headers = {
        "X-Request-ID": "test-request-id-123456",
        "X-Package-Name": "com.example.tts.demo",
        "X-Country-Code": "CN",
        "HMS-APPLICATION-ID": "110594240",
        "X-Mlkit-Version": "1.0.0",
        "Accept": "application/json",
        'x-api-key': config['PERSONAL-API-KEY'],
        'x-uid': config['PERSONAL-UID'],
        'x-hag-trace-id': str(uuid.uuid4()),
        'x-skill-id': 'xiaoyi_tts_list',
        'x-request-from': 'openclaw'
    }

    payload = {

    }

    try:
        # 发送 GET 请求
        response = requests.post(api_url, json=payload, headers=headers)

        # 打印状态码
        print(f"✅ Status Code: {response.status_code}")

        # 尝试解析 JSON
        try:
            result = response.json()
            # 格式化输出，供大模型直接读取
            print(f"✅ 请求成功")
            print("✅ === TTS List ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        except ValueError:
            print("\n响应不是合法 JSON：")
            print(response.text)

    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    call_tts_list_api()