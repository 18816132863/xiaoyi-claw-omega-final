// AVX-512 优化实现

#pragma once

#include <immintrin.h>
#include <cstdint>
#include <cstddef>
#include <cmath>
#include <algorithm>
#include <vector>

namespace claw {
namespace avx512 {

// ============================================================================
// 检测 AVX-512 支持
// ============================================================================
inline bool has_avx512() {
    uint32_t eax, ebx, ecx, edx;
    __cpuid_count(7, 0, eax, ebx, ecx, edx);
    return (ebx & (1 << 16)) != 0;  // AVX512F
}

inline bool has_avx512dq() {
    uint32_t eax, ebx, ecx, edx;
    __cpuid_count(7, 0, eax, ebx, ecx, edx);
    return (ebx & (1 << 17)) != 0;  // AVX512DQ
}

inline bool has_avx512bw() {
    uint32_t eax, ebx, ecx, edx;
    __cpuid_count(7, 0, eax, ebx, ecx, edx);
    return (ebx & (1 << 30)) != 0;  // AVX512BW
}

// ============================================================================
// 向量运算
// ============================================================================

// 点积 (AVX-512)
inline float dot_product(const float* a, const float* b, size_t dim) {
    __m512 sum = _mm512_setzero_ps();
    
    size_t i = 0;
    for (; i + 16 <= dim; i += 16) {
        __m512 va = _mm512_loadu_ps(a + i);
        __m512 vb = _mm512_loadu_ps(b + i);
        sum = _mm512_fmadd_ps(va, vb, sum);
    }
    
    float result = _mm512_reduce_add_ps(sum);
    
    // 处理剩余元素
    for (; i < dim; ++i) {
        result += a[i] * b[i];
    }
    
    return result;
}

// 向量范数
inline float vector_norm(const float* v, size_t dim) {
    return std::sqrt(dot_product(v, v, dim));
}

// 余弦相似度
inline float cosine_similarity(const float* a, const float* b, size_t dim) {
    float dot = dot_product(a, b, dim);
    float norm_a = vector_norm(a, dim);
    float norm_b = vector_norm(b, dim);
    return dot / (norm_a * norm_b + 1e-8f);
}

// 批量余弦相似度
inline void batch_cosine_similarity(
    const float* query,
    const float* const* vectors,
    size_t num_vectors,
    size_t dim,
    float* scores
) {
    float query_norm = vector_norm(query, dim);
    
    #pragma omp parallel for
    for (size_t i = 0; i < num_vectors; ++i) {
        float dot = dot_product(query, vectors[i], dim);
        float norm = vector_norm(vectors[i], dim);
        scores[i] = dot / (query_norm * norm + 1e-8f);
    }
}

// 向量加法
inline void vector_add(const float* a, const float* b, float* c, size_t dim) {
    size_t i = 0;
    for (; i + 16 <= dim; i += 16) {
        __m512 va = _mm512_loadu_ps(a + i);
        __m512 vb = _mm512_loadu_ps(b + i);
        __m512 vc = _mm512_add_ps(va, vb);
        _mm512_storeu_ps(c + i, vc);
    }
    
    for (; i < dim; ++i) {
        c[i] = a[i] + b[i];
    }
}

// 向量标量乘法
inline void vector_scale(const float* a, float scale, float* b, size_t dim) {
    __m512 vs = _mm512_set1_ps(scale);
    
    size_t i = 0;
    for (; i + 16 <= dim; i += 16) {
        __m512 va = _mm512_loadu_ps(a + i);
        __m512 vb = _mm512_mul_ps(va, vs);
        _mm512_storeu_ps(b + i, vb);
    }
    
    for (; i < dim; ++i) {
        b[i] = a[i] * scale;
    }
}

// ============================================================================
// 内存操作
// ============================================================================

// 内存复制
inline void fast_memcpy(void* dst, const void* src, size_t size) {
    __m512i* d = static_cast<__m512i*>(dst);
    const __m512i* s = static_cast<const __m512i*>(src);
    
    size_t i = 0;
    for (; i + 64 <= size; i += 64) {
        __m512i data = _mm512_loadu_si512(s + i / 64);
        _mm512_storeu_si512(d + i / 64, data);
    }
    
    // 处理剩余字节
    if (i < size) {
        __mmask64 mask = (1ULL << (size - i)) - 1;
        __m512i data = _mm512_maskz_loadu_epi8(mask, reinterpret_cast<const void*>(s + i / 64));
        _mm512_mask_storeu_epi8(d + i / 64, mask, data);
    }
}

// 内存比较
inline int fast_memcmp(const void* a, const void* b, size_t size) {
    const __m512i* pa = static_cast<const __m512i*>(a);
    const __m512i* pb = static_cast<const __m512i*>(b);
    
    size_t i = 0;
    for (; i + 64 <= size; i += 64) {
        __m512i va = _mm512_loadu_si512(pa + i / 64);
        __m512i vb = _mm512_loadu_si512(pb + i / 64);
        
        __mmask64 diff = _mm512_cmpneq_epi8_mask(va, vb);
        if (diff) {
            return static_cast<int>(__builtin_popcountll(diff & ((1ULL << (size - i)) - 1)));
        }
    }
    
    // 处理剩余字节
    for (; i < size; ++i) {
        if (static_cast<const uint8_t*>(a)[i] != static_cast<const uint8_t*>(b)[i]) {
            return static_cast<const uint8_t*>(a)[i] - static_cast<const uint8_t*>(b)[i];
        }
    }
    
    return 0;
}

// 内存设置
inline void fast_memset(void* dst, uint8_t value, size_t size) {
    __m512i v = _mm512_set1_epi8(value);
    __m512i* d = static_cast<__m512i*>(dst);
    
    size_t i = 0;
    for (; i + 64 <= size; i += 64) {
        _mm512_storeu_si512(d + i / 64, v);
    }
    
    if (i < size) {
        __mmask64 mask = (1ULL << (size - i)) - 1;
        _mm512_mask_storeu_epi8(d + i / 64, mask, v);
    }
}

// ============================================================================
// 字符串操作
// ============================================================================

// 字符串长度
inline size_t fast_strlen(const char* str) {
    const __m512i* p = reinterpret_cast<const __m512i*>(str);
    __m512i zero = _mm512_setzero_si512();
    
    size_t offset = 0;
    while (true) {
        __m512i chunk = _mm512_loadu_si512(p);
        __mmask64 mask = _mm512_cmpeq_epi8_mask(chunk, zero);
        
        if (mask) {
            int idx = __builtin_ctzll(mask);
            return offset + idx;
        }
        
        offset += 64;
        ++p;
    }
}

// 字符串查找
inline const char* fast_strstr(const char* haystack, const char* needle) {
    size_t needle_len = fast_strlen(needle);
    if (needle_len == 0) return haystack;
    
    __m512i first_char = _mm512_set1_epi8(needle[0]);
    
    for (size_t i = 0; haystack[i]; i += 64) {
        __m512i chunk = _mm512_loadu_si512(reinterpret_cast<const __m512i*>(haystack + i));
        __mmask64 match = _mm512_cmpeq_epi8_mask(chunk, first_char);
        
        while (match) {
            int idx = __builtin_ctzll(match);
            if (fast_memcmp(haystack + i + idx, needle, needle_len) == 0) {
                return haystack + i + idx;
            }
            match &= match - 1;
        }
    }
    
    return nullptr;
}

// ============================================================================
// 哈希计算
// ============================================================================

// 简单哈希 (用于快速校验)
inline uint64_t fast_hash(const void* data, size_t size) {
    const uint64_t* p = static_cast<const uint64_t*>(data);
    __m512i hash = _mm512_setzero_si512();
    
    size_t i = 0;
    for (; i + 64 <= size; i += 64) {
        __m512i chunk = _mm512_loadu_si512(reinterpret_cast<const __m512i*>(p + i / 8));
        hash = _mm512_xor_si512(hash, chunk);
        hash = _mm512_mullo_epi64(hash, _mm512_set1_epi64(0x5851F42D4C957F2D));
    }
    
    // 合并 512 位到 64 位
    __m256i lo = _mm512_castsi512_si256(hash);
    __m256i hi = _mm512_extracti64x4_epi64(hash, 1);
    __m256i combined = _mm256_xor_si256(lo, hi);
    
    __m128i lo2 = _mm256_castsi256_si128(combined);
    __m128i hi2 = _mm256_extracti128_si256(combined, 1);
    __m128i final = _mm_xor_si128(lo2, hi2);
    
    uint64_t result = _mm_extract_epi64(final, 0) ^ _mm_extract_epi64(final, 1);
    
    // 处理剩余字节
    const uint8_t* remaining = static_cast<const uint8_t*>(data) + i;
    for (; i < size; ++i) {
        result ^= static_cast<uint64_t>(remaining[i - (size - (size % 64))]) << ((i % 8) * 8);
    }
    
    return result;
}

} // namespace avx512
} // namespace claw
