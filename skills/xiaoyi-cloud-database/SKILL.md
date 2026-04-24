---
name: xiaoyi-cloud-database
description: 给网页应用接入云数据库的额外能力。端到端流程：云数据库服务后端应用创建 → 数据库设计 → 前端对接。当用户明确提到需要支持多用户共用数据库实例或者需要部署网站（且不需要端侧能力）时，你可以利用本 skill，如果网页应用需要支持端侧能力（比如相机、端侧数据库等），那就一定不能使用本 skill。如果用户既要多用户共用数据库实例、网站部署，又要支持端侧能力，本 skill 不支持，并告知用户无法支持该请求
---

## 一、目标

端到端流程：从用户需求到可访问的前后端应用，其中后端不需要编写代码，完全基于 AiPexBase BaaS 实现。

**注**：本 skill 适用于小艺 claw。因此，本 skill 中一些步骤不直接访问或调用 AipexBase BaaS 后端服务。相关步骤会调用小艺云侧接口，经由此将参数透传给 AipexBase BaaS 后端服务。

**端到端流程**：获取小艺云侧服务的相关环境变量 → 数据库表设计及 AipexBase 后端应用和数据表创建 → 前端对接 → 【必需】部署上线。除部署上线需要用到 `xiaoyi-web-deploy` skill 外，无需其他技能支持。

## ⚠️ 矛盾识别与用户决策

在开始创建应用之前，**必须先分析用户需求是否涉及端侧/云侧矛盾**。如果检测到以下矛盾，**暂停并让用户决策**，不得自行选择方案：

### 矛盾检测规则

| 用户需求特征 | 端侧能力 | 云侧能力 | 是否矛盾 |
|-------------|---------|---------|---------|
| 需要拍照/相机 | ✅ HarmonyBridge.camera | ❌ 无法调用 | — |
| 需要多用户共用数据库实例/多人查看 | ❌ 端侧SQLite仅本地 | ✅ 云数据库天然共享 | — |
| **同时需要拍照 + 多用户共用数据库实例** | ✅ 拍照 ✅ | ❌ 拍照 ❌ | **⚠️ 矛盾** |
| 需要端侧AI识图/抠图/图生图 | ✅ HarmonyBridge.ai | ❌ 无法调用 | — |
| **同时需要端侧AI + 多用户共用数据库实例** | ✅ AI ✅ | ❌ AI ❌ | **⚠️ 矛盾** |

### 矛盾处理流程

当检测到矛盾时，按以下流程处理：

1. **暂停创建**，不执行任何后端应用创建、表设计或代码编写
2. **向用户明确说明矛盾**，格式如下：

```
⚠️ 检测到需求冲突

您的需求同时涉及：
- 端侧能力：[具体能力，如"拍照打卡"]
- 云侧能力：[具体能力，如"管理员查看所有数据"]

当前这两个能力无法在同一个应用中同时实现：
- 端侧应用（运行在手机WebView）：支持拍照，但数据仅存本地，无法共享
- 云侧应用（运行在浏览器）：支持多用户共用数据库实例，但无法调用手机相机

请选择您优先的方案：
A. 端侧优先：生成端侧HTML文件，支持拍照，数据存本地（管理员无法远程查看）
B. 云侧优先：生成云侧网页，支持多用户共用数据库实例（拍照降级为文件上传）
C. 混合方案：生成两个页面——端侧页面负责拍照+本地存储，云侧管理页面负责数据查看（需要额外开发）
```

3. **等待用户选择后**，再按用户决策执行对应方案
4. 用户选择方案 C 时，端侧页面使用 `Photo-Recognition-Tool` skill 生成，云侧管理页面使用本 skill 生成

---

## 二、开发原则

### 2.1 自动化原则

**新建应用** 和 **迭代开发** 全程自动执行，无需向用户确认。

- **新建应用**：获取小艺云侧服务的相关环境变量 → 建 BaaS 应用和表 → 编写前端代码
- **迭代开发**：直接修改前端代码或表结构，复用已有的 `baas-config.json`

**仅部署上线，需要用户确认后再执行。** 当用户确认后，部署方法再去参看 `xiaoyi-web-deploy` skill。

### 2.2 数据隔离原则

**每个项目必须创建独立的 BaaS 应用**，通过不同的 `apiKey` 实现数据隔离。

每个项目目录下有一个 `baas-config.json`，包含该项目专属的连接信息，所有 CLI 和 SDK 操作统一使用这一个配置文件。

### 2.3 开发步骤概览

0. **小艺云侧环境变量获取**：由于向 AipexBase BaaS 服务的请求会经由小艺云侧服务透传，因此需要先获取小艺云侧环境变量
1. **后端准备**：如果前端需要用到 aipexbase 能力（数据库、AI、文件等），先创建应用和表
2. **前端页面开发**：生成前端代码（HTML/Vue/React 等），集成 aipexbase-js SDK
3. **构建发布**：询问用户后部署。部署方法再去参看 `xiaoyi-web-deploy` skill。

---

## 三、项目初始化

### 3.1 配置文件说明

| 配置文件 | 位置 | 说明 |
|---------|------|------|
| **全局配置** `config.json` | 本 skill(`xiaoyi-cloud-database/`) 目录下 | 包含 `baseUrl` 可以用该文件中的默认 `baseUrl` |
| **项目配置** `baas-config.json` | 项目目录下 | 新建应用时从全局配置复制，批量创建后添加 `apiKey` 和 `appId`；迭代开发时直接使用 |

### 3.2 判断逻辑

检查项目目录下的 `baas-config.json`：

- **不存在或缺少 `apiKey`** → 新建应用
- **存在且包含 `apiKey`** → 迭代开发

**注意**：需要检查的是 `apiKey`, 不是 `xiaoyiApiKey`。

### 3.3 初始化步骤

**步骤 1：检查并初始化全局配置**

读取 `<skill目录>/config.json`，检查 `baseUrl` 是否已配置。这个 baseUrl 指的是 AipexBase BaaS 服务的 `baseUrl`。

**步骤 2：项目配置**

```bash
cd <项目目录，建议放到 /tmp/时间戳/项目名称 目录下>
cp <当前skill目录>/config.json ./baas-config.json
```

**步骤 3：获取小艺云侧服务的相关环境变量**

运行 `<skill目录>/scripts/read_xiaoyienv.py` python 文件。成功运行后会输出一个 json 格式字符串，其中包含四个字段：`xiaoyiBaseUrl`, `xiaoyiUserId`, `xiaoyiApiKey`, `xiaoyiTraceId`。 注意区分 `xiaoyiBaseUrl` 和 `baseUrl`。

**步骤 4：增加项目配置**

在项目目录下的 `baas-config.json` 中增加上一步中获得的各字段的值（`xiaoyiBaseUrl`, `xiaoyiUserId`, `xiaoyiApiKey`, `xiaoyiTraceId`）。用 Edit 工具添加。

**步骤 5：获取 payload**

之后的步骤中，在调用小艺云侧 API 时，需要频繁使用下面的 payload

```json
{
  "actions": [
    {
      "actionExecutorTask": {
          "actionName": "baasApi",
          "content": <content>,
          "pluginId": "abf9388fed6b4df89daac71be85fc62c",
          "replyCard": false
      },
      "actionSn": "81ef5ac1b5e74e85b90832503ea34a07"
    }
  ],
  "endpoint": {
      "countryCode": "",
      "device": {
          "deviceId": "5682d99dbb90973b775b7e9bf774ff9f",
          "phoneType": "2in1",
          "prdVer": "11.6.2.202"
      }
  },
  "session": {
      "interactionId": "0",
      "isNew": false,
      "sessionId": "xxx"
  },
  "utterance": {
      "original": "",
      "type": "text"
  },
  "version": "1.0"
}
```
其中，`<content>` 是一个 placeholder，会根据不同场景填入不同内容。其余字段均写死。

---

## 四、新建应用流程

### 4.1 生成 app-schema.json

根据用户需求，在项目目录下创建 `app-schema.json`：

```json
{
  "name": "应用名称",
  "needAuth": true,
  "authTable": "tableName",
  "rlsPolicies": ["policy1", "policy2"],
  "tables": [
    {
      "tableName": "表名",
      "description": "表说明",
      "columns": [
        {
          "columnName": "id",
          "columnType": "INT",
          "columnComment": "主键ID（必需）",
          "isNullable": true,
          "isPrimary": true,
          "isShow": true
        },
        {
          "columnName": "user_name",
          "columnType": "VARCHAR(255)",
          "columnComment": "用户名",
          "isNullable": true,
          "isPrimary": false,
          "isShow": true
        },
        {
          "columnName": "字段名",
          "columnType": "字段类型",
          "columnComment": "字段说明",
          "isNullable": true,
          "isPrimary": false,
          "isShow": true
        }
      ]
    }
  ]
}
```

**字段说明**：

- `needAuth`：是否需要用户认证（true/false）。**以下场景必须将 `needAuth` 设置为 `false`**，禁止默认设为 true：
  - 需求中没有登录、注册、用户认证等功能
  - 简化了注册流程（如无需真正注册即可使用）
  - 实际未调用注册、登录 API（即使需求提及用户概念，但未使用 auth 相关接口）
- `authTable`：认证使用的表名
- `rlsPolicies`：行级安全策略列表，如果有就设计，没有就不用设计
- `isNullable`：**true=必填，false=非必填**（注意：字段名虽叫 isNullable，但在本系统中语义为 true 代表必填、false 代表非必填，请严格按此理解）
- `columnType`：如果为 `VARCHAR` 必须指定长度，比如 `VARCHAR(255)`
- **DATETIME 字段规则（强制）**：所有 `columnType` 为 `DATETIME` 或 `datetime` 的字段，`isNullable` 必须设置为 `false`（非必填）。**严禁将任何 datetime 字段的 isNullable 设为 true（必填）**，无论该字段名称是什么（包括但不限于 created_at、updated_at、start_time、end_time、publish_time 等）。datetime 字段在前端表单中不显示红色星号、不添加 required 属性


### 4.2 字段类型参考

| 类型 | 说明 | 使用场景 | 示例 |
|------|------|---------|------|
| `varchar` | 短文本（≤255字符） | 姓名、标题、用户名 | "张三" |
| `fullText` | 长文本 | json长串，超过512字符长度 | "这是超长内容..." |
| `number` | 整数 | 年龄、数量、评分 | 25 |
| `decimal` | 小数 | 价格、金额、评分 | 99.99 |
| `boolean` | 布尔值 | 是否启用、是否公开 | true / false |
| `date` | 日期 | 生日、发布日期 | "2024-01-01" |
| `datetime` | 日期时间（通常非必填，会自动赋值） | 创建时间、更新时间 | "2024-01-01 12:00:00" |
| `password` | 密码（自动加密） | 用户密码 | "******" |
| `phone` | 手机号（自动验证） | 联系电话 | "13800138000" |
| `email` | 邮箱（自动验证） | 电子邮件 | "user@example.com" |
| `images` | 图片 | 头像、封面图 | ["url1", "url2"] |
| `files` | 文件 | 附件、文档 | ["url1"] |
| `videos` | 视频 | 视频内容 | ["url1"] |
| `quote` | 关联对象 | 外键关联 | "rec_xxx" |

### 4.3 字段定义格式

```json
{
  "columnName": "字段名",
  "columnType": "字段类型",
  "columnComment": "字段说明",
  "isNullable": true,
  "isPrimary": false,
  "isShow": true,
  "referenceTableName": "关联表名",
  "showName": "关联表显示字段"
}
```

#### 字段属性说明

- **columnName**：字段名称，只能包含字母、数字和下划线
- **columnType**：字段类型（见上表）
- **columnComment**：字段描述/注释
- **isNullable**：**true=必填，false=非必填**（字段名虽叫 isNullable，但语义为 true 代表必填、false 代表非必填）
- **isPrimary**：是否为主键（通常为 false）
- **isShow**：是否在列表中显示（true=显示，false=隐藏）
- **referenceTableName**：关联表名（仅当 columnType 为 "quote" 时需要）
- **showName**：关联表显示字段（仅当 columnType 为 "quote" 时需要）

#### 特殊字段类型说明

- `columnType` 如果为 `VARCHAR`，必须写明字符长度，比如：`VARCHAR(255)`

- **关联字段（quote 类型）**：用于建立表之间的关系，必须指定 `referenceTableName`。
  - 关联字段名通常以 `_id` 结尾
  - `referenceTableName` 必须是已存在的表名
  - 关联查询会自动处理外键关系

### 4.4 强制规则（必须遵守）

- 在 `app-schema.json` 中，任何 `columnType` 都**禁止**写成裸 `VARCHAR`
- 只能写成带长度的格式：`VARCHAR(n)`，例如 `VARCHAR(50)`、`VARCHAR(255)`、`VARCHAR(1024)`
- 发现 `columnType: "VARCHAR"` 时，必须立即改成带长度格式后再执行 `batch-create`
- 推荐默认长度：通用文本字段使用 `VARCHAR(255)`，短标识可用 `VARCHAR(50)`，URL 可用 `VARCHAR(1024)`
- 长文本类型选择：字段预期内容超过 512 字符时，优先使用 `FULLTEXT`，不使用 `TEXT`
- `TEXT` 仅用于不超过 512 字符的中短文本场景

### 4.5 表设计注意

- **必须设计主键**：每个表必须有且仅有一个主键字段
  - 字段名建议使用 `id`
  - 类型必须为 `INT`
  - `isPrimary` 必须设置为 `true`

### 4.6 表设计检查清单（必读）

在生成 `app-schema.json` 或创建表之前，确认：

- [ ] 每个表都包含主键字段（INT 类型，isPrimary: true）
- [ ] 字段类型符合规范（参考"字段类型说明"部分）
- [ ] 所有字符串字段的 `columnType` 均为 `VARCHAR(n)`，不存在裸 `VARCHAR`
- [ ] 长文本字段（超过 512 字符）已使用 `FULLTEXT`，未误用 `TEXT`
- [ ] 所有 DATETIME/datetime 字段的 `isNullable` 均为 `false`（非必填），无一例外
- [ ] 认证表设计正确（如需要用户认证）

### 4.7 批量创建 BaaS 应用和表

创建 `app-schema.json` 之后，就可以进行表创建。首先你需要从之前的 `baas-config.json` 中读取 `xiaoyiBaseUrl`, `xiaoyiUserId`, `xiaoyiApiKey`, `xiaoyiTraceId`。

然后，你要读取整个 `app-schema.json`，并把这一部分内容嵌入上述的 payload 中。以下是一个例子

```bash
cd <项目目录>

curl -X POST '<xiaoyiBaseUrl>/celia-claw/v1/rest-api/skill/execute' \
  -H 'Content-Type: application/json' \
  -H 'x-api-type: manageApplicationBatch' \
  -H 'x-skill-id: cloud_database' \
  -H 'x-request-from: openclaw' \
  -H 'x-hag-trace-id: <xiaoyiTraceId>' \
  -H 'x-uid: <xiaoyiUserId>' \
  -H 'x-api-key: <xiaoyiApiKey>' \
  -d '{
  "actions": [
    {
      "actionExecutorTask": {
          "actionName": "baasApi",
          "content": {
              "name": "应用名称",
              "needAuth": true,
              "authTable": "tableName",
              "rlsPolicies": ["policy1", "policy2"],
              "tables": [
                {
                  "tableName": "表名",
                  "description": "表说明",
                  "columns": [
                    {
                      "columnName": "id",
                      "columnType": "INT",
                      "columnComment": "主键ID（必需）",
                      "isNullable": true,
                      "isPrimary": true,
                      "isShow": true
                    },
                    {
                      "columnName": "user_name",
                      "columnType": "VARCHAR(255)",
                      "columnComment": "用户名",
                      "isNullable": true,
                      "isPrimary": false,
                      "isShow": true
                    },
                    {
                      "columnName": "字段名",
                      "columnType": "字段类型",
                      "columnComment": "字段说明",
                      "isNullable": true,
                      "isPrimary": false,
                      "isShow": true
                    }
                  ]
                }
              ]
            },
          "pluginId": "abf9388fed6b4df89daac71be85fc62c",
          "replyCard": false
      },
      "actionSn": "81ef5ac1b5e74e85b90832503ea34a07"
    }
  ],
  "endpoint": {
      "countryCode": "",
      "device": {
          "deviceId": "5682d99dbb90973b775b7e9bf774ff9f",
          "phoneType": "2in1",
          "prdVer": "11.6.2.202"
      }
  },
  "session": {
      "interactionId": "0",
      "isNew": false,
      "sessionId": "xxx"
  },
  "utterance": {
      "original": "",
      "type": "text"
  },
  "version": "1.0"
}'
```

### 4.8 更新 baas-config.json

批量创建成功后，使用 Edit 工具添加返回的 `apiKey` 和 `appId`。注意区分这里的 `apiKey` 和之前从小艺云侧服务获取的 `xiaoyiApiKey`。

---

## 五、迭代开发流程

### 5.1 新增表

如果需要在已有应用中新增表：

```bash
curl -X POST '<xiaoyiBaseUrl>/celia-claw/v1/rest-api/skill/execute' \
  -H 'Content-Type: application/json' \
  -H 'x-api-type: manageTable' \
  -H 'x-skill-id: cloud_database' \
  -H 'x-request-from: openclaw' \
  -H 'x-hag-trace-id: <xiaoyiTraceId>' \
  -H 'x-uid: <xiaoyiUserId>' \
  -H 'x-api-key: <xiaoyiApiKey>' \
  -d '{
  "actions": [
    {
      "actionExecutorTask": {
          "actionName": "baasApi",
          "content": {
            "appId": "<appId>",
            "tableName": "表名",
            "description": "表说明",
            "columns": [
              {
                "columnName": "id",
                "columnType": "INT",
                "columnComment": "主键ID（必需）",
                "isNullable": true,
                "isPrimary": true,
                "isShow": true
              },
              {
                "columnName": "name",
                "columnType": "VARCHAR(255)",
                "columnComment": "名称",
                "isNullable": true,
                "isPrimary": false,
                "isShow": true
              },
              {
                "columnName": "字段名",
                "columnType": "字段类型",
                "columnComment": "字段说明",
                "isNullable": true,
                "isPrimary": false,
                "isShow": true
              }
            ]
          },
          "pluginId": "abf9388fed6b4df89daac71be85fc62c",
          "replyCard": false
      },
      "actionSn": "81ef5ac1b5e74e85b90832503ea34a07"
    }
  ],
  "endpoint": {
      "countryCode": "",
      "device": {
          "deviceId": "5682d99dbb90973b775b7e9bf774ff9f",
          "phoneType": "2in1",
          "prdVer": "11.6.2.202"
      }
  },
  "session": {
      "interactionId": "0",
      "isNew": false,
      "sessionId": "xxx"
  },
  "utterance": {
      "original": "",
      "type": "text"
  },
  "version": "1.0"
}'
```

**注意**：
- `xiaoyiBaseUrl`, `xiaoyiUserId`, `xiaoyiApiKey`, `xiaoyiTraceId` 从 `baas-config.json` 中读取
- columns 是 JSON 数组格式
- 字段类型参考"字段类型说明"部分
- 字段 `columnType` 如果为 `VARCHAR` 必须指定长度，比如 `VARCHAR(255)`，严禁使用裸 `VARCHAR`

### 5.2 插入表数据

使用项目级配置：

> 导入数据的时候，如果主键已经设置 int 类型，并且为 isPrimary，那么 id 的值会从 1 开始逐渐自增。
> 必须使用 baas 进行数据插入，不要使用其他脚本等操作。

假设插入数据的请求体为

```bash
{
  "table": <table_name>,
  "method": "add",
  "apiKey": <apiKey>,
  "tableData": {
    "name": "张三",
    "age": 18,
    "email": "zhangsan@example.com"
}
```

那么插入数据的命令为

```bash
curl -X POST '<xiaoyiBaseUrl>/celia-claw/v1/rest-api/skill/execute' \
  -H 'Content-Type: application/json' \
  -H 'x-api-type: tableAddData' \
  -H 'x-skill-id: cloud_database' \
  -H 'x-request-from: openclaw' \
  -H 'x-hag-trace-id: <xiaoyiTraceId>' \
  -H 'x-uid: <xiaoyiUserId>' \
  -H 'x-api-key: <xiaoyiApiKey>' \
  -d '{
    "actions": [
        {
            "actionExecutorTask": {
                "actionName": "baasApi",
                "content": {
                  "table": <table_name>,
                  "method": "add",
                  "apiKey": <apiKey>,
                  "tableData": {
                    "name": "张三",
                    "age": 18,
                    "email": "zhangsan@example.com"
                },
                "pluginId": "abf9388fed6b4df89daac71be85fc62c",
                "replyCard": false
            },
            "actionSn": "81ef5ac1b5e74e85b90832503ea34a07"
        }
    ],
    "endpoint": {
        "countryCode": "",
        "device": {
            "deviceId": "5682d99dbb90973b775b7e9bf774ff9f",
            "phoneType": "2in1",
            "prdVer": "11.6.2.202"
        }
    },
    "session": {
        "interactionId": "0",
        "isNew": false,
        "sessionId": "xxx"
    },
    "utterance": {
        "original": "",
        "type": "text"
    },
    "version": "1.0"
}'
```

查询数据用以下命令
```bash
curl -X POST '<xiaoyiBaseUrl>/celia-claw/v1/rest-api/skill/execute' \
  -H 'Content-Type: application/json' \
  -H 'x-api-type: tableQueryData' \
  -H 'x-skill-id: cloud_database' \
  -H 'x-request-from: openclaw' \
  -H 'x-hag-trace-id: <xiaoyiTraceId>' \
  -H 'x-uid: <xiaoyiUserId>' \
  -H 'x-api-key: <xiaoyiApiKey>' \
  -d '{
    "actions": [
      {
        "actionExecutorTask": {
            "actionName": "baasApi",
            "content": {
                "table": <table_name>,
                "method": "list",
                "apiKey": <apiKey>
              },
            "pluginId": "abf9388fed6b4df89daac71be85fc62c",
            "replyCard": false
        },
        "actionSn": "81ef5ac1b5e74e85b90832503ea34a07"
      }
    ],
    "endpoint": {
        "countryCode": "",
        "device": {
            "deviceId": "5682d99dbb90973b775b7e9bf774ff9f",
            "phoneType": "2in1",
            "prdVer": "11.6.2.202"
        }
    },
    "session": {
        "interactionId": "0",
        "isNew": false,
        "sessionId": "xxx"
    },
    "utterance": {
        "original": "",
        "type": "text"
    },
    "version": "1.0"
}'
```
`xiaoyiBaseUrl`, `xiaoyiUserId`, `xiaoyiApiKey`, `xiaoyiTraceId`, `apiKey` 需要从 `baas-config.json` 中获取。注意区分 `xiaoyiApiKey` 和 `apiKey`。`table_name` 即为你想要插入数据或查询的表格名。

---

## 六、开发步骤

1. 引入 aipexbase-js SDK（CDN 或 npm）
2. 从 `baas-config.json` 读取 baseUrl 和 apiKey（注意不是 xiaoyiBaseUrl 和 xiaoyiApiKey），使用 `aipexbase.createClient()` 初始化客户端

### 6.1 任务模板

开发 {page_name}.html 页面

## 前置读取（必须）
编写代码前，必须先用 Read 工具读取以下文件的完整内容：
1. {skill_dir}/references/html-template.html — 学习页面结构和 SDK 初始化模板，可以把这个当成一个例子。
2. {skill_dir}/references/aipexbase-js-api.md — 所有 API 操作的唯一正确用法

也需要确定你是否还记得下面内容：
1. 数据库数据表结构和字段定义（若忘记，可从 `{project_dir}/app-schema.json` 获取）
2. API 配置（baseUrl、apiKey）（若忘记，可从 `{project_dir}/baas-config.json` 获取）

## 开发约束
- 必填字段（isNullable: true）在 label 旁标注红色星号 *
- 图片/文件类型字段必须提供上传组件，禁止纯文本输入框
- 表单字段必须与 app-schema.json 中的定义一一对应
- 登录成功后必须调用 getUser() 获取完整用户信息
- 禁止使用 client.from()，必须使用 client.db.from()
- 当调用数据表增删改查 API 时，涉及到日期或者时间，必须都为合法日期、合法时间，包括在 `.leq`、`.geq` 等条件判断中。如不允许出现 `2026-4-31` 这种不存在的日期

## 认证流程规范（如涉及登录功能）

### 登录流程
1. 步骤一：提交表单
2. 步骤二：`auth.login()`。保存 token 到 localStorage
3. 步骤三：`getUser()`。获取完整用户信息用于页面展示
4. 步骤四：跳转主页面

### 页面加载流程（已登录检测）
1. 步骤一：页面加载
2. 步骤二：检查 token。没有 token 或 token 无效，则显示登录表单，要求用户输入账号密码进行登录；若为 `true`，继续执行步骤三
3. 步骤三：`getUser()`
4. 步骤四：跳转主页面

### 认证禁止事项
- 禁止：直接使用 login() 返回值展示用户信息
- 必须：登录后调用 getUser() 获取完整信息
- 禁止：登录页面重复登录（已登录则跳转）
- 必须：登录和自动登录共用同一进入主页面逻辑

## 完成标准
- [ ] 表单字段与 app-schema.json 一一对应
- [ ] 必填字段有红色星号和 required 属性
- [ ] 图片字段有上传组件
- [ ] 页面可独立运行，无 JS 错误
- [ ] 页面跳转逻辑正确
```

### 6.2 前置读取清单（快速参考）

| 文件 | 作用 |
|------|------|
| `references/html-template.html` | 页面结构和 SDK 初始化模板 |
| `references/aipexbase-js-api.md` | API 调用方式、方法链顺序、参数格式 |
| `app-schema.json` | 表结构定义 |
| `baas-config.json` | API 配置（baseUrl、apiKey） |