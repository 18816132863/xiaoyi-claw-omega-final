# HEXAGONAL_ARCHITECTURE.md - 六边形架构系统

## 目的
实现六边形架构(端口适配器架构)的智能设计。

## 架构组件

### 核心 (Core)
- 领域模型
- 业务服务
- 端口定义

### 端口 (Ports)
- **驱动端口(入站)** - API, CLI, Web
- **被驱动端口(出站)** - Database, Messaging, External

### 适配器 (Adapters)
- **驱动适配器** - REST控制器, CLI处理器
- **被驱动适配器** - JPA仓储, Kafka生产者

## 核心优势

| 优势 | 说明 |
|------|------|
| 依赖方向 | 外部依赖核心 |
| 可测试性 | 核心独立测试 |
| 可替换性 | 适配器可替换 |
| 技术无关 | 核心不依赖技术 |

## 使用示例

```bash
# 创建六边形架构项目
openclaw hexagonal create --name "myapp"

# 添加驱动端口
openclaw hexagonal port --type driving --name "UserApi"

# 添加被驱动端口
openclaw hexagonal port --type driven --name "UserRepository"

# 添加适配器
openclaw hexagonal adapter --port "UserApi" --type "RestController"
```

---
*V16.0 六边形架构系统*
