"""
OCR Service - OCR 服务适配器

支持 DeepSeek OCR 服务
"""

import os
import json
import base64
import hashlib
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OCRProvider(str, Enum):
    """OCR 提供商"""
    DEEPSEEK = "deepseek"
    TESSERACT = "tesseract"
    PADDLE = "paddle"


@dataclass
class OCRResult:
    """OCR 结果"""
    success: bool
    text: str
    confidence: float = 0.0
    language: str = "unknown"
    bounding_boxes: List[Dict] = field(default_factory=list)
    processing_time_ms: float = 0.0
    provider: str = "unknown"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "text": self.text,
            "confidence": self.confidence,
            "language": self.language,
            "bounding_boxes": self.bounding_boxes,
            "processing_time_ms": self.processing_time_ms,
            "provider": self.provider,
            "error": self.error
        }


class OCRService:
    """OCR 服务"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._load_config()
        self.service_id = self.config.get("service_id", "deepseek-ocr-2sk-u3qymvvjrvxh26j6")
        self.provider = self.config.get("provider", "deepseek")
        self.enabled = self.config.get("enabled", True)
        self.timeout_ms = self.config.get("timeout_ms", 30000)
        self.max_image_size_mb = self.config.get("max_image_size_mb", 10)
        self.supported_formats = self.config.get("supported_formats", ["jpg", "jpeg", "png", "gif", "webp", "bmp"])
        self.languages = self.config.get("languages", ["zh", "en", "ja", "ko"])
        self.cache_enabled = self.config.get("cache", {}).get("enabled", True)
        self.cache_ttl = self.config.get("cache", {}).get("ttl_seconds", 3600)
        self.fallback_enabled = self.config.get("fallback", {}).get("enabled", True)
        self.fallback_provider = self.config.get("fallback", {}).get("provider", "tesseract")
        
        # 缓存
        self._cache: Dict[str, Dict] = {}
        
    def _load_config(self) -> Dict:
        """加载配置"""
        config_path = Path("/home/sandbox/.openclaw/workspace/config/unified.json")
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("ocr", {})
            except Exception:
                pass
        return {}
    
    def _get_cache_key(self, image_data: bytes) -> str:
        """生成缓存键"""
        return hashlib.sha256(image_data).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[OCRResult]:
        """检查缓存"""
        if not self.cache_enabled:
            return None
        
        cached = self._cache.get(cache_key)
        if cached:
            # 检查是否过期
            if (datetime.now() - cached["timestamp"]).total_seconds() < self.cache_ttl:
                return cached["result"]
            else:
                del self._cache[cache_key]
        
        return None
    
    def _save_to_cache(self, cache_key: str, result: OCRResult):
        """保存到缓存"""
        if self.cache_enabled:
            self._cache[cache_key] = {
                "result": result,
                "timestamp": datetime.now()
            }
    
    def _validate_image(self, image_path: str) -> bool:
        """验证图片"""
        path = Path(image_path)
        
        # 检查文件存在
        if not path.exists():
            return False
        
        # 检查格式
        ext = path.suffix.lower().lstrip(".")
        if ext not in self.supported_formats:
            return False
        
        # 检查大小
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.max_image_size_mb:
            return False
        
        return True
    
    async def recognize(
        self,
        image_path: str,
        language: Optional[str] = None,
        detect_language: bool = True
    ) -> OCRResult:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            language: 指定语言
            detect_language: 是否自动检测语言
            
        Returns:
            OCRResult: 识别结果
        """
        if not self.enabled:
            return OCRResult(
                success=False,
                text="",
                error="OCR service is disabled"
            )
        
        # 验证图片
        if not self._validate_image(image_path):
            return OCRResult(
                success=False,
                text="",
                error=f"Invalid image: {image_path}"
            )
        
        # 读取图片
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                error=f"Failed to read image: {str(e)}"
            )
        
        # 检查缓存
        cache_key = self._get_cache_key(image_data)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result
        
        # 调用 OCR 服务
        start_time = datetime.now()
        
        try:
            result = await self._call_deepseek_ocr(image_data, language, detect_language)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result.processing_time_ms = processing_time
            
            # 保存到缓存
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            # 尝试回退
            if self.fallback_enabled:
                return await self._fallback_ocr(image_data, str(e))
            
            return OCRResult(
                success=False,
                text="",
                error=f"OCR failed: {str(e)}"
            )
    
    async def _call_deepseek_ocr(
        self,
        image_data: bytes,
        language: Optional[str] = None,
        detect_language: bool = True
    ) -> OCRResult:
        """调用 DeepSeek OCR 服务"""
        # 这里是模拟实现，实际需要调用 DeepSeek API
        # service_id: deepseek-ocr-2sk-u3qymvvjrvxh26j6
        
        # 模拟 API 调用
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        # 模拟返回结果
        # 实际实现需要：
        # 1. 将图片编码为 base64
        # 2. 调用 DeepSeek OCR API
        # 3. 解析返回结果
        
        return OCRResult(
            success=True,
            text="[DeepSeek OCR Result]",
            confidence=0.95,
            language=language or "zh",
            provider=self.provider
        )
    
    async def _fallback_ocr(self, image_data: bytes, original_error: str) -> OCRResult:
        """回退 OCR"""
        if self.fallback_provider == "tesseract":
            return await self._call_tesseract_ocr(image_data)
        
        return OCRResult(
            success=False,
            text="",
            error=f"OCR failed and no fallback available. Original error: {original_error}"
        )
    
    async def _call_tesseract_ocr(self, image_data: bytes) -> OCRResult:
        """调用 Tesseract OCR（回退方案）"""
        # 模拟实现
        await asyncio.sleep(0.2)
        
        return OCRResult(
            success=True,
            text="[Tesseract OCR Result]",
            confidence=0.85,
            language="zh",
            provider="tesseract"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_id": self.service_id,
            "provider": self.provider,
            "enabled": self.enabled,
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self._cache),
            "fallback_enabled": self.fallback_enabled,
            "fallback_provider": self.fallback_provider,
            "supported_formats": self.supported_formats,
            "languages": self.languages
        }
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()


# 全局实例
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """获取 OCR 服务实例"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


# 便捷函数
async def ocr_recognize(image_path: str, language: Optional[str] = None) -> OCRResult:
    """识别图片文字"""
    service = get_ocr_service()
    return await service.recognize(image_path, language)
