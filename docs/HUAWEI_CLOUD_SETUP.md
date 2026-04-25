# 华为云免费试用申请指南

## 一、华为云数据库服务

### 1. GaussDB (PostgreSQL 兼容)

**免费试用**：
- 地址：https://www.huaweicloud.com/product/gaussdb.html
- 额度：免费试用 1 个月
- 规格：2核4GB

**申请步骤**：
1. 注册华为云账号
2. 实名认证
3. 进入 GaussDB 产品页
4. 点击"免费试用"
5. 选择区域（建议：cn-north-4 北京四）
6. 创建实例

**获取连接字符串**：
```
postgresql://username:password@host:8000/database
```

### 2. DCS (Redis)

**免费试用**：
- 地址：https://www.huaweicloud.com/product/dcs.html
- 额度：免费 1GB 实例
- 规格：单机版

**申请步骤**：
1. 进入 DCS 产品页
2. 点击"免费试用"
3. 选择 Redis 6.0
4. 选择区域（与 GaussDB 同区）
5. 创建实例

**获取连接字符串**：
```
redis://password@host:6379
```

## 二、配置环境变量

获取服务后，设置环境变量：

```bash
# GaussDB
export DATABASE_URL="postgresql://root:password@host:8000/postgres"

# DCS Redis
export REDIS_URL="redis://password@host:6379"
```

## 三、运行迁移

```bash
# 测试连接
python scripts/test_redis_connection.py

# 迁移数据库
python scripts/migrate_to_postgres.py

# 启动 Celery
python scripts/start_celery_production.py

# 运行验收
python scripts/production_acceptance.py
```

## 四、替代方案

如果华为云免费试用不可用，可以使用：

### 国际免费服务

| 服务 | 类型 | 免费额度 | 地址 |
|------|------|----------|------|
| Supabase | PostgreSQL | 500MB | https://supabase.com |
| Neon | PostgreSQL | 3GB | https://neon.tech |
| Railway | PostgreSQL + Redis | $5/月 | https://railway.app |
| Upstash | Redis | 10K 请求/天 | https://upstash.com |
| Redis Cloud | Redis | 30MB | https://redis.com/try-free |

### 国内免费服务

| 服务 | 类型 | 免费额度 | 地址 |
|------|------|----------|------|
| 阿里云 RDS | PostgreSQL | 试用 1 个月 | https://aliyun.com/product/rds |
| 腾讯云 MySQL | MySQL | 试用 1 个月 | https://cloud.tencent.com/product/cdb |
| 七牛云 | PostgreSQL | 试用 | https://qiniu.com |

## 五、当前状态

| 项目 | 状态 |
|------|------|
| 受限环境版 | ✅ 完成 |
| 生产基础设施版 | ⏳ 等待云服务配置 |

## 六、下一步

1. 申请华为云 GaussDB 和 DCS 免费试用
2. 获取连接字符串
3. 设置环境变量
4. 运行迁移脚本
5. 验收测试

---

**备注**：当前环境已使用 SQLite + FakeRedis 完成所有功能验证，生产环境迁移只需配置环境变量即可。
