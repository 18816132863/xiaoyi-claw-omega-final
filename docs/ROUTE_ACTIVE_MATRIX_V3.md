# ROUTE ACTIVE MATRIX V3

## 状态说明

| 状态 | 说明 |
|------|------|
| generated | 自动生成，结构合规 |
| verified | 通过静态检查、handler 可导入、schema 可验证 |
| active | 至少被真实执行过，并写入 audit |
| failed | 执行验证失败 |
| deprecated | 旧 route，不再使用 |

## 核心 Route 矩阵 (15条)

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
| route.xiaoyi_gui_agent | xiaoyi_gui_agent | L4 | strong_confirm | ⚠️ VERIFIED | ✅ | ✅ | - |
| route.bootstrap | bootstrap | L4 | strong_confirm | ⚠️ VERIFIED | ✅ | ✅ | - |

## 统计

- **Total Routes**: 54
- **Active**: 13 (核心 route L0-L3)
- **Verified**: 41 (含 2 条 L4)
- **Generated**: 0
- **Failed**: 0
- **Deprecated**: 0

## 风险分布

| Risk Level | Count | Percentage |
|------------|-------|------------|
| L0 | 18 | 33% |
| L1 | 6 | 11% |
| L2 | 12 | 22% |
| L3 | 16 | 30% |
| L4 | 2 | 4% |
| BLOCKED | 0 | 0% |

## L4 Route 说明 (2条)

L4 route 需要 strong_confirm，不能自动执行，只保持 verified 状态：

### route.xiaoyi_gui_agent
- **Capability**: xiaoyi_gui_agent
- **Risk Level**: L4
- **Policy**: strong_confirm
- **User Intents**: 手机操作, GUI操作, 小艺帮帮忙, 视觉操作, 操作手机, 自动操作手机, 打开手机操作, 小艺操作, 手机界面操作
- **Auto-execute**: ❌ BLOCKED
- **Status**: verified

### route.bootstrap
- **Capability**: bootstrap
- **Risk Level**: L4
- **Policy**: strong_confirm
- **User Intents**: 引导
- **Auto-execute**: ❌ BLOCKED
- **Status**: verified

## 统计口径说明

- **总路由数**: 54 (所有 route)
- **L4 数量**: 2 (xiaoyi_gui_agent + bootstrap)
- **Active 数量**: 13 (核心 route 中 L0-L3 的 active 数量)
- **Verified 数量**: 41 (其余 route + 2 条 L4)
- **L4 不计入 Active**: 因为 L4 需要 strong_confirm，不能自动执行
