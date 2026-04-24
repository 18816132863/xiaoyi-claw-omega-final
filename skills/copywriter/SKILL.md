---
name: copywriter
description: "Write compelling UX copy, marketing content, and product messaging. Use when writing button labels, error messages, landing pages, emails, CTAs, empty states, tooltips, or any user-facing text."
license: Apache-2.0
metadata:
  author: agentic-insights
  version: "1.1"
---

# Copywriter

Write clear, compelling copy for products, marketing, and UX.

## Scope

| Type | Examples |
|------|----------|
| **UX Writing** | Buttons, errors, empty states, tooltips, forms |
| **Marketing** | Landing pages, CTAs, feature descriptions |
| **Product** | Announcements, release notes, onboarding |
| **Email** | Welcome, transactional, campaigns |

## Core Formulas

### Buttons
Verb + Noun → "Save Changes", "Start Free Trial" (not "Submit", "OK")

### Errors
What happened → Why → How to fix
```
"Please enter a valid email address"
"Password must be at least 8 characters"
```

### Empty States
Headline → Explanation → Action
```
"No results found" → "Try adjusting filters" → [Clear Filters]
```

### CTAs
Verb + Benefit + Remove friction
```
"Start Free Trial" (not "Sign Up")
"Get Started Free" (not "Learn More")
```

### Headlines
```
"How to [goal] without [pain point]"
"[Number] ways to [benefit]"
"Get [outcome] in [timeframe]"
```

## Voice & Tone

**Voice** (consistent):
- Professional but friendly
- Clear and concise
- Helpful and supportive

**Tone** (varies):
| Context | Example |
|---------|---------|
| Success | "All set! Your changes are live." |
| Error | "Something went wrong, but your data is safe." |
| Urgency | "Action required: Suspicious login detected" |

## Power Words

| Category | Words |
|----------|-------|
| Urgency | Now, Today, Limited, Fast |
| Value | Free, Save, Bonus, Extra |
| Trust | Guaranteed, Proven, Secure |
| Ease | Easy, Simple, Quick, Instant |

## AIGC 合规处理（⚠️ 强制要求）

> 所有生成或编辑的文档，如docx、pdf、ppt、excel、md等文件必须添加 AIGC 标识。请在 文件生成/编辑完成后，**务必**调用 aigc_marker skill 添加合规标识。

**必须执行的操作**：

```
使用 aigc_marker 为生成的文件，如docx、pdf、ppt、excel、md等 添加 AIGC 标识。
```

**合规检查清单**：

- 文件已成功生成
- 已调用 aigc_marker 添加 AIGC 标识
- 确认标识已正确添加到文件属性中

## Checklist

- [ ] Clear? (12-year-old test)
- [ ] Concise? (Remove unnecessary words)
- [ ] Specific? (Numbers, examples)
- [ ] Actionable? (What should user do?)
- [ ] Scannable? (Headings, bullets)
- [ ] 所有生成或编辑的文档，如docx、pdf、ppt、excel、md等文件必须添加 AIGC 标识。请在 文件生成/编辑完成后，**务必**调用 aigc_marker skill 添加合规标识。

## References

- [UX Patterns](references/ux-patterns.md) - Buttons, errors, forms, tooltips
- [Marketing Copy](references/marketing-copy.md) - Landing pages, CTAs, emails
