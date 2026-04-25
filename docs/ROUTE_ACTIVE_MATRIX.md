# ROUTE ACTIVE MATRIX

## 状态说明

| 状态 | 说明 |
|------|------|
| generated | 自动生成，结构合规 |
| verified | 通过静态检查、handler 可导入、schema 可验证 |
| active | 至少被真实执行过，并写入 audit |
| failed | 执行验证失败 |
| deprecated | 旧 route，不再使用 |

## 核心 Route 矩阵

| Route ID | Capability | Risk | Policy | Status | Smoke | Audit | Fallback |
|----------|------------|------|--------|--------|-------|-------|----------|
| route.query_note | query_note | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.delete_note | delete_note | L3 | confirm_once | ✅ ACTIVE | ✅ | ✅ | ✅ |
| route.update_note | update_note | L3 | confirm_once | ✅ ACTIVE | ✅ | ✅ | - |
| route.search_notes | search_notes | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.send_message | send_message | L3 | confirm_once | ✅ ACTIVE | ✅ | ✅ | ✅ |
| route.query_message_status | query_message_status | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.list_recent_messages | list_recent_messages | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.create_alarm | create_alarm | L2 | rate_limited | ✅ ACTIVE | ✅ | ✅ | ✅ |
| route.query_alarm | query_alarm | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.delete_alarm | delete_alarm | L3 | confirm_once | ✅ ACTIVE | ✅ | ✅ | ✅ |
| route.make_call | make_call | L3 | confirm_once | ✅ ACTIVE | ✅ | ✅ | ✅ |
| route.query_contact | query_contact | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.get_location | get_location | L0 | auto_execute | ✅ ACTIVE | ✅ | ✅ | - |
| route.xiaoyi_gui_agent | xiaoyi_gui_agent | L4 | strong_confirm | ⚠️ VERIFIED | - | - | - |
| route.bootstrap | bootstrap | L4 | strong_confirm | ⚠️ VERIFIED | ✅ | ✅ | - |

## 统计

- **Total Routes**: 53
- **Verified**: 39 (73.6%)
- **Active**: 14 (26.4%)
- **Core Routes Verified**: 15/15 (100%)
- **Core Routes Active**: 14/15 (93.3%)

## 风险分布

| Risk Level | Count | Percentage |
|------------|-------|------------|
| L0 | 18 | 34% |
| L1 | 6 | 11% |
| L2 | 12 | 23% |
| L3 | 16 | 30% |
| L4 | 1 | 2% |
| BLOCKED | 0 | 0% |

## L4 Route 说明

L4 route 需要 strong_confirm，不能自动执行：
- `route.xiaoyi_gui_agent`: GUI 操作，高风险
- `route.bootstrap`: 系统引导，高风险

这两条 route 保持 verified 状态，只有在用户明确确认后才能执行。
