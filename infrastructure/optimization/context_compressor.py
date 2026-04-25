"""上下文压缩器 - V1.0.0"""

from typing import Dict, List, Any
import re
from collections import Counter

class ContextCompressor:
    """上下文压缩器 - 减少上下文长度"""
    
    def __init__(self):
        self.compression_rules = {
            # 移除多余空白
            r'\s+': ' ',
            # 移除注释
            r'#.*$': '',
            r'//.*$': '',
            # 移除空行
            r'\n\s*\n': '\n\n',
            # 压缩重复
            r'(.)\1{3,}': r'\1\1\1',
        }
        self.stop_words = set(['的', '了', '是', '在', '和', '与', '或', '等', '这', '那'])
    
    def compress(self, text: str, level: str = "medium") -> str:
        """压缩文本"""
        if level == "none":
            return text
        
        # 应用压缩规则
        for pattern, replacement in self.compression_rules.items():
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        
        if level == "high":
            # 高压缩: 移除停用词
            words = text.split()
            words = [w for w in words if w not in self.stop_words]
            text = ' '.join(words)
        
        return text.strip()
    
    def compress_dict(self, data: Dict, level: str = "medium") -> Dict:
        """压缩字典"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.compress(value, level)
            elif isinstance(value, dict):
                result[key] = self.compress_dict(value, level)
            else:
                result[key] = value
        return result
    
    def extract_key_info(self, text: str) -> Dict[str, Any]:
        """提取关键信息"""
        # 提取数字
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        # 提取日期
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        
        # 提取 URL
        urls = re.findall(r'https?://[^\s]+', text)
        
        # 提取关键词
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text)
        word_freq = Counter(words).most_common(10)
        
        return {
            "numbers": numbers[:5],
            "dates": dates[:3],
            "urls": urls[:3],
            "keywords": [w[0] for w in word_freq if w[0] not in self.stop_words][:5]
        }
    
    def get_stats(self, original: str, compressed: str) -> Dict:
        """获取压缩统计"""
        return {
            "original_length": len(original),
            "compressed_length": len(compressed),
            "compression_ratio": 1 - (len(compressed) / max(1, len(original))),
            "tokens_saved": (len(original) - len(compressed)) // 4  # 估算
        }
