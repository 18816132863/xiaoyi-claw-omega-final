---
name: docs-write
description: Write documentation following Metabase's conversational, clear, and user-focused style. Use when creating or editing documentation files (markdown, MDX, etc.).
allowed-tools: Read, Write, Grep, Bash, Glob
---

# Documentation Writing Skill

@./../_shared/metabase-style-guide.md

## When writing documentation

### Start here

1. **Who is this for?** Match complexity to audience. Don't oversimplify hard things or overcomplicate simple ones.
2. **What do they need?** Get them to the answer fast. Nobody wants to be in docs longer than necessary.
3. **What did you struggle with?** Those common questions you had when learning? Answer them (without literally including the question).

### Writing process

**Draft:**

- Write out the steps/explanation as you'd tell a colleague
- Lead with what to do, then explain why
- Use headings that state your point: "Set SAML before adding users" not "SAML configuration timing"

**Edit:**

- Read aloud. Does it sound like you talking? If it's too formal, simplify.
- Cut anything that doesn't directly help the reader
- Check each paragraph has one clear purpose
- Verify examples actually work (don't give examples that error)

**Polish:**

- Make links descriptive (never "here")
- Backticks only for code/variables, **bold** for UI elements
- American spelling, serial commas
- Keep images minimal and scoped tight

**Format:**

- Run prettier on the file after making edits: `bun run prettier --write <file-path>`
- This ensures consistent formatting across all documentation

### Common patterns

**Instructions:**

```markdown
Run:
\`\`\`
command-to-run
\`\`\`

Then:
\`\`\`
next-command
\`\`\`

This ensures you're getting the latest changes.
```

Not: "(remember to run X before Y...)" buried in a paragraph.

**Headings:**

- "Use environment variables for configuration" ✅
- "Environment variables" ❌ (too vague)
- "How to use environment variables for configuration" ❌ (too wordy)

**Links:**

- "Check out the [SAML documentation](link)" ✅
- "Read the docs [here](link)" ❌

---
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

### Watch out for

- Describing tasks as "easy" (you don't know the reader's context)
- Using "we" when talking about Metabase features (use "Metabase" or "it")
- Formal language: "utilize", "reference", "offerings"
- Too peppy: multiple exclamation points
- Burying the action in explanation
- Code examples that don't work
- Numbers that will become outdated



### Quick reference

| Write This                 | Not This           |
| -------------------------- | ------------------ |
| people, companies          | users              |
| summarize                  | aggregate          |
| take a look at             | reference          |
| can't, don't               | cannot, do not     |
| **Filter** button          | \`Filter\` button  |
| Check out [the docs](link) | Click [here](link) |

