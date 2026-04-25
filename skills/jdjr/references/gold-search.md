---
name: gold-search
description: 查询黄金、白银、铂金等贵金属实时行情、历史走势。适用于"黄金现在多少钱"、"白银走势"等请求。
---

# 黄金/贵金属查询

查询黄金、白银、铂金实时行情、历史走势。

## 什么时候用

用户想查询以下内容时：
- 黄金、白银实时行情、价格、涨跌
- 贵金属历史走势（K线）
- 近 N 天/周/月/年行情

支持：
- 黄金：`Au99.99`、`Au99.95`、`Au100g`、`Au(T+D)`、`mAu(T+D)`、`iAu99.99`
- 白银：`Ag99.99`、`Ag(T+D)`
- 铂金：`Pt99.95`
- 期货黄金：`au2602`（沪金）

## 怎么用

### 脚本调用

```bash
# 黄金实时行情
python3 scripts/query_gold.py Au99.99

# 白银实时行情
python3 scripts/query_gold.py Ag99.99

# 列出所有支持的品种
python3 scripts/query_gold.py --list
python3 scripts/query_gold.py -l

# 黄金 K线（支持 day/week/month）
python3 scripts/query_stock.py kline SGE-Au99.99 --k-type day   # 日K （近N<=30天）
python3 scripts/query_stock.py kline SGE-Au99.99 --k-type week  # 周K

# 黄金走势图表（近N<=30天）
python3 scripts/query_stock.py chart SGE-Au99.99 --days 15
```

### 意图识别

| 用户说 | 使用脚本 |
|--------|----------|
| 黄金/白银现在多少钱/实时行情 | `query_gold.py` |
| 列出所有黄金品种 | `query_gold.py --list` 或 `-l` |
| 日K/周K/月K/历史走势 | `query_stock.py kline SGE-xxx --k-type [day/week/month]` |
| 近N天走势/图表 | `query_stock.py chart SGE-xxx --days N` |

**注意**：查询历史走势用 `query_stock.py`，查询实时行情用 `query_gold.py`

## 怎么对用户输出（严格按照以下格式输出）

详细格式规范见 [references/output-format.md](references/output-format.md)

Agent 输出时按该文档格式渲染。

## 失败处理

- 品种代码错误 → "请使用正确的品种代码，如 Au99.99、Ag99.99，或输入 --list 查看所有支持的品种"
- 接口失败 → "服务异常，请稍后重试"
- 查不到数据 → "未找到相关数据"
