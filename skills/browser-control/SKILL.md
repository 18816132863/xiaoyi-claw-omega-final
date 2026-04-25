# Browser Control Skill

浏览器自动化控制技能，支持启动浏览器、打开页面、截图、点击、输入等操作。

## Profile 说明

- `openclaw` - OpenClaw 管理的独立浏览器实例
- `chrome` - Chrome 扩展中继，接管用户已有的 Chrome 标签页（需点击工具栏按钮附加标签页）

## 基本操作

### 1. 启动浏览器

```python
browser(action="start", profile="openclaw")
```

### 2. 打开页面

```python
result = browser(action="open", profile="openclaw", targetUrl="https://example.com")
tid = result["targetId"]  # 保存 targetId 用于后续操作
```

### 3. 截图

```python
browser(action="screenshot", profile="openclaw", targetId=tid)
```

### 4. 获取页面结构（点击前必做）

```python
browser(action="snapshot", profile="openclaw", targetId=tid)
```

返回页面元素引用（如 `e12`），用于后续点击/输入操作。

### 5. 点击元素

```python
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "click", "ref": "e12"})
```

### 6. 输入文本

```python
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "type", "ref": "e5", "text": "你好"})
```

### 7. 按键

```python
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "press", "key": "Enter"})
```

### 8. 关闭标签页

```python
browser(action="close", profile="openclaw", targetId=tid)
```

## 完整示例：自动化登录

```python
# 1. 启动浏览器
browser(action="start", profile="openclaw")

# 2. 打开登录页面
result = browser(action="open", profile="openclaw", targetUrl="https://example.com/login")
tid = result["targetId"]

# 3. 获取页面结构
browser(action="snapshot", profile="openclaw", targetId=tid)

# 4. 输入用户名
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "type", "ref": "e5", "text": "myuser"})

# 5. 输入密码
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "type", "ref": "e8", "text": "mypass"})

# 6. 点击登录按钮
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "click", "ref": "e12"})

# 7. 截图确认
browser(action="screenshot", profile="openclaw", targetId=tid)
```

## 其他操作

### 导航

```python
browser(action="navigate", profile="openclaw", targetId=tid, url="https://another.com")
```

### 等待加载

```python
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "wait", "loadState": "networkidle"})
```

### 执行 JavaScript

```python
browser(action="act", profile="openclaw", targetId=tid, request={"kind": "evaluate", "fn": "document.title"})
```

### 全页面截图

```python
browser(action="screenshot", profile="openclaw", targetId=tid, fullPage=True)
```

## 注意事项

1. **点击前必须先 snapshot** - 获取元素引用
2. **保持 targetId 一致** - 同一标签页的操作使用相同的 targetId
3. **Chrome 扩展模式** - 需要用户点击工具栏按钮附加标签页
4. **refs 参数** - 默认使用 role-based 引用，可用 `refs="aria"` 获取更稳定的 aria 引用

## 操作类型 (kind)

| kind | 说明 | 必需参数 |
|------|------|----------|
| click | 点击元素 | ref |
| type | 输入文本 | ref, text |
| press | 按键 | key |
| hover | 悬停 | ref |
| fill | 填充表单 | fields |
| select | 下拉选择 | ref, values |
| wait | 等待 | loadState 或 timeMs |
| evaluate | 执行 JS | fn |
| close | 关闭标签页 | - |
