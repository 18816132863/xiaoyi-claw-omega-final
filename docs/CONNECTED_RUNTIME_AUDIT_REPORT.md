# CONNECTED RUNTIME AUDIT REPORT

Generated: 2026-04-25T10:51:55.715010

## Summary

- Total Records: 50
- Allowed: 26
- Blocked: 24
- Probe Only: 10

## Recent Records

| Audit ID | Route | Risk | Mode | Status |
|----------|-------|------|------|--------|
| audit_4f1afac1a53c... | route.xiaoyi_gui_agent | L4 | connected_runtime | blocked |
| audit_a5732fd2bee6... | route.bootstrap | L4 | connected_runtime | blocked |
| audit_f5b35cb4b0db... | route.query_note | L0 | connected_runtime | allowed |
| audit_9ba8332e2b2e... | route.search_notes | L0 | connected_runtime | allowed |
| audit_a1946ecee54f... | route.query_alarm | L0 | connected_runtime | allowed |
| audit_ea8f4e60ccb6... | route.get_location | L0 | connected_runtime | allowed |
| audit_a17ebeade276... | route.send_message | L3 | connected_runtime | blocked |
| audit_4a9bbbe6164d... | route.delete_note | L3 | connected_runtime | blocked |
| audit_f901d3eea459... | route.xiaoyi_gui_agent | L4 | connected_runtime | blocked |
| audit_ed1b52a88320... | route.bootstrap | L4 | connected_runtime | blocked |
| audit_0cce7c563b81... | route.query_note | L0 | connected_runtime | allowed |
| audit_cf90bfa8f754... | route.search_notes | L0 | connected_runtime | allowed |
| audit_d6af17d6310f... | route.query_alarm | L0 | connected_runtime | allowed |
| audit_444b50490330... | route.get_location | L0 | connected_runtime | allowed |
| audit_d9c80d188b24... | route.send_message | L3 | connected_runtime | blocked |
| audit_d90c133b842b... | route.delete_note | L3 | connected_runtime | blocked |
| audit_db1bc26aa3e5... | route.xiaoyi_gui_agent | L4 | connected_runtime | blocked |
| audit_b525ddaffb13... | route.bootstrap | L4 | connected_runtime | blocked |
| audit_b2688e25f1f9... | route.query_note | L0 | connected_runtime | allowed |
| audit_884874348654... | route.search_notes | L0 | connected_runtime | allowed |

## Audit Fields

Each audit record contains:
- `audit_id`: Unique identifier
- `timestamp`: Execution time
- `runtime_mode`: dry_run/fake_device/probe_only/connected_runtime
- `route_id`: Route identifier
- `device_adapter`: Adapter used
- `risk_level`: L0/L1/L2/L3/L4/BLOCKED
- `policy`: auto_execute/confirm_once/strong_confirm/blocked
- `confirmation_id`: Confirmation session ID (if required)
- `side_effecting`: Whether action has side effects
- `probe_only`: Whether in probe-only mode
- `dry_run`: Whether dry-run execution
- `actual_execution`: Whether real execution occurred
- `device_result_redacted`: Result (redacted)
- `screen_summary_redacted`: Screen summary (redacted)
- `fallback_used`: Whether fallback was triggered
- `recovery_action`: Recovery action taken
