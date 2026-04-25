---
name: xiaoyi-web-deploy
description: 部署网页应用到云服务器中。当用户需要部署网页应用时，使用本 Skill。
---

## 部署上线

> ⚠️ **部署前必须询问用户确认**，得到明确同意后再执行打包和部署操作。
> ⚠️ **部署前必须在 AipexBase 创建一个 BaaS 应用**。如果之前没有创建过 AipexBase BaaS 应用，我们需要首先创建一个不含任何表格的 BaaS 应用；如果之前创建过，忽略这一条。

### 创建 BaaS 应用（不含任何表格）

⚠️ 如果之前没有创建过 AipexBase BaaS 应用，我们需要首先创建一个不含任何表格的 BaaS 应用；如果之前创建过，不需要重新创建。

#### 配置文件说明

| 配置文件 | 位置 | 说明 |
|---------|------|------|
| **全局配置** `config.json` | 本 skill(`xiaoyi-web-deploy/`) 目录下 | 包含 `baseUrl`，可以用该文件中的默认 `baseUrl` |
| **项目配置** `baas-config.json` | 项目目录下 | 新建应用时从全局配置复制，批量创建后添加 `apiKey` 和 `appId`；迭代开发时直接使用 |

检查项目目录下的 `baas-config.json`：

- **不存在或缺少 `apiKey`** → 新建应用
- **存在且包含 `apiKey`** → 迭代开发

**注意**：需要检查的是 `apiKey`, 不是 `xiaoyiApiKey`。

#### 初始化步骤

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

#### 新建应用流程

假如你只想创建一个空 BaaS 应用（不含任何表格），你可以使用下面的方法进行创建：

```bash
curl -X POST '<xiaoyiBaseUrl>/celia-claw/v1/rest-api/skill/execute' \
  -H 'Content-Type: application/json' \
  -H 'x-api-type: manageApplication' \
  -H 'x-skill-id: web_deploy' \
  -H 'x-request-from: openclaw' \
  -H 'x-hag-trace-id: <xiaoyiTraceId>' \
  -H 'x-uid: <xiaoyiUserId>' \
  -H 'x-api-key: <xiaoyiApiKey>' \
  -d '{
  "actions": [
    {
      "actionExecutorTask": {
          "actionName": "baasApi",
          "content": {"name": "应用名称"},
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

注：
- 需要从 `baas-config.json` 中读取 `xiaoyiBaseUrl`, `xiaoyiUserId`, `xiaoyiApiKey`, `xiaoyiTraceId`

#### 更新 baas-config.json

BaaS 应用创建成功后，使用 Edit 工具添加返回的 `apiKey` 和 `appId`。注意区分这里的 `apiKey` 和之前从小艺云侧服务获取的 `xiaoyiApiKey`。

### 打包策略

根据项目类型选择对应的打包方式：

**纯 HTML 项目（无构建步骤）**：

```bash
cd <项目目录>
zip -r project.zip . -x "node_modules/*" -x ".git/*" -x "*.zip"
```

**Vue/React 等需要构建的项目**：

```bash
cd <项目目录>
# 1. 执行构建
npm run build  # 或 yarn build

cd dist   # 或 cd build
zip -r ../project.zip .
```

### 将 zip 包上传至小艺文件存储服务

将上述的 zip 包上传小艺 OBS，上传成功后会返回一个 URL（命名为 `xiaoyiFileUrl`）。

### 执行部署

**cURL 示例**：

```bash
curl -X POST POST '<xiaoyiBaseUrl>/celia-claw/v1/rest-api/skill/execute' \
  -H 'Content-Type: application/json' \
  -H 'x-api-type: deploy' \
  -H 'x-skill-id: web_deploy' \
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
            "appUrl": <xiaoyiFileUrl>,
            "apiKey": <apiKey>,
            "appId": <appId>
          }
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

**注意**：此接口使用 `apiKey` 进行认证。`apiKey`、`appId`、`xiaoyiBaseUrl`、 `xiaoyiUserId`、 `xiaoyiApiKey`、 `xiaoyiTraceId` 需要从项目目录中的 `baas-config.json` 中获取。注意区分 `apiKey` 和 `xiaoyiApiKey`。

部署成功后返回：

```json
{
  "code": 0,
  "data": {
    "url": "<部署 URL>"
  },
  "message": "ok",
  "success": true
}
```

### 输出
部署后的 URL 展示给用户。**需要**把 URL 渲染成可以点击的形式，比如

```markdown
[链接文字](<部署 URL>)
```