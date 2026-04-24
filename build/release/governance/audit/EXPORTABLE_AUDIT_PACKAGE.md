# EXPORTABLE_AUDIT_PACKAGE.md - 可导出的审计与证据包

## 目的
定义可导出的审计包和证据包的结构和规则，满足客户、审计、合规复核需求。

## 适用范围
平台所有审计包和证据包的导出场景。

## 与其他模块联动
| 模块 | 联动内容 |
|------|----------|
| evidence | 证据链管理 |
| audit | 审计记录 |
| reporting | 报表导出 |
| compliance | 合规检查 |

## 适用场景

### 导出场景
| 场景 | 说明 | 审批要求 |
|------|------|----------|
| 客户审计 | 客户要求审计数据 | 客户授权 |
| 合规复核 | 监管或合规检查 | 合规审批 |
| 内部审计 | 内部审计需要 | 审计部门审批 |
| 法律要求 | 法律程序要求 | 法务审批 |
| 用户请求 | 用户DSAR请求 | 身份验证 |

### 场景配置
```yaml
export_scenarios:
  customer_audit:
    description: "客户审计请求"
    allowed_content:
      - tenant_specific_data
      - operation_logs
      - compliance_records
    approval_required: true
    approver: "tenant_admin"
  
  compliance_review:
    description: "合规复核"
    allowed_content:
      - audit_logs
      - evidence_chains
      - compliance_records
    approval_required: true
    approver: "compliance_officer"
  
  internal_audit:
    description: "内部审计"
    allowed_content:
      - all_audit_data
      - system_logs
      - evidence_chains
    approval_required: true
    approver: "audit_department"
  
  legal_requirement:
    description: "法律要求"
    allowed_content:
      - as_required_by_law
    approval_required: true
    approver: "legal_department"
  
  user_dsar:
    description: "用户数据请求"
    allowed_content:
      - user_personal_data
    approval_required: false
    verification_required: true
```

## 包含内容

### 标准审计包内容
```yaml
standard_audit_package:
  metadata:
    - package_id
    - export_time
    - export_scope
    - export_reason
    - approver_info
  
  audit_records:
    - operation_logs
    - access_logs
    - change_logs
    - error_logs
  
  evidence_chains:
    - conclusion_evidence_mappings
    - source_references
    - confidence_scores
  
  compliance_records:
    - consent_records
    - data_processing_records
    - privacy_impact_assessments
  
  system_state:
    - configuration_snapshot
    - model_versions
    - security_status
```

### 完整证据包内容
```yaml
full_evidence_package:
  metadata:
    - package_id
    - export_time
    - case_reference
    - legal_basis
  
  all_evidences:
    - evidence_objects
    - source_documents
    - extracted_claims
  
  evidence_chains:
    - complete_chains
    - claim_mappings
    - inference_records
  
  verification_records:
    - integrity_checks
    - authenticity_verification
    - chain_validations
  
  supporting_documents:
    - policies_referenced
    - procedures_followed
    - approvals_obtained
```

## 脱敏要求

### 脱敏规则
| 数据类型 | 脱敏方法 | 说明 |
|----------|----------|------|
| 用户标识 | 假名化 | 替换为假名 |
| PII数据 | 遮蔽或删除 | 按场景处理 |
| 敏感内容 | 摘要化 | 保留摘要 |
| 内部路径 | 泛化 | 移除具体路径 |
| IP地址 | 部分遮蔽 | 保留前两段 |

### 脱敏配置
```yaml
masking_config:
  user_identifiers:
    method: "pseudonymization"
    format: "user_XXXXX"
  
  pii_data:
    method: "redact_or_mask"
    rules:
      phone: "keep_first_3"
      email: "keep_first_3_domain"
      name: "keep_first_char"
      id_number: "redact_all"
  
  sensitive_content:
    method: "summarize"
    max_length: 100
  
  internal_paths:
    method: "generalize"
    pattern: "/internal/..."
  
  ip_addresses:
    method: "partial_mask"
    format: "XXX.XXX.*.*"
```

### 脱敏验证
```yaml
masking_verification:
  checks:
    - no_unmasked_pii
    - no_identifiable_info
    - no_sensitive_paths
    - no_raw_credentials
  
  validation:
    - automated_scan
    - manual_review
    - compliance_check
```

## 审批要求

### 审批流程
```yaml
approval_flow:
  steps:
    - name: "提交申请"
      actions:
        - specify_export_scope
        - justify_export_reason
        - identify_recipient
    
    - name: "风险评估"
      actions:
        - assess_data_sensitivity
        - evaluate_export_risk
        - check_legal_basis
    
    - name: "审批决策"
      actions:
        - reviewer_evaluation
        - apply_conditions
        - grant_or_deny
    
    - name: "执行导出"
      actions:
        - apply_masking
        - generate_package
        - secure_delivery
```

### 审批条件
| 条件 | 说明 |
|------|------|
| 明确目的 | 导出目的明确 |
| 合法依据 | 有法律或合同依据 |
| 最小范围 | 仅导出必要数据 |
| 安全传输 | 传输方式安全 |
| 保留期限 | 明确保留期限 |

## 导出格式

### 支持格式
| 格式 | 说明 | 适用场景 |
|------|------|----------|
| JSON | 结构化数据 | 系统对接 |
| PDF | 文档报告 | 审计报告 |
| ZIP | 打包文件 | 完整包导出 |
| CSV | 表格数据 | 日志导出 |

### 包结构
```
audit_package_YYYYMMDD_HHMMSS/
├── manifest.json           # 包清单
├── metadata.json           # 元数据
├── audit_records/
│   ├── operations.jsonl    # 操作记录
│   ├── accesses.jsonl      # 访问记录
│   └── changes.jsonl       # 变更记录
├── evidence_chains/
│   ├── chains.jsonl        # 证据链
│   └── mappings.jsonl      # 映射关系
├── compliance/
│   ├── consents.jsonl      # 同意记录
│   └── processing.jsonl    # 处理记录
├── verification/
│   ├── integrity.json      # 完整性验证
│   └── signatures.json     # 签名信息
└── README.txt              # 说明文档
```

## 校验完整性

### 完整性校验方法
| 方法 | 说明 |
|------|------|
| 哈希校验 | 验证文件哈希 |
| 签名验证 | 验证数字签名 |
| 清单比对 | 比对manifest |
| 时间戳验证 | 验证时间戳 |

### 校验文件格式
```json
{
  "package_id": "pkg_20260406_220000",
  "verification": {
    "hash_algorithm": "sha256",
    "package_hash": "abc123...",
    "file_hashes": {
      "manifest.json": "def456...",
      "metadata.json": "ghi789...",
      "audit_records/operations.jsonl": "jkl012..."
    },
    "signature": {
      "algorithm": "rsa-sha256",
      "signature_value": "signature...",
      "signer": "system",
      "signed_at": "2026-04-06T22:00:00+08:00"
    },
    "timestamp": {
      "authority": "internal_tsa",
      "timestamp": "2026-04-06T22:00:00+08:00",
      "token": "tsa_token..."
    }
  },
  "validation_result": {
    "hash_valid": true,
    "signature_valid": true,
    "manifest_complete": true,
    "timestamp_valid": true,
    "overall_valid": true
  }
}
```

## 安全传输

### 传输方式
| 方式 | 说明 | 安全要求 |
|------|------|----------|
| 安全下载 | 平台内下载 | 需认证+审计 |
| 加密邮件 | 加密邮件发送 | 端到端加密 |
| 安全API | API拉取 | 认证+加密 |
| 物理介质 | 离线传输 | 加密+签收 |

### 传输配置
```yaml
delivery_config:
  secure_download:
    enabled: true
    authentication: required
    audit: true
    link_expiry: 24h
  
  encrypted_email:
    enabled: true
    encryption: pgp
    max_size: 50MB
  
  secure_api:
    enabled: true
    authentication: api_key
    rate_limit: 10/hour
  
  physical_media:
    enabled: false
    requires_approval: true
```

## 引用文件
- `evidence/EVIDENCE_SCHEMA.json` - 证据对象结构
- `evidence/EVIDENCE_CHAIN_POLICY.md` - 证据链规则
- `evidence/CLAIM_TO_SOURCE_MAPPING.md` - 结论来源映射
- `audit/AUDIT_POLICY.md` - 审计策略
- `reporting/EXPORT_POLICY.md` - 导出规则
