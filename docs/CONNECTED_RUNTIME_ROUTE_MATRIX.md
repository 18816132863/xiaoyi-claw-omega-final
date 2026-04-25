# CONNECTED RUNTIME ROUTE MATRIX

Generated: 2026-04-25T10:51:49.934875

## Safe Routes (L0/L1)

| Route ID | Risk Level | Policy | Execution Status | Side Effect Blocked |
|----------|------------|--------|------------------|--------------------|
| route.query_note | L0 | auto_execute | blocked | True |
| route.search_notes | L0 | auto_execute | blocked | True |
| route.list_recent_messages | L0 | auto_execute | blocked | True |
| route.query_message_status | L0 | auto_execute | blocked | True |
| route.query_alarm | L0 | auto_execute | blocked | True |
| route.query_contact | L0 | auto_execute | blocked | True |
| route.get_location | L0 | auto_execute | blocked | True |
| route.check_calendar_conflicts | L1 | auto_execute | blocked | True |
| route.query_note | L0 | auto_execute | allowed | False |
| route.search_notes | L0 | auto_execute | allowed | False |
| route.list_recent_messages | L0 | auto_execute | allowed | False |
| route.query_message_status | L0 | auto_execute | allowed | False |
| route.query_alarm | L0 | auto_execute | allowed | False |
| route.query_contact | L0 | auto_execute | allowed | False |
| route.get_location | L0 | auto_execute | allowed | False |
| route.check_calendar_conflicts | L1 | auto_execute | allowed | False |

## Confirmation Required Routes (L3/L4)

| Route ID | Risk Level | Policy | Requires Confirmation | Blocked Reason |
|----------|------------|--------|----------------------|----------------|
| route.send_message | L3 | confirm_once | True | L3 requires confirm_once |
| route.delete_note | L3 | confirm_once | True | L3 requires confirm_once |
| route.update_note | L2 | rate_limited | False | probe_only blocks all execution |
| route.delete_alarm | L3 | confirm_once | True | L3 requires confirm_once |
| route.make_call | L3 | confirm_once | True | L3 requires confirm_once |
| route.xiaoyi_gui_agent | L4 | strong_confirm | True | L4 requires strong_confirm |
| route.bootstrap | L4 | strong_confirm | True | L4 requires strong_confirm |

## Statistics

- Total Routes Tested: 23
- Allowed: 8
- Blocked: 15
