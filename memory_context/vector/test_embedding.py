"""
测试 Embedding API 连接
"""
import os
import sys

# 设置环境变量（如果未设置）
if not os.environ.get("API_TOKEN"):
    os.environ["API_TOKEN"] = "JEHMRUUDOKBQQLCSWIIA0EYHKDZJ3KORM2NEVLPM"
if not os.environ.get("GITEE_AI_API_KEY"):
    os.environ["GITEE_AI_API_KEY"] = "JEHMRUUDOKBQQLCSWIIA0EYHKDZJ3KORM2NEVLPM"

try:
    from openai import OpenAI
except ImportError:
    print("请手动安装 openai 库: pip install openai")
    sys.exit(1)

print("=" * 50)
print("Qwen3-Embedding-8B API 测试")
print("=" * 50)

# 创建客户端
client = OpenAI(
    base_url="https://ai.gitee.com/v1",
    api_key=os.environ.get("API_TOKEN"),
    default_headers={"X-Failover-Enabled": "true"},
)

# 测试不同维度
test_text = "Today is a sunny day and I will get some ice cream."

print(f"\n测试文本: {test_text}")
print("\n维度测试:")

for dim in [1024, 2048, 4096]:
    try:
        response = client.embeddings.create(
            input=test_text,
            model="Qwen3-Embedding-8B",
            dimensions=dim,
        )
        vector = response.data[0].embedding
        print(f"  ✅ 维度 {dim}: 成功 (向量长度: {len(vector)})")
    except Exception as e:
        print(f"  ❌ 维度 {dim}: 失败 ({e})")

# 批量测试
print("\n批量测试:")
texts = [
    "机器学习是人工智能的一个分支",
    "深度学习使用神经网络进行学习",
    "自然语言处理处理人类语言"
]

try:
    response = client.embeddings.create(
        input=texts,
        model="Qwen3-Embedding-8B",
        dimensions=4096,
    )
    print(f"  ✅ 批量生成: {len(response.data)} 个向量")
except Exception as e:
    print(f"  ❌ 批量生成失败: {e}")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
