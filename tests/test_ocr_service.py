"""
Test OCR Service - 测试 OCR 服务
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.ocr_service import (
    OCRService,
    OCRResult,
    OCRProvider,
    get_ocr_service,
    ocr_recognize
)


class TestOCRService:
    """OCR 服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建 OCR 服务"""
        config = {
            "service_id": "deepseek-ocr-2sk-u3qymvvjrvxh26j6",
            "provider": "deepseek",
            "enabled": True,
            "timeout_ms": 30000,
            "max_image_size_mb": 10,
            "supported_formats": ["jpg", "jpeg", "png", "gif", "webp", "bmp"],
            "languages": ["zh", "en", "ja", "ko"],
            "cache": {
                "enabled": True,
                "ttl_seconds": 3600
            },
            "fallback": {
                "enabled": True,
                "provider": "tesseract"
            }
        }
        return OCRService(config)
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service.service_id == "deepseek-ocr-2sk-u3qymvvjrvxh26j6"
        assert service.provider == "deepseek"
        assert service.enabled == True
        assert service.timeout_ms == 30000
        assert service.max_image_size_mb == 10
    
    def test_supported_formats(self, service):
        """测试支持的格式"""
        assert "jpg" in service.supported_formats
        assert "png" in service.supported_formats
        assert "gif" in service.supported_formats
        assert "webp" in service.supported_formats
    
    def test_languages(self, service):
        """测试支持的语言"""
        assert "zh" in service.languages
        assert "en" in service.languages
        assert "ja" in service.languages
        assert "ko" in service.languages
    
    def test_cache_enabled(self, service):
        """测试缓存启用"""
        assert service.cache_enabled == True
        assert service.cache_ttl == 3600
    
    def test_fallback_enabled(self, service):
        """测试回退启用"""
        assert service.fallback_enabled == True
        assert service.fallback_provider == "tesseract"
    
    def test_get_status(self, service):
        """测试获取状态"""
        status = service.get_status()
        
        assert status["service_id"] == "deepseek-ocr-2sk-u3qymvvjrvxh26j6"
        assert status["provider"] == "deepseek"
        assert status["enabled"] == True
        assert status["cache_enabled"] == True
        assert status["fallback_enabled"] == True
    
    @pytest.mark.asyncio
    async def test_recognize_disabled_service(self):
        """测试禁用服务的识别"""
        config = {"enabled": False}
        service = OCRService(config)
        
        result = await service.recognize("/tmp/test.jpg")
        
        assert result.success == False
        assert "disabled" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_recognize_invalid_image(self, service):
        """测试无效图片"""
        result = await service.recognize("/tmp/nonexistent_image.jpg")
        
        assert result.success == False
        assert "invalid" in result.error.lower()
    
    def test_clear_cache(self, service):
        """测试清除缓存"""
        service._cache["test_key"] = {"result": None, "timestamp": None}
        assert len(service._cache) == 1
        
        service.clear_cache()
        assert len(service._cache) == 0


class TestOCRResult:
    """OCR 结果测试"""
    
    def test_result_creation(self):
        """测试结果创建"""
        result = OCRResult(
            success=True,
            text="Hello World",
            confidence=0.95,
            language="en",
            provider="deepseek"
        )
        
        assert result.success == True
        assert result.text == "Hello World"
        assert result.confidence == 0.95
        assert result.language == "en"
        assert result.provider == "deepseek"
    
    def test_result_to_dict(self):
        """测试结果转字典"""
        result = OCRResult(
            success=True,
            text="Test",
            confidence=0.9,
            language="zh",
            provider="deepseek"
        )
        
        d = result.to_dict()
        
        assert d["success"] == True
        assert d["text"] == "Test"
        assert d["confidence"] == 0.9
        assert d["language"] == "zh"
        assert d["provider"] == "deepseek"
    
    def test_result_with_error(self):
        """测试带错误的结果"""
        result = OCRResult(
            success=False,
            text="",
            error="Something went wrong"
        )
        
        assert result.success == False
        assert result.error == "Something went wrong"


class TestGlobalService:
    """全局服务测试"""
    
    def test_get_ocr_service_singleton(self):
        """测试单例"""
        service1 = get_ocr_service()
        service2 = get_ocr_service()
        
        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
