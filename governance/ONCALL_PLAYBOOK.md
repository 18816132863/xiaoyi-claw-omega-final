# 值守手册 V1.0

## 一、值守职责

1. 监控告警通知
2. 及时确认和处理
3. 记录处理过程
4. 必要时升级

## 二、值守工具

### 2.1 查看当前状态

```bash
# 查看告警
python scripts/generate_alerts.py

# 查看看板
python scripts/build_ops_dashboard.py

# 查看 incidents
python scripts/incident_cli.py list
```

### 2.2 处理 incident

```bash
# 确认
python scripts/incident_cli.py acknowledge INC-xxx your_name

# 添加备注
python scripts/incident_cli.py annotate INC-xxx "正在排查"

# 关闭
python scripts/incident_cli.py resolve INC-xxx "已修复"
```

## 三、值守检查清单

### 3.1 每日检查

- [ ] 查看夜间巡检结果
- [ ] 检查 open incidents
- [ ] 确认告警已处理

### 3.2 每周检查

- [ ] 审查告警趋势
- [ ] 清理已关闭 incidents
- [ ] 更新运维文档

## 四、应急响应

### 4.1 P0 阻塞

1. 立即确认 incident
2. 10分钟内定位问题
3. 30分钟内修复或升级

### 4.2 发布阻塞

1. 立即确认 incident
2. 评估是否需要回滚
3. 修复后重新验证

## 五、升级流程

```
发现问题 → 确认 incident → 尝试修复
    ↓
30分钟未解决 → 升级到二级
    ↓
60分钟未解决 → 升级到三级
    ↓
创建紧急 incident
```

## 六、联系方式

| 级别 | 负责人 | 联系方式 |
|------|--------|----------|
| 一级 | [待填写] | [待填写] |
| 二级 | [待填写] | [待填写] |
| 三级 | [待填写] | [待填写] |

---

**版本**: V1.0  
**更新时间**: 2026-04-12
