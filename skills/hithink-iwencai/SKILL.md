---
name: hithink-iwencai
description: 同花顺i问财综合金融数据查询技能。整合行情查询、财务查询、基金查询、宏观查询、指数查询、A股选股、期货选股、公告搜索、新闻搜索、研报搜索等十大核心能力。支持股票、ETF、基金、期货、宏观经济等多维度金融数据查询，以及公告、新闻、研报等资讯搜索。当用户需要查询股票行情、财务数据、基金信息、宏观数据、选股筛选、公告新闻研报时，使用此技能。
license: Complete terms in LICENSE.txt
---

# 同花顺i问财综合技能

## 版本
`1.0.0`

## 技能概述

本技能整合了同花顺i问财的十大核心查询能力，提供一站式金融数据与资讯服务：

### 📊 行情数据查询 (market-query)
- 股票实时价格、涨跌幅、涨跌额
- 成交量、成交额、换手率
- 主力资金流向、大单小单、主力净流入
- 技术指标（MACD、KDJ、RSI、布林线等）
- ETF 行情数据
- 指数行情数据（上证指数、沪深300、创业板指等）

### 📈 财务数据查询 (finance-query)
- 上市公司财务报表数据
- 营收、净利润、毛利率、ROE等财务指标
- 资产负债表、利润表、现金流量表数据
- 财务比率分析

### 💰 基金数据查询 (fund-query)
- 基金净值、涨跌幅
- 基金持仓、基金经理信息
- 基金业绩排名
- 基金类型筛选

### 🌏 宏观经济查询 (macro-query)
- GDP、CPI、PPI等宏观经济指标
- 货币供应量、利率数据
- 进出口贸易数据
- 行业经济数据

### 📉 指数数据查询 (zhishu-query)
- 各类市场指数行情
- 行业指数、主题指数
- 指数成分股查询
- 指数估值数据

### 🔍 A股选股筛选 (astock-selector)
- 多维度选股条件筛选
- 技术指标选股
- 财务指标选股
- 行业板块选股

### 📊 期货选股筛选 (futures-selector)
- 期货行情查询
- 期货品种筛选
- 期货技术分析
- 期现套利机会

### 📢 公告搜索 (announcement-search)
- A股、港股、基金、ETF公告查询
- 定期财务报告、分红派息公告
- 回购增持、资产重组公告
- 重大合同、业绩预告公告

### 📰 新闻搜索 (news-search)
- 财经新闻实时搜索
- 个股相关新闻
- 行业动态新闻
- 市场热点追踪

### 📑 研报搜索 (report-search)
- 主流投研机构研究报告
- 投资评级、目标价信息
- 行业深度分析报告
- 公司研究报告

数据来源：**同花顺问财**（https://www.iwencai.com）

---

## 首次使用 - 获取 API Key

所有功能都需要 `IWENCAI_API_KEY` 环境变量才能使用。

### 获取步骤

**步骤 1**：在浏览器打开同花顺i问财SkillHub页面：https://www.iwencai.com/skillhub

**步骤 2**：登录账号

**步骤 3**：点击具体的Skill，打开弹窗查看详情，在「安装方式 - Agent用户」中找到您的 `IWENCAI_API_KEY`，复制

**步骤 4**：配置环境变量

### 环境变量配置

**macOS / Linux (bash/zsh):**
```bash
export IWENCAI_API_KEY="your-api-key-here"
```

**Windows (PowerShell):**
```powershell
$env:IWENCAI_API_KEY="your-api-key-here"
```

**Windows (CMD):**
```cmd
set IWENCAI_API_KEY=your-api-key-here
```

---

## 接口规范

### HTTP Header 要求
所有发往问财 OpenAPI 网关的请求必须包含以下 Header：

| Header | 取值说明 |
|--------|----------|
| `X-Claw-Call-Type` | `normal`：正常请求；`retry`：失败后的重试 |
| `X-Claw-Skill-Id` | 技能标识，见下方子技能ID对照表 |
| `X-Claw-Skill-Version` | 当前技能版本号，固定为 `1.0.0` |
| `X-Claw-Plugin-Id` | 插件 ID，固定为 `none` |
| `X-Claw-Plugin-Version` | 插件版本，固定为 `none` |
| `X-Claw-Trace-Id` | 每次请求新生成的64字符全局唯一追踪ID |

### 子技能ID对照表

| 功能 | Skill ID |
|------|----------|
| 行情查询 | `hithink-market-query` |
| 财务查询 | `hithink-finance-query` |
| 基金查询 | `hithink-fund-query` |
| 宏观查询 | `hithink-macro-query` |
| 指数查询 | `hithink-zhishu-query` |
| A股选股 | `hithink-astock-selector` |
| 期货选股 | `hithink-futures-selector` |
| 公告搜索 | `announcement-search` |
| 新闻搜索 | `news-search` |
| 研报搜索 | `report-search` |

### 基础信息
- **Base URL**: `https://openapi.iwencai.com`
- **接口路径**: `/v1/comprehensive/search`
- **请求方式**: POST
- **认证方式**: Bearer Token

### 认证要求
```http
Authorization: Bearer {IWENCAI_API_KEY}
```

### 请求参数示例

**行情/财务/基金/宏观/指数/选股查询：**
```json
{
  "channels": ["stock"],
  "app_id": "AIME_SKILL",
  "query": "贵州茅台今日行情"
}
```

**公告搜索：**
```json
{
  "channels": ["announcement"],
  "app_id": "AIME_SKILL",
  "query": "贵州茅台公告"
}
```

**新闻搜索：**
```json
{
  "channels": ["news"],
  "app_id": "AIME_SKILL",
  "query": "人工智能行业新闻"
}
```

**研报搜索：**
```json
{
  "channels": ["report"],
  "app_id": "AIME_SKILL",
  "query": "新能源汽车行业研报"
}
```

---

## 使用场景

### 行情查询场景
- "贵州茅台今天股价多少？"
- "上证指数最新行情"
- "主力资金流入最多的股票"
- "MACD金叉的股票有哪些"

### 财务查询场景
- "贵州茅台去年营收多少"
- "ROE大于15%的公司"
- "净利润同比增长超过50%的公司"

### 基金查询场景
- "易方达蓝筹精选基金净值"
- "近一年收益最好的科技基金"
- "张坤管理的基金有哪些"

### 宏观查询场景
- "中国GDP增速"
- "最新CPI数据"
- "M2货币供应量"

### 选股筛选场景
- "市盈率小于20且ROE大于15%的股票"
- "连续三年净利润增长超过20%的公司"
- "北向资金持股比例增加的股票"

### 资讯搜索场景
- "贵州茅台最新公告"
- "人工智能行业最新新闻"
- "比亚迪研报"

---

## 命令行使用

```bash
# 行情查询
python scripts/cli.py market -q "贵州茅台今日行情"

# 财务查询
python scripts/cli.py finance -q "贵州茅台财务数据"

# 基金查询
python scripts/cli.py fund -q "易方达蓝筹精选"

# 宏观查询
python scripts/cli.py macro -q "中国GDP增速"

# 公告搜索
python scripts/cli.py announcement -q "贵州茅台公告" -l 10

# 新闻搜索
python scripts/cli.py news -q "人工智能新闻" -l 20

# 研报搜索
python scripts/cli.py report -q "新能源汽车研报" -l 5

# 导出结果
python scripts/cli.py report -q "芯片行业研报" -o results.csv -f csv
```

---

## curl 示例

```bash
curl -X POST "https://openapi.iwencai.com/v1/comprehensive/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $IWENCAI_API_KEY" \
  -H "X-Claw-Call-Type: normal" \
  -H "X-Claw-Skill-Id: hithink-market-query" \
  -H "X-Claw-Skill-Version: 1.0.0" \
  -H "X-Claw-Plugin-Id: none" \
  -H "X-Claw-Plugin-Version: none" \
  -H "X-Claw-Trace-Id: $(python -c 'import secrets; print(secrets.token_hex(32))')" \
  -d '{
    "channels": ["stock"],
    "app_id": "AIME_SKILL",
    "query": "贵州茅台今日行情"
  }'
```

---

## 技能内部逻辑

### 查询处理流程
1. **接收用户查询**：获取用户的金融数据或资讯搜索需求
2. **意图识别**：判断用户需要哪类数据（行情/财务/基金/宏观/资讯等）
3. **查询优化**：生成标准化的专业查询关键词
4. **API调用**：构建请求，携带正确的Header和认证信息
5. **数据处理**：解析返回结果，提取关键信息
6. **结果返回**：格式化输出，标注数据来源

### 错误处理
- 网络异常自动重试（最多3次）
- API限流时等待后重试
- 无结果时给出友好提示

---

## 数据来源标注

**重要**: 所有数据均来源于同花顺问财，回答时必须标注来源。

示例：
- "根据同花顺问财数据..."
- "数据来源：同花顺问财"
- "同花顺问财显示..."

---

## 目录结构

```
hithink-iwencai/
├── SKILL.md                 # 技能主文档
├── README.md                # 说明文档
├── LICENSE.txt              # 许可证
├── references/              # 参考文档
│   └── api.md              # API文档
└── scripts/                 # 源代码
    ├── __main__.py         # 入口点
    ├── cli.py              # 命令行接口
    ├── api_client.py       # API客户端
    ├── config.py           # 配置管理
    ├── data_processor.py   # 数据处理
    ├── announcement_search.py  # 公告搜索
    ├── news_search.py      # 新闻搜索
    ├── research_report_search.py  # 研报搜索
    ├── utils.py            # 工具函数
    ├── requirements.txt    # Python依赖
    └── test_basic.py       # 测试文件
```

---

## 注意事项

1. **API Key 安全**：切勿将 API Key 硬编码到代码中
2. **请求频率**：遵守接口调用频率限制
3. **数据来源**：必须标注数据来源于同花顺问财
4. **错误处理**：实现完善的错误处理机制
5. **版本兼容**：Header 中的版本号需与技能版本一致
