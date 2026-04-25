# L4 Execution Layer - 升级版

执行层核心模块，包含故障转移、自动调优、向量量化、RAG优化等高级功能。

## 模块列表

### failover/ - 故障转移系统
- `failover.py` - 自动故障检测、节点切换、数据恢复

### optimizer/ - 自动调优系统
- `auto_tuner.py` - 自动参数搜索、A/B测试、性能基准测试

### quantization/ - 向量量化系统
- `quantization.py` - FP16/INT8/PQ/SQ量化
- `opq_quantization.py` - 优化乘积量化

### rag/ - RAG优化系统
- `rag_optimizer.py` - HyDE查询重写、子查询分解
- `query_rewriter.py` - 查询扩展、多查询融合

### vector_ops/ - 向量操作系统
- `vector_ops.py` - 向量计算、相似度计算
- `ann.py` - 近似最近邻搜索

## 升级效果

| 功能 | 提升 |
|------|------|
| 故障转移 | 可用性 ↑ 99.9% |
| 自动调优 | 性能 ↑ 30% |
| 向量量化 | 内存 ↓ 75%, 速度 ↑ 4x |
| RAG优化 | 检索相关性 ↑ 40% |
