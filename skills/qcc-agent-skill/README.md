# QCC Agent Skill - 企查查智能体数据平台

> OpenClaw 技能包：企业信息查询 CLI 工具，提供 65 项工具，覆盖企业工商、风险、知识产权、经营信息。

## 📦 安装

### 1. 安装 CLI 工具

```bash
npm install -g qcc-agent-cli
```

### 2. 初始化配置

```bash
# 需要先在 http://agent.qcc.com/ 注册获取 API Key
qcc init --authorization "Bearer YOUR_API_KEY"
```

### 3. 安装技能到 OpenClaw

将此技能目录复制到 OpenClaw 的 skills 目录：

```bash
cp -r qcc-agent-skill ~/.openclaw/workspace/skills/qcc-agent
```

## 🛠️ 工具统计

| Server | 工具数量 | 说明 |
|:---:|:---:|---|
| company | 12 | 企业基础信息（工商、股东、人员等） |
| risk | 34 | 企业风险信息（司法、失信、被执行等） |
| ipr | 6 | 企业知识产权（商标、专利、著作权等） |
| operation | 13 | 企业经营信息（招投标、融资、舆情等） |
| **总计** | **65** | |

## 📖 使用示例

```bash
# 查询企业工商信息
qcc company get_company_registration_info "企查查科技股份有限公司"

# 查询企业股东信息
qcc company get_shareholder_info "企查查科技股份有限公司"

# 查询企业失信信息
qcc risk get_dishonest_info "企查查科技股份有限公司"

# 查询企业专利信息
qcc ipr get_patent_info "企查查科技股份有限公司"

# 查询企业招投标信息
qcc operation get_bidding_info "企查查科技股份有限公司"
```

## 🔧 MCP Server 配置

可配置为 OpenClaw 的 MCP Server：

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

## 📋 文件说明

- `SKILL.md` - 技能定义文件（OpenClaw 自动加载）
- `TEST_REPORT.md` - 完整测试报告（65 项工具 100% 通过）
- `README.md` - 本说明文件

## ⚠️ 注意事项

1. 需要在 http://agent.qcc.com/ 注册账号获取 API Key
2. API 调用需要消耗额度
3. CLI 工具路径：`/home/sandbox/openclaw/lib/node_modules/qcc-agent-cli/bin/index.js`
4. 可使用 `node <path>/bin/index.js` 执行命令

## 📄 License

MIT

## 🔗 相关链接

- [企查查智能体平台](http://agent.qcc.com/)
- [OpenClaw 官网](https://openclaw.ai)
- [ClawdHub 技能市场](https://clawhub.com)
