# Cloudflare Pages 部署指南

## 项目结构

```
prototype/
├── index.html          # 原型页面
└── (其他静态资源)
```

## 部署方式

### 方式1：Wrangler CLI（推荐）

```bash
# 安装 Wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 部署到 Cloudflare Pages
cd prototype
wrangler pages deploy . --project-name=your-project-name
```

### 方式2：Cloudflare Dashboard

1. 访问 https://dash.cloudflare.com
2. 进入 **Workers & Pages** → **Create**
3. 选择 **Pages** → **Upload assets**
4. 拖入 `prototype` 文件夹
5. 设置项目名称，点击部署

### 方式3：连接 Git 仓库

1. 访问 https://dash.cloudflare.com
2. 进入 **Workers & Pages** → **Create**
3. 选择 **Pages** → **Connect to Git**
4. 选择 GitHub 仓库
5. 构建设置：
   - **Build command**: 留空（静态站点）
   - **Build output directory**: `/` 或 `public`
6. 点击 **Save and Deploy**

## 环境变量（可选）

如需配置环境变量：

1. 进入项目设置 → **Environment variables**
2. 添加变量（如 `API_URL`）
3. 重新部署生效

## 自定义域名（可选）

1. 进入项目设置 → **Custom domains**
2. 点击 **Set up a custom domain**
3. 输入你的域名
4. 按提示配置 DNS 记录

## 常见问题

### 1. 404 错误
确保 `index.html` 在根目录

### 2. 路由问题
添加 `_redirects` 文件：
```
/*    /index.html   200
```

### 3. 缓存问题
Cloudflare 自动处理缓存，无需额外配置

## 优势

- ✅ **国内可访问** - 无需科学上网
- ✅ **免费额度充足** - 每月 500 次构建
- ✅ **自动 HTTPS** - 免费 SSL 证书
- ✅ **全球 CDN** - 访问速度快
- ✅ **无需备案** - pages.dev 域名

## 示例地址

部署后会获得类似地址：
```
https://your-project.pages.dev
https://abc12345.your-project.pages.dev
```
