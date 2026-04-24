# 同花顺i问财综合技能

一站式金融数据与资讯查询技能，整合同花顺i问财十大核心能力。

## 功能概览

| 模块 | 功能 | 示例查询 |
|------|------|----------|
| 📊 行情查询 | 股票、ETF、指数实时行情 | "贵州茅台今日行情" |
| 📈 财务查询 | 上市公司财务数据 | "茅台去年营收多少" |
| 💰 基金查询 | 基金净值、持仓、业绩 | "易方达蓝筹精选净值" |
| 🌏 宏观查询 | GDP、CPI等宏观数据 | "中国最新GDP增速" |
| 📉 指数查询 | 各类市场指数数据 | "沪深300成分股" |
| 🔍 A股选股 | 多维度选股筛选 | "ROE大于15%的股票" |
| 📊 期货选股 | 期货行情与筛选 | "铜期货主力合约" |
| 📢 公告搜索 | 公司公告查询 | "茅台最新公告" |
| 📰 新闻搜索 | 财经新闻搜索 | "人工智能行业新闻" |
| 📑 研报搜索 | 投研报告搜索 | "新能源车行业研报" |

## 快速开始

### 1. 获取 API Key

访问 [同花顺i问财SkillHub](https://www.iwencai.com/skillhub)，登录后在任意Skill详情中获取您的 `IWENCAI_API_KEY`。

### 2. 配置环境变量

```bash
export IWENCAI_API_KEY="your-api-key-here"
```

### 3. 安装依赖

```bash
pip install -r scripts/requirements.txt
```

### 4. 开始使用

```bash
# 命令行方式
python scripts/cli.py market -q "贵州茅台今日行情"

# 或作为模块调用
python -m scripts market -q "贵州茅台今日行情"
```

## 使用示例

### 行情查询
```bash
python scripts/cli.py market -q "主力资金流入最多的股票"
```

### 财务查询
```bash
python scripts/cli.py finance -q "净利润增长超过50%的公司"
```

### 研报搜索
```bash
python scripts/cli.py report -q "人工智能行业研报" -l 10 -o report.csv -f csv
```

## 数据来源

所有数据均来源于 **同花顺问财** (https://www.iwencai.com)

## 许可证

详见 [LICENSE.txt](LICENSE.txt)

## 版本历史

- v1.0.0 - 整合十大核心功能，统一API接口
