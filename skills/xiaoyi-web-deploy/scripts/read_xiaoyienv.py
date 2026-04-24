import os
import uuid

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

if __name__ == '__main__':
    env_dict = read_xiaoyienv()
    SERVICE_URL = env_dict.get('SERVICE_URL', '')
    UID = env_dict.get('PERSONAL-UID', '')
    API_KEY = env_dict.get('PERSONAL-API-KEY', '')
    trace_id = str(uuid.uuid4())
    output_dict = {
        "xiaoyiBaseUrl": SERVICE_URL,
        "xiaoyiUserId": UID,
        "xiaoyiApiKey": API_KEY,
        "xiaoyiTraceId": trace_id,
    }
    print(output_dict)