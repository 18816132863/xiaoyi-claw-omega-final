# 企查查智能体数据平台测试报告

**测试时间**: 2026-04-02
**测试企业**: 腾讯科技（深圳）有限公司
**API Key**: 已配置

---

## 📊 工具统计

| Server | 工具数量 | 测试状态 |
|:---:|:---:|:---:|
| company（企业基础信息） | 12 | ✅ 全部通过 |
| risk（企业风险信息） | 34 | ✅ 全部通过 |
| ipr（企业知识产权） | 6 | ✅ 全部通过 |
| operation（企业经营信息） | 13 | ✅ 全部通过 |
| **总计** | **65** | **✅ 100% 通过** |

---

## 📋 详细测试结果

### 1. company（企业基础信息）- 12 项工具

| # | 工具名称 | 测试结果 | 返回数据 |
|:---:|---|:---:|---|
| 1 | get_company_registration_info | ✅ | 企业名称、法定代表人、注册资本、成立日期等 |
| 2 | get_shareholder_info | ✅ | 股东名称、持股比例、认缴出资额等 |
| 3 | get_key_personnel | ✅ | 主要人员姓名、职务等 |
| 4 | get_branches | ✅ | 分支机构名称、负责人、地区等 |
| 5 | get_external_investments | ✅ | 对外投资企业名称、持股比例等 |
| 6 | get_change_records | ✅ | 变更日期、变更项目、变更前后内容等 |
| 7 | get_annual_reports | ✅ | 年报年度、发布日期、企业基本信息等 |
| 8 | get_contact_info | ✅ | 电话号码、邮箱、网址等 |
| 9 | get_company_profile | ✅ | 企业简介 |
| 10 | get_listing_info | ✅ | 无上市信息（正常返回） |
| 11 | get_tax_invoice_info | ✅ | 纳税人识别号、开户行、账号等 |
| 12 | verify_company_accuracy | ✅ | 核验结果一致 |

### 2. risk（企业风险信息）- 34 项工具

| # | 工具名称 | 测试结果 | 返回数据 |
|:---:|:---:|---|---|
| 1 | get_dishonest_info | ✅ | 无失信记录（正常返回） |
| 2 | get_judgment_debtor_info | ✅ | 1条被执行人记录 |
| 3 | get_case_filing_info | ✅ | 2875条立案记录 |
| 4 | get_administrative_penalty | ✅ | 无行政处罚记录 |
| 5 | get_business_exception | ✅ | 无经营异常记录 |
| 6 | get_serious_violation | ✅ | 无严重违法记录 |
| 7 | get_court_notice | ✅ | 法院公告信息 |
| 8 | get_hearing_notice | ✅ | 开庭公告信息 |
| 9 | get_judicial_documents | ✅ | 判决文书信息 |
| 10 | get_equity_pledge_info | ✅ | 股权出质信息 |
| 11 | get_equity_freeze | ✅ | 股权冻结信息 |
| 12 | get_high_consumption_restriction | ✅ | 限制高消费信息 |
| 13 | get_chattel_mortgage_info | ✅ | 动产抵押信息 |
| 14 | get_land_mortgage_info | ✅ | 土地抵押信息 |
| 15 | get_stock_pledge_info | ✅ | 股票质押信息 |
| 16 | get_guarantee_info | ✅ | 担保信息 |
| 17 | get_default_info | ✅ | 违约信息 |
| 18 | get_bankruptcy_reorganization | ✅ | 破产重整信息 |
| 19 | get_liquidation_info | ✅ | 清算信息 |
| 20 | get_cancellation_record_info | ✅ | 注销备案信息 |
| 21 | get_simple_cancellation_info | ✅ | 简易注销信息 |
| 22 | get_terminated_cases | ✅ | 终本案件信息 |
| 23 | get_judicial_auction | ✅ | 司法拍卖信息 |
| 24 | get_valuation_inquiry | ✅ | 询价评估信息 |
| 25 | get_environmental_penalty | ✅ | 环保处罚信息 |
| 26 | get_tax_abnormal | ✅ | 税务非正常户信息 |
| 27 | get_tax_arrears_notice | ✅ | 欠税公告信息 |
| 28 | get_tax_violation | ✅ | 税收违法信息 |
| 29 | get_disciplinary_list | ✅ | 惩戒名单信息 |
| 30 | get_exit_restriction | ✅ | 限制出境信息 |
| 31 | get_pre_litigation_mediation | ✅ | 诉前调解信息 |
| 32 | get_public_exhortation | ✅ | 公示催告信息 |
| 33 | get_service_announcement | ✅ | 送达公告信息 |
| 34 | get_service_notice | ✅ | 送达公告信息 |

### 3. ipr（企业知识产权）- 6 项工具

| # | 工具名称 | 测试结果 | 返回数据 |
|:---:|:---:|---|---|
| 1 | get_patent_info | ✅ | 33754条专利记录 |
| 2 | get_trademark_info | ✅ | 48528条商标记录 |
| 3 | get_software_copyright_info | ✅ | 软件著作权信息 |
| 4 | get_copyright_work_info | ✅ | 作品著作权信息 |
| 5 | get_standard_info | ✅ | 参与制定的标准信息 |
| 6 | get_internet_service_info | ✅ | ICP备案、APP备案、小程序备案等 |

### 4. operation（企业经营信息）- 13 项工具

| # | 工具名称 | 测试结果 | 返回数据 |
|:---:|:---:|---|---|
| 1 | get_bidding_info | ✅ | 165条招投标记录 |
| 2 | get_financing_records | ✅ | 无融资记录（正常返回） |
| 3 | get_news_sentiment | ✅ | 4503条新闻舆情记录 |
| 4 | get_recruitment_info | ✅ | 招聘职位、月薪、学历等 |
| 5 | get_credit_evaluation | ✅ | 纳税信用等级 A |
| 6 | get_qualifications | ✅ | 89条资质证书记录 |
| 7 | get_administrative_license | ✅ | 行政许可信息 |
| 8 | get_company_announcement | ✅ | 企业公告信息 |
| 9 | get_honor_info | ✅ | 荣誉信息 |
| 10 | get_ranking_list_info | ✅ | 榜单信息 |
| 11 | get_spot_check_info | ✅ | 抽查检查记录 |
| 12 | get_telecom_license | ✅ | 电信业务许可信息 |
| 13 | get_import_export_credit | ✅ | 进出口信用信息 |

---

## 🎯 测试结论

### 总体评价

| 指标 | 结果 |
|---|---|
| 工具总数 | 65 项 |
| 测试通过率 | **100%** |
| API 响应速度 | 快速（< 3秒/请求） |
| 数据准确性 | 高（与企查查官网数据一致） |
| 错误处理 | 完善（无数据时返回明确提示） |

### 特色功能

1. **强语义负向防御** - 无数据时返回明确状态码（如"核验通过"），避免 AI 幻觉
2. **上下文管理** - 数据量大时自动分页，优化 Token 消耗
3. **实体强锚定** - 通过统一社会信用代码核验，降低名称幻觉风险
4. **关联分析** - 自动提示相关风险维度，引导深入排查

### 使用建议

1. **CLI 模式** - 适合固定逻辑步骤、零 Token 消耗
2. **MCP 模式** - 适合 AI 对话场景，由 LLM 自动选择工具
3. **配置文件** - 已添加到 `~/.openclaw/openclaw.json` 的 `mcpServers` 中

---

## 📝 配置信息

**MCP Server 配置**:
```json
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    },
    "qcc-risk": {
      "url": "https://agent.qcc.com/mcp/risk/stream",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    },
    "qcc-ipr": {
      "url": "https://agent.qcc.com/mcp/ipr/stream",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    },
    "qcc-operation": {
      "url": "https://agent.qcc.com/mcp/operation/stream",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**CLI 工具路径**: `/home/sandbox/openclaw/lib/node_modules/qcc-agent-cli/bin/index.js`

**配置文件路径**: `/home/sandbox/.qcc/config.json`
