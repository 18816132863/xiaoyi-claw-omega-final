---
name: stock-search
description: 查询股票实时行情、历史走势、K线图表。适用于"查一下股票行情"、"近3个月走势"等请求。
---

# 股票查询

查询股票实时行情、历史走势。

## 什么时候用

用户想查询以下内容时：
- 股票实时行情、价格、涨跌
- 股票的历史走势（K线）
- 近 N 天/周/月/年行情

支持：
- A股：`SZ-000001`、`SH-600519`
- 港股：`HK-00700`
- 美股：`US-AAPL`

## 怎么用

### 脚本调用

```bash
# 股票实时行情
python3 scripts/query_stock.py quote SZ-000001

# 股票分时走势
python3 scripts/query_stock.py intraday SZ-000001

# 股票 K线（支持 day/week/month）
python3 scripts/query_stock.py kline SZ-000001 --k-type day   # 日K （近N<=30天）
python3 scripts/query_stock.py kline SZ-000001 --k-type week  # 周K
python3 scripts/query_stock.py kline SZ-000001 --k-type month # 月K

# 股票走势图表（近N<=30天）
python3 scripts/query_stock.py chart SZ-000001 --days 15
```

### 意图识别

| 用户说 | 使用脚本 |
|--------|----------|
| 实时行情/价格/涨跌 | `query_stock.py quote` |
| 分时走势 | `query_stock.py intraday` |
| 日K/周K/月K/历史走势 | `query_stock.py kline --k-type [day/week/month]` |
| 近N天走势/图表 | `query_stock.py chart --days N` |

## 怎么对用户输出（严格按照以下格式输出）

详细格式规范见 [references/output-format.md](references/output-format.md)

Agent 输出时按该文档格式渲染。

## 失败处理

- 股票代码格式错误 → "请使用股票代码，例如 SZ-000001、SH-600519"
- 无法识别股票名称 → "抱歉，无法识别股票名称，请提供股票代码，例如 SH-688336"
- 接口失败 → "服务异常，请稍后重试"
- 查不到数据 → "未找到相关数据"
