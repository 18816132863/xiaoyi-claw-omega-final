"""
核心模块
v4.1 - 全面性能优化
"""

from .sqlite_ext import (
    sqlite3,
    connect,
    connect_with_extension,
    get_sqlite_module,
    detect_sqlite_implementations,
    get_best_sqlite,
    print_sqlite_status,
    get_vec_installation_guide,
    is_extension_supported,
    HAS_PYSQLITE3,
    SUPPORTS_EXTENSION
)
from .sqlite_vec import (
    connect as sqlite_vec_connect,
    connect_with_extension as sqlite_vec_connect_with_extension,
    is_vec_available as sqlite_vec_available,
    get_vec_version as sqlite_vec_version,
    get_installation_guide as sqlite_vec_installation_guide
)
from .vector_ops import (
    VectorOps,
    AVX512VectorOps,
    get_vector_ops,
    cosine_similarity,
    euclidean_distance,
    top_k_search,
    detect_simd_support,
    SIMD_SUPPORT
)
from .gpu_ops import (
    GPUVectorOps,
    get_gpu_ops,
    detect_gpu_backend,
    GPU_INFO,
    CUDA_AVAILABLE,
    OPENCL_AVAILABLE
)
from .ann import (
    ANNIndex,
    BruteForceANN,
    LSHIndex,
    HNSWIndex,
    IVFIndex,
    create_ann_index
)
from .quantization import (
    FP16Quantizer,
    INT8Quantizer,
    ScalarQuantizer,
    ProductQuantizer,
    BinaryQuantizer,
    create_quantizer
)

# v4.0 新增
from .cpu_optimizer import CPUOptimizer, get_optimizer, optimize_for_intel_xeon
from .numba_accel import (
    cosine_similarity_numba,
    euclidean_distance_numba,
    dot_product_numba,
    int8_dot_product_vnni,
    top_k_search_numba,
    normalize_vector_numba,
    normalize_vectors_numba,
    warmup,
    is_numba_available,
    get_num_threads
)
from .cache_optimizer import CacheOptimizer, MemoryPool, get_cache_optimizer, get_memory_pool

# v4.1 新增
from .gpu_accel import GPUAccelerator, get_accelerator, is_gpu_available, detect_gpu
from .vnni_search import VNNISearcher, INT8Quantizer as VNNIQuantizer, check_vnni_support
from .ann_selector import ANNSelector
from .async_ops import AsyncVectorSearch, AsyncLLMClient, AsyncEmbeddingClient, AsyncMemoryPipeline
from .index_persistence import IndexPersistence, IncrementalIndexUpdater
# hugepage_manager.py 已删除 - 需要 root 权限

# v4.2 新增
from .distributed_search import DistributedSearcher, VectorSharder
from .query_cache import QueryCache, QueryResultCache
from .opq_quantization import OPQQuantizer
from .query_rewriter import QueryRewriter, QueryOptimizer
from .wal_optimizer import WALOptimizer, BatchWriter
from .auto_tuner import AutoTuner, PerformanceBenchmark, ABTestFramework
from .hardware_optimize import HardwareOptimizer, AMXAccelerator, NeuralEngineAccelerator, NEONAccelerator

# v5.2.18 新增 - NUMA 亲和性优化
from .numa_optimizer import NUMATopology, NUMAOptimizer, get_numa_optimizer, check_numa_status
# cache_aware_scheduler.py 已删除 - 需要 root 权限
# irq_isolator.py 已删除 - 需要 root 权限

# v5.2.22 新增 - FMA 加速
from .fma_accelerator import FMADetector, FMAAccelerator, get_fma_accelerator, check_fma_status

# v5.2.23 新增 - 华为鲲鹏/海思 ARM64 优化
from .kunpeng_optimizer import KunpengDetector, KunpengOptimizer, get_kunpeng_optimizer, check_kunpeng_status

# v5.2.24 新增 - 计算存储优化
from .computational_storage import ComputationalStorageDetector, ComputationalStorageOptimizer, get_computational_storage_optimizer, check_computational_storage_status

# v5.2.26 新增 - 缓存预取、内存对齐、RAG 优化
from .cache_prefetch import (
    CACHE_LINE_SIZE,
    CACHE_INFO,
    get_cache_info,
    align_to_cache_line,
    AlignedArray,
    CachePrefetcher,
    PrefetchOptimizedSearch,
    create_aligned_vectors,
    print_cache_status
)
from .memory_alignment import (
    SIMD_ALIGNMENT,
    SIMD512_ALIGNMENT,
    PAGE_SIZE,
    align_up,
    align_down,
    is_aligned,
    AlignedAllocator,
    AlignedVectorStorage,
    MemoryPool as AlignedMemoryPool,
    AlignedMatrix,
    optimize_vector_layout,
    get_alignment_recommendation,
    print_alignment_info
)
from .rag_optimizer import (
    HyDEQueryRewriter,
    SubQueryDecomposer,
    QueryExpander,
    MultiQueryFusion,
    RAGQueryOptimizer,
    print_optimization_summary
)

# v5.2.27 新增 - 零拷贝优化
# realtime_scheduler.py 已删除 - 需要 root 权限
from .zero_copy import (
    MappedFile,
    ZeroCopyVectorLoader,
    SharedMemoryVectorStore,
    ZeroCopyBuffer,
    sendfile_zero_copy,
    copy_file_zero_copy,
    check_zero_copy_capability,
    print_zero_copy_status
)

# v5.2.28 新增 - 缓存阻塞、ZRAM检测、MKL加速
from .cache_blocking import (
    get_cache_sizes,
    calculate_optimal_block_size,
    CacheBlockedMatrixMultiply,
    CacheBlockedVectorSearch,
    CacheBlockedBatchCompute,
    print_cache_blocking_info
)
from .zram_detector import (
    ZRAMDetector,
    ZswapDetector,
    MemoryCompressionStatus,
    check_zram_status,
    check_zswap_status,
    get_memory_compression_status,
    print_memory_compression_status
)
from .mkl_accelerator import (
    check_mkl_available,
    check_amx_available,
    check_intel_cpu,
    MKLAccelerator,
    FMALAccelerator,
    OptimizedMatrixOps,
    INT8QuantizedOps,
    print_mkl_status,
    check_mkl_status,
    check_fmal_status
)

# v5.2.29 新增 - 安全确认
from .security_confirmation import (
    SecurityConfirmation,
    require_confirmation,
    check_system_modification_allowed,
    load_security_config,
    save_security_config,
    print_security_status
)

# v6.0 新增 - RAGCache、近似缓存、多分辨率搜索、CXL优化、稀疏向量
from .rag_cache import (
    RAGCache,
    KnowledgeTree,
    LRUKCache,
    CacheEntry,
    RetrievalInferenceOverlap,
    print_ragcache_status
)
from .approximate_cache import (
    ApproximateCache,
    ApproximateCacheEntry,
    SemanticSimilarityMatcher,
    SemanticPromptCache,
    print_approximate_cache_status
)
from .multiresolution_search import (
    ResolutionLevel,
    MultiResolutionIndex,
    QueryComplexityEstimator,
    MultiResolutionSearcher,
    DistributedParallelSearcher,
    print_multiresolution_status
)
from .cxl_optimizer import (
    MemoryType,
    MemoryNode,
    CXLMemoryDetector,
    AdaptiveScheduler,
    HotDataMigrator,
    CXLOptimizer,
    print_cxl_status
)
from .sparse_anns import (
    SparseVector,
    SparseInvertedIndex,
    CompressedSparseStorage,
    SparseANNS,
    dense_to_sparse,
    sparse_to_dense,
    print_sparse_anns_status
)

# v5.0 新增
from .multimodal_search import MultimodalEncoder, MultimodalSearcher
from .cross_lingual import LanguageDetector, CrossLingualEncoder, CrossLingualSearcher
# Web API 已删除 - 不再提供 HTTP 服务
# monitor_dashboard.py 已删除 - 不再提供 HTTP 监控服务
from .cli_tool import CLITool
from .access_control import Permission, Role, User, AccessControlManager
from .conversation import Message, Conversation, ConversationManager, MemoryCompressor
from .llm_streaming import StreamChunk, LLMStreamer, SSEServer, WebSocketHandler
from .failover import NodeStatus, Node, HealthChecker, FailoverManager
from .model_router import TaskType, ModelCapability, Model, ModelRouter

__all__ = [
    # SQLite 扩展
    'sqlite3',
    'connect',
    'connect_with_extension',
    'get_sqlite_module',
    'detect_sqlite_implementations',
    'get_best_sqlite',
    'print_sqlite_status',
    'get_vec_installation_guide',
    'is_extension_supported',
    'HAS_PYSQLITE3',
    'SUPPORTS_EXTENSION',
    'sqlite_vec_connect',
    'sqlite_vec_connect_with_extension',
    'sqlite_vec_available',
    'sqlite_vec_version',
    'sqlite_vec_installation_guide',
    
    # AVX512 向量操作
    'VectorOps',
    'AVX512VectorOps',
    'get_vector_ops',
    'cosine_similarity',
    'euclidean_distance',
    'top_k_search',
    'detect_simd_support',
    'SIMD_SUPPORT',
    
    # GPU 加速
    'GPUVectorOps',
    'get_gpu_ops',
    'detect_gpu_backend',
    'GPU_INFO',
    'CUDA_AVAILABLE',
    'OPENCL_AVAILABLE',
    
    # ANN
    'ANNIndex',
    'BruteForceANN',
    'LSHIndex',
    'HNSWIndex',
    'IVFIndex',
    'create_ann_index',
    
    # 量化
    'FP16Quantizer',
    'INT8Quantizer',
    'ScalarQuantizer',
    'ProductQuantizer',
    'BinaryQuantizer',
    'create_quantizer',
    
    # v4.0 新增
    'CPUOptimizer',
    'get_optimizer',
    'optimize_for_intel_xeon',
    'cosine_similarity_numba',
    'euclidean_distance_numba',
    'dot_product_numba',
    'int8_dot_product_vnni',
    'top_k_search_numba',
    'normalize_vector_numba',
    'normalize_vectors_numba',
    'warmup',
    'is_numba_available',
    'get_num_threads',
    'CacheOptimizer',
    'MemoryPool',
    'get_cache_optimizer',
    'get_memory_pool',
    
    # v4.1 新增
    'GPUAccelerator',
    'get_accelerator',
    'is_gpu_available',
    'detect_gpu',
    'VNNISearcher',
    'VNNIQuantizer',
    'check_vnni_support',
    'ANNSelector',
    'AsyncVectorSearch',
    'AsyncLLMClient',
    'AsyncEmbeddingClient',
    'AsyncMemoryPipeline',
    'IndexPersistence',
    'IncrementalIndexUpdater',
    # HugePageManager 已删除 - 需要 root 权限
    
    # v4.2 新增
    'DistributedSearcher',
    'VectorSharder',
    'QueryCache',
    'QueryResultCache',
    'OPQQuantizer',
    'QueryRewriter',
    'QueryOptimizer',
    'WALOptimizer',
    'BatchWriter',
    'AutoTuner',
    'PerformanceBenchmark',
    'ABTestFramework',
    'HardwareOptimizer',
    'AMXAccelerator',
    'NeuralEngineAccelerator',
    'NEONAccelerator',
    
    # v5.2.18 新增 - NUMA 亲和性优化
    'NUMATopology',
    'NUMAOptimizer',
    'get_numa_optimizer',
    'check_numa_status',
    # CacheAwareScheduler 已删除 - 需要 root 权限
    # IRQIsolator 已删除 - 需要 root 权限
    
    # v5.2.22 新增 - FMA 加速
    'FMADetector',
    'FMAAccelerator',
    'get_fma_accelerator',
    'check_fma_status',
    
    # v5.2.23 新增 - 华为鲲鹏/海思 ARM64 优化
    'KunpengDetector',
    'KunpengOptimizer',
    'get_kunpeng_optimizer',
    'check_kunpeng_status',
    
    # v5.2.24 新增 - 计算存储优化
    'ComputationalStorageDetector',
    'ComputationalStorageOptimizer',
    'get_computational_storage_optimizer',
    'check_computational_storage_status',
    
    # v5.2.26 新增 - 缓存预取优化
    'CACHE_LINE_SIZE',
    'CACHE_INFO',
    'get_cache_info',
    'align_to_cache_line',
    'AlignedArray',
    'CachePrefetcher',
    'PrefetchOptimizedSearch',
    'create_aligned_vectors',
    'print_cache_status',
    
    # v5.2.26 新增 - 内存对齐优化
    'SIMD_ALIGNMENT',
    'SIMD512_ALIGNMENT',
    'PAGE_SIZE',
    'align_up',
    'align_down',
    'is_aligned',
    'AlignedAllocator',
    'AlignedVectorStorage',
    'AlignedMemoryPool',
    'AlignedMatrix',
    'optimize_vector_layout',
    'get_alignment_recommendation',
    'print_alignment_info',
    
    # v5.2.26 新增 - RAG 优化
    'HyDEQueryRewriter',
    'SubQueryDecomposer',
    'QueryExpander',
    'MultiQueryFusion',
    'RAGQueryOptimizer',
    'print_optimization_summary',
    
    # v5.2.27 新增 - 实时调度（已删除 - 需要 root 权限）
    
    # v5.2.27 新增 - 零拷贝
    'MappedFile',
    'ZeroCopyVectorLoader',
    'SharedMemoryVectorStore',
    'ZeroCopyBuffer',
    'sendfile_zero_copy',
    'copy_file_zero_copy',
    'check_zero_copy_capability',
    'print_zero_copy_status',
    
    # v5.2.28 新增 - 缓存阻塞
    'get_cache_sizes',
    'calculate_optimal_block_size',
    'CacheBlockedMatrixMultiply',
    'CacheBlockedVectorSearch',
    'CacheBlockedBatchCompute',
    'print_cache_blocking_info',
    
    # v5.2.28 新增 - ZRAM/Zswap
    'ZRAMDetector',
    'ZswapDetector',
    'MemoryCompressionStatus',
    'check_zram_status',
    'check_zswap_status',
    'get_memory_compression_status',
    'print_memory_compression_status',
    
    # v5.2.28 新增 - MKL/FMAL
    'check_mkl_available',
    'check_amx_available',
    'check_intel_cpu',
    'MKLAccelerator',
    'FMALAccelerator',
    'OptimizedMatrixOps',
    'INT8QuantizedOps',
    'print_mkl_status',
    'check_mkl_status',
    'check_fmal_status',
    
    # v5.2.29 新增 - 安全确认
    'SecurityConfirmation',
    'require_confirmation',
    'check_system_modification_allowed',
    'load_security_config',
    'save_security_config',
    'print_security_status',
    
    # v6.0 新增 - RAGCache
    'RAGCache',
    'KnowledgeTree',
    'LRUKCache',
    'CacheEntry',
    'RetrievalInferenceOverlap',
    'print_ragcache_status',
    
    # v6.0 新增 - 近似缓存
    'ApproximateCache',
    'ApproximateCacheEntry',
    'SemanticSimilarityMatcher',
    'SemanticPromptCache',
    'print_approximate_cache_status',
    
    # v6.0 新增 - 多分辨率搜索
    'ResolutionLevel',
    'MultiResolutionIndex',
    'QueryComplexityEstimator',
    'MultiResolutionSearcher',
    'DistributedParallelSearcher',
    'print_multiresolution_status',
    
    # v6.0 新增 - CXL 优化
    'MemoryType',
    'MemoryNode',
    'CXLMemoryDetector',
    'AdaptiveScheduler',
    'HotDataMigrator',
    'CXLOptimizer',
    'print_cxl_status',
    
    # v6.0 新增 - 稀疏向量 ANNS
    'SparseVector',
    'SparseInvertedIndex',
    'CompressedSparseStorage',
    'SparseANNS',
    'dense_to_sparse',
    'sparse_to_dense',
    'print_sparse_anns_status',
    
    # v5.0 新增
    'MultimodalEncoder',
    'MultimodalSearcher',
    'LanguageDetector',
    'CrossLingualEncoder',
    'CrossLingualSearcher',
    # Web API 已删除
    'CLITool',
    'Permission',
    'Role',
    'User',
    'AccessControlManager',
    'Message',
    'Conversation',
    'ConversationManager',
    'MemoryCompressor',
    'StreamChunk',
    'LLMStreamer',
    'SSEServer',
    'WebSocketHandler',
    'NodeStatus',
    'Node',
    'HealthChecker',
    'FailoverManager',
    'TaskType',
    'ModelCapability',
    'Model',
    'ModelRouter',
    
    # monitor_dashboard 已删除
]
