# Memory Context - 记忆层

## 职责
- 记忆上下文管理
- 知识库存储与检索
- 统一搜索服务
- 向量索引管理

## 目录结构
```
memory_context/
├── index/          # 索引文件
├── vector/         # 向量存储
├── search/         # 搜索服务
├── data/           # 数据文件
└── cache/          # 缓存
```

## 核心模块
- unified_search.py - 统一搜索入口
- vector/ - 向量引擎
- index/ - 索引管理

## 健康指标
- 索引大小: < 10MB
- 搜索延迟: < 500ms
- 缓存命中率: > 80%
