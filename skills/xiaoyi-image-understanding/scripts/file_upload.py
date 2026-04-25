#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小艺文件上传 - 将本地文件上传到小艺文件存储服务，获取可访问的文件 URL

用法:
  python file_upload.py "/path/to/image.jpg"
  python file_upload.py "/path/to/image.png" --debug
"""

import hashlib
import json
import os
import sys

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


def calculate_sha256(file_path):
    """计算文件的 SHA256 哈希值"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def upload_file(file_path, object_type="TEMPORARY_MATERIAL_DOC", debug=False):
    """
    将本地文件上传到小艺文件存储服务（三阶段上传：prepare → upload → complete）

    Args:
        file_path: 本地文件路径
        object_type: 文件类型（默认 TEMPORARY_MATERIAL_DOC）
        debug: 是否打印调试信息

    Returns:
        dict: {"objectId": "...", "fileUrl": "..."} 或 None
    """
    try:
        # 校验文件存在
        if not os.path.isfile(file_path):
            print(f'❌ 文件不存在：{file_path}')
            return None

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

        base_url = 'https://hag-drcn.op.dbankcloud.com'
        print(f'✅ 文件上传服务地址：{base_url}')

        # 准备文件信息
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_sha256 = calculate_sha256(file_path)
        uid = config['PERSONAL-UID']

        if debug:
            print(f'\n[DEBUG] 文件名: {file_name}')
            print(f'[DEBUG] 文件大小: {file_size} bytes')
            print(f'[DEBUG] SHA256: {file_sha256}')

        # 公共请求头
        common_headers = {
            'Content-Type': 'application/json',
            'x-uid': uid,
            'x-api-key': config['PERSONAL-API-KEY'],
            'x-request-from': 'openclaw',
        }

        # ── 阶段 1: Prepare ──────────────────────────────────────────────────────
        prepare_url = f'{base_url}/osms/v1/file/manager/prepare'
        print(f'\n📤 阶段 1/3 - Prepare 上传请求...')
        if debug:
            print(f'[DEBUG] Prepare URL: {prepare_url}')

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
            timeout=30
        )

        if prepare_resp.status_code != 200:
            print(f'❌ Prepare 请求失败: HTTP {prepare_resp.status_code}')
            print(f'❌ 响应内容: {prepare_resp.text}')
            return None

        prepare_data = prepare_resp.json()

        if debug:
            print(f'[DEBUG] Prepare 响应: {json.dumps(prepare_data, ensure_ascii=False, indent=2)}')

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

        print(f'✅ Prepare 成功: objectId={object_id}')

        # ── 阶段 2: Upload ───────────────────────────────────────────────────────
        print(f'\n📤 阶段 2/3 - 上传文件数据...')
        if debug:
            print(f'[DEBUG] Upload URL: {upload_url}')
            print(f'[DEBUG] Upload Method: {upload_method}')

        with open(file_path, 'rb') as f:
            file_data = f.read()

        upload_resp = requests.request(
            method=upload_method,
            url=upload_url,
            headers=upload_headers,
            data=file_data,
            timeout=120
        )

        if upload_resp.status_code not in (200, 204):
            print(f'❌ 文件上传失败: HTTP {upload_resp.status_code}')
            if debug:
                print(f'[DEBUG] 响应内容: {upload_resp.text}')
            return None

        print(f'✅ 文件上传成功')

        # ── 阶段 3: Complete ─────────────────────────────────────────────────────
        complete_url = f'{base_url}/osms/v1/file/manager/completeAndQuery'
        print(f'\n📤 阶段 3/3 - Complete 完成上传...')
        if debug:
            print(f'[DEBUG] Complete URL: {complete_url}')

        complete_payload = {
            'objectId': object_id,
            'draftId': draft_id,
        }

        complete_resp = requests.post(
            complete_url,
            headers=common_headers,
            json=complete_payload,
            timeout=30
        )

        if complete_resp.status_code != 200:
            print(f'❌ Complete 请求失败: HTTP {complete_resp.status_code}')
            if debug:
                print(f'[DEBUG] 响应内容: {complete_resp.text}')
            return None

        complete_data = complete_resp.json()
        if debug:
            print(f'[DEBUG] Complete 响应: {json.dumps(complete_data, ensure_ascii=False, indent=2)}')

        print(f'✅ Complete 成功')

        # 从 completeAndQuery 响应中直接获取文件下载 URL
        file_url = complete_data.get('fileDetailInfo', {}).get('url', '')

        return {
            'objectId': object_id,
            'fileUrl': file_url,
            'fileName': file_name,
        }

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


def format_result(result, file_path):
    """
    格式化输出结果

    Args:
        result: 上传结果
        file_path: 本地文件路径
    """
    if not result:
        print('❌ 文件上传失败')
        return

    print(f'\n🎉 文件上传完成')
    print(f'📁  本地文件: {file_path}')
    print('=' * 80)
    print(f'🔑 objectId: {result["objectId"]}')
    print(f'🔗 文件 URL: {result["fileUrl"]}')
    print('\n' + '=' * 80)

    # 打印 JSON 格式结果供大模型读取
    print(json.dumps(result, ensure_ascii=False))


def main():
    """主程序"""
    if len(sys.argv) < 2:
        print('小艺文件上传 - 上传本地文件到小艺文件存储服务')
        print('')
        print('用法:')
        print('  python file_upload.py "/path/to/image.jpg"')
        print('  python file_upload.py "/path/to/image.jpg" --debug')
        print('')
        print('示例:')
        print('  python file_upload.py "/tmp/photo.jpg"')
        print('  python file_upload.py "/tmp/photo.png" --debug')
        sys.exit(0)

    file_path = sys.argv[1]
    debug = '--debug' in sys.argv or '-d' in sys.argv

    result = upload_file(file_path, debug=debug)
    format_result(result, file_path)


# 导出函数供外部调用
__all__ = ['upload_file']

# 如果直接运行则执行主程序
if __name__ == '__main__':
    main()
