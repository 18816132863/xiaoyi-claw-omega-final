"""统一搜索集成 - V4.3.2 第三阶段最终微修

修复问题：
1. Vector 模式明确输出 (embedding / degraded)
2. Token 预算硬限制
3. 搜索结果质量（二进制文件过滤）
4. Rewrite 质量过滤
5. 移除硬编码路径
6. Token 预算与 LazyLoader 联动重置
"""

from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import hashlib
import json
import re
import time
import os
import urllib.request
import urllib.error

from infrastructure.path_resolver import get_project_root
from infrastructure.token_budget import get_token_manager, get_lazy_loader

# 配置路径 - 通过 path_resolver 获取
def _get_config_path() -> Path:
    return get_project_root() / "skills" / "llm-memory-integration" / "config" / "llm_config.json"

@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    title: str
    content: str
    snippet: str
    score: float
    source: str
    metadata: Dict[str, Any] = None

class QwenEmbeddingEngine:
    """真实 Qwen3-Embedding-8B 引擎 - V6.0.0
    
    状态分离：
    - config_loaded: 配置是否成功加载
    - connection_ok: 连接测试是否成功
    - mode: embedding / degraded
    - reason: 明确的失败原因
    
    重要：连接失败不会清空配置字段，方便诊断
    """
    
    # 默认配置
    DEFAULT_CONFIG = {
        "provider": "openai_compatible",
        "base_url": "https://ai.gitee.com/v1",
        "model": "Qwen3-Embedding-8B",
        "dimensions": 1024,
        "timeout_seconds": 30
    }
    
    def __init__(self):
        # 状态字段
        self.config_loaded = False
        self.connection_ok = False
        self._mode = "unknown"
        self._reason = None
        self._exception_type = None
        self._exception_message = None
        
        # 配置字段（即使连接失败也保留）
        self.provider = None
        self.base_url = None
        self.model = None
        self.api_key = None
        self.dimensions = 128
        self.timeout = 30
        self.headers = {}
        
        # API Key 来源
        self._api_key_source = None
        
        # 只加载配置，不做连接测试
        self._load_config()
    
    def _load_config(self):
        """只加载配置，不做连接测试"""
        # 1. 从配置文件加载
        config = self._load_config_file()
        emb_config = config.get("embedding", {})
        
        # 2. 设置各字段
        self.provider = emb_config.get("provider", self.DEFAULT_CONFIG["provider"])
        self.base_url = emb_config.get("base_url", self.DEFAULT_CONFIG["base_url"])
        self.model = emb_config.get("model", self.DEFAULT_CONFIG["model"])
        self.dimensions = emb_config.get("dimensions", self.DEFAULT_CONFIG["dimensions"])
        self.timeout = emb_config.get("timeout_seconds", self.DEFAULT_CONFIG["timeout_seconds"])
        
        # 3. API Key：环境变量优先
        env_api_key = os.environ.get("EMBEDDING_API_KEY")
        if env_api_key:
            self.api_key = env_api_key
            self._api_key_source = "环境变量 EMBEDDING_API_KEY"
        else:
            self.api_key = emb_config.get("api_key")
            if self.api_key:
                self._api_key_source = "配置文件 llm_config.json"
        
        # 4. 设置请求头
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        # 5. 检查配置是否完整
        if self.api_key and self.base_url:
            self.config_loaded = True
            self._mode = "unknown"  # 需要测试连接才能确定
            self._reason = "config_loaded_but_not_tested"
        else:
            self.config_loaded = False
            self._mode = "degraded"
            if not self.api_key:
                self._reason = "api_key_missing"
            elif not self.base_url:
                self._reason = "base_url_missing"
    
    def _load_config_file(self) -> Dict:
        """从项目内加载配置文件"""
        config_path = _get_config_path()
        if config_path.exists():
            try:
                return json.loads(config_path.read_text())
            except Exception as e:
                self._exception_type = type(e).__name__
                self._exception_message = str(e)
        return {}
    
    def test_connection(self) -> bool:
        """显式测试连接"""
        if not self.api_key:
            self.connection_ok = False
            self._mode = "degraded"
            self._reason = "api_key_missing"
            return False
        
        if not self.base_url:
            self.connection_ok = False
            self._mode = "degraded"
            self._reason = "base_url_missing"
            return False
        
        try:
            data = json.dumps({
                "model": self.model,
                "input": ["test"]
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/embeddings",
                data=data,
                headers=self.headers
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result.get("data") and len(result["data"]) > 0:
                    self.connection_ok = True
                    self._mode = "embedding"
                    self._reason = None
                    self._exception_type = None
                    self._exception_message = None
                    return True
                else:
                    self.connection_ok = False
                    self._mode = "degraded"
                    self._reason = "bad_response_empty_data"
                    return False
                    
        except urllib.error.HTTPError as e:
            self.connection_ok = False
            self._mode = "degraded"
            self._exception_type = "HTTPError"
            self._exception_message = f"{e.code} {e.reason}"
            if e.code == 401:
                self._reason = "unauthorized"
            elif e.code == 403:
                self._reason = "forbidden"
            elif e.code == 404:
                self._reason = "endpoint_not_found"
            else:
                self._reason = f"http_error_{e.code}"
            return False
            
        except urllib.error.URLError as e:
            self.connection_ok = False
            self._mode = "degraded"
            self._exception_type = "URLError"
            self._exception_message = str(e.reason)
            if "timed out" in str(e.reason).lower():
                self._reason = "timeout"
            elif "name or service not known" in str(e.reason).lower():
                self._reason = "dns_failed"
            else:
                self._reason = "network_error"
            return False
            
        except Exception as e:
            self.connection_ok = False
            self._mode = "degraded"
            self._exception_type = type(e).__name__
            self._exception_message = str(e)
            self._reason = "request_failed"
            return False
    
    def get_mode(self) -> str:
        """返回当前模式（如果未测试，先测试连接）"""
        if self._mode == "unknown":
            self.test_connection()
        return self._mode
    
    def get_reason(self) -> Optional[str]:
        """返回失败原因"""
        return self._reason
    
    def get_exception_info(self) -> Tuple[Optional[str], Optional[str]]:
        """返回异常信息"""
        return self._exception_type, self._exception_message
    
    def get_config_info(self) -> Dict:
        """返回完整配置信息"""
        return {
            "config_loaded": self.config_loaded,
            "connection_ok": self.connection_ok,
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "api_key": "已配置" if self.api_key else "未配置",
            "api_key_source": self._api_key_source,
            "dimensions": self.dimensions,
            "timeout": self.timeout,
            "mode": self._mode,
            "reason": self._reason,
            "exception_type": self._exception_type,
            "exception_message": self._exception_message
        }
    
    def encode(self, text: str) -> List[float]:
        """编码文本为向量"""
        # 确保已测试连接
        if self._mode == "unknown":
            self.test_connection()
        
        if self._mode == "degraded":
            raise RuntimeError(f"Embedding engine is in degraded mode: {self._reason}")
        
        try:
            data = json.dumps({
                "model": self.model,
                "input": [text[:8000]]
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/embeddings",
                data=data,
                headers=self.headers
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result["data"][0]["embedding"]
                
        except Exception as e:
            # 更新状态
            self.connection_ok = False
            self._mode = "degraded"
            self._exception_type = type(e).__name__
            self._exception_message = str(e)
            self._reason = "encode_failed"
            raise RuntimeError(f"Embedding encode failed: {type(e).__name__}: {e}")
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码文本"""
        if self._mode == "unknown":
            self.test_connection()
        
        if self._mode == "degraded":
            raise RuntimeError(f"Embedding engine is in degraded mode: {self._reason}")
        
        try:
            data = json.dumps({
                "model": self.model,
                "input": [t[:8000] for t in texts]
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/embeddings",
                data=data,
                headers=self.headers
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout * 2) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return [item["embedding"] for item in result["data"]]
                
        except Exception as e:
            self.connection_ok = False
            self._mode = "degraded"
            self._exception_type = type(e).__name__
            self._exception_message = str(e)
            self._reason = "encode_batch_failed"
            raise RuntimeError(f"Embedding encode_batch failed: {type(e).__name__}: {e}")
    
    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算向量相似度"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

class IndexExcludeList:
    """索引排除名单 - V5.0.0 统一排除规则
    
    重要：此排除规则必须与打包排除规则、变更检测排除规则完全一致
    """
    
    def __init__(self):
        self.exclude_dirs = {
            "node_modules", "__pycache__", ".git", ".svn",
            "archive", "reports", "backups", "tmp", "temp",
            "dist", "build", ".cache", "logs",
            "repo", "site-packages", "bin", "sbin",
            "backup",  # 新增：备份目录
            # 注意：不排除 "index"，因为 memory_context/index/ 需要打包
        }
        self.exclude_extensions = {
            ".pyc", ".pyo", ".so", ".dll", ".dylib",
            ".tar", ".gz", ".zip", ".rar", ".7z",
            ".mp3", ".mp4", ".avi", ".mov", ".wav",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
            ".pdf",  # PDF 文件排除
            ".db", ".sqlite", ".sqlite3",
            ".bin", ".exe", ".sh", ".bat", ".cmd", ".run",
            ".out", ".o", ".a", ".lib",
        }
        self.max_file_size = 10 * 1024 * 1024
        self.exclude_files = {
            "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
            "composer.lock", "Cargo.lock", "poetry.lock",
            # 索引文件不排除，需要打包
            "RECORD",
        }
        self.exclude_patterns = [
            "site-packages",
            # 不排除 index 目录，索引文件需要打包
            "/bin/",
            "/sbin/",
            "backup",  # 新增：备份相关路径
        ]
        # 无扩展名的可执行文件名模式
        self.exclude_no_ext_patterns = [
            "acp2service", "vsearch", "llm-analyze",
        ]
    
    def should_exclude(self, path: Path) -> bool:
        """统一排除规则 - V5.0.0
        
        重要：只检查相对路径的目录部分，不检查绝对路径中的系统目录
        """
        # 跳过符号链接 - 统一规则
        if path.is_symlink():
            return True
        
        # 获取相对路径部分（排除系统临时目录等）
        # 只检查项目内的目录名
        path_parts = path.parts
        
        # 找到项目根目录的起始位置
        # 项目根目录特征：包含 workspace 或 core/skills/infrastructure 等项目目录
        project_markers = {'workspace', 'core', 'skills', 'infrastructure', 'governance', 
                          'execution', 'orchestration', 'memory', 'memory_context',
                          'plugins', '.openclaw'}
        start_idx = 0
        for i, part in enumerate(path_parts):
            if part in project_markers:
                start_idx = i
                break
        
        # 只检查项目内的目录（从 workspace 或 .openclaw 开始）
        project_parts = path_parts[start_idx:]
        
        # 跳过 workspace 和 .openclaw 本身，只检查其子目录
        if project_parts and project_parts[0] in {'workspace', '.openclaw'}:
            project_parts = project_parts[1:]
        
        for part in project_parts:
            if part in self.exclude_dirs:
                return True
        
        # 检查文件名
        if path.name in self.exclude_files:
            return True
        
        # 检查无扩展名的可执行文件
        if path.suffix == "" or path.suffix == ".":
            name_lower = path.name.lower()
            for pattern in self.exclude_no_ext_patterns:
                if pattern in name_lower:
                    return True
            # 无扩展名且在 bin 目录
            if "bin" in project_parts:
                return True
        
        # 检查扩展名
        if path.suffix.lower() in self.exclude_extensions:
            return True
        
        # 检查路径模式（只检查项目内路径）
        path_str = str(Path(*project_parts)) if project_parts else str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        
        # 检查文件大小
        try:
            if path.is_file() and path.stat().st_size > self.max_file_size:
                return True
        except:
            pass
        
        return False

class QueryRewriter:
    """查询改写器 - 增强质量过滤"""
    
    def __init__(self):
        self.synonyms = {
            "搜索": ["查找", "寻找", "检索", "search", "find"],
            "创建": ["新建", "添加", "生成", "create", "add", "new"],
            "删除": ["移除", "清除", "去掉", "delete", "remove"],
            "更新": ["修改", "编辑", "update", "edit", "modify"],
            "查询": ["查看", "获取", "query", "get", "show"],
            "文档": ["文件", "document", "file", "doc"],
            "配置": ["设置", "config", "setting", "configuration"],
            "架构": ["结构", "architecture", "structure", "framework"],
            "记忆": ["存储", "memory", "storage", "remember"],
        }
        # 破坏性模式 - 过滤掉
        self.destructive_patterns = [
            r'^[a-z]$',  # 单字母
            r'^\W+$',    # 纯符号
            r'^\d+$',    # 纯数字
        ]
    
    def rewrite(self, query: str) -> List[str]:
        rewrites = [query]
        
        # 同义词扩展
        for word, syns in self.synonyms.items():
            if word in query:
                for syn in syns:
                    if syn != word:
                        new_query = query.replace(word, syn)
                        if self._is_valid_rewrite(new_query, query):
                            rewrites.append(new_query)
        
        # 移除停用词
        stop_words = ["的", "了", "是", "在", "有", "和", "与", "或", "等", "这", "那", "the", "a", "an", "is", "are"]
        simplified = query
        for sw in stop_words:
            simplified = simplified.replace(sw, " ")
        simplified = " ".join(simplified.split())
        if simplified != query and simplified and self._is_valid_rewrite(simplified, query):
            rewrites.append(simplified)
        
        # 去重并过滤
        valid_rewrites = []
        seen = set()
        for r in rewrites:
            r_lower = r.lower()
            if r_lower not in seen and self._is_valid_rewrite(r, query):
                seen.add(r_lower)
                valid_rewrites.append(r)
        
        return valid_rewrites[:5]
    
    def _is_valid_rewrite(self, rewrite: str, original: str) -> bool:
        """检查 rewrite 是否有效"""
        # 长度检查
        if len(rewrite) < 2:
            return False
        
        # 不能比原查询短太多
        if len(rewrite) < len(original) * 0.5:
            return False
        
        # 检查破坏性模式
        for pattern in self.destructive_patterns:
            if re.match(pattern, rewrite):
                return False
        
        # 检查是否只是删除了字符（如 architecture -> rchitecture）
        if rewrite in original or original in rewrite:
            # 如果 rewrite 是 original 的子串，检查是否只是删除
            if len(rewrite) < len(original):
                # 只允许同义词替换产生的变化
                return False
        
        return True

class SnippetGenerator:
    """摘要生成器"""
    
    def __init__(self, max_length: int = 200):
        self.max_length = max_length
    
    def generate(self, content: str, query: str) -> str:
        if not content:
            return ""
        
        query_lower = query.lower()
        content_lower = content.lower()
        
        idx = content_lower.find(query_lower)
        if idx == -1:
            words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', query_lower)
            for word in words:
                idx = content_lower.find(word)
                if idx != -1:
                    break
        
        if idx != -1:
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query) + 100)
            snippet = content[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
        else:
            snippet = content[:self.max_length]
            if len(content) > self.max_length:
                snippet = snippet + "..."
        
        return snippet.strip()

class IndexPersistence:
    """索引持久化 - V5.0.0 单一 canonical file_states
    
    重要规则：
    1. 只有一个正式状态文件：memory_context/index/file_states.json
    2. .cache/file_states.json 等旧缓存不再参与首启判断
    3. 符号链接统一跳过，不写入 file_states
    """
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or get_project_root() / "memory_context" / "index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # 唯一的 canonical 状态文件
        self.keyword_index_file = self.index_dir / "keyword_index.json"
        self.fts_index_file = self.index_dir / "fts_index.json"
        self.vector_index_file = self.index_dir / "vector_index.json"
        self.metadata_file = self.index_dir / "index_metadata.json"
        self.file_states_file = self.index_dir / "file_states.json"
        
        self._index_files = {
            str(self.keyword_index_file),
            str(self.fts_index_file),
            str(self.vector_index_file),
            str(self.metadata_file),
            str(self.file_states_file),
        }
    
    def is_index_file(self, path: Path) -> bool:
        return str(path) in self._index_files or path.name in {
            "keyword_index.json", "fts_index.json", "vector_index.json",
            "index_metadata.json", "file_states.json"
        }
    
    def save(self, keyword_index: Dict, fts_index: Dict, vector_index: Dict, 
             metadata: Dict, file_states: Dict = None):
        self.keyword_index_file.write_text(json.dumps(keyword_index, ensure_ascii=False))
        self.fts_index_file.write_text(json.dumps(fts_index, ensure_ascii=False))
        self.vector_index_file.write_text(json.dumps(vector_index, ensure_ascii=False))
        self.metadata_file.write_text(json.dumps(metadata, ensure_ascii=False))
        if file_states is not None:
            self.file_states_file.write_text(json.dumps(file_states, ensure_ascii=False))
    
    def load(self) -> Tuple[Dict, Dict, Dict, Dict, Dict]:
        """加载索引 - 只从 canonical 位置加载"""
        keyword_index = {}
        fts_index = {}
        vector_index = {}
        metadata = {}
        file_states = {}
        
        if self.keyword_index_file.exists():
            try:
                keyword_index = json.loads(self.keyword_index_file.read_text())
            except:
                pass
        
        if self.fts_index_file.exists():
            try:
                fts_index = json.loads(self.fts_index_file.read_text())
            except:
                pass
        
        if self.vector_index_file.exists():
            try:
                vector_index = json.loads(self.vector_index_file.read_text())
            except:
                pass
        
        if self.metadata_file.exists():
            try:
                metadata = json.loads(self.metadata_file.read_text())
            except:
                pass
        
        # 只从 canonical 位置加载 file_states
        if self.file_states_file.exists():
            try:
                file_states = json.loads(self.file_states_file.read_text())
            except:
                pass
        
        return keyword_index, fts_index, vector_index, metadata, file_states
    
    def get_file_state(self, path: Path) -> Dict:
        try:
            return {
                "mtime": path.stat().st_mtime,
                "size": path.stat().st_size,
                "hash": hashlib.md5(path.read_bytes()).hexdigest()[:16]
            }
        except:
            return {}
    
    def get_changed_files(self, base_path: Path, file_states: Dict, 
                          index_exclude: 'IndexExcludeList') -> Tuple[List[Path], List[Path], set]:
        """变更检测 - V5.0.0 统一排除规则
        
        重要：必须与建索引时使用同一套排除规则
        1. 跳过符号链接
        2. 使用 IndexExcludeList 统一排除
        """
        new_files = []
        modified_files = []
        current_files = set()
        
        for f in base_path.rglob("*"):
            if not f.is_file():
                continue
            # 跳过符号链接 - 统一规则
            if f.is_symlink():
                continue
            if self.is_index_file(f):
                continue
            # 使用统一的排除规则
            if index_exclude.should_exclude(f):
                continue
            
            try:
                file_id = str(f.relative_to(base_path))
                current_files.add(file_id)
                
                current_state = self.get_file_state(f)
                saved_state = file_states.get(file_id, {})
                
                if not saved_state:
                    new_files.append(f)
                elif (saved_state.get("mtime", 0) < current_state.get("mtime", 0) or
                      saved_state.get("hash") != current_state.get("hash")):
                    modified_files.append(f)
            except:
                pass
        
        deleted_files = set(file_states.keys()) - current_files
        
        return new_files, modified_files, deleted_files

class KeywordSearch:
    """关键词搜索"""
    
    def __init__(self, index_exclude: IndexExcludeList = None):
        self.index_exclude = index_exclude or IndexExcludeList()
        self.keyword_index: Dict[str, List[str]] = {}
    
    def index_file(self, file_path: Path, base_path: Path):
        if not file_path.is_file():
            return
        if self.index_exclude.should_exclude(file_path):
            return
        
        try:
            content = file_path.read_text(errors='ignore')
            keywords = self._extract_keywords(content)
            file_id = str(file_path.relative_to(base_path))
            
            for kw in keywords:
                if kw not in self.keyword_index:
                    self.keyword_index[kw] = []
                if file_id not in self.keyword_index[kw]:
                    self.keyword_index[kw].append(file_id)
        except:
            pass
    
    def remove_file(self, file_id: str):
        for kw in list(self.keyword_index.keys()):
            if file_id in self.keyword_index[kw]:
                self.keyword_index[kw].remove(file_id)
                if not self.keyword_index[kw]:
                    del self.keyword_index[kw]
    
    def index(self, base_path: Path, batch_size: int = 100):
        self.keyword_index.clear()
        
        files = list(base_path.rglob("*"))
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            for file_path in batch:
                self.index_file(file_path, base_path)
    
    def _extract_keywords(self, content: str) -> List[str]:
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9_]+', content.lower())
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      '的', '了', '是', '在', '有', '和', '与', '或', '等', '这', '那',
                      'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as'}
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        keywords = self._extract_keywords(query)
        results = []
        
        file_scores: Dict[str, float] = {}
        for kw in keywords:
            if kw in self.keyword_index:
                for file_id in self.keyword_index[kw]:
                    file_scores[file_id] = file_scores.get(file_id, 0) + 1
        
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        for file_id, score in sorted_files:
            results.append(SearchResult(
                id=file_id,
                title=Path(file_id).name,
                content="",
                snippet="",
                score=score / max(len(keywords), 1),
                source="keyword"
            ))
        
        return results

class FTSSearch:
    """全文搜索"""
    
    def __init__(self, index_exclude: IndexExcludeList = None):
        self.index_exclude = index_exclude or IndexExcludeList()
        self.documents: Dict[str, str] = {}
    
    def index_file(self, file_path: Path, base_path: Path):
        if not file_path.is_file():
            return
        if self.index_exclude.should_exclude(file_path):
            return
        
        try:
            content = file_path.read_text(errors='ignore')
            file_id = str(file_path.relative_to(base_path))
            self.documents[file_id] = content.lower()
        except:
            pass
    
    def remove_file(self, file_id: str):
        if file_id in self.documents:
            del self.documents[file_id]
    
    def index(self, base_path: Path, batch_size: int = 100):
        self.documents.clear()
        
        files = list(base_path.rglob("*"))
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            for file_path in batch:
                self.index_file(file_path, base_path)
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        query_lower = query.lower()
        results = []
        
        file_scores: Dict[str, float] = {}
        for file_id, content in self.documents.items():
            count = content.count(query_lower)
            if count > 0:
                file_scores[file_id] = count
        
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        for file_id, score in sorted_files:
            results.append(SearchResult(
                id=file_id,
                title=Path(file_id).name,
                content="",
                snippet="",
                score=min(score / 10, 1.0),
                source="fts"
            ))
        
        return results

class VectorSearch:
    """向量搜索 - V5.0.0
    
    重要：vector_mode 必须来自引擎的真实健康状态
    """
    
    def __init__(self, index_exclude: IndexExcludeList = None):
        self.index_exclude = index_exclude or IndexExcludeList()
        self.embedding_engine = QwenEmbeddingEngine()
        self.embeddings: Dict[str, List[float]] = {}
        self.documents: Dict[str, str] = {}
    
    def get_mode(self) -> str:
        """返回引擎的真实健康状态"""
        return self.embedding_engine.get_mode()
    
    def get_reason(self) -> Optional[str]:
        """返回 degraded 原因"""
        return self.embedding_engine.get_reason()
    
    def index_file(self, file_path: Path, base_path: Path):
        if not file_path.is_file():
            return
        if self.index_exclude.should_exclude(file_path):
            return
        
        try:
            content = file_path.read_text(errors='ignore')
            file_id = str(file_path.relative_to(base_path))
            
            # 只有 embedding 模式才真正编码
            if self.embedding_engine.get_mode() == "embedding":
                embedding = self.embedding_engine.encode(content[:1000])
                self.embeddings[file_id] = embedding
            self.documents[file_id] = content
        except Exception as e:
            # 索引时失败，跳过该文件
            pass
    
    def remove_file(self, file_id: str):
        if file_id in self.embeddings:
            del self.embeddings[file_id]
        if file_id in self.documents:
            del self.documents[file_id]
    
    def index(self, base_path: Path, batch_size: int = 50):
        self.embeddings.clear()
        self.documents.clear()
        
        files = list(base_path.rglob("*"))
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            for file_path in batch:
                self.index_file(file_path, base_path)
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """向量搜索 - 如果 embedding 失败，返回空列表"""
        # 只有 embedding 模式才执行向量搜索
        if self.embedding_engine.get_mode() != "embedding":
            return []
        
        try:
            query_vec = self.embedding_engine.encode(query)
        except Exception as e:
            # 编码失败，返回空
            return []
        
        results = []
        for file_id, vec in self.embeddings.items():
            sim = self.embedding_engine.similarity(query_vec, vec)
            
            if sim > 0.1:
                results.append(SearchResult(
                    id=file_id,
                    title=Path(file_id).name,
                    content="",
                    snippet="",
                    score=sim,
                    source="vector"
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

class RRFFusion:
    """RRF 融合"""
    
    def __init__(self, k: int = 40):
        self.k = k
    
    def fuse(self, result_lists: List[List[SearchResult]], weights: List[float] = None) -> List[SearchResult]:
        if weights is None:
            weights = [1.0] * len(result_lists)
        
        scores: Dict[str, float] = {}
        result_map: Dict[str, SearchResult] = {}
        
        for results, weight in zip(result_lists, weights):
            for rank, result in enumerate(results, 1):
                if result.id not in scores:
                    scores[result.id] = 0
                    result_map[result.id] = result
                scores[result.id] += weight / (self.k + rank)
        
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        fused = []
        for result_id, score in sorted_ids:
            result = result_map[result_id]
            fused.append(SearchResult(
                id=result.id,
                title=result.title,
                content=result.content,
                snippet=result.snippet,
                score=score,
                source="rrf_fused"
            ))
        
        return fused

class SemanticDedup:
    """语义去重"""
    
    def dedup(self, results: List[SearchResult], threshold: float = 0.9) -> List[SearchResult]:
        if not results:
            return results
        
        deduped = []
        seen_titles = set()
        
        for result in results:
            title_lower = result.title.lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                deduped.append(result)
        
        return deduped

class UnifiedSearch:
    """统一搜索入口 - V4.3.2 第三阶段最终修正"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or get_project_root()
        
        # 索引排除名单
        self.index_exclude = IndexExcludeList()
        
        # 搜索引擎
        self.keyword_search = KeywordSearch(self.index_exclude)
        self.fts_search = FTSSearch(self.index_exclude)
        self.vector_search = VectorSearch(self.index_exclude)
        
        # 新增组件
        self.query_rewriter = QueryRewriter()
        self.snippet_generator = SnippetGenerator()
        
        # 融合和后处理
        self.rrf = RRFFusion(k=40)
        self.dedup = SemanticDedup()
        
        # 索引持久化
        self.index_persistence = IndexPersistence()
        
        # Token/加载治理
        self.token_manager = get_token_manager()
        self.lazy_loader = get_lazy_loader()
        
        # 缓存
        self._cache: Dict[str, List[SearchResult]] = {}
        self._indexed = False
        self._file_states: Dict[str, Dict] = {}
    
    def get_vector_mode(self) -> str:
        return self.vector_search.get_mode()
    
    def get_performance_mode(self) -> str:
        return "maximum"
    
    def build_index(self, force: bool = False) -> Dict:
        """构建索引 - V5.0.0 修复首启逻辑
        
        修复问题：
        1. 先检查索引文件是否存在
        2. 先加载持久化状态（keyword_index, fts_index, vector_index, metadata, file_states）
        3. 再做变更比较
        4. 如果索引存在 + metadata 存在 + file_states 存在 + changed_files == [] → 直接返回 mode=loaded
        
        禁止的错误结果：
        - incremental + files_indexed = 0
        - 第一次先 full_rebuild，第二次才 loaded
        """
        result = {
            "mode": "unknown",
            "files_indexed": 0,
            "time_ms": 0,
            "incremental": False
        }
        
        start = time.time()
        
        if not force:
            # 1. 先检查索引文件是否存在
            keyword_idx, fts_idx, vector_idx, metadata, file_states = self.index_persistence.load()
            
            # 2. 检查所有必要文件是否都存在
            all_exist = (
                self.index_persistence.keyword_index_file.exists() and
                self.index_persistence.fts_index_file.exists() and
                self.index_persistence.vector_index_file.exists() and
                self.index_persistence.metadata_file.exists() and
                self.index_persistence.file_states_file.exists()
            )
            
            # 3. 如果索引存在，先加载再做变更比较
            if all_exist and keyword_idx and file_states:
                new_files, modified_files, deleted_files = self.index_persistence.get_changed_files(
                    self.base_dir, file_states, self.index_exclude
                )
                
                # 4. 如果没有变更，直接返回 loaded
                if not new_files and not modified_files and not deleted_files:
                    self.keyword_search.keyword_index = keyword_idx
                    self.fts_search.documents = fts_idx
                    self.vector_search.embeddings = vector_idx
                    self._file_states = file_states
                    self._indexed = True
                    
                    result["mode"] = "loaded"
                    result["incremental"] = True
                    result["time_ms"] = int((time.time() - start) * 1000)
                    return result
                
                # 5. 有变更，执行增量更新
                result["incremental"] = True
                result["mode"] = "incremental"
                
                self.keyword_search.keyword_index = keyword_idx
                self.fts_search.documents = fts_idx
                self.vector_search.embeddings = vector_idx
                self._file_states = file_states.copy()
                
                for file_id in deleted_files:
                    self.keyword_search.remove_file(file_id)
                    self.fts_search.remove_file(file_id)
                    self.vector_search.remove_file(file_id)
                    if file_id in self._file_states:
                        del self._file_states[file_id]
                
                for f in new_files:
                    self.keyword_search.index_file(f, self.base_dir)
                    self.fts_search.index_file(f, self.base_dir)
                    self.vector_search.index_file(f, self.base_dir)
                    file_id = str(f.relative_to(self.base_dir))
                    self._file_states[file_id] = self.index_persistence.get_file_state(f)
                
                for f in modified_files:
                    self.keyword_search.index_file(f, self.base_dir)
                    self.fts_search.index_file(f, self.base_dir)
                    self.vector_search.index_file(f, self.base_dir)
                    file_id = str(f.relative_to(self.base_dir))
                    self._file_states[file_id] = self.index_persistence.get_file_state(f)
                
                result["files_indexed"] = len(new_files) + len(modified_files)
                
                self.index_persistence.save(
                    self.keyword_search.keyword_index,
                    self.fts_search.documents,
                    self.vector_search.embeddings,
                    {"indexed_time": time.time()},
                    self._file_states
                )
                
                self._indexed = True
                result["time_ms"] = int((time.time() - start) * 1000)
                return result
        
        # 全量重建
        result["mode"] = "full_rebuild"
        result["incremental"] = False
        
        self.keyword_search.index(self.base_dir)
        self.fts_search.index(self.base_dir)
        self.vector_search.index(self.base_dir)
        
        # 重建 file_states - 使用统一排除规则
        self._file_states = {}
        for f in self.base_dir.rglob("*"):
            if not f.is_file():
                continue
            # 跳过符号链接
            if f.is_symlink():
                continue
            # 使用统一排除规则
            if self.index_exclude.should_exclude(f):
                continue
            if self.index_persistence.is_index_file(f):
                continue
            
            try:
                file_id = str(f.relative_to(self.base_dir))
                self._file_states[file_id] = self.index_persistence.get_file_state(f)
                result["files_indexed"] += 1
            except:
                pass
        
        self.index_persistence.save(
            self.keyword_search.keyword_index,
            self.fts_search.documents,
            self.vector_search.embeddings,
            {"indexed_time": time.time()},
            self._file_states
        )
        
        self._indexed = True
        result["time_ms"] = int((time.time() - start) * 1000)
        return result
    
    def search(self, query: str, mode: str = "balanced", limit: int = 10) -> Dict:
        """统一搜索 - V4.3.3 第四阶段搜索质量精修
        
        改进：
        1. 文件类型权重调整
        2. SKILL.md / 测试文件降权
        3. 核心文件优先
        """
        start = time.time()
        
        # 重置 token 预算和 lazy_loader 状态（联动重置）
        self.token_manager.reset()
        self.lazy_loader.reset()
        
        # 查询改写
        rewrites = self.query_rewriter.rewrite(query)
        
        # 检查缓存
        cache_key = hashlib.md5(f"{query}:{mode}:{limit}".encode()).hexdigest()
        if cache_key in self._cache:
            return {
                "results": self._cache[cache_key],
                "source": "cache",
                "time_ms": 5,
                "vector_mode": self.get_vector_mode(),
                "performance_mode": self.get_performance_mode(),
                "rewrites": rewrites,
                "token_budget": self.token_manager.get_summary(),
                "lazy_loader_status": self.lazy_loader.get_status()
            }
        
        # 确保索引已建立
        if not self._indexed:
            self.build_index()
        
        # 根据模式选择搜索策略
        if mode == "fast":
            results = self.keyword_search.search(query, limit)
        elif mode == "full":
            keyword_results = self.keyword_search.search(query, limit * 2)
            fts_results = self.fts_search.search(query, limit * 2)
            vector_results = self.vector_search.search(query, limit * 2)
            
            # rewrite 参与 - 只使用高质量 rewrite
            rewrite_results = []
            for rewrite in rewrites[1:3]:
                if len(rewrite) >= len(query) * 0.7:  # 长度检查
                    kw_r = self.keyword_search.search(rewrite, limit)
                    fts_r = self.fts_search.search(rewrite, limit)
                    rewrite_results.extend(kw_r)
                    rewrite_results.extend(fts_r)
            
            all_results = [keyword_results, fts_results, vector_results, rewrite_results]
            weights = [1.0, 1.5, 2.0, 0.5]
            
            results = self.rrf.fuse(all_results, weights)
        else:
            keyword_results = self.keyword_search.search(query, limit * 2)
            fts_results = self.fts_search.search(query, limit * 2)
            
            rewrite_results = []
            for rewrite in rewrites[1:2]:
                if len(rewrite) >= len(query) * 0.7:
                    rewrite_results.extend(self.keyword_search.search(rewrite, limit))
            
            results = self.rrf.fuse([keyword_results, fts_results, rewrite_results], [1.0, 1.5, 0.5])
        
        # 去重
        results = self.dedup.dedup(results)
        
        # 第四阶段新增：应用文件类型权重
        results = self._apply_file_weights(results)
        
        # LazyLoader 接入 - 带硬限制
        for result in results:
            file_path = self.base_dir / result.id
            if file_path.exists():
                # 检查预算是否已超
                if self.token_manager.current_usage >= self.token_manager.max_tokens:
                    # 预算已超，停止加载
                    result.content = "[budget exceeded]"
                    result.snippet = ""
                    continue
                
                self.lazy_loader.register(result.id, file_path)
                content = self.lazy_loader.load(result.id, "L4")
                
                if content:
                    result.content = content
                    result.snippet = self.snippet_generator.generate(content, query)
                else:
                    try:
                        raw_content = file_path.read_text(errors='ignore')
                        # 硬截断
                        max_chars = 500
                        result.content = raw_content[:max_chars]
                        result.snippet = self.snippet_generator.generate(raw_content, query)
                    except:
                        pass
        
        # 限制结果数量
        results = results[:limit]
        
        # 缓存
        self._cache[cache_key] = results
        
        elapsed_ms = int((time.time() - start) * 1000)
        
        return {
            "query": query,
            "rewrites": rewrites,
            "mode": mode,
            "vector_mode": self.get_vector_mode(),
            "performance_mode": self.get_performance_mode(),
            "results": [
                {
                    "id": r.id,
                    "title": r.title,
                    "snippet": r.snippet[:200] if r.snippet else "",
                    "score": round(r.score, 4),
                    "source": r.source
                }
                for r in results
            ],
            "total": len(results),
            "time_ms": elapsed_ms,
            "source": "search",
            "token_budget": self.token_manager.get_summary(),
            "lazy_loader_status": self.lazy_loader.get_status()
        }
    
    def _apply_file_weights(self, results: List[SearchResult]) -> List[SearchResult]:
        """应用文件类型权重 - V4.3.3 第四阶段
        
        降低 SKILL.md、测试文件、文档文件的权重
        提升核心代码文件的权重
        """
        # 文件类型权重配置
        high_value_patterns = [
            "core/", "infrastructure/", "governance/", 
            "orchestration/", "execution/", "memory_context/"
        ]
        low_value_patterns = [
            "SKILL.md", "README.md", "test_", "_test.py",
            "tests/", "examples/", "docs/", "CHANGELOG",
            "CONTRIBUTING", "LICENSE"
        ]
        
        for result in results:
            file_id = result.id
            weight = 1.0
            
            # 检查高价值模式
            for pattern in high_value_patterns:
                if pattern in file_id:
                    weight = 1.3
                    break
            
            # 检查低价值模式
            for pattern in low_value_patterns:
                if pattern in file_id:
                    weight = 0.3
                    break
            
            # 应用权重
            result.score = result.score * weight
        
        # 重新排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def clear_cache(self):
        self._cache.clear()
        self.token_manager.reset()

# 全局实例
_unified_search: Optional[UnifiedSearch] = None

def get_unified_search() -> UnifiedSearch:
    global _unified_search
    if _unified_search is None:
        _unified_search = UnifiedSearch()
    return _unified_search
