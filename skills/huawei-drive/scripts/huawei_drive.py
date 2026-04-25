import argparse
import json
import os
import shutil
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import logging
import requests
import sys
import zipfile
import time
import tempfile
import re

zip_input_files_url = "https://h5hosting-drcn.dbankcdn.cn/cch5/HAG/D1E0CiDwLKSTla6LZEqEHDzqA/import.json"
BASE_DIR = "/home/sandbox/.openclaw"
PARENT_FOLDER_NAME = "小艺Claw"
DRIVE_URL_PATH = "/drive/v1/files"
QUERY_ROOT_PARAM = "&queryParam=recycled=false%20and%20parentFolder='root'%20and%20"
QUERY_FILE_FIELDS = "files(mimeType,size,editedTime,fileName)"
MAX_TIMEOUT = 30
QUERY_ERROR = "查询异常"
QUERY_FAIL = "查询失败"
FOLDER_NOT_EXIST = "小艺Claw目录不存在"
FILE_NOT_EXIST = "文件不存在"


# 日志文件路径
LOG_DIR = os.path.join(tempfile.gettempdir(), "logs")
print("log:", LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, f"{os.path.basename(__file__).replace('.py', '')}.log")


# 创建日志目录并设置权限
os.makedirs(LOG_DIR, mode=0o700, exist_ok=True)

# 创建日志文件并设置权限（如果不存在）
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f1:
        pass
    os.chmod(LOG_FILE, 0o600)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# Token 过期错误提示
TOKEN_EXPIRED_MESSAGE = {
    "status": "error",
    "error_code": "TOKEN_EXPIRED",
    "message": "云空间授权已过期，请退出小艺Claw后重新进入，系统将自动刷新授权。"
}


def check_token_expired(response):
    """
    检查响应是否表示 token 过期
    :param response: HTTP 响应对象
    :return: True 如果 token 过期，否则 False
    """
    if response.status_code == 401:
        return True
    # 有些接口可能返回 403 或其他状态码表示授权问题
    if response.status_code == 403:
        try:
            result = response.json()
            # 检查是否是授权相关的错误
            if 'code' in result and result.get('code') in [401, 403, 'Unauthorized', 'Forbidden']:
                return True
        except:
            pass
    return False


def print_token_expired():
    """打印 token 过期的友好提示"""
    print(json.dumps(TOKEN_EXPIRED_MESSAGE, ensure_ascii=False))


class UploadFileHwDrive(object):
    def __init__(self, auth):
        self.trace_id = str(uuid.uuid4())[:16]
        self.auth = f"Bearer {auth}"

    def about_get(self):
        """
        调用 /drive/v1/about 接口云空间用户相关信息
        :return: 用户相关信息
        """
        base_url = get_base_url()
        url = f"{base_url}/drive/v1/about?fields=*"
        headers = {
            "Authorization": self.auth
        }
        try:
            response = requests.get(url, headers=headers, timeout=MAX_TIMEOUT)
            if check_token_expired(response):
                logger.error("Token expired in about_get")
                return {"error": "TOKEN_EXPIRED"}
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"Error: An error occurred while creating directory: {e}")
            return None


    def get_celiaclaw_file_id(self):
        base_url = get_base_url()
        url = f"{base_url}{DRIVE_URL_PATH}?fields=files(id){QUERY_ROOT_PARAM}fileName='{PARENT_FOLDER_NAME}'"
        headers = {
            "Authorization": self.auth
        }
        try:
            response = requests.get(url, headers=headers, timeout=MAX_TIMEOUT)
            if check_token_expired(response):
                logger.error("Token expired in get_celiaclaw_file_id")
                return "TOKEN_EXPIRED"
            if response.status_code == 200:
                result = response.json()
                if result["files"]:
                    file_id = result["files"][0]["id"]
                    return file_id
                else:
                    return ""
            else:
                logger.error(f"Response: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error: An error occurred while creating directory: {e}")
            return ""


    def get_file_list(self, folder_id):
        """
        查询云盘指定路径下的所有文件列表（支持分页）
        :param folder_id: 云盘路径ID（父文件夹ID）
        :return: 文件列表JSON数据，失败返回None
        """
        base_url = get_base_url()
        all_files = []
        next_cursor = None
        page_count = 0
        
        while True:
            page_count += 1
            # 构建URL，包含分页参数
            url = f"{base_url}{DRIVE_URL_PATH}?fields={QUERY_FILE_FIELDS},nextCursor&queryParam=parentFolder='{folder_id}'&pageSize=100"
            if next_cursor:
                url += f"&cursor={next_cursor}"
            
            headers = {
                "Authorization": self.auth
            }
            logger.info(f"get_file_list page {page_count}, url: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=MAX_TIMEOUT)
                if response.status_code == 200:
                    result = response.json()
                    # 获取当前页的文件列表
                    files = result.get('files', [])
                    all_files.extend(files)
                    logger.info(f"get_file_list page {page_count}, files count: {len(files)}")
                    
                    # 检查是否还有下一页
                    next_cursor = result.get('nextCursor')
                    if not next_cursor:
                        # 没有更多数据，退出循环
                        break
                else:
                    logger.error(f"Response: {response.text}")
                    return f"{QUERY_FAIL},{response.text}"
            except Exception as e:
                logger.error(f"Error: An error occurred while getting file list: {e}")
                return f"{QUERY_ERROR},e"
        
        logger.info(f" total files count: {len(all_files)}")
        return all_files

    def get_space_detail(self):
        result = self.about_get()
        if result is None:
            logger.error(f"get cloud drive space failed")
            return 0
        if result == {"error": "TOKEN_EXPIRED"}:
            return "TOKEN_EXPIRED"
        print(f"总空间：{result["storageQuota"]["userCapacity"]}")
        print(f"已用空间：{result["storageQuota"]["usedSpace"]}")
        print(f"可用空间：{int(result["storageQuota"]["userCapacity"]) - int(result["storageQuota"]["usedSpace"])}")
        return result

    def get_clouddrive_available_space(self):
        result = self.about_get()
        if result is None:
            logger.error(f"get cloud drive space failed")
            return 0
        if result == {"error": "TOKEN_EXPIRED"}:
            return "TOKEN_EXPIRED"
        available_space = int(result["storageQuota"]["userCapacity"]) - int(result["storageQuota"]["usedSpace"])
        print(f"可用空间{available_space}")
        return available_space

    def check_space(self, file_size):
        available_space = self.get_clouddrive_available_space()
        if available_space == "TOKEN_EXPIRED":
            return "TOKEN_EXPIRED"
        if available_space < file_size:
            logger.error(f"file size {file_size} is less than available space {available_space}")
            return False
        else:
            return True

    def check_file_exists(self, file_name, folder_id):
        """
        检查云盘中是否存在指定文件名的文件
        :param file_name: 文件名
        :param folder_id: 文件夹ID
        :return: 存在返回True，不存在返回False
        """
        base_url = get_base_url()
        query_param = f"&queryParam=recycled=false%20and%20parentFolder='{folder_id}'%20and%20"
        url = f"{base_url}{DRIVE_URL_PATH}?fields={QUERY_FILE_FIELDS}{query_param}fileName='{file_name}'"
        headers = {
            "Authorization": self.auth
        }
        try:
            response = requests.get(url, headers=headers, timeout=MAX_TIMEOUT)
            if check_token_expired(response):
                logger.error("Token expired in check_file_exists")
                return "TOKEN_EXPIRED"
            if response.status_code == 200:
                result = response.json()
                if result.get("files"):
                    logger.info(f"the file {file_name} exists in the cloud drive")
                    return result.get("files")
                else:
                    logger.info(f"the file {file_name} does not exists in cloud drive")
                    return f"{FILE_NOT_EXIST}"
            else:
                logger.error(f"Response: {response.text}")
                return f"{QUERY_FAIL},{response.text}"
        except Exception as e:
            logger.error(f"Error: An error occurred while checking folder exists: {e}")
            return f"{QUERY_ERROR}, {e}"

    def check_folder_exists(self, folder_name):
        """
        检查云盘根目录下是否存在指定名称的文件夹
        :param folder_name: 文件夹名称
        :return: 存在返回True，不存在返回False
        """
        base_url = get_base_url()
        url = f"{base_url}{DRIVE_URL_PATH}?fields=files(id){QUERY_ROOT_PARAM}fileName='{folder_name}'"
        headers = {
            "Authorization": self.auth
        }
        try:
            response = requests.get(url, headers=headers, timeout=MAX_TIMEOUT)
            if check_token_expired(response):
                logger.error("Token expired in check_folder_exists")
                return "TOKEN_EXPIRED"
            if response.status_code == 200:
                result = response.json()
                if result.get("files"):
                    logger.info(f"the folder {folder_name} exists in the cloud drive")
                    return "小艺Claw目录存在"
                else:
                    logger.info(f"the folder {folder_name} does not exists in cloud drive")
                    return "小艺Claw目录不存在"
            else:
                logger.error(f"Response: {response.text}")
                return f"{QUERY_FAIL}, {response.text}"
        except Exception as e:
            logger.error(f"Error: An error occurred while checking folder exists: {e}")
            return f"{QUERY_ERROR}, {e}"

    # 创建云空间目录
    def create_file_dir(self,dir_name):
        """
        调用 /drive/v1/files 接口创建文件夹
        :return: 创建的文件夹信息
        """
        cloud_namespace_base_url = get_base_url()
        url = f"{cloud_namespace_base_url}{DRIVE_URL_PATH}?fields=id,fileName&autoRename=false"
        data = {
            "parentFolder": ["root"],
            "fileName": dir_name,
            "mimeType": "application/vnd.huawei-apps.folder"
        }
        create_trace_id = f"{self.trace_id}_create"
        headers = {
            "Authorization": self.auth
        }
        logger.info("create dir trace_id: {}".format(create_trace_id))

        try:
            response = requests.post(url, headers=headers, json=data, verify=True, timeout=MAX_TIMEOUT)
            if check_token_expired(response):
                logger.error("Token expired in create_file_dir")
                return "TOKEN_EXPIRED"
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(f"Error: Failed to create directory, status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error: An error occurred while creating directory: {e}")
            print(e)
            return None

    def query_file(self, file_name, parent_folder_id):
        base_url = get_base_url()
        query_file_params = \
            f"&queryParam=recycled=false%20and%20parentFolder='{parent_folder_id}'%20and%20fileName='{file_name}'"
        url = f"{base_url}{DRIVE_URL_PATH}?fields=files(id){query_file_params}"
        headers = {
            "Authorization": self.auth
        }
        try:
            response = requests.get(url, headers=headers, timeout=MAX_TIMEOUT)
            if check_token_expired(response):
                logger.error("Token expired in query_file")
                return "TOKEN_EXPIRED"
            if response.status_code == 200:
                result = response.json()
                if result["files"]:
                    file_id = result["files"][0]["id"]
                    return file_id
                else:
                    return ""
            else:
                print(f"Response: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error: An error occurred while creating directory: {e}")
            print(e)
            return ""


    def create_file_content(self, file_name, content):
        cloud_namespace_base_url = get_base_url()
        url = f"{cloud_namespace_base_url}/upload/drive/v1/files?uploadType=content&fields=*"
        headers = {
            "Authorization": self.auth,
            "x-hw-properties": f"filename={file_name}"
        }

        try:
            response = requests.post(url, headers=headers, data=content, verify=True, timeout=MAX_TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(f"Error: Failed to create file, status code: {response.status_code}")
                logger.info(f"Response: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error: An error occurred while creating file: {e}")
            print(e)
            return None

    # 创建云空间文件
    def create_file_resume(self, file_name, file_id, file_size):
        cloud_namespace_base_url = get_base_url()
        url = f"{cloud_namespace_base_url}/upload/drive/v1/files?uploadType=resume&fields=*"
        data = {
            "parentFolder": [file_id],
            "fileName": file_name
        }
        create_trace_id = f"{self.trace_id}_create_resume"
        headers = {
            "Authorization": self.auth,
            "X-Upload-Content-Length": file_size,
            "x-hw-trace-id": create_trace_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        logger.info("create trace_id: {}".format(create_trace_id))

        try:
            response = requests.post(url, headers=headers, json=data, verify=True, timeout=MAX_TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                headers = response.headers
                logger.info(f"headers = {headers}")
                resultHeader = response.headers.get("Location")
                logger.info(f"resultHeader = {resultHeader}")
                result["uploadUrl"] = resultHeader
                return result
            else:
                logger.error(f"Error: Failed to create resume, status code: {response.status_code}")
                logger.info(f"Response: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error: An error occurred while creating resume: {e}")
            print(e)
            return None


    def update_file_resume(self, file_name, file_id, file_size, parent_folder_id):
        cloud_namespace_base_url = get_base_url()
        url = f"{cloud_namespace_base_url}/upload/drive/v1/files/{file_id}?uploadType=resume&fields=*"
        data = {
            "fileName": file_name,
            "parentFolder": [parent_folder_id],
        }
        create_trace_id = f"{self.trace_id}_create_resume"
        headers = {
            "Authorization": self.auth,
            "X-Upload-Content-Length": file_size,
            "x-hw-trace-id": create_trace_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            response = requests.patch(url, headers=headers, json=data, verify=True, timeout=MAX_TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                headers = response.headers
                logger.info(f"headers = {headers}")
                resultHeader = response.headers.get("Location")
                logger.info(f"resultHeader = {resultHeader}")
                result["uploadUrl"] = resultHeader
                return result
            else:
                logger.error(f"Error: Failed to create resume, status code: {response.status_code}")
                logger.info(f"Response: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error: An error occurred while creating resume: {e}")
            print(e)
            return None


    def upload_file_in_chunks(self, server_id, upload_id, file_path, chunk_size=67108864):
        """
        循环上传 ZIP 文件，每次上传固定大小的块
        :param server_id: 服务器 ID
        :param upload_id: 上传 ID
        :param file_path: 文件路径
        :param chunk_size: 每次上传的字节数（默认 64MB）
        :return: 上传结果
        """
        if not os.path.exists(file_path):
            logger.info("文件不存在")
            return None

        file_size = os.path.getsize(file_path)
        logger.info(f"文件大小: {file_size} 字节")
        cloud_namespace_base_url = get_base_url()
        upload_trace_id = f"{self.trace_id}_upload"
        start_byte = 0

        while start_byte < file_size:
            end_byte = min(start_byte + chunk_size - 1, file_size - 1)
            content_range = f"bytes {start_byte}-{end_byte}/{file_size}"
            logger.info(f"上传范围: {content_range}")

            # 分块读取文件内容，避免一次性加载大文件到内存
            with open(file_path, "rb") as f:
                f.seek(start_byte)
                chunk_data = f.read(end_byte - start_byte + 1)

            url = f"{cloud_namespace_base_url}/upload/drive/v1/{server_id}/files"
            request_url = f"{url}?fields=*&uploadType=resume&uploadId={upload_id}"

            headers = {
                "Authorization": self.auth,
                "Content-Type": "application/json;charset=UTF-8",
                "Content-Range": content_range,
                "x-hw-trace-id": upload_trace_id,
            }
            try:
                response = requests.put(
                    request_url,
                    headers=headers,
                    data=chunk_data,
                    verify=True,
                    timeout=MAX_TIMEOUT
                )
                if response.status_code == 308:
                    start_byte = end_byte + 1
                    continue
                if response.status_code == 200:
                    logger.info("上传成功")
                else:
                    logger.info(f"响应内容: {response.text}")
                    return None
            except Exception as e:
                logger.error(f"请求异常: {e}")
                return None

        # 文件上传完成后，调用一次接口，不传Content-Range，传Content-Length为0
        final_url = f"{cloud_namespace_base_url}/upload/drive/v1/{server_id}/files"
        final_request_url = f"{final_url}?fields=*&uploadType=resume&uploadId={upload_id}"
        final_headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json;charset=UTF-8",
            "Content-Length": "0"
        }
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.put(
                    final_request_url,
                    headers=final_headers,
                    data=b"",
                    verify=True,
                    timeout=MAX_TIMEOUT
                )
                if response.status_code == 200:
                    response_text = response.text
                    response_json = json.loads(response_text)
                    logger.info(f"上传完成接口调用成功，返回的文件ID : {str(response_json.get('id'))}")
                    return response_json.get("id")
                elif response.status_code == 308:
                    retry_count += 1
                    logger.info(f"上传完成接口返回308，等待2秒后重试（第{retry_count}次）")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"上传完成接口调用失败，状态码: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
                    return None
            except Exception as e:
                logger.info(f"上传完成接口调用异常: {e}")
                return None

        logger.error(f"上传完成接口重试{max_retries}次后仍返回308，放弃")
        return None

def parse_url(url):
    """
    解析 URL，提取 server_id 和 uploadId
    :param url: 完整的 URL
    :return: server_id 和 uploadId
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    query_params = parse_qs(parsed_url.query)

    server_id = path_parts[4] if len(path_parts) > 4 else None
    upload_id = query_params.get("uploadId", [None])[0]

    return server_id, upload_id


def get_properties(url, setting_key):
    try:
        response = requests.get(url, stream=True, timeout=MAX_TIMEOUT)
        response.raise_for_status()
        # 解析 JSON 内容
        try:
            content = response.json()
        except requests.exceptions.JSONDecodeError:
            logging.error("下载的文件不是有效的 JSON 格式。")
            return None

        # 读配置
        result = content.get(setting_key)
        logger.info(f"json content: {result}")
        return result
    except Exception as e:
        return None

def get_base_url():
    return get_properties(zip_input_files_url, "cloud_namespace_drive_base_url")

def get_drive_token():
    file_path = "/home/sandbox/.openclaw/.xiaoyienv"
    with open(file_path, 'r') as file:
        content = file.read()
    # 使用正则表达式解析内容
    key_value_pattern = re.compile(r'([^=\s]+)\s*=\s*(.+)')
    config = key_value_pattern.findall(content)
    for key, value in config:
        if (key == "USER_CREDENTIAL_TEMP_DRIVE_TOKEN"):
            return value
    return ""

def set_upload_result(result, status, message):
    result["status"] = status
    result["message"] = message
    logger.info(json.dumps(result))
    print(json.dumps(result, ensure_ascii=False))


def query_space_detail(auth):
    """
    查询云空间详情
    :param auth: 认证token
    :return: int类型可用空间
    """
    hw_drive = UploadFileHwDrive(auth)
    result = hw_drive.get_space_detail()
    return result

def query_available_space(auth):
    """
    查询云空间剩余可用空间
    :param auth: 认证token
    :return: int类型可用空间
    """
    hw_drive = UploadFileHwDrive(auth)
    available_space = hw_drive.get_clouddrive_available_space()
    if available_space == "TOKEN_EXPIRED":
        print_token_expired()
        return -1
    logger.info(f"available space is {available_space}")
    return int(available_space)


def get_celiaclaw_file_list(auth):
    """
    查询文件是否存在
    :param auth: 认证token
    :return: 小艺Claw目录下的文件列表
    """
    hw_drive = UploadFileHwDrive(auth)
    folder_id = hw_drive.get_celiaclaw_file_id()
    if folder_id == "TOKEN_EXPIRED":
        print_token_expired()
        return "TOKEN_EXPIRED"
    if folder_id == "":
        print(f"{FOLDER_NOT_EXIST}")
        return f"{FOLDER_NOT_EXIST}"
    result = hw_drive.get_file_list(folder_id)
    print(result)
    return result

def query_file_exists(auth, file_name):
    """
    查询文件是否存在
    :param auth: 认证token
    :param file_name: 文件名
    :return: 0表示存在，1表示不存在
    """
    hw_drive = UploadFileHwDrive(auth)
    parent_folder_id = hw_drive.get_celiaclaw_file_id()
    if parent_folder_id == "TOKEN_EXPIRED":
        print_token_expired()
        return "TOKEN_EXPIRED"
    if parent_folder_id == "":
        # 文件夹不存在，文件也不存在
        print(f"{FILE_NOT_EXIST}")
        return f"{FILE_NOT_EXIST}"
    result = hw_drive.check_file_exists(file_name, parent_folder_id)
    print(result)
    return result


def query_folder_exists(auth, folder_name):
    """
    查询文件夹是否存在
    :param auth: 认证token
    :param folder_name: 文件夹名称
    :return: 0表示存在，1表示不存在,
    """
    hw_drive = UploadFileHwDrive(auth)
    result = hw_drive.check_folder_exists(folder_name)
    if result == "TOKEN_EXPIRED":
        print_token_expired()
    print(result)
    return result


def create_folder(auth, folder_name):
    """
    在云盘根路径下创建文件夹
    :param auth: 认证token
    :param folder_name: 文件夹名称
    """
    if (folder_name != PARENT_FOLDER_NAME):
        logger.error("the folder name is not allowed")
        return 1
    hw_drive = UploadFileHwDrive(auth)
    create_result = hw_drive.create_file_dir(folder_name)
    if create_result == "TOKEN_EXPIRED":
        print_token_expired()
        return -1
    if create_result:
        logger.info(f"create the folder {folder_name} success")
        return 0
    else:
        logger.info(f"create the folder {folder_name} fail")
        return 1


def upload_file_to_celiaclaw(auth, file_path, mode):
    """
    resume的方式上传指定文件到云空间
    """
    result = {
        "status": "success",
        "mode": "upload",
        "file_id": None,
        "file_path": file_path
    }
    if auth == "":
        set_upload_result(result, "error", "auth is empty")
        return
    if not os.path.exists(file_path):
        set_upload_result(result, "error", f"本地文件不存在: {file_path}")
        return
    hw_drive = UploadFileHwDrive(auth)
    parent_folder_id = hw_drive.get_celiaclaw_file_id()
    
    # 检测 token 是否过期
    if parent_folder_id == "TOKEN_EXPIRED":
        print_token_expired()
        return -1
    
    if parent_folder_id == "":
        # 创建小艺根目录
        create_folder_result = hw_drive.create_file_dir(PARENT_FOLDER_NAME)
        if create_folder_result == "TOKEN_EXPIRED":
            print_token_expired()
            return -1
        if create_folder_result:
            parent_folder_id = create_folder_result["id"]
    if parent_folder_id == "":
        set_upload_result(result, "error", "创建文件夹失败")
        return

    try:
        # 创建云空间文件
        file_name = os.path.basename(file_path)
        file_size = str(os.path.getsize(file_path))
        space_check = hw_drive.check_space(int(file_size))
        if space_check == "TOKEN_EXPIRED":
            print_token_expired()
            return -1
        if not space_check:
            set_upload_result(result, "error", "云空间不足")
            return

        file_id = hw_drive.query_file(file_name, parent_folder_id)
        if file_id == "TOKEN_EXPIRED":
            print_token_expired()
            return -1
        if not file_id == "" and mode == "overwrite":
            create_resume_result = hw_drive.update_file_resume(file_name, file_id, file_size, parent_folder_id)
        else:
            create_resume_result = hw_drive.create_file_resume(
                f"{file_name}",
                parent_folder_id,
                file_size
            )

        if create_resume_result == "TOKEN_EXPIRED":
            print_token_expired()
            return -1
        if not create_resume_result:
            set_upload_result(result, "error", "文件创建失败")
            return
        slice_size = create_resume_result["sliceSize"]
        upload_url = create_resume_result["uploadUrl"]
        server_id, upload_id = parse_url(upload_url)

        # 上传文件
        resume_result = hw_drive.upload_file_in_chunks(
            server_id, upload_id, file_path, slice_size
        )
        if resume_result == "TOKEN_EXPIRED":
            print_token_expired()
            return -1
        if not resume_result:
            set_upload_result(result, "error", "文件上传失败")
            return
        result["file_id"] = resume_result
        set_upload_result(result, "success", "文件上传成功")
        return

    except Exception as e:
        logger.error(f"上传过程发生错误: {str(e)}")
        set_upload_result(result, "error", f"上传过程发生错误: {str(e)}")
        return


def parse_arguments():
    parser = argparse.ArgumentParser(description="Huawei Cloud Drive CLI")
    parser.add_argument("--command", type=str, 
                        choices=["query", "query_folder", "upload", "create"],
                        help="命令类型: query, query_folder, upload, create")
    parser.add_argument("--key", type=str, help="查询ID，用于query命令")
    parser.add_argument("--file_name", type=str, help="文件名，用于query或query_folder命令")
    parser.add_argument("--mode", type=str, 
                        choices=["overwrite", "rename"],
                        help="上传模式: overwrite或rename")
    parser.add_argument("--folder_name", type=str, help="文件夹名称，用于create命令")
    parser.add_argument("--path", type=str, help="文件路径: path=上传文件路径")
    parser.add_argument("--Authorization", type=str, help="用于云空间接口at")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # 获取认证token
    if not args.Authorization:
        auth = get_drive_token()
    else:
        auth = args.Authorization
    if auth == "":
        logger.error("Authorization is empty")
        print(json.dumps({
            "status": "error",
            "error_code": "TOKEN_EXPIRED",
            "message": "云空间授权已过期，请退出小艺Claw后重新进入，系统将自动刷新授权。"
        }, ensure_ascii=False))
        return -1
    # 根据command分发到不同处理逻辑
    command = args.command
    
    if command == "query":
        # 查询命令
        if args.key == "space":
            # 查询可用空间
            return query_space_detail(auth)
        elif args.key == "available_space":
            # 查询可用空间
            return query_available_space(auth)
        elif args.key == "file_list":
            return get_celiaclaw_file_list(auth)
        elif args.file_name:
            # 查询文件是否存在
            return query_file_exists(auth, args.file_name)
        else:
            print("please specify --id available_space or --file_name <file_name>")
            sys.exit(1)
    
    elif command == "query_folder":
        # 查询文件夹是否存在
        if args.file_name:
            return query_folder_exists(auth, args.file_name)
        else:
            print("please specify --file_name <folder_name>")
            sys.exit(1)
    
    elif command == "upload":
        # 上传命令
        if not args.path:
            print("please input --path xxx")
            sys.exit(1)
        if not args.mode:
            print("please specify --mode overwrite or --mode rename")
            sys.exit(1)
        return upload_file_to_celiaclaw(auth, args.path, args.mode)
    
    elif command == "create":
        # 创建文件夹命令
        if not args.folder_name:
            print("please specify --folder_name <folder_name>")
            sys.exit(1)
        return create_folder(auth, args.folder_name)

if __name__ == "__main__":
    main()