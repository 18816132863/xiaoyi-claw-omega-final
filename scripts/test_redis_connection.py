#!/usr/bin/env python3
"""
测试 Redis 连接 V1.0.0
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def test_redis_connection():
    """测试 Redis 连接"""
    
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    
    print("=" * 60)
    print("  测试 Redis 连接")
    print("=" * 60)
    print(f"  REDIS_URL: {redis_url}")
    print()
    
    try:
        import redis
        
        # 连接
        print("[1] 连接 Redis...")
        r = redis.from_url(redis_url)
        
        # PING
        print("[2] 发送 PING...")
        result = r.ping()
        print(f"  响应: {result}")
        
        if result:
            print("  ✅ Redis 连接成功")
        
        # 测试基本操作
        print()
        print("[3] 测试基本操作...")
        
        # SET
        r.set('test_key', 'test_value', ex=60)
        print("  SET test_key = test_value ✅")
        
        # GET
        value = r.get('test_key')
        print(f"  GET test_key = {value.decode()} ✅")
        
        # LPUSH/RPOP
        r.lpush('test_queue', 'task1', 'task2')
        print("  LPUSH test_queue ✅")
        
        item = r.rpop('test_queue')
        print(f"  RPOP test_queue = {item.decode()} ✅")
        
        # INFO
        print()
        print("[4] Redis 信息...")
        info = r.info()
        print(f"  版本: {info.get('redis_version')}")
        print(f"  已用内存: {info.get('used_memory_human')}")
        print(f"  连接数: {info.get('connected_clients')}")
        
        print()
        print("=" * 60)
        print("  ✅ Redis 连接测试通过")
        print("=" * 60)
        
        return True
    
    except ImportError:
        print("❌ 缺少 redis 库")
        print("  安装: pip install redis")
        return False
    
    except redis.exceptions.ConnectionError as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("免费 Redis 服务:")
        print("  - Upstash: https://upstash.com (免费 10,000 请求/天)")
        print("  - Redis Cloud: https://redis.com/try-free/ (免费 30MB)")
        print("  - Railway: https://railway.app (免费 $5/月)")
        return False
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    test_redis_connection()
